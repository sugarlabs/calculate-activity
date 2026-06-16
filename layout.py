# -*- coding: utf-8 -*-
# layout.py, sugar calculator, by:
#   Reinier Heeres <reinier@heeres.eu>
#   Miguel Alvarez <miguel@laptop.org>
#   Aneesh Dogra <lionaneesh@gmail.com>
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

from gettext import gettext as _
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango
import sugar4.profile
from sugar4.graphics.style import FONT_SIZE
from sugar4.graphics.combobox import ComboBox
from toolbars import EditToolbar
from toolbars import AlgebraToolbar
from toolbars import TrigonometryToolbar
from toolbars import BooleanToolbar
from toolbars import MiscToolbar

from numerals import local as _n

try:
    from sugar4.graphics.toolbarbox import ToolbarButton, ToolbarBox
    from sugar4.activity.widgets import ActivityToolbarButton
    from sugar4.activity.widgets import StopButton
except ImportError:
    pass


class CalcLayout:

    FONT_SMALL_POINTS = FONT_SIZE * 2
    FONT_SMALL = "sans %d" % FONT_SMALL_POINTS
    FONT_SMALL_NARROW = "sans italic %d" % FONT_SMALL_POINTS
    FONT_BIG_POINTS = FONT_SIZE * 2.8
    FONT_BIG = "sans bold %d" % FONT_BIG_POINTS
    FONT_BIG_NARROW = "sans italic %d" % FONT_BIG_POINTS
    FONT_BIGGER_POINTS = FONT_SIZE * 3.6
    FONT_BIGGER = "sans bold %d" % FONT_BIGGER_POINTS

    def __init__(self, parent):
        self._parent = parent

        self._own_equations = []
        self._other_equations = []
        self._showing_history = True
        self._showing_all_history = True
        self._var_textviews = {}
        self.graph_selected = None

        self.create_dialog()

    def create_color(self, rf, gf, bf):
        return Gdk.RGBA(red=rf, green=gf, blue=bf, alpha=1.0)

    def create_button_data(self):
        """Create a list with button information. We need to do that here
        because we want to include the lambda functions."""
        
        mul_sym = self._parent.ml.mul_sym
        div_sym = self._parent.ml.div_sym
        equ_sym = self._parent.ml.equ_sym

        self.button_data = [
            # [x, y, width, label, bgcol, cb]
            [0, 0, 2, 1, '\u2190', self.col_gray3,
                lambda w: self._parent.move_left()],
            [2, 0, 2, 1, '\u2192', self.col_gray3,
                lambda w: self._parent.move_right()],
            [4, 0, 2, 1, '\u232B', self.col_gray3,
                lambda w: self._parent.remove_character(-1)],

            [0, 1, 1, 2, _n('7'), self.col_gray2,
                lambda w: self._parent.add_text(_n('7'))],
            [1, 1, 1, 2, _n('8'), self.col_gray2,
                lambda w: self._parent.add_text(_n('8'))],
            [2, 1, 1, 2, _n('9'), self.col_gray2,
                lambda w: self._parent.add_text(_n('9'))],

            [0, 3, 1, 2, _n('4'), self.col_gray2,
                lambda w: self._parent.add_text(_n('4'))],
            [1, 3, 1, 2, _n('5'), self.col_gray2,
                lambda w: self._parent.add_text(_n('5'))],
            [2, 3, 1, 2, _n('6'), self.col_gray2,
                lambda w: self._parent.add_text(_n('6'))],

            [0, 5, 1, 2, _n('1'), self.col_gray2,
                lambda w: self._parent.add_text(_n('1'))],
            [1, 5, 1, 2, _n('2'), self.col_gray2,
                lambda w: self._parent.add_text(_n('2'))],
            [2, 5, 1, 2, _n('3'), self.col_gray2,
                lambda w: self._parent.add_text(_n('3'))],

            [0, 7, 2, 2, _n('0'), self.col_gray2,
                lambda w: self._parent.add_text(_n('0'))],

            [2, 7, 1, 2, '.', self.col_gray2,
                lambda w: self._parent.add_text('.')],

            [3, 1, 3, 2, _('Clear'), self.col_gray1,
                lambda w: self._parent.clear()],

            [3, 3, 1, 2, '+', self.col_gray3,
                lambda w: self._parent.add_text('+')],
            [4, 3, 1, 2, '-', self.col_gray3,
                lambda w: self._parent.add_text('-')],
            [5, 3, 1, 2, '(', self.col_gray3,
                lambda w: self._parent.add_text('(')],
            [3, 5, 1, 2, mul_sym, self.col_gray3,
                lambda w: self._parent.add_text(mul_sym)],
            [4, 5, 1, 2, div_sym, self.col_gray3,
                lambda w: self._parent.add_text(div_sym)],
            [5, 5, 1, 2, ')', self.col_gray3,
                lambda w: self._parent.add_text(')')],

            [3, 7, 3, 2, equ_sym, self.col_gray1,
                lambda w: self._parent.process()],
        ]

    def create_dialog(self):
        """Setup most of the dialog."""

