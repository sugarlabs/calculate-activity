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
import os
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango

# GTK4 compatibility: Add insert_text method to Gtk.Entry
# (GTK3 had this, but GTK4 doesn't)
def _entry_insert_text(self, text, position=-1):
    """Insert text at the specified position (GTK3 compatibility)."""
    current_text = self.get_text()
    if position < 0 or position > len(current_text):
        position = len(current_text)
    new_text = current_text[:position] + text + current_text[position:]
    # Use buffer to preserve GTK4 behavior
    self.set_text(new_text)
    # Set cursor position after insertion
    # In GTK4, we need to call set_position after set_text
    self.set_position(position + len(text))

# Apply the monkeypatch
if not hasattr(Gtk.Entry, 'insert_text'):
    Gtk.Entry.insert_text = _entry_insert_text

# Try to import from sugar4, provide GTK4 fallbacks if unavailable
HAS_SUGAR4 = False
try:
    import sugar4.profile
    from sugar4.graphics.style import FONT_SIZE
    from sugar4.graphics.combobox import ComboBox
    from sugar4.graphics.toolbarbox import ToolbarButton, ToolbarBox
    from sugar4.activity.widgets import ActivityToolbarButton
    from sugar4.activity.widgets import StopButton
    HAS_SUGAR4 = True
except ImportError:
    # Default font size for GTK4 apps
    FONT_SIZE = 10
    # Create a fallback XoColor class for when sugar4 is unavailable
    class XoColor:
        """Fallback XoColor for standalone execution."""
        def __init__(self, stroke='#808080', fill='#ffffff'):
            self.stroke = stroke
            self.fill = fill
        
        def get_stroke_color(self):
            return self.stroke
        
        def get_fill_color(self):
            return self.fill
    class ComboBox(Gtk.ComboBoxText):
        """ComboBox replacement for standalone execution."""
        def __init__(self):
            Gtk.ComboBoxText.__init__(self)
            self._items = {}
        
        def append_item(self, item_id, label):
            self._items[len(self._items)] = (item_id, label)
            self.append_text(label)
        
        def get_active(self):
            return Gtk.ComboBoxText.get_active(self)
    
    class ToolbarButton(Gtk.Button):
        """ToolbarButton replacement for standalone execution."""
        def __init__(self):
            Gtk.Button.__init__(self)
            self.page = None
            self.props = type('obj', (object,), {
                'page': None,
                'icon_name': None,
                'label': None
            })()
        
        @property
        def props(self):
            return self._props
        
        @props.setter
        def props(self, value):
            self._props = value
    
    class ToolbarBox(Gtk.Box):
        """ToolbarBox replacement for standalone execution."""
        def __init__(self):
            Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            self.toolbar = Gtk.Toolbar(orientation=Gtk.Orientation.HORIZONTAL)
            self.append(self.toolbar)
    
    class ActivityToolbarButton(Gtk.Button):
        """ActivityToolbarButton replacement for standalone execution."""
        def __init__(self, activity):
            Gtk.Button.__init__(self, label="Activity")
            self.activity = activity
    
    class StopButton(Gtk.Button):
        """StopButton replacement for standalone execution."""
        def __init__(self, activity):
            Gtk.Button.__init__(self, label="Stop")
            self.activity = activity
            self.connect('clicked', lambda w: activity.close())

# GTK4 compatibility: EventBox doesn't exist in GTK4, use Box instead
if not hasattr(Gtk, 'EventBox'):
    class EventBox(Gtk.Box):
        """EventBox replacement for GTK4 using Box."""
        def __init__(self):
            Gtk.Box.__init__(self)
            self._child = None
        
        def add(self, widget):
            """Add a child widget."""
            if self._child is not None:
                self.remove(self._child)
            self._child = widget
            self.append(widget)
        
        def get_child(self):
            """Get the child widget."""
            return self._child
    
    Gtk.EventBox = EventBox

# GTK4 compatibility: Add pack_start and pack_end methods to Gtk.Box
_original_box_init = Gtk.Box.__init__

def _patched_box_init(self, **kwargs):
    """Patched Box.__init__ that adds GTK3 compatibility methods."""
    _original_box_init(self, **kwargs)

def _pack_start(self, widget, expand=False, fill=False, padding=0):
    """GTK3 compatibility: pack_start method."""
    self.append(widget)
    if expand:
        widget.set_hexpand(True)
        if self.get_orientation() == Gtk.Orientation.VERTICAL:
            widget.set_vexpand(True)
    if padding > 0:
        widget.set_margin_start(padding)
        widget.set_margin_end(padding)

