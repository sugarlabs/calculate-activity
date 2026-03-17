# -*- coding: utf-8 -*-
# calculate.py, sugar calculator, by:
#   Reinier Heeres <reinier@heeres.eu>
#   Miguel Alvarez <miguel@laptop.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
# Change log:
#    2007-07-03: rwh, first version

from gettext import gettext as _
from numerals import local as _n, standard as _s
import logging
_logger = logging.getLogger('Calculate')

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from gi.repository import Gdk
import base64

# Try to import from sugar4, provide GTK4 fallbacks if unavailable
try:
    import sugar4.profile
    from sugar4.graphics.xocolor import XoColor
except ImportError:
    # GTK4 replacement for XoColor
    class XoColor:
        """Minimal XoColor replacement for standalone execution."""
        def __init__(self, color_string="#FF0000,#FFFFFF", colors=None):
            if colors is not None:
                self.colors = colors
            else:
                parts = color_string.split(',')
                self.stroke = parts[0] if len(parts) > 0 else "#FF0000"
                self.fill = parts[1] if len(parts) > 1 else "#FFFFFF"
                self.colors = None

        def get_fill_color(self):
            if self.colors:
                return self.colors[0]
            return getattr(self, 'fill', '#FFFFFF')

        def get_stroke_color(self):
            if self.colors:
                return self.colors[1] if len(self.colors) > 1 else '#000000'
            return getattr(self, 'stroke', '#000000')

        def to_string(self):
            return f"{self.get_stroke_color()},{self.get_fill_color()}"

    class _FakeProfile:
        _color = None
        
        @staticmethod
        def get_color():
            if not _FakeProfile._color:
                _FakeProfile._color = XoColor()
            return _FakeProfile._color
    
    sugar4 = type('module', (), {'profile': _FakeProfile})()

from shareable_activity import ShareableActivity
from layout import CalcLayout
from mathlib import MathLib
from astparser import AstParser, ParserError, ParseError, RuntimeError
from svgimage import SVGImage

from decimal import Decimal
from rational import Rational


def findchar(text, chars, ofs=0):
    '''
    Find a character in set <chars> starting from offset ofs.
    Everything between brackets '()' is ignored.
    '''

    level = 0
    for i in range(ofs, len(text)):
        if text[i] in chars and level == 0:
            return i
        elif text[i] == '(':
            level += 1
        elif text[i] == ')':
            level -= 1

    return -1


def _textview_realize_cb(widget):
    '''Change textview properties once window is created.'''
    # GTK4: Use event controller for cursor instead of window manipulation
    cursor = Gdk.Cursor.new_from_name('grab')
    widget.set_cursor(cursor)
    return False