# Toolbar
        self._toolbar_box = ToolbarBox()
        self._toolbar_box.set_orientation(Gtk.Orientation.VERTICAL)
        self._toolbar_box.set_hexpand(True)
        self._toolbar_box.set_vexpand(False)

        if hasattr(self._toolbar_box, "get_toolbar"):
            self._toolbar = self._toolbar_box.get_toolbar()
        else:
            self._toolbar = self._toolbar_box.toolbar
        if hasattr(self._toolbar, "set_orientation"):
            self._toolbar.set_orientation(Gtk.Orientation.HORIZONTAL)
        
        activity_button = ActivityToolbarButton(self._parent)
        activity_button.set_hexpand(False)
        self._toolbar.append(activity_button)

        def append(icon_name, label, page):
            toolbar_button = ToolbarButton()
            if hasattr(toolbar_button, "set_page"):
                toolbar_button.set_page(page)
            else:
                toolbar_button.props.page = page
            if hasattr(toolbar_button, "set_icon_name"):
                toolbar_button.set_icon_name(icon_name)
            else:
                toolbar_button.props.icon_name = icon_name
            toolbar_button.set_tooltip(label)
            toolbar_button.set_hexpand(False)
            self._toolbar.append(toolbar_button)
        append('toolbar-edit',
               _('Edit'),
               EditToolbar(self._parent))
        append('toolbar-algebra',
               _('Algebra'),
               AlgebraToolbar(self._parent))
        append('toolbar-trigonometry',
               _('Trigonometry'),
               TrigonometryToolbar(self._parent))
        append('toolbar-boolean',
               _('Boolean'),
               BooleanToolbar(self._parent))
        self._misc_toolbar = MiscToolbar(
            self._parent,
            target_toolbar=self._toolbar)
        append('toolbar-constants',
               _('Miscellaneous'),
               self._misc_toolbar)
        self._stop_separator = Gtk.Separator()
        self._stop_separator.set_hexpand(True)
        self._stop_separator.show()
        self._toolbar.append(self._stop_separator)
        self._stop = StopButton(self._parent)
        self._stop.set_hexpand(False)
        self._toolbar.append(self._stop)
        self._toolbar_box.show()
        self._parent.set_toolbar_box(self._toolbar_box)

# Some layout constants
        self.input_font = Pango.FontDescription(
            'sans bold %d' % (FONT_SIZE * 4))
        self.button_font = Pango.FontDescription(
            'sans bold %d' % (FONT_SIZE * 4))
        self.col_white = self.create_color(1.00, 1.00, 1.00)
        self.col_gray1 = self.create_color(0.76, 0.76, 0.76)
        self.col_gray2 = self.create_color(0.50, 0.50, 0.50)
        self.col_gray3 = self.create_color(0.25, 0.25, 0.25)
        self.col_black = self.create_color(0.00, 0.00, 0.00)
        self.col_red = self.create_color(1.00, 0.00, 0.00)

# Big - Table, 16 rows, 10 columns, homogeneously divided
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(False)  # Allow different row heights
        self.grid.set_row_spacing(0)
        self.grid.set_column_spacing(4)
        self.grid.set_hexpand(True)
        self.grid.set_vexpand(True)

