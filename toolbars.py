# -*- coding: utf-8 -*-
# toolbars.py, see CalcActivity.py for info

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from gi.repository import Gdk
from mathlib import MathLib

from sugar4.graphics.palette import Palette
from sugar4.graphics.menuitem import MenuItem
from sugar4.graphics.toolbutton import ToolButton
from sugar4.graphics.toggletoolbutton import ToggleToolButton
from sugar4.graphics.style import GRID_CELL_SIZE

import logging
_logger = logging.getLogger('calc-activity')

from gettext import gettext as _


def _icon_exists(name):
    if name == '':
        return False

    theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
    if theme.has_icon(name):
        return True

    return False


class IconToolButton(ToolButton):

    def __init__(self, icon_name, text, cb, help_cb=None, alt_html=''):
        ToolButton.__init__(self)
        self.add_css_class("calc-button")
        self.add_css_class("calc-operator-btn")

        if _icon_exists(icon_name):
            self.props.icon_name = icon_name
        else:
            if alt_html == '':
                alt_html = icon_name

            label = Gtk.Label()
            label.add_css_class("toolbar-fallback-label")
            label.set_markup(alt_html)
            self.set_child(label)

        self.create_palette(text, help_cb)

        self.connect('clicked', cb)

    def create_palette(self, text, help_cb):
        p = Palette(text)

        if help_cb is not None:
            item = MenuItem(_('Help'), 'action-help')
            item.connect('activate', help_cb)
            p.menu.append(item)

        self.set_palette(p)


class IconToggleToolButton(ToggleToolButton):

    def __init__(self, items, cb, desc):
        ToggleToolButton.__init__(self)
        self.add_css_class("calc-button")
        self.add_css_class("calc-operator-btn")
        self.items = items
        if 'icon' in items[0] and _icon_exists(items[0]['icon']):
            self.props.icon_name = items[0]['icon']
        elif 'html' in items[0]:
            self.set_label(items[0]['html'])
#        self.set_tooltip(items[0][1])
        self.set_tooltip(desc)
        self.selected = 0
        self.connect('clicked', self.toggle_button)
        self.callback = cb

    def toggle_button(self, w):
        self.selected = (self.selected + 1) % len(self.items)
        but = self.items[self.selected]
        if 'icon' in but and _icon_exists(but['icon']):
            self.props.icon_name = but['icon']
        elif 'html' in but:
            _logger.info('Setting html: %s', but['html'])
            self.set_label(but['html'])
#        self.set_tooltip(but[1])
        if self.callback is not None:
            if 'html' in but:
                self.callback(but['html'])
            else:
                self.callback(but)


class TextToggleToolButton(Gtk.ToggleButton):

    def __init__(self, items, cb, desc, index=False):
        Gtk.ToggleButton.__init__(self)
        self.add_css_class("calc-button")
        self.add_css_class("calc-operator-btn")
        self.items = items
        self.set_label(items[0])
        self.selected = 0
        self.connect('toggled', self.toggle_button)
        self.callback = cb
        self.index = index
        self.set_tooltip_text(desc)

    def toggle_button(self, w):
        self.selected = (self.selected + 1) % len(self.items)
        but = self.items[self.selected]
        self.set_label(but)
        if self.callback is not None:
            if self.index:
                self.callback(self.selected)
            else:
                self.callback(but)


class LineSeparator(Gtk.Separator):

    def __init__(self):
        Gtk.Separator.__init__(self, orientation=Gtk.Orientation.VERTICAL)


class EditToolbar(Gtk.Box):

    def __init__(self, calc):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)

        copy_tool = ToolButton('edit-copy')
        copy_tool.set_tooltip(_('Copy'))
        copy_tool.set_accelerator(_('<ctrl>c'))
        copy_tool.connect('clicked', lambda x: calc.text_copy())
        self.append(copy_tool)

        menu_item = MenuItem(_('Cut'))

        try:
            menu_item.set_accelerator(_('<ctrl>x'))
        except AttributeError:
            pass

        menu_item.connect('activate', lambda x: calc.text_cut())
        copy_tool.get_palette().menu.append(menu_item)

        self.append(IconToolButton('edit-paste', _('Paste'),
                                   lambda x: calc.text_paste(),
                                   alt_html='Paste'))