class Equation:

    def __init__(self, label=None, eqn=None, res=None, col=None, owner=None,
                 eqnstr=None, ml=None):

        if eqnstr is not None:
            self.parse(eqnstr)
        elif eqn is not None:
            self.set(label, eqn, res, col, owner)

        self.ml = ml

    def set(self, label, eqn, res, col, owner):
        """Set equation properties."""

        self.label = label
        self.equation = eqn
        self.result = res
        self.color = col
        self.owner = owner

    def __str__(self):
        if isinstance(self.result, SVGImage):
            svg_data = "<svg>" + base64.b64encode(self.result.get_svg_data())
            return "%s;%s;%s;%s;%s\n" % \
                (self.label, self.equation, svg_data,
                 self.color.to_string(), self.owner)
        else:
            return "%s;%s;%s;%s;%s\n" % \
                (self.label, self.equation, self.result,
                 self.color.to_string(), self.owner)

    def parse(self, str):
        """Parse equation object string representation."""

        str = str.rstrip("\r\n")
        k = str.split(';')
        if len(k) != 5:
            _logger.error(_('Equation.parse() string invalid (%s)'), str)
            return False

        if k[2].startswith("<svg>"):
            k[2] = SVGImage(data=base64.b64decode(k[2][5:]))

        # Should figure out how to use MathLib directly in a non-hacky way
        else:
            try:
                k[2] = Decimal(k[2])
            except Exception:
                pass

        self.set(k[0], k[1], k[2], XoColor(color_string=k[3]), k[4])

    def determine_font_size(self, *tags):
        size = 0
        for tag in tags:
            try:
                size = max(size, tag.get_property('size'))
            except:
                pass
        return size

    def append_with_superscript_tags(self, buf, text, *tags):
        '''Add a text to a Gtk.TextBuffer with superscript tags.'''
        fontsize = self.determine_font_size(*tags)
        _logger.debug('font-size: %d', fontsize)
        tagsuper = buf.create_tag(rise=fontsize / 2)

        ENDSET = list(AstParser.DIADIC_OPS)
        ENDSET.extend((',', '(', ')'))
        ASET = list(AstParser.DIADIC_OPS)
        ofs = 0
        bracket_level = 0
        level = 0
        while ofs <= len(text) and text.find('**', ofs) != -1:
            nextofs = text.find('**', ofs)
            buf.insert_with_tags(buf.get_end_iter(), text[ofs:nextofs], *tags)
            nextofs2 = findchar(text, ENDSET, nextofs + 2)
            for i in range(nextofs, len(text)):
                if text[i] in ['(', '+', '-', ')']:
                    if text[i] == '(':
                        bracket_level = bracket_level + 1
                    elif text[i] == ')':
                        nextofs2 = i + 1
                        bracket_level = bracket_level - 1
                        if bracket_level == 0:
                            break
                    elif text[i] == '+':
                        if level == 0 and bracket_level == 0:
                            nextofs2 = findchar(text, ASET, i)
                            break
                        if bracket_level == 0:
                            nextofs2 = findchar(text, ASET, i + 1)
                            break
                    elif text[i] == '-':
                        if bracket_level == 0:
                            if i == nextofs + 2:
                                nextofs2 = findchar(text, ASET, i + 1)
                                break
                            else:
                                nextofs2 = findchar(text, ASET, i)
                                break

            _logger.debug('nextofs2: %d, char=%c', nextofs2, text[nextofs2])
            if nextofs2 == -1:
                nextofs2 = len(text)
            buf.insert_with_tags(
                buf.get_end_iter(), text[nextofs + 2:nextofs2],
                tagsuper, *tags)
            ofs = nextofs2

        if ofs < len(text):
            buf.insert_with_tags(buf.get_end_iter(), text[ofs:], *tags)

    def create_lasteq_textbuf(self):
        '''
        Return a Gtk.TextBuffer properly formatted for last equation
        Gtk.TextView.
        '''

        is_error = isinstance(self.result, ParserError)
        buf = Gtk.TextBuffer()
        tagsmallnarrow = buf.create_tag(font=CalcLayout.FONT_SMALL_NARROW)
        tagbignarrow = buf.create_tag(font=CalcLayout.FONT_BIG_NARROW)
        tagbigger = buf.create_tag(font=CalcLayout.FONT_BIGGER)
        tagjustright = buf.create_tag(justification=Gtk.Justification.RIGHT)
        tagred = buf.create_tag(foreground='#FF0000')

        # Add label and equation
        if len(self.label) > 0:
            labelstr = '%s:' % self.label
            buf.insert_with_tags(buf.get_end_iter(), labelstr, tagbignarrow)
        eqnoffset = buf.get_end_iter().get_offset()
        eqnstr = '%s\n' % str(self.equation)
        if is_error:
            buf.insert_with_tags(buf.get_end_iter(), eqnstr, tagbignarrow)
        else:
            self.append_with_superscript_tags(buf, eqnstr, tagbignarrow)

        # Add result
        if type(self.result) in (bytes, str):
            resstr = str(self.result)
            resstr = resstr.rstrip('0').rstrip('.') \
                if '.' in resstr else resstr
            buf.insert_with_tags(buf.get_end_iter(), resstr,
                                 tagsmallnarrow, tagjustright)
        elif is_error:
            resstr = str(self.result)
            resstr = resstr.rstrip('0').rstrip('.') \
                if '.' in resstr else resstr
            buf.insert_with_tags(buf.get_end_iter(), resstr, tagsmallnarrow)
            range = self.result.get_range()
            eqnstart = buf.get_iter_at_offset(eqnoffset + range[0])
            eqnend = buf.get_iter_at_offset(eqnoffset + range[1])
            buf.apply_tag(tagred, eqnstart, eqnend)
        elif not isinstance(self.result, SVGImage):
            resstr = self.ml.format_number(self.result)
            resstr = str(resstr).rstrip('0').rstrip('.') \
                if '.' in resstr else resstr
            self.append_with_superscript_tags(buf, resstr, tagbigger,
                                              tagjustright)

        return buf

    def create_history_object(self):
        """
        Create a history object for this equation.
        In case of an SVG result this will be the image, otherwise it will
        return a properly formatted Gtk.TextView.
        """

        if isinstance(self.result, SVGImage):
            return self.result.get_image()

        w = Gtk.TextView()
        # GTK4: Use CSS classes for styling instead of custom colors
        w.add_css_class("calculator-equation")
        w.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        # GTK4: set_border_window_size is removed, use CSS margins instead
        w.set_margin_start(4)
        w.set_margin_end(4)
        w.set_margin_top(4)
        w.set_margin_bottom(4)
        w.connect('realize', _textview_realize_cb)
        buf = w.get_buffer()

        tagsmall = buf.create_tag(font=CalcLayout.FONT_SMALL)
        tagsmallnarrow = buf.create_tag(font=CalcLayout.FONT_SMALL_NARROW)
        tagbig = buf.create_tag(font=CalcLayout.FONT_BIG,
                                justification=Gtk.Justification.RIGHT)
        # GTK4: Use Gdk.RGBA.parse() instead of Gdk.color_parse()
        fill_color = Gdk.RGBA()
        fill_color.parse(self.color.get_fill_color())
        bright = (fill_color.red + fill_color.green + fill_color.blue) / 3.0
        if bright < 0.5:
            col = 'white'
        else:
            col = 'black'
        tagcolor = buf.create_tag(foreground=col)

        # Add label, equation and result
        if len(self.label) > 0:
            labelstr = '%s:' % self.label
            buf.insert_with_tags(buf.get_end_iter(), labelstr, tagsmallnarrow)
        eqnstr = '%s\n' % str(self.equation)
        self.append_with_superscript_tags(buf, eqnstr, tagsmall)

        resstr = self.ml.format_number(self.result)
        resstr = str(resstr).rstrip('0').rstrip('.') \
            if '.' in resstr else resstr
        if len(resstr) > 30:
            restag = tagsmall
        else:
            restag = tagbig
        self.append_with_superscript_tags(buf, resstr, restag)

        buf.apply_tag(tagcolor, buf.get_start_iter(), buf.get_end_iter())

        return w


