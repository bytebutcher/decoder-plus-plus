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
from qtpy.QtCore import QRect, Signal, QTimer, Qt
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QFrame, QHBoxLayout, QLabel

from dpp.core.icons import icon, Icon
from dpp.ui import IconLabel
from dpp.ui.widget.clickable_label import ClickableLabel


class MessageWidget(QFrame):
    """ Widget which shows messages. """

    messageReceived = Signal('PyQt_PyObject', 'PyQt_PyObject')
    messageClicked = Signal()
    infoClicked = Signal()
    errorClicked = Signal()

    class CountWidget(QFrame):
        """ A widget with an icon and a counter. """

        icon_clicked = Signal()

        def __init__(self, icon: QIcon, count: int=0, parent=None):
            super(__class__, self).__init__(parent)
            self._icon = IconLabel(parent, icon)
            self._icon.setHoverEffect(True)
            self._icon.clicked.connect(lambda: self.icon_clicked.emit())
            self._label = QLabel(self)
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

        self._log_info_count_widget = MessageWidget.CountWidget(icon(Icon.MSG_INFO), 0, self)
        self._log_info_count_widget.icon_clicked.connect(lambda: self.infoClicked.emit())
        self._log_info_count_widget.mouseDoubleClickEvent = lambda e: self.infoClicked.emit()
        self._log_error_count_widget = MessageWidget.CountWidget(icon(Icon.MSG_ERROR), 0, self)
        self._log_error_count_widget.icon_clicked.connect(lambda: self.errorClicked.emit())
        self._log_error_count_widget.mouseDoubleClickEvent = lambda e: self.errorClicked.emit()

        layout.addWidget(self._log_info_count_widget)
        layout.addWidget(self._log_error_count_widget)

        line = QFrame(self)
        line.setGeometry(QRect(320, 150, 118, 3))
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line, 0, Qt.AlignLeft)

        self._log_message_icon_label = IconLabel(self, icon(Icon.STATUS_READY))
        self._log_message_icon_label.setHoverEffect(True)
        self._log_message_icon_label.clicked.connect(lambda evt: self.messageClicked.emit())
        self._log_message_icon_label.setHoverEffect(True)
        self._log_message_text_label = ClickableLabel("Ready.")
        self._log_message_text_label.doubleClicked.connect(lambda e: self.messageClicked.emit())
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
            self.showMessage(message, icon(Icon.STATUS_INFO))

    def showError(self, message: str, log_only: bool=False):
        """ Shows error message in the statusbar. Adds error message to the log. Increments error count. """
        self._log_message("ERROR", message)
        self._log_error_count_widget.incrementCount()
        if not log_only:
            self.showMessage(message, icon(Icon.STATUS_ERROR))

    def showMessage(self, message: str, _icon: QIcon):
        """
        Displays a message (shortened to 100 characters) for 5 seconds in the statusbar.
        :param message: the message to display.
        :param icon_type: the type of the icon (e.g. INFO, ERROR).
        """
        if message:
            def _show_ready():
                self._log_message_icon_label.setIcon(icon(Icon.STATUS_READY))
                self._log_message_text_label.setText("Ready.")

            message = self._shorten_message(message, 100)
            self._log_message_icon_label.setIcon(_icon)
            self._log_message_text_label.setText(message)
            QTimer.singleShot(5000, _show_ready)

    def _shorten_message(self, message: str, max_length: int):
        """
        Removes new-lines and shortens message to the specified max_length.
        :param message: the message to shorten.
        :param max_length: the max length of the message.
        :return: the shortened message.
        """
        if not message:
            return ""
        merged_lines = " ".join(message.splitlines())
        if len(merged_lines) > (max_length - 3):
            return merged_lines[:(max_length - 3)] + "..."
        else:
            return merged_lines

    def resetCount(self):
        """ Resets the info- and error-log-counters to zero. """
        self._log_info_count_widget.resetCount()
        self._log_error_count_widget.resetCount()
