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
        self._do_repaint = True
        self._icon = icon
        self._last_height = None

    def setIcon(self, icon):
        """ Sets the icon. """
        self._do_repaint = True
        self._icon = icon

    def setHoverEffect(self, status: bool):
        """ Enables/Disables the hover effect for the IconLabel (default = False). """
        if status:
            self.setStyleSheet("""
            QLabel:hover {
                background-color: rgb(217, 217, 217);
            }

            QLabel[pressed="true"] {
                background-color: rgb(189, 189, 189);     
            }
            """)
        else:
            self.setStyleSheet("")

    def mousePressEvent(self, event):
        """ Updates the stylesheet to indicate that the IconLabel is being pressed. """
        self.setProperty("pressed", True)
        self.style().polish(self)
        super(IconLabel, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """ Updates the stylesheet to indicate that the IconLabel is being released. """
        self.setProperty("pressed", False)
        self.style().polish(self)
        super(IconLabel, self).mouseReleaseEvent(event)

    def paintEvent(self, event=None):
        """ Paints the specified icon (if any). """
        super(IconLabel, self).paintEvent(event)
        if self._do_repaint or (self._icon is not None and self.height() is not self._last_height):
            pxm = self._icon.pixmap(self.height(), self.height())
            self.setPixmap(pxm)
            self._last_height = self.height()
            self._do_repaint = False