def _pack_end(self, widget, expand=False, fill=False, padding=0):
    """GTK3 compatibility: pack_end method."""
    # In GTK4, we append and let the order determine packing
    # For proper pack_end behavior, we'd need to use insert_child_after,
    # but for simplicity, we append and rely on widget ordering
    self.append(widget)
    if expand:
        widget.set_hexpand(True)
        if self.get_orientation() == Gtk.Orientation.VERTICAL:
            widget.set_vexpand(True)
    if padding > 0:
        widget.set_margin_start(padding)
        widget.set_margin_end(padding)

# Monkeypatch Gtk.Box with compatibility methods
Gtk.Box.pack_start = _pack_start
Gtk.Box.pack_end = _pack_end

from toolbars import EditToolbar
from toolbars import AlgebraToolbar
from toolbars import TrigonometryToolbar
from toolbars import BooleanToolbar
from toolbars import MiscToolbar

from numerals import local as _n


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

    def _resolve_icon(self, icon_name):
        """Resolve icon name for toolbar buttons."""
        # In GTK4, we pass the icon name directly
        return icon_name

    def append_toolbar(self, icon_name, label, page):
        """Append a toolbar button with the given icon, label, and page."""
        page.set_hexpand(True)
        toolbar_button = ToolbarButton()
        toolbar_button.props.page = page
        toolbar_button.props.icon_name = self._resolve_icon(icon_name)
        toolbar_button.props.label = label
        toolbar_button.set_tooltip_text(label)
        if hasattr(toolbar_button, 'page_widget') and toolbar_button.page_widget is not None:
            toolbar_button.page_widget.set_hexpand(True)
        # Use append instead of insert for simplicity
        self._toolbar_box.toolbar.append(toolbar_button)

    def create_color(self, rf, gf, bf):
        # GTK4: Use Gdk.RGBA instead of Gdk.Color
        color = Gdk.RGBA()
        color.red = rf
        color.green = gf
        color.blue = bf
        color.alpha = 1.0
        return color

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
        activity_button = ActivityToolbarButton(self._parent)
        self._toolbar_box.toolbar.insert(activity_button, 0)

        self.append_toolbar('toolbar-edit',
                           _('Edit'),
                           EditToolbar(self._parent))
        self.append_toolbar('toolbar-algebra',
                           _('Algebra'),
                           AlgebraToolbar(self._parent))
        self.append_toolbar('toolbar-trigonometry',
                           _('Trigonometry'),
                           TrigonometryToolbar(self._parent))
        self.append_toolbar('toolbar-boolean',
                           _('Boolean'),
                           BooleanToolbar(self._parent))
        self._misc_toolbar = MiscToolbar(
            self._parent,
            target_toolbar=self._toolbar_box.toolbar)
        self.append_toolbar('toolbar-constants',
                           _('Miscellaneous'),
                           self._misc_toolbar)
        self._stop_separator = Gtk.SeparatorToolItem()
        self._stop_separator.set_draw(False)
        self._stop_separator.set_expand(True)
        self._stop_separator.show()
        self._toolbar_box.toolbar.insert(self._stop_separator, -1)
        self._stop = StopButton(self._parent)
        self._toolbar_box.toolbar.insert(self._stop, -1)
        # GTK4: show_all() is deprecated, show() is automatic
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
        self.grid.set_row_spacing(0)
        self.grid.set_column_spacing(4)
        # GTK4: Set grid to expand and fill available space
        self.grid.set_hexpand(True)
        self.grid.set_vexpand(True)