class AlgebraToolbar(Gtk.Box):

    def __init__(self, calc):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)

        self.append(IconToolButton('algebra-square', _('Square'),
                                   lambda x: calc.button_pressed(
                                       calc.TYPE_OP_POST, '**2'),
                                   lambda x: calc.button_pressed(
                                       calc.TYPE_TEXT, 'help(square)'),
                                   alt_html='x<sup>2</sup>'))

        self.append(IconToolButton('algebra-sqrt', _('Square root'),
                                   lambda x: calc.button_pressed(
                                       calc.TYPE_FUNCTION, 'sqrt'),
                                   lambda x: calc.button_pressed(
                                       calc.TYPE_TEXT, 'help(sqrt)'),
                                   alt_html='√x'))

        self.append(IconToolButton('algebra-xinv', _('Inverse'),
                                   lambda x: calc.button_pressed(
                                       calc.TYPE_OP_POST, '**-1'),
                                   lambda x: calc.button_pressed(
                                       calc.TYPE_TEXT, 'help(inv)'),
                                   alt_html='x<sup>-1</sup>'))

        self.append(LineSeparator())

        self.append(IconToolButton('algebra-exp', _('e to the power x'),
                                   lambda x: calc.button_pressed(
                                       calc.TYPE_FUNCTION, 'exp'),
                                   lambda x: calc.button_pressed(
                                       calc.TYPE_TEXT, 'help(exp)'),
                                   alt_html='e<sup>x</sup>'))

        self.append(IconToolButton('algebra-xpowy', _('x to the power y'),
                                   lambda x: calc.button_pressed(
                                       calc.TYPE_FUNCTION, 'pow'),
                                   lambda x: calc.button_pressed(
                                       calc.TYPE_TEXT, 'help(pow)'),
                                   alt_html='x<sup>y</sup>'))

        self.append(IconToolButton('algebra-ln', _('Natural logarithm'),
                                   lambda x: calc.button_pressed(
                                       calc.TYPE_FUNCTION, 'ln'),
                                   lambda x: calc.button_pressed(
                                       calc.TYPE_TEXT, 'help(ln)')))

        self.append(LineSeparator())

        self.append(IconToolButton(
            'algebra-fac', _('Factorial'),
            lambda x: calc.button_pressed(calc.TYPE_FUNCTION, 'factorial'),
            lambda x: calc.button_pressed(calc.TYPE_TEXT,
                                          'help(factorial)')))


class TrigonometryToolbar(Gtk.Box):

    def __init__(self, calc):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)

        self.append(IconToolButton(
            'trigonometry-sin', _('Sine'),
            lambda x: calc.button_pressed(calc.TYPE_FUNCTION, 'sin'),
            lambda x: calc.button_pressed(calc.TYPE_TEXT, 'help(sin)')))

        self.append(IconToolButton(
            'trigonometry-cos', _('Cosine'),
            lambda x: calc.button_pressed(calc.TYPE_FUNCTION, 'cos'),
            lambda x: calc.button_pressed(calc.TYPE_TEXT, 'help(cos)')))

        self.append(IconToolButton(
            'trigonometry-tan', _('Tangent'),
            lambda x: calc.button_pressed(calc.TYPE_FUNCTION, 'tan'),
            lambda x: calc.button_pressed(calc.TYPE_TEXT, 'help(tan)')))

        self.append(LineSeparator())

        self.append(IconToolButton(
            'trigonometry-asin', _('Arc sine'),
            lambda x: calc.button_pressed(calc.TYPE_FUNCTION, 'asin'),
            lambda x: calc.button_pressed(calc.TYPE_TEXT, 'help(asin)')))

        self.append(IconToolButton(
            'trigonometry-acos', _('Arc cosine'),
            lambda x: calc.button_pressed(calc.TYPE_FUNCTION, 'acos'),
            lambda x: calc.button_pressed(calc.TYPE_TEXT, 'help(acos)')))

        self.append(IconToolButton(
            'trigonometry-atan', _('Arc tangent'),
            lambda x: calc.button_pressed(calc.TYPE_FUNCTION, 'atan'),
            lambda x: calc.button_pressed(calc.TYPE_TEXT, 'help(atan)')))

        self.append(LineSeparator())

        self.append(IconToolButton(
            'trigonometry-sinh', _('Hyperbolic sine'),
            lambda x: calc.button_pressed(calc.TYPE_FUNCTION, 'sinh'),
            lambda x: calc.button_pressed(calc.TYPE_TEXT, 'help(sinh)')))

        self.append(IconToolButton(
            'trigonometry-cosh', _('Hyperbolic cosine'),
            lambda x: calc.button_pressed(calc.TYPE_FUNCTION, 'cosh'),
            lambda x: calc.button_pressed(calc.TYPE_TEXT, 'help(cosh)')))

        self.append(IconToolButton(
            'trigonometry-tanh', _('Hyperbolic tangent'),
            lambda x: calc.button_pressed(calc.TYPE_FUNCTION, 'tanh'),
            lambda x: calc.button_pressed(calc.TYPE_TEXT, 'help(tanh)')))


class BooleanToolbar(Gtk.Box):

    def __init__(self, calc):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)

        self.append(IconToolButton(
            'boolean-and', _('Logical and'),
            lambda x: calc.button_pressed(calc.TYPE_OP_POST, '&'),
            lambda x: calc.button_pressed(calc.TYPE_TEXT, 'help(And)')))

        self.append(IconToolButton(
            'boolean-or', _('Logical or'),
            lambda x: calc.button_pressed(calc.TYPE_OP_POST, '|'),
            lambda x: calc.button_pressed(calc.TYPE_TEXT, 'help(Or)')))

