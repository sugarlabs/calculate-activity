# -*- coding: utf-8 -*-
# mathlib.py, generic math library wrapper
# by Reinier Heeres <reinier@heeres.eu>
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

import types
import math
from decimal import Decimal
from rational import Rational

import logging
_logger = logging.getLogger('MathLib')

from gettext import gettext as _
import locale

# Python 2.5 does not have a binary formatter built-in
# This requires a function b10bin() to interpret the result


def format_bin(n):
    bits = ''
    while n > 0:
        if n & 1:
            bits = '1' + bits
        else:
            bits = '0' + bits
        n >>= 1

    return 'b10bin(%s)' % bits

try:
    _BIN = bin
except:
    _BIN = format_bin


class MathLib:
    ANGLE_DEG = math.pi / 180
    ANGLE_RAD = 1
    ANGLE_GRAD = 1

    FORMAT_EXPONENT = 1
    FORMAT_SCIENTIFIC = 2

    def __init__(self):
        self.set_format_type(self.FORMAT_SCIENTIFIC)
        self.set_digit_limit(9)
        self.set_chop_zeros(True)
        self.set_integer_base(10)

        self._setup_i18n()

    def _setup_i18n(self):
        loc = locale.localeconv()

        # The separator to mark thousands (default: ',')
        self.thousand_sep = loc['thousands_sep']
        if self.thousand_sep == "" or self.thousand_sep is None:
            self.thousand_sep = ","

        # The separator to mark fractions (default: '.')
        self.fraction_sep = loc['decimal_point']
        if self.fraction_sep == "" or self.fraction_sep is None:
            self.fraction_sep = "."

        # TRANS: multiplication symbol (default: '×')
        self.mul_sym = _('mul_sym')
        if len(self.mul_sym) == 0 or len(self.mul_sym) > 3:
            self.mul_sym = '×'

        # TRANS: division symbol (default: '÷')
        self.div_sym = _('div_sym')
        if len(self.div_sym) == 0 or len(self.div_sym) > 3:
            self.div_sym = '÷'

        # TRANS: equal symbol (default: '=')
        self.equ_sym = _('equ_sym')
        if len(self.equ_sym) == 0 or len(self.equ_sym) > 3:
            self.equ_sym = '='

    def set_format_type(self, fmt, digit_limit=9):
        self.format_type = fmt
        _logger.debug('Format type set to %s', fmt)

    def set_integer_base(self, base):
        if base not in (2, 8, 10, 16):
            _logger.warning('Unsupported integer base requested')
            return False
        self.integer_base = base
        _logger.debug('Integer base set to %s', base)

    def set_digit_limit(self, digits):
        self.digit_limit = digits
        _logger.debug('Digit limit set to %s', digits)

    def set_chop_zeros(self, chop):
        self.chop_zeros = bool(chop)
        _logger.debug('Chop zeros set to %s', self.chop_zeros)

    def d(self, val):
        if isinstance(val, Decimal):
            return val
        elif type(val) in (types.IntType, types.LongType):
            return Decimal(val)
        elif isinstance(val, str):
            d = Decimal(val)
            return d.normalize()
        elif isinstance(val, float) or hasattr(val, '__float__'):
            s = '%.18e' % float(val)
            d = Decimal(s)
            return d.normalize()
        else:
            return None

    def parse_number(self, s):
        s = s.replace(self.fraction_sep, '.')

        try:
            d = Decimal(s)
            if self.is_int(d):
                return int(d)
            else:
                return Decimal(s)
        except Exception:
            return None

    _BASE_FUNC_MAP = {
        2: _BIN,
        8: oct,
        16: hex,
    }

    def format_int(self, n, base=None):
        if base is None:
            base = self.integer_base
        ret = self._BASE_FUNC_MAP[base](long(n))
        return ret.rstrip('L')

    def format_decimal(self, n):
        a = int(n)
        if a == n:
            return str(n)
        if self.chop_zeros:
            n = n.normalize()
        (sign, digits, exp) = n.as_tuple()
        if n < 1 and n > -1:
            res = round(n, self.digit_limit)

        else:
            round_to = self.digit_limit - (len(digits) + exp)
            if round_to > 0:
                res = round(n, round_to)
            else:
                res = round(n, self.digit_limit)
        return res

    def format_number(self, n):
        if isinstance(n, bool):
            if n:
                return 'True'
            else:
                return 'False'
        elif isinstance(n, str):
            return n
        elif isinstance(n, unicode):
            return n
        elif isinstance(n, str):
            return _('Undefined')
        elif isinstance(n, int):
            n = self.d(n)
        elif isinstance(n, float):
            n = self.d(n)
        elif isinstance(n, long):
            n = self.d(n)
        elif isinstance(n, Rational):
            n = self.d(Decimal(n.n) / Decimal(n.d))
        elif not isinstance(n, Decimal):
            return _('Error: unsupported type')

        if self.is_int(n) and self.integer_base != 10:
            return self.format_int(n)
        else:
            return self.format_decimal(n)

    def short_format(self, n):
        ret = self.format_number(n)
        if len(ret) > 7:
            ret = "%1.1e" % n
        return ret

    def is_int(self, n):
        if isinstance(n, int) or isinstance(n, long):
            return True

        if not isinstance(n, Decimal):
            n = self.d(n)
            if n is None:
                return False

        (sign, d, e) = n.normalize().as_tuple()
        return e >= 0

if __name__ == "__main__":
    ml = MathLib()
    val = 0.99999999999999878
    print 'is_int(%.18e): %s' % (val, ml.is_int(val))
    # Beyond float precision
    val = 0.999999999999999999
    print 'is_int(%.18e): %s' % (val, ml.is_int(val))
    val = ml.d(0.99999999999999878) ** 2
    print 'is_int(%s): %s' % (val, ml.is_int(val))
    vals = ('0.1230', '12.340', '0.0123', '1230', '123.0', '1.230e17')
    for valstr in vals:
        val = Decimal(valstr)
        print 'Formatted value: %s (from %s)' % (ml.format_number(val), valstr)
    for base in (2, 8, 16):
        print 'Format 252 in base %d: %s' % (base, ml.format_int(252, base))