# Left part: container and input
        vc1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        hc1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        eb = Gtk.EventBox()
        eb.add(hc1)
        eb.set_margin_start(12)
        eb.set_margin_end(12)
        eb.set_margin_top(12)
        eb.set_margin_bottom(12)
        eb2 = Gtk.EventBox()
        eb2.add(eb)
        label1 = Gtk.Label(label=_('Label:'))
        # GTK4: Use halign/valign instead of set_alignment
        label1.set_halign(Gtk.Align.END)
        label1.set_valign(Gtk.Align.CENTER)
        hc1.pack_start(label1, expand=False, fill=False, padding=10)
        self.label_entry = Gtk.Entry()
        # GTK4: Let Sugar theme handle styling
        hc1.pack_start(self.label_entry, expand=True, fill=True, padding=0)
        vc1.pack_start(eb2, False, True, 0)

        self.text_entry = Gtk.Entry()
        try:
            self.text_entry.props.im_module = 'gtk-im-context-simple'
        except AttributeError:
            pass
        self.text_entry.set_size_request(-1, 75)
        # GTK4: Ensure text_entry is visible and expandable
        self.text_entry.set_visible(True)
        self.text_entry.set_hexpand(True)
        # GTK4: Use EventControllerKey instead of key_press_event signal
        key_controller = Gtk.EventControllerKey.new()
        key_controller.connect("key-pressed", self._parent.ignore_key_cb)
        self.text_entry.add_controller(key_controller)
        # GTK4: Apply font using CSS class - rely on Sugar theme
        self.text_entry.add_css_class("text-entry-large")
        eb = Gtk.EventBox()
        eb.add(self.text_entry)
        eb.set_margin_start(12)
        eb.set_margin_end(12)
        eb.set_margin_top(12)
        eb.set_margin_bottom(12)
        eb2 = Gtk.EventBox()
        eb2.add(eb)
        vc1.pack_start(eb2, expand=True, fill=True, padding=0)
        self.grid.attach(vc1, 0, 0, 7, 6)

# Left part: buttons
        self.pad = Gtk.Grid()
        self.pad.set_column_homogeneous(True)
        self.pad.set_row_spacing(6)
        self.pad.set_column_spacing(6)
        self.create_button_data()
        self.buttons = {}
        for x, y, w, h, cap, bgcol, cb in self.button_data:
            # GTK4: Simplified button creation - colors handled by CSS classes
            button = self.create_button(
                _(cap), cb, w, h)
            button.set_vexpand(True)
            self.buttons[cap] = button
            self.pad.attach(button, x, y, w, h)

        eb = Gtk.EventBox()
        eb.add(self.pad)
        # GTK4: Let Sugar theme handle styling
        self.grid.attach(eb, 0, 6, 7, 20)

# Right part: container and equation button
        hc2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        combo = ComboBox()
        combo.append_item(0, _('All equations'))
        combo.append_item(1, _('My equations'))
        combo.append_item(2, _('Show variables'))
        combo.set_active(0)
        combo.connect('changed', self._history_filter_cb)
        hc2.pack_start(combo, True, True, 0)
        # GTK4: Use margins instead of border_width
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
        # GTK4: Apply styling using CSS classes from Sugar theme
        self.last_eq.add_css_class("calculator-history")
        self.last_eq.set_margin_start(4)
        self.last_eq.set_margin_end(4)
        self.last_eq.set_margin_top(4)
        self.last_eq.set_margin_bottom(4)
        # GTK4: Ensure the widget expands to fill available space
        self.last_eq.set_hexpand(True)
        self.last_eq.set_vexpand(True)

        xo_color = sugar4.profile.get_color() if HAS_SUGAR4 else XoColor()
        fill_rgba = Gdk.RGBA()
        fill_rgba.parse(xo_color.get_fill_color())
        bright = (fill_rgba.red + fill_rgba.green + fill_rgba.blue) / 3.0
        # Apply text color based on background brightness
        if bright < 0.5:
            self.last_eq.add_css_class("text-light")
        else:
            self.last_eq.add_css_class("text-dark")

        self.grid.attach(self.last_eq, 7, 2, 4, 5)