#        self.append(IconToolButton('boolean-xor', _('Logical xor'),
#            lambda x: calc.button_pressed(calc.TYPE_OP_POST, '^'),
#            lambda x: calc.button_pressed(calc.TYPE_TEXT, 'help(xor)')))

        self.append(LineSeparator())

        self.append(IconToolButton(
            'boolean-eq', _('Equals'),
            lambda x: calc.button_pressed(calc.TYPE_OP_POST, '==')))

        self.append(IconToolButton(
            'boolean-neq', _('Not equals'),
            lambda x: calc.button_pressed(calc.TYPE_OP_POST, '!=')))


class MiscToolbar(Gtk.Box):

    def __init__(self, calc, target_toolbar=None):
        self._target_toolbar = target_toolbar

        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)

        self.append(IconToolButton('constants-pi', _('Pi'),
                                   lambda x: calc.button_pressed(
                                       calc.TYPE_TEXT, 'pi'),
                                   alt_html='π'))

        self.append(IconToolButton(
            'constants-e', _('e'),
            lambda x: calc.button_pressed(calc.TYPE_TEXT, 'e')))

        self.append(IconToolButton(
            'constants-eulersconstant', _('γ'),
            lambda x: calc.button_pressed(calc.TYPE_TEXT,
                                          '0.577215664901533')))

        self.append(IconToolButton(
            'constants-goldenratio', _('φ'),
            lambda x: calc.button_pressed(calc.TYPE_TEXT,
                                          '1.618033988749895')))

        self._line_separator1 = LineSeparator()
        self._line_separator2 = LineSeparator()

        self._plot_button = IconToolButton(
            'plot', _('Plot'),
            lambda x: calc.button_pressed(calc.TYPE_FUNCTION, 'plot'),
            lambda x: calc.button_pressed(calc.TYPE_TEXT, 'help(plot)'))

        el = [
            {'icon': 'format-deg', 'desc': _('Degrees'), 'html': 'deg'},
            {'icon': 'format-rad', 'desc': _('Radians'), 'html': 'rad'},
        ]
        self._angle_button = IconToggleToolButton(
            el,
            lambda x: self.update_angle_type(x, calc),
            _('Degrees / Radians'))
        self.update_angle_type('deg', calc)

        el = [
            {'icon': 'format-sci', 'html': 'sci'},
            {'icon': 'format-exp', 'html': 'exp'},
        ]
        self._format_button = IconToggleToolButton(
            el,
            lambda x: self.update_format_type(x, calc),
            _('Exponent / Scientific notation'))

        el = [
            {'icon': 'digits-9', 'html': '9'},
            {'icon': 'digits-3', 'html': '3'},
            {'icon': 'digits-6', 'html': '6'},
            {'icon': 'digits-12', 'html': '12'},
            {'icon': 'digits-15', 'html': '15'},
        ]
        self._digits_button = IconToggleToolButton(
            el,
            lambda x: self.update_digits(x, calc),
            _('Number of shown digits'))

        el = [
            {'icon': 'base-10', 'html': '10'},
            {'icon': 'base-2', 'html': '2'},
            {'icon': 'base-16', 'html': '16'},
            {'icon': 'base-8', 'html': '8'}
        ]

        self._base_button = IconToggleToolButton(
            el,
            lambda x: self.update_int_base(x, calc),
            _('Integer formatting base'))

        self.update_layout()

    def update_layout(self):
        target_toolbar = self._target_toolbar if self._target_toolbar else self

        for item in [self._line_separator1, self._plot_button,
                     self._line_separator2, self._angle_button,
                     self._format_button, self._digits_button,
                     self._base_button]:
            if item.get_parent():
                item.get_parent().remove(item)
            target_toolbar.append(item)

    def _remove_buttons(self, toolbar):
        for item in [self._plot_button, self._line_separator1,
                     self._line_separator2, self._angle_button,
                     self._format_button, self._digits_button,
                     self._base_button]:
            if item.get_parent() == toolbar:
                toolbar.remove(item)

    def update_angle_type(self, text, calc):
        var = calc.parser.get_var('angle_scaling')
        if var is None:
            _logger.warning('Variable angle_scaling not defined.')
            return

        if text == 'deg':
            var.value = MathLib.ANGLE_DEG
        elif text == 'rad':
            var.value = MathLib.ANGLE_RAD
        _logger.debug('Angle scaling: %s', var.value)

    def update_format_type(self, text, calc):
        if text == 'exp':
            calc.ml.set_format_type(MathLib.FORMAT_EXPONENT)
        elif text == 'sci':
            calc.ml.set_format_type(MathLib.FORMAT_SCIENTIFIC)
        _logger.debug('Format type: %s', calc.ml.format_type)

    def update_digits(self, text, calc):
        calc.ml.set_digit_limit(int(text))
        _logger.debug('Digit limit: %s', calc.ml.digit_limit)

    def update_int_base(self, text, calc):
        calc.ml.set_integer_base(int(text))
        _logger.debug('Integer base: %s', calc.ml.integer_base)