class Calculate(ShareableActivity):

    TYPE_FUNCTION = 1
    TYPE_OP_PRE = 2
    TYPE_OP_POST = 3
    TYPE_TEXT = 4

    SELECT_NONE = 0
    SELECT_SELECT = 1
    SELECT_TAB = 2

    KEYMAP = {
        'Return': lambda o: o.process(),
        'period': '.',
        'equal': '=',
        'plus': '+',
        'minus': '-',
        'asterisk': '*',
        'multiply': '×',
        'divide': '÷',
        'slash': '/',
        'BackSpace': lambda o: o.remove_character(-1),
        'Delete': lambda o: o.remove_character(1),
        'parenleft': '(',
        'parenright': ')',
        'exclam': '!',
        'ampersand': '&',
        'bar': '|',
        'asciicircum': '^',
        'less': '<',
        'greater': '>',
        'percent': '%',
        'comma': ',',
        'underscore': '_',
        'Left': lambda o: o.move_left(),
        'Right': lambda o: o.move_right(),
        'Up': lambda o: o.get_older(),
        'Down': lambda o: o.get_newer(),
        'colon': lambda o: o.label_entered(),
        'Home': lambda o: o.text_entry.set_position(0),
        'End': lambda o: o.text_entry.set_position(
            len(o.text_entry.get_text())),
        'Tab': lambda o: o.tab_complete(),
    }

    CTRL_KEYMAP = {
        'c': lambda o: o.text_copy(),
        'v': lambda o: o.text_paste(),
        'x': lambda o: o.text_cut(),
        'q': lambda o: o.close(),
        'a': lambda o: o.text_select_all(),
    }

    SHIFT_KEYMAP = {
        'Left': lambda o: o.expand_selection(-1),
        'Right': lambda o: o.expand_selection(1),
        'Home': lambda o: o.expand_selection(-1000),
        'End': lambda o: o.expand_selection(1000),
    }

    IDENTIFIER_CHARS = \
        "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_ "

    def __init__(self, handle):
        ShareableActivity.__init__(self, handle)

        self.old_eqs = []

        self.ml = MathLib()
        self.parser = AstParser(self.ml)

        # These will result in 'Ans <operator character>' being inserted
        self._chars_ans_diadic = [op[0]
                                  for op in self.parser.get_diadic_operators()]
        if '-' in self._chars_ans_diadic:
            self._chars_ans_diadic.remove('-')

        self.KEYMAP['multiply'] = self.ml.mul_sym
        self.KEYMAP['divide'] = self.ml.div_sym
        self.KEYMAP['equal'] = self.ml.equ_sym

        # GTK4: Clipboard will be initialized lazily when needed
        self._clipboard = None
        self.select_reason = self.SELECT_SELECT
        self.buffer = ""
        self.showing_version = 0
        self.showing_error = False
        self.ans_inserted = False
        self.show_vars = False

        # GTK4: Use EventControllerKey instead of key_press_event signal
        key_controller = Gtk.EventControllerKey.new()
        key_controller.connect("key-pressed", self.keypress_cb)
        self.add_controller(key_controller)
        
        self.connect("destroy", self.cleanup_cb)
        self.color = sugar4.profile.get_color()

        self.layout = CalcLayout(self)
        self.label_entry = self.layout.label_entry
        self.text_entry = self.layout.text_entry
        self.last_eq_sig = None
        self.last_eqn_textview = None

        # GTK4: Connect to text_entry 'changed' signal for live preview
        self.text_entry.connect('changed', self._on_text_entry_changed)

        self.reset()
        self.layout.show_it()

        # Connect to 'joined' signal for collaboration (if available in sugar4)
        try:
            self.connect('joined', self._joined_cb)
        except TypeError:
            # Signal not available in standalone mode (no sugar4)
            pass

        self.parser.log_debug_info()

    def ignore_key_cb(self, widget, event):
        # GTK4: key event handlers return Gdk.EVENT_STOP to stop propagation
        return Gdk.EVENT_STOP

    def cleanup_cb(self, arg):
        _logger.debug('Cleaning up...')

    @property
    def clipboard(self):
        """Lazy-initialize clipboard on first access."""
        if self._clipboard is None:
            try:
                display = Gdk.Display.get_default()
                if display is not None:
                    self._clipboard = display.get_clipboard()
            except Exception:
                pass
        return self._clipboard

    def _apply_textview_colors(self, textview, color):
        """GTK4 helper: Apply XoColor colors to a textview using CSS."""
        # In GTK4, we use CSS to style widgets
        # For now, we access the RGBA components directly from the color strings
        fill_rgba = Gdk.RGBA()
        fill_rgba.parse(color.get_fill_color())
        stroke_rgba = Gdk.RGBA()
        stroke_rgba.parse(color.get_stroke_color())
        
        # Create CSS provider with background color
        css = f".calc-history {{\n  background-color: rgba({int(stroke_rgba.red*255)}, {int(stroke_rgba.green*255)}, {int(stroke_rgba.blue*255)}, {stroke_rgba.alpha});\n}}"
        provider = Gtk.CssProvider()
        try:
            provider.load_from_data(css.encode())
            context = textview.get_style_context()
            context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            context.add_class("calc-history")
        except Exception as e:
            _logger.warning("Failed to apply CSS styling: %s", e)

    def equation_pressed_cb(self, eqn):
        """Callback for when an equation box is clicked."""

        if isinstance(eqn.result, SVGImage):
            return True

        if len(eqn.label) > 0:
            text = eqn.label
        else:
            # don't insert plain text
            if type(eqn.result) in (bytes, str):
                text = ''
            else:
                text = self.parser.ml.format_number(eqn.result)
                text = text.rstrip('0').rstrip('.') if '.' in text else text

        self.button_pressed(self.TYPE_TEXT, text)
        return True

    def set_last_equation(self, eqn, show_full=True):
        """Set the 'last equation' TextView.
        
        Args:
            eqn: the equation object
            show_full: if True, show equation + result; if False, show only result
        """

        if self.last_eq_sig is not None:
            self.layout.last_eq.disconnect(self.last_eq_sig)
            self.last_eq_sig = None

        # GTK4: Try to connect to button-press-event, fall back if unavailable
        if not isinstance(eqn.result, ParserError):
            try:
                self.last_eq_sig = self.layout.last_eq.connect(
                    'button-press-event',
                    lambda a1, a2, e: self.equation_pressed_cb(e), eqn)
            except TypeError:
                # Signal may not exist in GTK4, skip connection
                pass

        if show_full:
            # Show full equation + result (for live preview)
            buf = eqn.create_lasteq_textbuf()
        else:
            # Show only the result (for final display after pressing =)
            buf = Gtk.TextBuffer()
            res_str = str(eqn.result)
            res_str = res_str.rstrip('0').rstrip('.') if '.' in res_str else res_str
            buf.set_text(res_str)
        
        self.layout.last_eq.set_buffer(buf)
        # GTK4: Make sure the widget is visible and focused
        self.layout.last_eq.set_visible(True)

    def set_error_equation(self, eqn):
        """Set equation with error markers. Since set_last_equation implements
        this we can just forward the call."""
        # Show full equation for error display
        self.set_last_equation(eqn, show_full=True)

    def clear_equations(self):
        """Clear the list of old equations."""
        self.old_eqs = []
        self.showing_version = 0

    def add_equation(self, eq, prepend=False, drawlasteq=False, tree=None):
        """
        Insert equation in the history list and set variable if assignment.
        Input:
            eq: the equation object
            prepend: if True, prepend to list, else append
            drawlasteq: if True, draw in 'last equation' textbox and queue the
            buffer to be added to the history next time an equation is added.
            tree: the parsed tree, this will be used to set the label variable
            so that the equation can be used symbolicaly.
            """
        if eq.equation is not None and len(eq.equation) > 0:
            if prepend:
                self.old_eqs.insert(0, eq)
            else:
                self.old_eqs.append(eq)

            self.showing_version = len(self.old_eqs)

        if self.last_eqn_textview is not None and drawlasteq:
            # Prepending here should be the opposite: prepend -> eqn on top.
            # We always own this equation
            self.layout.add_equation(self.last_eqn_textview, True,
                                     prepend=not prepend)
            self.last_eqn_textview = None

        if eq.label is not None and len(eq.label) > 0:
            w = self.create_var_textview(eq.label, eq.result)
            if w is not None:
                self.layout.add_variable(eq.label, w)

            if tree is None:
                tree = self.parser.parse(eq.equation)
            try:
                self.parser.set_var(eq.label, tree)
            except Exception as e:
                eq.result = ParseError(str(e), 0, "")
                self.set_error_equation(eq)
                return

        own = (eq.owner == self.get_owner_id())
        w = eq.create_history_object()
        # GTK4: Try to connect button-press-event, may not exist
        try:
            w.connect('button-press-event', lambda w,
                      e: self.equation_pressed_cb(eq))
        except TypeError:
            # Signal may not exist in GTK4
            pass
        if drawlasteq:
            self.set_last_equation(eq)

            # SVG images can't be plotted in last equation window
            if isinstance(eq.result, SVGImage):
                self.layout.add_equation(w, own, prepend=not prepend)
            else:
                self.last_eqn_textview = w
        else:
            self.layout.add_equation(w, own, prepend=not prepend)

    def process_async(self, eqn):
        """Parse and process an equation asynchronously."""

    def _on_text_entry_changed(self, widget):
        """Handle text entry changes for live preview of results."""
        text = self.text_entry.get_text().strip()
        
        # If empty, clear the output
        if not text:
            self.layout.last_eq.set_buffer(Gtk.TextBuffer())
            return
        
        # Try to parse and show a preview
        try:
            s = _s(text)
            tree = self.parser.parse(s)
            res = self.parser.evaluate(tree)
            
            # Create a temporary equation for display
            eqn = Equation('', _n(s), _n(str(res)), self.color,
                          self.get_owner_id(), ml=self.ml)
            buf = eqn.create_lasteq_textbuf()
            self.layout.last_eq.set_buffer(buf)
        except Exception:
            # If there's an error during parsing, just clear the output
            # Don't show errors until user presses Enter
            self.layout.last_eq.set_buffer(Gtk.TextBuffer())

    def process(self):
        """Parse the equation entered and show the result."""

        s = _s(self.text_entry.get_text())
        
        # GTK4: Don't process if input is empty
        if not s or s.strip() == '':
            return False
        
        label = self.label_entry.get_text()
        _logger.debug('process(): parsing %r, label: %r', s, label)
        try:
            tree = self.parser.parse(s)
            res = self.parser.evaluate(tree)
        except ParserError as e:
            res = e
            self.showing_error = True

        if isinstance(res, str) and res.find('</svg>') > -1:
            res = SVGImage(data=res)

        _logger.debug('Result: %r', res)

        # Check whether assigning this label would cause recursion
        if not isinstance(res, ParserError) and len(label) > 0:
            lastpos = self.parser.get_var_used_ofs(label)
            if lastpos is not None:
                res = RuntimeError(
                    _('Can not assign label: will cause recursion'),
                    lastpos)

        # If parsing went ok, see if we have to replace the previous answer
        # to get a (more) exact result
        if self.ans_inserted and not isinstance(res, ParserError) \
                and not isinstance(res, SVGImage):
            ansvar = self.format_insert_ans()
            pos = s.find(ansvar)
            if len(ansvar) > 6 and pos != -1:
                s2 = s.replace(ansvar, 'LastEqn')
                _logger.debug(
                    'process(): replacing previous answer %r: %r', ansvar, s2)
                tree = self.parser.parse(s2)
                res = self.parser.evaluate(tree)

        if isinstance(res, ParserError):
            eqn = Equation(label, _n(s), res, self.color,
                           self.get_owner_id(), ml=self.ml)
            self.set_error_equation(eqn)
        else:
            eqn = Equation(label, _n(s), _n(str(res)), self.color,
                           self.get_owner_id(), ml=self.ml)
            # Don't draw to last_eq here - we'll handle it after setting the variable
            self.add_equation(eqn, drawlasteq=False, tree=tree)
            self.send_message("add_eq", value=str(eqn))

            self.parser.set_var('Ans', eqn.result)

            # Setting LastEqn to the parse tree would certainly be faster,
            # however, it introduces recursion problems
            self.parser.set_var('LastEqn', eqn.result)

            self.showing_error = False
            self.ans_inserted = False
            # GTK4: Show only the result (not the equation) after pressing =
            self.set_last_equation(eqn, show_full=False)
            # GTK4: Block signal before clearing to avoid triggering live preview
            self.text_entry.handler_block_by_func(self._on_text_entry_changed)
            self.text_entry.set_text('')
            self.label_entry.set_text('')
            self.text_entry.handler_unblock_by_func(self._on_text_entry_changed)
            # Return focus to input field for next calculation
            self.text_entry.grab_focus()

        return res is not None

    def create_var_textview(self, name, value):
        """Create a Gtk.TextView for a variable."""

        reserved = ["Ans", "LastEqn", "help"]
        if name in reserved:
            return None
        w = Gtk.TextView()
        # GTK4: Use CSS classes for styling instead of custom colors
        w.add_css_class("calculator-variable")
        w.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        # GTK4: set_border_window_size is removed, use CSS margins instead
        w.set_margin_start(4)
        w.set_margin_end(4)
        w.set_margin_top(4)
        w.set_margin_bottom(4)
        w.connect('realize', _textview_realize_cb)
        buf = w.get_buffer()

        # GTK4: Use Gdk.RGBA.parse() instead of Gdk.color_parse()
        fill_color = Gdk.RGBA()
        fill_color.parse(self.color.get_fill_color())
        bright = (fill_color.red + fill_color.green + fill_color.blue) / 3.0
        if bright < 0.5:
            col = 'white'
        else:
            col = 'black'

        tag = buf.create_tag(font=CalcLayout.FONT_SMALL_NARROW,
                             foreground=col)
        text = '%s:' % (name)
        buf.insert_with_tags(buf.get_end_iter(), text, tag)
        tag = buf.create_tag(font=CalcLayout.FONT_SMALL,
                             foreground=col)
        text = '%s' % (str(value))
        buf.insert_with_tags(buf.get_end_iter(), text, tag)

        return w

    def clear(self):
        self.text_entry.set_text('')
        self.text_entry.grab_focus()
        return True

    def reset(self):
        self.clear()
        return True

