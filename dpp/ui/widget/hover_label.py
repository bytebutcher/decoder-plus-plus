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
from qtpy import QtCore

from dpp.ui.widget.clickable_label import ClickableLabel


class HoverLabel(ClickableLabel):
    """ A label a hover effect. """

    def __init__(self, parent):
        super(HoverLabel, self).__init__(parent)
        self._is_toggled = False
        self.setHoverEffect(True)

    def isToggled(self) -> bool:
        return self._is_toggled

    def toggle(self):
        self._is_toggled = not self._is_toggled
        self.setProperty("toggled", self._is_toggled)
        self.style().polish(self)

    def setHoverEffect(self, status: bool):
        """ Enables/Disables the hover effect for the IconLabel (default = True). """
        if status:
            self.setStyleSheet("""
            QLabel:hover {
                background-color: rgb(217, 217, 217);
            }

            QLabel[pressed="true"] {
                background-color: rgb(189, 189, 189);     
            }
            
            QLabel[toggled="true"] {
                background-color: rgb(189, 189, 189);     
            }
            """)
        else:
            self.setStyleSheet("")

    def mousePressEvent(self, event):
        """ Updates the stylesheet to indicate that the IconLabel is being pressed. """
        if event.button() == QtCore.Qt.LeftButton:
            self.setProperty("pressed", True)
            self.style().polish(self)
        super(HoverLabel, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """ Updates the stylesheet to indicate that the IconLabel is being released. """
        if event.button() == QtCore.Qt.LeftButton:
            self.setProperty("pressed", False)
            self.style().polish(self)
        super(HoverLabel, self).mouseReleaseEvent(event)
