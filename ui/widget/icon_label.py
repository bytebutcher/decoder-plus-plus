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

from PyQt5.QtWidgets import QLabel


class IconLabel(QLabel):
    """ A widget for showing an icon. """

    def __init__(self, parent, icon):
        super(IconLabel, self).__init__(parent)
        self.setIcon(icon)

    def setIcon(self, icon):
        """ Sets the icon. """
        self._icon = icon

    def paintEvent(self, event=None):
        """ Paints the specified icon (if any). """
        super(IconLabel, self).paintEvent(event)
        if self._icon is not None:
            pxm = self._icon.pixmap(self.height(), self.height())
            self.setPixmap(pxm)