#
# Journal functions
#

    def write_file(self, file_path):
        """Write journal entries, Calculate Journal Version (cjv) 1.0"""

        _logger.info(_('Writing to journal (%s)'), file_path)

        f = open(file_path, 'w')
        f.write("cjv 1.0\n")

        sel = self.text_entry.get_selection_bounds()
        pos = self.text_entry.get_position()
        if len(sel) == 0:
            sel = (pos, pos)
            f.write("%s;%d;%d;%d\n" %
                    (self.text_entry.get_text(), pos, sel[0], sel[1]))

        # In reverse order
        for eq in self.old_eqs:
            f.write(str(eq))

        f.close()

    def read_file(self, file_path):
        """Read journal entries, version 1.0"""

        _logger.info('Reading from journal (%s)', file_path)

        f = open(file_path, 'r')
        str = f.readline().rstrip("\r\n")   # chomp
        k = str.split()
        if len(k) != 2:
            _logger.error('Unable to determine version')
            return False

        version = k[1]
        if len(version) > 1 and version[0:2] == "1.":
            _logger.info('Reading journal entry (version %s)', version)

            str = f.readline().rstrip("\r\n")
            k = str.split(';')
            if len(k) != 4:
                _logger.error('State line invalid (%s)', str)
                return False

            self.text_entry.set_text(k[0])
            self.text_entry.set_position(int(k[1]))
            if k[2] != k[3]:
                self.text_entry.select_region(int(k[2]), int(k[3]))

            self.clear_equations()
            for str in f:
                eq = Equation(eqnstr=str, ml=self.ml)
                self.add_equation(eq, prepend=False)

            return True
        else:
            _logger.error(
                'Unable to read journal entry, unknown version (%s)', version)
            return False