# Right part: history
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER,
                                   Gtk.PolicyType.AUTOMATIC)

        self.history_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                                    spacing=4)
        self.history_vbox.set_homogeneous(False)
        # GTK4: border_width(0) is default, no need to set

        self.variable_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                                     spacing=4)
        self.variable_vbox.set_homogeneous(False)
        # GTK4: border_width(0) is default, no need to set

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.pack_start(self.history_vbox, True, True, 0)
        vbox.pack_start(self.variable_vbox, True, True, 0)
        # GTK4: Use set_child instead of add_with_viewport
        scrolled_window.set_child(vbox)
        self.grid.attach(scrolled_window, 7, 7, 4, 19)

        # GTK4: Gdk.Screen doesn't exist, use window signals instead
        try:
            Gdk.Screen.get_default().connect('size-changed',
                                             self._configure_cb)
        except AttributeError:
            # GTK4: Defer window resize handling
            # Could connect to window configure event when window is available
            pass

    def _configure_cb(self, event):
        # Maybe redo layout
        self._toolbar_box.toolbar.remove(self._stop)
        self._toolbar_box.toolbar.remove(self._stop_separator)
        self._misc_toolbar.update_layout()
        self._toolbar_box.toolbar.insert(self._stop_separator, -1)
        self._toolbar_box.toolbar.insert(self._stop, -1)

    def show_it(self):
        """Show the dialog."""
        self._parent.set_canvas(self.grid)
        # GTK4: Explicitly show all widgets to ensure visibility
        self.grid.set_visible(True)
        self.text_entry.set_visible(True)
        self.last_eq.set_visible(True)
        self.history_vbox.set_visible(True)
        self.pad.set_visible(True)
        # GTK4: show_all() is deprecated, show() is automatic
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
            widget.set_visible_window(True)
            widget.set_above_child(True)
            self.graph_selected = widget
            # GTK4: Use CSS class for selection highlighting
            widget.add_css_class("selected")
        else:
            widget.set_visible_window(False)
            if widget.has_css_class("selected"):
                widget.remove_css_class("selected")
            self.graph_selected = False

    def add_equation(self, textview, own, prepend=False):
        """Add a Gtk.TextView of an equation to the history_vbox."""

        GraphEventBox = None
        if isinstance(textview, Gtk.Image):
            # Add the image inside the eventBox
            GraphEventBox = Gtk.EventBox()
            GraphEventBox.add(textview)
            GraphEventBox.set_visible_window(False)
            GraphEventBox.connect(
                'button_press_event', self.toggle_select_graph)
            GraphEventBox.show()

        if prepend:
            if GraphEventBox:
                self.history_vbox.pack_start(GraphEventBox, False, True, 0)
                self.history_vbox.reorder_child(GraphEventBox, 0)
            else:
                self.history_vbox.pack_start(textview, False, True, 0)
                self.history_vbox.reorder_child(textview, 0)
        else:
            if GraphEventBox:
                self.history_vbox.pack_end(GraphEventBox, False, True)
            else:
                self.history_vbox.pack_end(textview, False, True)

        if own:
            if GraphEventBox:
                self._own_equations.append(GraphEventBox)
                GraphEventBox.get_child().show()
            else:
                self._own_equations.append(textview)
                textview.show()
        else:
            if self._showing_all_history:
                if GraphEventBox:
                    self._other_equations.append(GraphEventBox)
                    GraphEventBox.get_child().show()
                else:
                    self._other_equations.append(textview)
                    textview.show()

    def show_all_history(self):
        """Show both owned and other equations."""
        self._showing_all_history = True
        for key in self._other_equations:
            if isinstance(key, Gtk.EventBox):
                key.get_child().show()
            else:
                key.show()

    def show_own_history(self):
        """Show only owned equations."""
        self._showing_all_history = False
        for key in self._other_equations:
            if isinstance(key, Gtk.EventBox):
                key.get_child().hide()
            else:
                key.hide()

    def add_variable(self, varname, textview):
        """Add a Gtk.TextView of a variable to the variable_vbox."""

        if varname in self._var_textviews:
            self.variable_vbox.remove(self._var_textviews[varname])
            del self._var_textviews[varname]

        self._var_textviews[varname] = textview
        self.variable_vbox.pack_start(textview, False, True, 0)

        # Reorder textviews for a sorted list
        names = list(self._var_textviews.keys())
        names.sort()
        for i in range(len(names)):
            self.variable_vbox.reorder_child(self._var_textviews[names[i]], i)

        textview.show()

    def show_variables(self):
        """Show the variables VBox."""
        self._showing_history = False
        self.history_vbox.hide()
        self.variable_vbox.show()

    def create_button(self, cap, cb, width, height):
        """Create a button that is set up properly."""
        button = Gtk.Button(label=cap)
        self.modify_button_appearance(button, width, height)
        button.connect("clicked", cb)
        # GTK4: Use EventControllerKey instead of key_press_event signal
        key_controller = Gtk.EventControllerKey.new()
        key_controller.connect("key-pressed", self._parent.ignore_key_cb)
        button.add_controller(key_controller)
        return button

    def modify_button_appearance(self, button, width, height):
        """Modify button size using GTK properties."""
        width = 50 * width
        button.get_child().set_size_request(width, height)
        # GTK4: Use CSS class for button styling - let Sugar theme handle colors
        button.add_css_class("calculator-button")

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
        # GTK4: Use Gdk.Cursor.new_from_name instead of Gdk.Cursor.new
        cursor = Gdk.Cursor.new_from_name('grab')
        widget.set_cursor(cursor)
        return False
