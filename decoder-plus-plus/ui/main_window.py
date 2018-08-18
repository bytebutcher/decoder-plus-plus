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

import datetime
import os
from typing import List

import qtawesome
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer, Qt, QRect, QEvent
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QMainWindow

from core.logging.log_entry import LogEntry
from core.logging.log_filter import LogFilter
from ui import MainWindowWidget, IconLabel
from ui.dialog.hidden_dialog import HiddenDialog
from ui.dock.log_dock import LogDock


class MainWindow(QMainWindow):

    def __init__(self, context: 'core.context.Context'):
        super().__init__()
        self._context = context
        self._logger = context.logger()
        self._log_entries = []
        self._log_dock = LogDock(self, self._log_entries)
        self._log_dock.setHidden(True)
        self._log_dock.clearEvent.connect(self._reset_log_counters)
        self._logger.handlers[0].addFilter(self._init_log_filter())
        self.statusBar().addWidget(self._init_message_widget())
        self.statusBar().addPermanentWidget(self._init_hidden_dialog())
        self._log_plugins_unresolved_dependencies(context)
        self._init_window_size()
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self._log_dock)
        self.setWindowTitle("Decoder++")
        self.setWindowIcon(QIcon(os.path.join(self._context.getAppPath(), 'images', 'dpp.png')))
        self._main_window_widget = MainWindowWidget(self, self._context)
        self.setCentralWidget(self._main_window_widget)
        self._logger.info("Ready")
        self.show()

    def _log_plugins_unresolved_dependencies(self, context: 'core.context.Context'):
        """ Show unresolved dependencies of plugins in LogDock. """
        try:
            for plugin_name in context.getUnresolvedDependencies():
                unresolved_dependencies = context.getUnresolvedDependencies()[plugin_name]
                count = int(self._log_error_count_label.text())
                self._log_error_count_label.setText(str(count + 1))
                self._log_message("ERROR", "{}: Unresolved dependencies {}".format(
                    plugin_name, ", ".join(unresolved_dependencies)))
        except Exception as e:
            print(e)

    def _init_log_filter(self):
        """ Initializes the log filter which catches log events to be shown in the statusbar. """
        log_filter = LogFilter(self)
        log_filter.logInfoEvent.connect(self.showInfo)
        log_filter.logErrorEvent.connect(self.showError)
        log_filter.logDebugEvent.connect(self.showDebug)
        return log_filter

    def _init_window_size(self):
        """ Initializes the window size. Looks and uses any previously saved sizing. """
        size = self._context.config().getSize()
        if size:
            self.resize(self._context.config().getSize())
        self.setMinimumWidth(520)
        self.setMinimumHeight(300)

    def _init_message_widget(self):
        """ Inits the message widget located in the statusbar. """
        message_frame = QFrame()
        message_layout = QHBoxLayout()
        self._log_info_count_icon_label = IconLabel(self, qtawesome.icon("fa.info-circle"))
        self._log_info_count_icon_label.mouseDoubleClickEvent = lambda e: self._toggle_log_dock(LogDock.Filter.INFO)
        self._log_info_count_label = QLabel("0")
        self._log_info_count_label.mouseDoubleClickEvent = lambda e: self._toggle_log_dock(LogDock.Filter.INFO)
        message_layout.addWidget(self._log_info_count_icon_label)
        message_layout.addWidget(self._log_info_count_label)

        self._log_error_count_icon_label = IconLabel(self, qtawesome.icon("fa.exclamation-triangle"))
        self._log_error_count_icon_label.mouseDoubleClickEvent = lambda e: self._toggle_log_dock(LogDock.Filter.ERROR)
        self._log_error_count_label = QLabel("0")
        self._log_error_count_label.mouseDoubleClickEvent = lambda e: self._toggle_log_dock(LogDock.Filter.ERROR)
        message_layout.addWidget(self._log_error_count_icon_label)
        message_layout.addWidget(self._log_error_count_label)

        line = QFrame(self)
        line.setGeometry(QRect(320, 150, 118, 3))
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        message_layout.addWidget(line, 0, Qt.AlignLeft)

        self._log_message_icon_label = IconLabel(self, qtawesome.icon("fa.check"))
        self._log_message_icon_label.mouseDoubleClickEvent = lambda e: self._toggle_log_dock(LogDock.Filter.INFO, LogDock.Filter.ERROR)
        self._log_message_text_label = QLabel("Ready.")
        self._log_message_text_label.mouseDoubleClickEvent = lambda e: self._toggle_log_dock(LogDock.Filter.INFO, LogDock.Filter.ERROR)
        message_layout.addWidget(self._log_message_icon_label)
        message_layout.addWidget(self._log_message_text_label)

        message_frame.setLayout(message_layout)
        return message_frame

    def _init_hidden_dialog(self):
        """ Inits the icon which opens the hidden dialog on mouse press. """
        about_label = IconLabel(self, QIcon(os.path.join(self._context.getAppPath(), 'images', 'hidden.png')))
        about_label.mousePressEvent = lambda e: self._show_hidden_dialog()
        return about_label

    def _log_message(self, type: str, message: str):
        """
        Adds the message to the log dock.
        :param type: the type of the message (e.g. info, error, debug).
        :param message: the message.
        """
        now = datetime.datetime.now().time()
        log_entry = LogEntry(
            "{hour:02d}:{minute:02d}:{second:02d}".format(hour=now.hour, minute=now.minute, second=now.second), type,
            message)
        if self._log_dock:
            self._log_dock.addItem(log_entry)
        self._log_entries.append(log_entry)

    def _show_hidden_dialog(self):
        """ Shows the hidden dialog. """
        hidden_dialog = HiddenDialog(self, self._context)
        hidden_dialog.exec_()

    def _toggle_log_dock(self, *filters: List[str], **kwargs):
        """ Shows/Hides the log dock. """
        self._log_dock.setVisible(self._log_dock.isHidden())
        if self._log_dock.isVisible():
            for filter in self._log_dock.getFilters():
                self._log_dock.setFilterChecked(filter, filter in filters)

    def _reset_log_counters(self):
        """ Resets the info- and error-log-counters to zero. """
        self._log_info_count_label.setText("0")
        self._log_error_count_label.setText("0")

    def showDebug(self, message: str):
        """ Adds debug message to the log. """
        self._log_message("DEBUG", message)

    def showInfo(self, message: str):
        """ Shows info message in the statusbar. Adds info message to the log. Increments info count. """
        self._log_message("INFO", message)
        count = int(self._log_info_count_label.text())
        self._log_info_count_label.setText(str(count + 1))
        self.showMessage(message)

    def showError(self, message: str):
        """ Shows error message in the statusbar. Adds error message to the log. Increments error count. """
        self._log_message("ERROR", message)
        count = int(self._log_error_count_label.text())
        self._log_error_count_label.setText(str(count + 1))
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

    def closeEvent(self, e: QEvent):
        """ Closes the main window and saves window-size and -position. """
        self._context.config().setSize(self.size())
        self._context.config().setPosition(self.pos())
        e.accept()
