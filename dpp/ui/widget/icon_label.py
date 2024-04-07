# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of Decoder++
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from qtpy.QtGui import QIcon

from dpp.ui.widget.hover_label import HoverLabel


class IconLabel(HoverLabel):
    """ A widget for showing an icon. """

    def __init__(self, parent, icon: QIcon = None):
        super(IconLabel, self).__init__(parent)
        self._icon = None
        self._do_repaint = None
        self._last_height = None
        if icon:
            self.setIcon(icon)
        self.setHoverEffect(False)

    def setIcon(self, icon: QIcon):
        """ Sets the icon. """
        assert isinstance(icon, QIcon), f'Illegal type! Expected QIcon, got {type(icon)}!'
        self._do_repaint = True
        self._icon = icon
        self.repaint()

    def paintEvent(self, event=None):
        """ Paints the specified icon (if any). """
        super(IconLabel, self).paintEvent(event)
        if self._do_repaint or (self._icon is not None and self.height() is not self._last_height):
            pxm = self._icon.pixmap(self.height(), self.height())
            self.setPixmap(pxm)
            self._last_height = self.height()
            self._do_repaint = False
