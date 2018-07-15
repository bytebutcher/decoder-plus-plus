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

import qtawesome
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer, Qt, QRect
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QMainWindow

from core.logging.log_entry import LogEntry
from core.logging.log_filter import LogFilter
from ui import MainWindowWidget, IconLabel
from ui.dialog.hidden_dialog import HiddenDialog
from ui.dock.log_dock import LogDock


class MainWindow(QMainWindow):

    def __init__(self, context):
        super().__init__()
        self._context = context
        self._logger = context.logger()
        self._log_entries = []
        self._log_dock = LogDock(self, self._log_entries)
        self._log_dock.setHidden(True)
        self._log_dock.clearEvent.connect(self._clear_log_widget)
        self._logger.handlers[0].addFilter(self._init_log_filter())
        self.statusBar().addWidget(self._init_message_widget())
        self.statusBar().addPermanentWidget(self._init_about_widget())
        self._log_plugins_unresolved_dependencies(context)
        self._init_window_size()
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self._log_dock)
        self.setWindowTitle("Decoder++")
        self.setWindowIcon(QIcon(os.path.join(self._context.getAppPath(), 'images', 'dpp.png')))
        self._main_window_widget = MainWindowWidget(self, self._context)
        self.setCentralWidget(self._main_window_widget)
        self._logger.info("Ready")
        self.show()

    """
    Show unresolved dependencies of plugins in LogDock.
    """
    def _log_plugins_unresolved_dependencies(self, context):
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
        log_filter = LogFilter(self)
        log_filter.logInfoEvent.connect(self.showInfo)
        log_filter.logErrorEvent.connect(self.showError)
        log_filter.logDebugEvent.connect(self.showDebug)
        return log_filter

    def _init_window_size(self):
        size = self._context.config().getSize()
        if size:
            self.resize(self._context.config().getSize())
        self.setMinimumWidth(520)
        self.setMinimumHeight(300)

    def _init_message_widget(self):
        message_frame = QFrame()
        message_layout = QHBoxLayout()
        self._log_info_count_icon_label = IconLabel(self, qtawesome.icon("fa.info-circle"))
        self._log_info_count_icon_label.mouseDoubleClickEvent = lambda e: self._show_log_dock(LogDock.Filter.INFO)
        self._log_info_count_label = QLabel("0")
        self._log_info_count_label.mouseDoubleClickEvent = lambda e: self._show_log_dock(LogDock.Filter.INFO)
        message_layout.addWidget(self._log_info_count_icon_label)
        message_layout.addWidget(self._log_info_count_label)

        self._log_error_count_icon_label = IconLabel(self, qtawesome.icon("fa.exclamation-triangle"))
        self._log_error_count_icon_label.mouseDoubleClickEvent = lambda e: self._show_log_dock(LogDock.Filter.ERROR)
        self._log_error_count_label = QLabel("0")
        self._log_error_count_label.mouseDoubleClickEvent = lambda e: self._show_log_dock(LogDock.Filter.ERROR)
        message_layout.addWidget(self._log_error_count_icon_label)
        message_layout.addWidget(self._log_error_count_label)

        line = QFrame(self);
        line.setGeometry(QRect(320, 150, 118, 3));
        line.setFrameShape(QFrame.VLine);
        line.setFrameShadow(QFrame.Sunken);
        message_layout.addWidget(line, 0, Qt.AlignLeft)

        self._log_message_icon_label = IconLabel(self, qtawesome.icon("fa.check"))
        self._log_message_icon_label.mouseDoubleClickEvent = lambda e: self._show_log_dock(LogDock.Filter.INFO, LogDock.Filter.ERROR)
        self._log_message_text_label = QLabel("Ready.")
        self._log_message_text_label.mouseDoubleClickEvent = lambda e: self._show_log_dock(LogDock.Filter.INFO, LogDock.Filter.ERROR)
        message_layout.addWidget(self._log_message_icon_label)
        message_layout.addWidget(self._log_message_text_label)

        message_frame.setLayout(message_layout)
        return message_frame

    def _init_about_widget(self):
        about_label = IconLabel(self, QIcon(os.path.join(self._context.getAppPath(), 'images', 'hidden.png')))
        about_label.mousePressEvent = lambda e: self._show_hidden_dialog()
        return about_label

    def _log_message(self, type, message):
        now = datetime.datetime.now().time()
        log_entry = LogEntry(
            "{hour:02d}:{minute:02d}:{second:02d}".format(hour=now.hour, minute=now.minute, second=now.second), type,
            message)
        if self._log_dock:
            self._log_dock.addItem(log_entry)
        self._log_entries.append(log_entry)

    def _show_hidden_dialog(self):
        about_dialog = HiddenDialog(self, self._context)
        about_dialog.exec_()

    def _show_log_dock(self, *filters, **kwargs):
        self._log_dock.setVisible(self._log_dock.isHidden())
        if self._log_dock.isVisible():
            for filter in self._log_dock.getFilters():
                self._log_dock.setFilterChecked(filter, filter in filters)

    def _clear_log_widget(self):
        self._log_info_count_label.setText("0")
        self._log_error_count_label.setText("0")

    def showDebug(self, message):
        self._log_message("DEBUG", message)

    def showInfo(self, message):
        self._log_message("INFO", message)
        count = int(self._log_info_count_label.text())
        self._log_info_count_label.setText(str(count + 1))
        self.showMessage(message)

    def showError(self, message):
        self._log_message("ERROR", message)
        count = int(self._log_error_count_label.text())
        self._log_error_count_label.setText(str(count + 1))
        self.showMessage(message)

    def showMessage(self, message):
        self._log_message_text_label.setText(message)
        QTimer.singleShot(5000, lambda: self._log_message_text_label.setText("Ready."))

    def closeEvent(self, e):
        self._context.config().setSize(self.size())
        self._context.config().setPosition(self.pos())
        e.accept()
