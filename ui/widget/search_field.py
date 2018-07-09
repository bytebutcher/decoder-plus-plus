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

from PyQt5 import QtCore
from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QLineEdit


class SearchField(QLineEdit):
    """ Enhanced the standard QLineEdit. """

    enterPressed = pyqtSignal()
    escapePressed = pyqtSignal()
    arrowPressed = pyqtSignal()

    def __init__(self, parent=None):
        super(SearchField, self).__init__(parent)
        self._icon = None
        self._suppress_enter_key = False

    def suppressEnterKey(self, suppress=True):
        """ Suppresses the Key_Enter and Key_Return key-press-event when set to True (default = True). """
        self._suppress_enter_key = suppress

    def keyPressEvent(self, evt):
        """ Fires additional signals when a key is pressed. """
        key = evt.key()
        if not self._suppress_enter_key and (key == QtCore.Qt.Key_Enter or key == QtCore.Qt.Key_Return):
            self.enterPressed.emit()
        elif key == QtCore.Qt.Key_Escape:
            self.escapePressed.emit()
        elif key == QtCore.Qt.Key_Up or key == QtCore.Qt.Key_Down:
            self.arrowPressed.emit()
        super(SearchField, self).keyPressEvent(evt)

    def flashBackgroundColor(self, color):
        self.setStyleSheet('QLineEdit { background-color: ' + color + ' }')
        QTimer.singleShot(200, self._resetStyleSheet)

    def _resetStyleSheet(self):
        self.setStyleSheet("")

    def setIcon(self, icon):
        """ Sets the specified icon in front of the text. """
        if icon is None:
            self.setTextMargins(1, 1, 1, 1)
            self._icon = None
        else:
            self._icon = icon

    def paintEvent(self, event=None):
        """ Paints the specified icon (if any). """
        super(SearchField, self).paintEvent(event)
        if self._icon is not None:
            pxm = self._icon.pixmap(self.height() - 10, self.height() - 10)
            painter = QPainter(self)
            painter.drawPixmap(5, 5, pxm)
            self.setTextMargins(self.height(), 1, 1, 1)