#
# User interaction functions
#

    def remove_character(self, dir):
        pos = self.text_entry.get_position()
        sel = self.text_entry.get_selection_bounds()
        if len(sel) == 0:
            if pos + dir <= len(self.text_entry.get_text()) and pos + dir >= 0:
                if dir < 0:
                    self.text_entry.delete_text(pos + dir, pos)
                    pos -= 1
                else:
                    self.text_entry.delete_text(pos, pos + dir)
                    pos += 1
        else:
            self.text_entry.delete_text(sel[0], sel[1])
        self.text_entry.grab_focus()
        self.text_entry.set_position(pos)

    def move_left(self):
        pos = self.text_entry.get_position()
        if pos > 0:
            pos -= 1
            self.text_entry.set_position(pos)
        self.text_entry.grab_focus()
        self.text_entry.set_position(pos)

    def move_right(self):
        pos = self.text_entry.get_position()
        if pos < len(self.text_entry.get_text()):
            pos += 1
            self.text_entry.set_position(pos)
        self.text_entry.grab_focus()
        self.text_entry.set_position(pos)

    def label_entered(self):
        if len(self.label_entry.get_text()) > 0:
            return
        pos = self.text_entry.get_position()
        str = self.text_entry.get_text()
        self.label_entry.set_text(str[:pos])
        self.text_entry.set_text(str[pos:])

    def tab_complete(self):

        # Get start of variable name
        str = self.text_entry.get_text()
        if len(str) == 0:
            return

        sel = self.text_entry.get_selection_bounds()
        if len(sel) == 0:
            end_ofs = self.text_entry.get_position()
        else:
            end_ofs = sel[0]
        start_ofs = end_ofs - 1
        while start_ofs > 0 and str[start_ofs - 1] in self.IDENTIFIER_CHARS:
            start_ofs -= 1
        if end_ofs - start_ofs <= 0:
            return False
        partial_name = str[start_ofs:end_ofs]
        _logger.debug('tab-completing %s...', partial_name)

        # Lookup matching variables
        vars = self.parser.get_names(start=partial_name)
        if len(vars) == 0:
            return False

        # Nothing selected, select first match
        if len(sel) == 0:
            name = vars[0]
            self.text_entry.set_text(str[:start_ofs] + name + str[end_ofs:])

        # Select next matching variable
        else:
            full_name = str[start_ofs:sel[1]]
            if full_name not in vars:
                name = vars[0]
            else:
                name = vars[(vars.index(full_name) + 1) % len(vars)]
            self.text_entry.set_text(str[:start_ofs] + name + str[sel[1]:])

        self.text_entry.set_position(start_ofs + len(name))
        self.text_entry.select_region(end_ofs, start_ofs + len(name))
        self.select_reason = self.SELECT_TAB
        return True

    # Selection related functions

    def expand_selection(self, dir):
        # logger.info('Expanding selection in dir %d', dir)
        sel = self.text_entry.get_selection_bounds()
        slen = len(self.text_entry.get_text())
        pos = self.text_entry.get_position()
        if len(sel) == 0:
            sel = (pos, pos)
        if dir < 0:
            # apparently no such thing as a cursor position during select
            newpos = max(0, sel[0] + dir)
            self.text_entry.set_position(newpos)
            self.text_entry.select_region(newpos, sel[1])
        elif dir > 0:
            newpos = min(sel[1] + dir, slen)
            self.text_entry.set_position(newpos)
            self.text_entry.select_region(sel[0], newpos)
        self.select_reason = self.SELECT_SELECT

    def text_copy(self):
        if self.layout.graph_selected is not None:
            # GTK4: set_image replaced with set_pixbuf or async API
            pixbuf = self.layout.graph_selected.get_child().get_paintable()
            # Note: GTK4 clipboard operations are async, this is synchronous fallback
            if self.clipboard is not None:
                self.clipboard.set_texture(pixbuf)
            self.layout.toggle_select_graph(self.layout.graph_selected)
        else:
            str = self.text_entry.get_text()
            sel = self.text_entry.get_selection_bounds()
            # _logger.info('text_copy, sel: %r, str: %s', sel, str)
            if len(sel) == 2:
                (start, end) = sel
                # GTK4: set_text no longer takes -1, just pass the string
                if self.clipboard is not None:
                    self.clipboard.set_text(str[start:end])

    def text_select_all(self):
        end = self.text_entry.get_text_length()
        self.text_entry.select_region(0, end)

    def get_clipboard_text(self):
        # GTK4: Clipboard operations are async. For compatibility, attempt sync fallback
        # In a real GTK4 app, this should use read_text_async
        try:
            if self.clipboard is not None:
                text = self.clipboard.get_text()
            else:
                text = None
        except Exception:
            # Fallback for async-only clipboard
            text = None
        if text is None:
            return ""
        else:
            return text

    def text_paste(self):
        self.button_pressed(self.TYPE_TEXT, self.get_clipboard_text())

    def text_cut(self):
        self.text_copy()
        self.remove_character(1)

    def keypress_cb(self, widget, keyval, keycode, state):
        # GTK4: EventControllerKey passes different parameters
        if not self.text_entry.is_focus():
            return Gdk.EVENT_PROPAGATE

        key = Gdk.keyval_name(keyval)
        if keycode == 219:
            if (state & Gdk.ModifierType.SHIFT_MASK):
                key = 'divide'
            else:
                key = 'multiply'
        _logger.debug('Key: %s (%r, %r)', key,
                      keyval, keycode)

        if state & Gdk.ModifierType.CONTROL_MASK:
            if key in self.CTRL_KEYMAP:
                f = self.CTRL_KEYMAP[key]
                return Gdk.EVENT_STOP if f(self) else Gdk.EVENT_PROPAGATE
        elif (state & Gdk.ModifierType.SHIFT_MASK) and \
                key in self.SHIFT_KEYMAP:
            f = self.SHIFT_KEYMAP[key]
            return Gdk.EVENT_STOP if f(self) else Gdk.EVENT_PROPAGATE
        elif str(key) in self.IDENTIFIER_CHARS:
            self.button_pressed(self.TYPE_TEXT, key)
        elif key in self.KEYMAP:
            f = self.KEYMAP[key]
            if isinstance(f, str) or \
                    isinstance(f, str):
                self.button_pressed(self.TYPE_TEXT, f)
            else:
                return Gdk.EVENT_STOP if f(self) else Gdk.EVENT_PROPAGATE

        return Gdk.EVENT_STOP

    def get_older(self):
        self.showing_version = max(0, self.showing_version - 1)
        if self.showing_version == len(self.old_eqs) - 1:
            self.buffer = self.text_entry.get_text()
        if len(self.old_eqs) > 0:
            self.text_entry.set_text(
                self.old_eqs[self.showing_version].equation)

    def get_newer(self):
        self.showing_version = min(len(self.old_eqs), self.showing_version + 1)
        if self.showing_version == len(self.old_eqs):
            self.text_entry.set_text(self.buffer)
        else:
            self.text_entry.set_text(
                self.old_eqs[self.showing_version].equation)

    def add_text(self, input_str):
        self.button_pressed(self.TYPE_TEXT, input_str)

    # This function should be split up properly
    def button_pressed(self, str_type, input_str):
        sel = self.text_entry.get_selection_bounds()
        pos = self.text_entry.get_position()

        # If selection by tab completion just manipulate end
        if len(sel) == 2 and self.select_reason != self.SELECT_SELECT:
            pos = sel[1]
            sel = ()

        self.text_entry.grab_focus()
        if len(sel) == 2:
            (start, end) = sel
            text = self.text_entry.get_text()
        elif len(sel) != 0:
            _logger.error('button_pressed(): len(sel) != 0 or 2')
            return False

        if str_type == self.TYPE_FUNCTION:
            if len(sel) == 0:
                self.text_entry.insert_text(input_str + '()', pos)
                self.text_entry.set_position(pos + len(input_str) + 1)
            else:
                self.text_entry.set_text(
                    text[:start] + input_str + '(' + text[start:end] + ')' +
                    text[end:])
                self.text_entry.set_position(end + len(input_str) + 2)

        elif str_type == self.TYPE_OP_PRE:
            if len(sel) == 2:
                pos = start
            self.text_entry.insert_text(input_str, pos)
            self.text_entry.set_position(pos + len(input_str))

        elif str_type == self.TYPE_OP_POST:
            if len(sel) == 2:
                pos = end
            elif pos == 0:
                ans = self.format_insert_ans()
                input_str = ans + input_str
                self.ans_inserted = True
            self.text_entry.insert_text(input_str, pos)
            self.text_entry.set_position(pos + len(input_str))

        elif str_type == self.TYPE_TEXT:
            tlen = len(self.text_entry.get_text())
            if len(sel) == 2:
                tlen -= (end - start)

            if tlen == 0 and (input_str in self._chars_ans_diadic) and \
                    self.parser.get_var('Ans') is not None and \
                    type(self.parser.get_var('Ans')) is not str:
                ans = self.format_insert_ans()
                self.text_entry.set_text(ans + input_str)
                self.text_entry.set_position(len(ans) + len(input_str))
                self.ans_inserted = True
            elif len(sel) == 2:
                self.text_entry.set_text(text[:start] + input_str + text[end:])
                self.text_entry.set_position(
                    pos + start - end + len(input_str))
            else:
                self.text_entry.insert_text(input_str, pos)
                self.text_entry.set_position(pos + len(input_str))

        else:
            _logger.error(_('button_pressed(): invalid type'))

    def message_received(self, msg, **kwargs):
        _logger.debug('Message received: %s(%r)', msg, kwargs)

        value = kwargs.get('value', None)
        if msg == "add_eq":
            eq = Equation(eqnstr=str(value), ml=self.ml)
            self.add_equation(eq)
        elif msg == "req_sync":
            data = []
            for eq in self.old_eqs:
                data.append(str(eq))
            self.send_message("sync", value=data)
        elif msg == "sync":
            self.clear_equations()
            for eq_str in value:
                _logger.debug('receive_message: %s', str(eq_str))
                self.add_equation(Equation(eqnstr=str(eq_str)), ml=self.ml)

    def _joined_cb(self, gobj):
        _logger.debug('Requesting synchronization')
        self.send_message('req_sync')

    def format_insert_ans(self):
        ans = self.parser.get_var('Ans')
        if isinstance(ans, Rational):
            return str(ans)
        elif ans is not None:
            return self.ml.format_number(ans)
        else:
            return ''


def main():
    # GTK4: TOPLEVEL is the default, no need to specify it
    win = Gtk.Window()
    Calculate(win)
    Gtk.main()
    return 0


if __name__ == "__main__":
    main()
