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

from PyQt5.QtCore import pyqtSignal, Qt, QEvent
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QLineEdit


class SearchField(QLineEdit):
    """ Enhances the standard QLineEdit with an icon and additional key-press-events. """

    enterPressed = pyqtSignal()
    escapePressed = pyqtSignal()
    arrowPressed = pyqtSignal()

    def __init__(self, parent=None):
        super(__class__, self).__init__(parent)
        self._icon = None
        self._suppress_enter_key = False
        self._closable = False
        self.installEventFilter(self)

    def suppressEnterKey(self, suppress=True):
        """ Suppresses the Key_Enter and Key_Return key-press-event when set to True (default = True). """
        self._suppress_enter_key = suppress

    def keyPressEvent(self, evt):
        """ Fires additional signals when a key is pressed. """
        key = evt.key()
        if not self._suppress_enter_key and (key == Qt.Key_Enter or key == Qt.Key_Return):
            self.enterPressed.emit()
        elif key == Qt.Key_Escape:
            self.escapePressed.emit()
        elif key == Qt.Key_Up or key == Qt.Key_Down:
            self.arrowPressed.emit()
        else:
            super(__class__, self).keyPressEvent(evt)

    def eventFilter(self, watched, event):
        """ Catches Mouse-Move- and Mouse-Button-Press-Events for handling Close-Button. """
        if not self._closable:
            return False

        if watched != self:
            return False

        if event.type() != QEvent.MouseMove and event.type() != QEvent.MouseButtonPress:
            return False

        p = event.pos()
        if p.x() > (self.width() - 20):
            self.setCursor(Qt.ArrowCursor)
            if event.type() == QEvent.MouseButtonPress:
                self.setVisible(False)
        else:
            self.setCursor(Qt.IBeamCursor)

        return False

    def setClosable(self, closable):
        """ When True, this adds a close button to the search field. """
        self._closable = closable

    def isClosable(self):
        """ Returns whether the search field has a close button. """
        return self._closable

    def setIcon(self, icon):
        """ Sets the specified icon in front of the text. """
        if icon is None:
            self.setTextMargins(1, 1, 1, 1)
        self._icon = icon

    def hasIcon(self):
        return self._icon is not None

    def paintEvent(self, event=None):
        """ Paints the specified icon (if any). """
        super(__class__, self).paintEvent(event)
        if self.hasIcon() or self.isClosable():
            painter = QPainter(self)
            left, top, right, bottom = 1, 1, 1, 1
            if self.hasIcon():
                left = self.height()
                pxm = self._icon.pixmap(self.height() - 10, self.height() - 10)
                painter.drawPixmap(5, 5, pxm)
            if self.isClosable():
                right = 20
                painter.drawText(self.width() - 15, 15, "X")
            self.setTextMargins(left, top, right, bottom)