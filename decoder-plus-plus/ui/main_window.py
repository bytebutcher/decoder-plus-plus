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

from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow

from core.logging.log_entry import LogEntry
from core.logging.log_filter import LogFilter
from ui import MainWindowWidget, IconLabel
from ui.dialog.hidden_dialog import HiddenDialog
from ui.dock.log_dock import LogDock
from ui.widget.message_widget import MessageWidget


class MainWindow(QMainWindow):

    def __init__(self, context: 'core.context.Context'):
        super().__init__()
        self._context = context
        self._logger = context.logger()
        self._message_widget = self._init_message_widget()
        self._log_entries = []
        self._log_dock = LogDock(self, self._log_entries)
        self._log_dock.setHidden(True)
        self._log_dock.clearEvent.connect(self._message_widget.resetCount)
        self._logger.handlers[0].addFilter(self._init_log_filter())
        self.statusBar().addWidget(self._message_widget)
        self.statusBar().addPermanentWidget(self._init_hidden_dialog())
        self._log_plugins_unresolved_dependencies(context)
        self._init_window_size()
        self.addDockWidget(Qt.BottomDockWidgetArea, self._log_dock)
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
                self._message_widget.showError(
                    "{}: Unresolved dependencies {}".format(plugin_name, ", ".join(unresolved_dependencies)),
                    log_only=True
                )
        except Exception as e:
            print(e)

    def _init_log_filter(self):
        """ Initializes the log filter which catches log events to be shown in the statusbar. """
        log_filter = LogFilter(self)
        log_filter.logInfoEvent.connect(self._message_widget.showInfo)
        log_filter.logErrorEvent.connect(self._message_widget.showError)
        log_filter.logDebugEvent.connect(self._message_widget.showDebug)
        return log_filter

    def _init_window_size(self):
        """ Initializes the window size. Looks and uses any previously saved sizing. """
        size = self._context.config().getSize()
        if size:
            self.resize(self._context.config().getSize())
        self.setMinimumWidth(520)
        self.setMinimumHeight(300)

    def _init_message_widget(self) -> MessageWidget:
        """ Inits the message widget located in the statusbar. """
        message_widget = MessageWidget()
        message_widget.messageReceived.connect(self._log_message)
        message_widget.infoClicked.connect(lambda: self._toggle_log_dock(LogDock.Filter.INFO))
        message_widget.errorClicked.connect(lambda: self._toggle_log_dock(LogDock.Filter.ERROR))
        message_widget.messageClicked.connect(lambda: self._toggle_log_dock(LogDock.Filter.INFO, LogDock.Filter.ERROR))
        return message_widget

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

    def closeEvent(self, e: QEvent):
        """ Closes the main window and saves window-size and -position. """
        self._context.config().setSize(self.size())
        self._context.config().setPosition(self.pos())
        e.accept()