# Left part: container and input
        vc1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        vc1.set_vexpand(False)
        vc1.set_valign(Gtk.Align.START)
        hc1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hc1.set_margin_start(6)
        hc1.set_margin_end(6)
        hc1.set_margin_top(3)
        hc1.set_margin_bottom(3)
        
        label1 = Gtk.Label(label=_('Label:'))
        label1.set_halign(Gtk.Align.END)
        label1.set_valign(Gtk.Align.CENTER)
        label1.set_margin_start(5)
        label1.set_margin_end(5)
        hc1.append(label1)
        
        self.label_entry = Gtk.Entry()
        self.label_entry.set_hexpand(True)
        hc1.append(self.label_entry)
        vc1.append(hc1)

        self.text_entry = Gtk.Entry()
        try:
            self.text_entry.props.im_module = 'gtk-im-context-simple'
        except AttributeError:
            pass
        self.text_entry.set_size_request(-1, 60)
        
        controller = Gtk.EventControllerKey()
        controller.connect('key-pressed', self._parent.ignore_key_cb)
        self.text_entry.add_controller(controller)
        
        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        text_box.set_margin_start(6)
        text_box.set_margin_end(6)
        text_box.set_margin_top(3)
        text_box.set_margin_bottom(3)
        text_box.set_hexpand(True)
        text_box.append(self.text_entry)
        
        vc1.append(text_box)
        self.grid.attach(vc1, 0, 0, 7, 6)

# Left part: buttons
        self.pad = Gtk.Grid()
        self.pad.set_column_homogeneous(True)
        self.pad.set_row_homogeneous(False)  # Don't force equal row heights
        self.pad.set_row_spacing(6)
        self.pad.set_column_spacing(6)
        self.pad.set_vexpand(True)
        self.pad.set_hexpand(True)
        self.create_button_data()
        self.buttons = {}
        for x, y, w, h, cap, bgcol, cb in self.button_data:
            button = self.create_button(
                _(cap), cb, self.col_white, bgcol, w, h)
            button.set_vexpand(True)
            button.set_hexpand(True)
            self.buttons[cap] = button
            self.pad.attach(button, x, y, w, h)
            button.show()  # Explicitly show each button

        pad_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        pad_box.set_vexpand(True)
        pad_box.set_hexpand(True)
        pad_box.append(self.pad)
        self.grid.attach(pad_box, 0, 6, 7, 20)

# Right part: container and equation button
        hc2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        combo = ComboBox()
        combo.append_item(0, _('All equations'))
        combo.append_item(1, _('My equations'))
        combo.append_item(2, _('Show variables'))
        combo.set_active(0)
        combo.connect('changed', self._history_filter_cb)
        combo.set_hexpand(True)
        hc2.append(combo)
        hc2.set_margin_start(6)
        hc2.set_margin_end(6)
        hc2.set_margin_top(6)
        hc2.set_margin_bottom(6)
        self.grid.attach(hc2, 7, 0, 4, 2)

# Right part: last equation
        self.last_eq = Gtk.TextView()
        self.last_eq.set_editable(False)
        self.last_eq.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.last_eq.connect('realize', self._textview_realize_cb)
        
        # Set margins instead of border window size
        self.last_eq.set_top_margin(4)
        self.last_eq.set_bottom_margin(4)
        self.last_eq.set_left_margin(4)
        self.last_eq.set_right_margin(4)
        
        self.grid.attach(self.last_eq, 7, 2, 4, 5)

