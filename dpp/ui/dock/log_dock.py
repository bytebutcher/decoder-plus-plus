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

from typing import List

import qtawesome
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QSortFilterProxyModel, pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QTableView, QHBoxLayout, QToolButton, QVBoxLayout, QFrame, QWidget

from dpp.core.logging import LogEntry
from dpp.ui.widget.dock_widget import DockWidget
from dpp.ui.widget.spacer import VSpacer

class LogDock(DockWidget):
    """ A widget to show log events. """

    clearEvent = pyqtSignal()

    class Filter:

        INFO = "INFO"
        ERROR = "ERROR"
        DEBUG = "DEBUG"

    class ProxyModel(QSortFilterProxyModel):
        def __init__(self):
            super(LogDock.ProxyModel, self).__init__()
            self._filter_info = True
            self._filter_error = True
            self._filter_debug = False

        def filterAcceptsRow(self, rowProc, parentProc):
            sourceModel = self.sourceModel()
            indexProc = sourceModel.index(rowProc, 0, parentProc)
            node = sourceModel.data(indexProc)
            return self._filter("INFO", self._filter_info, node) or \
                   self._filter("ERROR", self._filter_error, node) or \
                   self._filter("DEBUG", self._filter_debug, node)

        def _filter(self, type: str, status: bool, nodeName: str):
            return (nodeName is not None) and (status and type == nodeName)

        def setFilterInfo(self, status: bool):
            self._filter_info = status

        def setFilterError(self, status: bool):
            self._filter_error = status

        def setFilterDebug(self, status: bool):
            self._filter_debug = status

    class Item(QStandardItem):

        def __init__(self, text: str):
            super(LogDock.Item, self).__init__(text)
            self.setEditable(False)

    def __init__(self, log_entries: List[LogEntry], parent: QWidget):
        super(LogDock, self).__init__("Logs", qtawesome.icon("fa.align-left"), parent)
        self._init_button_frame()
        self._init_table_frame(log_entries)
        self.addWidget(self._button_frame)
        self.addWidget(self._table_frame)

    def _init_button_frame(self):
        self._button_frame = QFrame()
        button_layout = QVBoxLayout()

        self._button_filter_info = self._init_tool_button(
            "fa.info-circle", "Filter info messages", True, True, self._filter_info_event)

        self._button_filter_error = self._init_tool_button(
            "fa.exclamation-triangle", "Filter error messages", True, True, self._filter_error_event)

        self._button_filter_debug = self._init_tool_button(
            "fa.bug", "Filter debug messages", True, False, self._filter_debug_event)

        self._button_entries_clear = self._init_tool_button(
            "fa.trash", "Clear log entries", False, False, self._clear_event)

        self._button_filters = {
            LogDock.Filter.INFO: self._button_filter_info,
            LogDock.Filter.ERROR: self._button_filter_error,
            LogDock.Filter.DEBUG: self._button_filter_debug
        }

        button_layout.addWidget(self._button_filter_info)
        button_layout.addWidget(self._button_filter_error)
        button_layout.addWidget(self._button_filter_debug)
        button_layout.addWidget(self._button_entries_clear)
        button_layout.addWidget(VSpacer(self))
        self._button_frame.setLayout(button_layout)

    def _init_tool_button(self, icon_name: str, tool_tip: str, checkable: bool, checked: bool, callback):
        button_filter = QToolButton()
        button_filter.setIcon(qtawesome.icon(icon_name))
        button_filter.setToolTip(tool_tip)
        button_filter.setCheckable(checkable)
        button_filter.setChecked(checked)
        button_filter.clicked.connect(callback)
        return button_filter

    def _init_table_frame(self, log_entries: List[LogEntry]):
        self._table_frame = QFrame()
        table_layout = QHBoxLayout()
        self._table = QTableView()
        self._init_model(log_entries)
        self._init_headers()
        table_layout.addWidget(self._table)
        self._table_frame.setLayout(table_layout)

    def _init_headers(self):
        header = self._table.horizontalHeader()
        header.setDefaultAlignment(QtCore.Qt.AlignLeft)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        # BUG: Loosing stretch when using ProxyModel
        # FIX: Use setStretchLastSection
        header.setStretchLastSection(True)
        self._table.verticalHeader().hide()

    def _init_model(self, log_entries: List[LogEntry]):
        self._filter_proxy_model = LogDock.ProxyModel()
        model = QStandardItemModel(len(log_entries), 3)
        model.setHorizontalHeaderLabels(["Type", "Time", "Message"])
        for index, log_entry in enumerate(log_entries):
            model.setItem(index, 0, LogDock.Item(log_entry.type()))
            model.setItem(index, 1, LogDock.Item(log_entry.time()))
            model.setItem(index, 2, LogDock.Item(log_entry.message()))
        self._filter_proxy_model.setSourceModel(model)
        self._filter_proxy_model.setFilterKeyColumn(0)
        self._table.setModel(self._filter_proxy_model)

    def addItems(self, *log_entries: List[LogEntry], **kwargs):
        for log_entry in log_entries:
            self.addItem(log_entry)

    def addItem(self, log_entry: LogEntry):
        if log_entry and log_entry.is_valid():
            model = self._table.model().sourceModel()
            nextIndex = model.rowCount()
            model.setItem(nextIndex, 0, LogDock.Item(log_entry.type()))
            model.setItem(nextIndex, 1, LogDock.Item(log_entry.time()))
            model.setItem(nextIndex, 2, LogDock.Item(log_entry.message()))

    def _filter_info_event(self):
        self._filter_proxy_model.setFilterInfo(self._button_filter_info.isChecked())
        self._filter_proxy_model.invalidateFilter()
        self._table.horizontalHeader().setStretchLastSection(True)

    def _filter_error_event(self):
        self._filter_proxy_model.setFilterError(self._button_filter_error.isChecked())
        self._filter_proxy_model.invalidateFilter()
        self._table.horizontalHeader().setStretchLastSection(True)

    def _filter_debug_event(self):
        self._filter_proxy_model.setFilterDebug(self._button_filter_debug.isChecked())
        self._filter_proxy_model.invalidateFilter()
        self._table.horizontalHeader().setStretchLastSection(True)

    def _clear_event(self):
        self._init_headers()
        self._init_model([])
        self.clearEvent.emit()

    def setFilterChecked(self, filter: str, checked: bool):
        if not filter in self._button_filters:
            raise Exception("Unknown filter '{}'.".format(filter))
        if (checked != self._button_filters[filter].isChecked()):
            self._button_filters[filter].click()

    def getFilters(self) -> List[str]:
        return [LogDock.Filter.INFO, LogDock.Filter.ERROR, LogDock.Filter.DEBUG]
