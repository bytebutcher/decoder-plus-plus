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
import qtawesome
from PyQt5.QtCore import QRect, pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel

from ui import IconLabel


class MessageWidget(QFrame):
    """ Widget which shows messages. """

    messageReceived = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject')
    messageClicked = pyqtSignal()
    infoClicked = pyqtSignal()
    errorClicked = pyqtSignal()


    class CountWidget(QFrame):
        """ A widget with an icon and a counter. """

        def __init__(self, icon: QIcon, count: int=0, parent=None):
            super(__class__, self).__init__(parent)
            self._icon = IconLabel(parent, icon)
            self._label = QLabel()
            self.setCount(count)
            layout = QHBoxLayout()
            layout.addWidget(self._icon)
            layout.addWidget(self._label)
            layout.setContentsMargins(0, 0, 0, 0)
            self.setLayout(layout)

        def setCount(self, count: int):
            """ Sets the counter to the specified value. """
            self._label.setText(str(count))

        def getCount(self) -> int:
            """ Returns the counter. """
            return int(self._label.text())

        def incrementCount(self):
            """ Increments the counter. """
            self._label.setText(str(self.getCount() + 1))

        def decrementCount(self):
            """ Decrements the counter. """
            self._label.setText(str(self.getCount() - 1))

        def resetCount(self):
            """ Resets the counter to zero. """
            self.setCount(0)

    def __init__(self, parent=None):
        super(__class__, self).__init__(parent)
        layout = QHBoxLayout()
        self._log_info_count_widget = MessageWidget.CountWidget(qtawesome.icon("fa.info-circle"), 0, self)
        self._log_info_count_widget.mouseDoubleClickEvent = lambda e: self.infoClicked.emit()
        self._log_error_count_widget = MessageWidget.CountWidget(qtawesome.icon("fa.exclamation-triangle"), 0, self)
        self._log_error_count_widget.mouseDoubleClickEvent = lambda e: self.errorClicked.emit()

        layout.addWidget(self._log_info_count_widget)
        layout.addWidget(self._log_error_count_widget)

        line = QFrame(self)
        line.setGeometry(QRect(320, 150, 118, 3))
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line, 0, Qt.AlignLeft)

        self._log_message_icon_label = IconLabel(self, qtawesome.icon("fa.check"))
        self._log_message_icon_label.mouseDoubleClickEvent = lambda e: self.messageClicked.emit()
        self._log_message_text_label = QLabel("Ready.")
        self._log_message_text_label.mouseDoubleClickEvent = lambda e: self.messageClicked.emit()
        layout.addWidget(self._log_message_icon_label)
        layout.addWidget(self._log_message_text_label)

        self.setLayout(layout)

    def _log_message(self, type: str, message: str):
        """
        Emits a message event.
        :param type: the type of the message (e.g. info, error, debug).
        :param message: the message.
        """
        self.messageReceived.emit(type, message)


    def showDebug(self, message: str, log_only: bool=False):
        """ Adds debug message to the log. """
        self._log_message("DEBUG", message)

    def showInfo(self, message: str, log_only: bool=False):
        """ Shows info message in the statusbar. Adds info message to the log. Increments info count. """
        self._log_message("INFO", message)
        self._log_info_count_widget.incrementCount()
        if not log_only:
            self.showMessage(message)

    def showError(self, message: str, log_only: bool=False):
        """ Shows error message in the statusbar. Adds error message to the log. Increments error count. """
        self._log_message("ERROR", message)
        self._log_error_count_widget.incrementCount()
        if not log_only:
            self.showMessage(message)

    def showMessage(self, message: str):
        """
        Displays a message (shortened to 100 characters) for 5 seconds in the statusbar.
        :param message: the message to display.
        """
        if message:
            message = self._shorten_message(message, 100)
            self._log_message_text_label.setText(message)
            QTimer.singleShot(5000, lambda: self._log_message_text_label.setText("Ready."))

    def _shorten_message(self, message: str, max_length: int):
        """
        Removes new-lines and shortens message to the specified max_length.
        :param message: the message to shorten.
        :param max_length: the max length of the message.
        :return: the shortened message.
        """
        merged_lines = " ".join(message.splitlines())
        if len(merged_lines) > (max_length - 3):
            return merged_lines[:(max_length - 3)] + "..."
        else:
            return merged_lines

    def resetCount(self):
        """ Resets the info- and error-log-counters to zero. """
        self._log_info_count_widget.resetCount()
        self._log_error_count_widget.resetCount()
