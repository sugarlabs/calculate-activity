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
from gi.repository import Gtk, Gdk, Pango, GLib
import sugar4.profile
from sugar4.graphics.style import FONT_SIZE
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
        return Gdk.RGBA(rf, gf, bf, 1.0)

    def create_button_data(self):
        """Create a list with button information."""

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
        self._toolbar_box.get_toolbar().append(activity_button)

        icons_path = os.path.join(os.environ.get('SUGAR_BUNDLE_PATH',
                                                  os.getcwd()), 'icons')

        def _resolve_icon(name):
            local = os.path.join(icons_path, name + '.svg')
            if os.path.exists(local):
                return local
            return name

        def append_toolbar(icon_name, label, page):
            page.set_hexpand(True)
            toolbar_button = ToolbarButton(page=page,
                                           icon_name=_resolve_icon(icon_name))
            toolbar_button.set_tooltip_text(label)
            if toolbar_button.page_widget is not None:
                toolbar_button.page_widget.set_hexpand(True)
            self._toolbar_box.get_toolbar().append(toolbar_button)

        append_toolbar('toolbar-edit',
                       _('Edit'),
                       EditToolbar(self._parent))
        append_toolbar('toolbar-algebra',
                       _('Algebra'),
                       AlgebraToolbar(self._parent))
        append_toolbar('toolbar-trigonometry',
                       _('Trigonometry'),
                       TrigonometryToolbar(self._parent))
        append_toolbar('toolbar-boolean',
                       _('Boolean'),
                       BooleanToolbar(self._parent))
        self._misc_toolbar = MiscToolbar(
            self._parent,
            target_toolbar=self._toolbar_box.get_toolbar())
        append_toolbar('toolbar-constants',
                       _('Miscellaneous'),
                       self._misc_toolbar)

        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        self._toolbar_box.get_toolbar().append(spacer)

        stop_button = StopButton(self._parent)
        self._toolbar_box.get_toolbar().append(stop_button)

        if hasattr(self._parent, 'set_toolbar_box'):
            self._parent.set_toolbar_box(self._toolbar_box)

        # Layout constants
        self.col_white = self.create_color(1.00, 1.00, 1.00)
        self.col_gray1 = self.create_color(0.76, 0.76, 0.76)
        self.col_gray2 = self.create_color(0.50, 0.50, 0.50)
        self.col_gray3 = self.create_color(0.25, 0.25, 0.25)
        self.col_black = self.create_color(0.00, 0.00, 0.00)
        self.col_red = self.create_color(1.00, 0.00, 0.00)


        # Big - Grid
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_spacing(0)
        self.grid.set_column_spacing(4)

        # Left part: container and input
        vc1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        hc1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        eb = Gtk.Box()
        eb.add_css_class("calc-display")
        eb.append(hc1)
        
        eb.set_margin_top(4)
        eb.set_margin_bottom(4)
        
        label1 = Gtk.Label(label=_('Label:'))
        label1.add_css_class("calc-label")
        label1.set_xalign(1.0)
        
        hc1.append(label1)
        
        self.label_entry = Gtk.Entry()
        self.label_entry.set_hexpand(True)
        hc1.append(self.label_entry)
        
        vc1.append(eb)

        self.text_entry = Gtk.Entry()
        self.text_entry.set_size_request(-1, 75)
        
        self.text_entry.add_css_class("calc-entry")
        self.text_entry.add_css_class("calc-display")

        entry_key_controller = Gtk.EventControllerKey()
        entry_key_controller.connect('key-pressed',
                                     self._parent.ignore_key_cb)
        self.text_entry.add_controller(entry_key_controller)
        
        vc1.append(self.text_entry)
        self.grid.attach(vc1, 0, 0, 7, 6)

        # Buttons
        self.pad = Gtk.Grid()
        self.pad.set_column_homogeneous(True)
        self.pad.set_row_spacing(6)
        self.pad.set_column_spacing(6)
        
        self.create_button_data()
        self.buttons = {}
        
        for x, y, w, h, cap, bgcol, cb in self.button_data:
            button = self.create_button(
                _(cap), cb, self.col_white, bgcol, w, h)
            button.set_vexpand(True)
            button.set_hexpand(True)
            self.buttons[cap] = button
            self.pad.attach(button, x, y, w, h)
            
        # Button container style
        eb_pad = Gtk.Box()
        eb_pad.add_css_class("calc-display")
        eb_pad.append(self.pad)
        
        self.grid.attach(eb_pad, 0, 6, 7, 20)

        # Right part: Filter Combo
        hc2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        
        combo = Gtk.ComboBoxText()
        combo.append("0", _('All equations'))
        combo.append("1", _('My equations'))
        combo.append("2", _('Show variables'))
        combo.set_active(0)
        combo.connect('changed', self._history_filter_cb)
        
        combo.set_hexpand(True)
        hc2.append(combo)
        hc2.set_margin_top(6) 
        hc2.set_margin_bottom(6)
        
        self.grid.attach(hc2, 7, 0, 4, 2)

        # Right part: Last Equation TextView
        self.last_eq = Gtk.TextView()
        self.last_eq.set_editable(False)
        self.last_eq.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.last_eq.add_css_class("history-view")
        self.last_eq.set_left_margin(4)
        self.last_eq.set_right_margin(4)
        
        self.grid.attach(self.last_eq, 7, 2, 4, 5)

        # Right part: History ScrolledWindow
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        self.history_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.variable_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.append(self.history_vbox)
        vbox.append(self.variable_vbox)
        
        scrolled_window.set_child(vbox)
        self.grid.attach(scrolled_window, 7, 7, 4, 19)

    def show_it(self):
        """Show the dialog."""
        self._parent.set_canvas(self.grid)
        self.show_history()
        self.text_entry.grab_focus()

    def showing_history(self):
        """Return whether we're currently showing the history."""
        return self._showing_history

    def show_history(self):
        """Show the history VBox."""
        self._showing_history = True
        self.variable_vbox.set_visible(False)
        self.history_vbox.set_visible(True)

    def toggle_select_graph(self, widget, host=None):

        # if we have a graph already selected, we must deselect it first
        if self.graph_selected and self.graph_selected != widget:
            self.toggle_select_graph(self.graph_selected)

        if not self.graph_selected:
            self.graph_selected = widget
            
            # Highlight with CSS
            widget.add_css_class("selected-graph") 
            
        else:
            widget.remove_css_class("selected-graph")
            self.graph_selected = None

    def add_equation(self, textview, own, prepend=False):
        """Add a Gtk.TextView of an equation to the history_vbox."""

        container = None
        if isinstance(textview, Gtk.Image):
            container = Gtk.Box()
            container.append(textview)
            
            click_gesture = Gtk.GestureClick()
            click_gesture.set_button(0)
            click_gesture.connect("pressed", lambda g, n, x, y: self.toggle_select_graph(container))
            container.add_controller(click_gesture)
        
        widget_to_add = container if container else textview

        if prepend:
            self.history_vbox.prepend(widget_to_add)
        else:
            self.history_vbox.append(widget_to_add)

        if own:
            self._own_equations.append(widget_to_add)
            widget_to_add.set_visible(True)
        else:
            if self._showing_all_history:
                self._other_equations.append(widget_to_add)
                widget_to_add.set_visible(True)
            else:
                self._other_equations.append(widget_to_add)
                widget_to_add.set_visible(False)

    def show_all_history(self):
        """Show both owned and other equations."""
        self._showing_all_history = True
        for key in self._other_equations:
            key.set_visible(True)

    def show_own_history(self):
        """Show only owned equations."""
        self._showing_all_history = False
        for key in self._other_equations:
            key.set_visible(False)

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
        
        for child in list(self._var_textviews.values()):
            if child.get_parent() == self.variable_vbox:
                 self.variable_vbox.remove(child)
        
        for name in names:
             self.variable_vbox.append(self._var_textviews[name])

        textview.set_visible(True)

    def show_variables(self):
        """Show the variables VBox."""
        self._showing_history = False
        self.history_vbox.set_visible(False)
        self.variable_vbox.set_visible(True)

    def create_button(self, cap, cb, fgcol, bgcol, width, height):
        """Create a button that is set up properly."""
        button = Gtk.Button(label=_(cap))
        self.modify_button_appearance(button, fgcol, bgcol, width, height)
        button.connect("clicked", cb)

        btn_key_controller = Gtk.EventControllerKey()
        btn_key_controller.connect('key-pressed',
                                    self._parent.ignore_key_cb)
        button.add_controller(btn_key_controller)

        return button

    def modify_button_appearance(self, button, fgcol, bgcol, width, height):

        button.add_css_class("calc-button")

        # Map color to semantic CSS class
        color_class_map = {
            id(self.col_white): "calc-white-btn",
            id(self.col_gray1): "calc-action-btn",
            id(self.col_gray2): "calc-numpad-btn",
            id(self.col_gray3): "calc-operator-btn",
            id(self.col_red): "calc-danger-btn",
        }
        css_class = color_class_map.get(id(bgcol))
        if css_class:
            button.add_css_class(css_class)
        
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