# Right part: history
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER,
                                   Gtk.PolicyType.AUTOMATIC)

        self.history_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                                    spacing=4)
        self.history_vbox.set_homogeneous(False)

        self.variable_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                                     spacing=4)
        self.variable_vbox.set_homogeneous(False)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.history_vbox.set_vexpand(True)
        self.variable_vbox.set_vexpand(True)
        vbox.append(self.history_vbox)
        vbox.append(self.variable_vbox)
        scrolled_window.set_child(vbox)
        self.grid.attach(scrolled_window, 7, 7, 4, 19)

        # Note: In GTK4, we could use surface state-changed events, 
        # but for simplicity we skip dynamic reconfiguration for now
        # The layout will be set on initial creation

    def _configure_cb(self, event):
        # Maybe redo layout
        self._toolbar.remove(self._stop)
        self._toolbar.remove(self._stop_separator)
        self._misc_toolbar.update_layout()
        self._toolbar.append(self._stop_separator)
        self._toolbar.append(self._stop)

    def show_it(self):
        """Show the dialog."""
        self._parent.set_canvas(self.grid)
        
        # In GTK4, we need to explicitly show widgets
        # Show toolbar
        self._toolbar_box.show()
        
        # Show all buttons in the calculator pad
        for button in self.buttons.values():
            button.show()
        
        # Show the pad grid itself
        self.pad.show()
        
        # Show input widgets
        self.label_entry.show()
        self.text_entry.show()
        
        # Show last equation TextView
        self.last_eq.show()
        
        # Show history/variable vboxes
        self.history_vbox.show()
        self.variable_vbox.show()
        
        # Show the main grid
        self.grid.show()
        
        self.show_history()
        self.text_entry.grab_focus()

    def showing_history(self):
        """Return whether we're currently showing the history (or otherwise
        the list of variables)."""
        return self._showing_history

    def show_history(self):
        """Show the history VBox."""
        self._showing_history = True
        self.variable_vbox.hide()
        self.history_vbox.show()

    def toggle_select_graph(self, widget, host=None):
        # if we have a graph already selected, we must deselect it first
        if self.graph_selected and self.graph_selected != widget:
            self.toggle_select_graph(self.graph_selected)

        if not self.graph_selected:
            self.graph_selected = widget
            # Use CSS for styling in GTK4
            css_provider = Gtk.CssProvider()
            css = "box { background-color: white; }"
            css_provider.load_from_data(css.encode())
            widget.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        else:
            # Remove CSS styling
            self.graph_selected = False

    def add_equation(self, textview, own, prepend=False):
        """Add a Gtk.TextView of an equation to the history_vbox."""

        GraphEventBox = None
        if isinstance(textview, Gtk.Image):
            # Use a regular Box instead of EventBox for GTK4
            GraphEventBox = Gtk.Box()
            GraphEventBox.append(textview)
            
            # Add gesture click controller for button press events
            gesture = Gtk.GestureClick()
            gesture.connect('pressed', lambda g, n, x, y: self.toggle_select_graph(GraphEventBox))
            GraphEventBox.add_controller(gesture)
            GraphEventBox.show()

        if prepend:
            if GraphEventBox:
                self.history_vbox.prepend(GraphEventBox)
            else:
                self.history_vbox.prepend(textview)
        else:
            if GraphEventBox:
                self.history_vbox.append(GraphEventBox)
            else:
                self.history_vbox.append(textview)

        if own:
            if GraphEventBox:
                self._own_equations.append(GraphEventBox)
                GraphEventBox.get_first_child().show()
            else:
                self._own_equations.append(textview)
                textview.show()
        else:
            if self._showing_all_history:
                if GraphEventBox:
                    self._other_equations.append(GraphEventBox)
                    GraphEventBox.get_first_child().show()
                else:
                    self._other_equations.append(textview)
                    textview.show()

    def show_all_history(self):
        """Show both owned and other equations."""
        self._showing_all_history = True
        for key in self._other_equations:
            if isinstance(key, Gtk.Box) and key.get_first_child():
                key.get_first_child().show()
            else:
                key.show()

    def show_own_history(self):
        """Show only owned equations."""
        self._showing_all_history = False
        for key in self._other_equations:
            if isinstance(key, Gtk.Box) and key.get_first_child():
                key.get_first_child().hide()
            else:
                key.hide()

    def add_variable(self, varname, textview):
        """Add a Gtk.TextView of a variable to the variable_vbox."""

        if varname in self._var_textviews:
            self.variable_vbox.remove(self._var_textviews[varname])
            del self._var_textviews[varname]

        self._var_textviews[varname] = textview
        self.variable_vbox.append(textview)

        # Reorder textviews for a sorted list
        names = list(self._var_textviews.keys())
        names.sort()
        for i in range(len(names)):
            self.variable_vbox.reorder_child_after(self._var_textviews[names[i]], 
                                                   self._var_textviews[names[i-1]] if i > 0 else None)

        textview.show()

    def show_variables(self):
        """Show the variables VBox."""
        self._showing_history = False
        self.history_vbox.hide()
        self.variable_vbox.show()

    def create_button(self, cap, cb, fgcol, bgcol, width, height):
        """Create a button that is set up properly."""
        button = Gtk.Button(label=_(cap))
        self.modify_button_appearance(button, fgcol, bgcol, width, height)
        button.connect("clicked", cb)
        controller = Gtk.EventControllerKey()
        controller.connect('key-pressed', self._parent.ignore_key_cb)
        button.add_controller(controller)
        return button

    def modify_button_appearance(self, button, fgcol, bgcol, width, height):
        """Modify button style."""
        width = 50 * width
        button.get_child().set_size_request(width, height)
        # Keep default GTK styling

    def _history_filter_cb(self, combo):
        selection = combo.get_active()
        if selection == 0:
            self.show_history()
            self.show_all_history()
        elif selection == 1:
            self.show_history()
            self.show_own_history()
        elif selection == 2:
            self.show_variables()

    def _textview_realize_cb(self, widget):
        '''Change textview properties once window is created.'''
        widget.set_cursor(Gdk.Cursor.new_from_name('pointer', None))
        return False
