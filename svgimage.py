# svgimage.py, svg image class by Reinier Heeres <reinier@heeres.eu>
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
#    2007-09-07: rwh, first version

import logging
_logger = logging.getLogger('SVGImage')

from gi.repository import Gtk, Gdk, GdkPixbuf


class SVGImage:

    def __init__(self, fn=None, data=None):
        self._svg_data = None
        if fn is not None:
            self.load(fn)
        elif data is not None:
            self.load_data(data)

    def get_image(self):
        return getattr(self, '_image', None)

    def get_svg_data(self):
        return self._svg_data
    
    def render_svg(self):
        b_data = self._svg_data.encode('utf-8') if isinstance(self._svg_data, str) else self._svg_data
        
        pixbuf = None
        
        try:
            loader = GdkPixbuf.PixbufLoader.new_with_type('svg')
            loader.write(b_data)
            loader.close()
            pixbuf = loader.get_pixbuf()
        except Exception as e:
            _logger.error("Failed to load SVG with PixbufLoader: %s", e)
        
        if not pixbuf:
            _logger.error("Could not render SVG to pixbuf.")
            return None

        _logger.debug("SVG rendered to pixbuf: %dx%d",
                       pixbuf.get_width(), pixbuf.get_height())

        texture = Gdk.Texture.new_for_pixbuf(pixbuf)
        
        self._image = Gtk.Picture()
        self._image.set_paintable(texture)

        self._image.set_size_request(pixbuf.get_width(),
                                     pixbuf.get_height())
        try:
            self._image.set_can_shrink(False)
        except AttributeError:
            pass
        
        self._image.set_halign(Gtk.Align.CENTER)
        self._image.set_valign(Gtk.Align.START)
        
        return self._image

    def load(self, fn):
        with open(fn, 'rb') as f:
            self._svg_data = f.read()
        return self.render_svg()

    def load_data(self, svgdat):
        self._svg_data = svgdat
        return self.render_svg()
