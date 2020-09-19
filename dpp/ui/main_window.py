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
import ctypes
import datetime
import os
from typing import List
import qtawesome

from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QDockWidget, QTabBar

from dpp.core.logging import LogEntry, LogFilter
from dpp.ui import IconLabel
from dpp.ui.dialog.config_dialog import ConfigDialog
from dpp.ui.dock.hex_dock import HexDock
from dpp.ui.dock.log_dock import LogDock
from dpp.ui.widget.message_widget import MessageWidget


class MainWindow(QMainWindow):

    def __init__(self, context: 'core.context.Context', input: str = None):
        super().__init__()
        self._context = context
        self._logger = context.logger()

        #############################################
        #   Initialize status bar
        #############################################

        self._message_widget = self._init_message_widget()
        self._logger.handlers[0].addFilter(self._init_log_filter(self._message_widget))
        self.statusBar().addWidget(self._message_widget)
        self.statusBar().addPermanentWidget(self._init_hidden_dialog())

        #############################################
        #   Initialize docks
        #############################################

        # Initialize empty dock
        self._empty_dock = QDockWidget("", self)
        self._empty_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(Qt.BottomDockWidgetArea, self._empty_dock)
        self._empty_dock.visibilityChanged.connect(self.show_dock)

        # Initialize log dock
        self._log_entries = []
        self._log_dock = LogDock(self._log_entries, self)
        self._log_dock.clearEvent.connect(self._message_widget.resetCount)
        self._log_dock.setFeatures(QDockWidget.DockWidgetFloatable)
        self.addDockWidget(Qt.BottomDockWidgetArea, self._log_dock)
        self.tabifyDockWidget(self._empty_dock, self._log_dock)
        self._log_dock.visibilityChanged.connect(self.show_dock)

        # Initialize hex dock
        self._hex_dock = HexDock(self._context, self)
        self._hex_dock.setFeatures(QDockWidget.DockWidgetFloatable)
        self.addDockWidget(Qt.BottomDockWidgetArea, self._hex_dock)
        self.tabifyDockWidget(self._empty_dock, self._hex_dock)
        self._hex_dock.visibilityChanged.connect(self.show_dock)

        # Initialize dock tab bar
        self._dock_tab_bar = self.findChild(QTabBar, "")
        self._dock_tab_bar.tabBarDoubleClicked.connect(lambda e: self._empty_dock.raise_())

        # Do only dock tab bar on startup
        self._empty_dock.raise_()

        #############################################
        #   Initialize window
        #############################################

        self._init_window_size()
        self.setWindowTitle("Decoder++")
        self.setWindowIcon(QIcon(os.path.join(self._context.getAppPath(), 'images', 'dpp_128.png')))

    def _init_log_filter(self, message_widget):
        """ Initializes the log filter which catches log events to be shown in the statusbar. """
        log_filter = LogFilter(self)
        log_filter.logInfoEvent.connect(message_widget.showInfo)
        log_filter.logErrorEvent.connect(message_widget.showError)
        log_filter.logDebugEvent.connect(message_widget.showDebug)
        return log_filter

    def _init_window_size(self):
        """ Initializes the window size. Looks and uses any previously saved sizing. """
        size = self._context.config.getSize()
        if size:
            self.resize(self._context.config.getSize())
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
        hidden_dialog = ConfigDialog(self, self._context)
        hidden_dialog.exec_()

    def _toggle_log_dock(self, *filters: List[str], **kwargs):
        """ Shows/Hides the log dock. """
        is_log_dock_visible = not self._log_dock.visibleRegion().isEmpty()
        if not is_log_dock_visible:
            self._log_dock.raise_()
            for filter in self._log_dock.getFilters():
                self._log_dock.setFilterChecked(filter, filter in filters)
        else:
            self._empty_dock.raise_()

    def _toggle_hex_dock(self):
        """ Shows/Hides the hex dock. """
        is_hex_dock_visible = not self._hex_dock.visibleRegion().isEmpty()
        if not is_hex_dock_visible:
            self._hex_dock.raise_()
        else:
            self._empty_dock.raise_()


    def show_dock(self, e: QEvent):
        """ Shows/Hides the docks. """
        is_empty_dock_visible = not self._empty_dock.visibleRegion().isEmpty()
        for dock in [self._log_dock, self._hex_dock]:
            if is_empty_dock_visible:
                if not dock.isFloating():
                    dock.hide()
            else:
                dock.show()

    def closeEvent(self, e: QEvent):
        """ Closes the main window and saves window-size and -position. """
        self._context.config.setSize(self.size())
        self._context.config.setPosition(self.pos())
        e.accept()

    def setWindowIcon(self, icon: QIcon):
        """ Sets the window icon of the main window. """
        super(__class__, self).setWindowIcon(icon)
        if os.name == 'nt':
            # Set explicit app id to show decoder-plus-plus icon in the taskbar.
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(self._context.getAppID())
