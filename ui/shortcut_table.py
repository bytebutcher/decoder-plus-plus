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
from PyQt5.QtCore import QSortFilterProxyModel, pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QTableView
from qtpy import QtWidgets

from ui.shortcut_table_item_delegate import ShortcutTableItemDelegate


class ShortcutTable(QTableView):

    shortcutUpdated = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject')

    def __init__(self, parent, shortcuts):
        super(ShortcutTable, self).__init__(parent)
        self._init_model(shortcuts)
        self._init_headers()
        self._init_proxy_model()
        self._init_item_delegate()

    def _init_item_delegate(self):
        self.setItemDelegate(ShortcutTableItemDelegate(self))

    def _init_headers(self):
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.verticalHeader().hide()

    def _init_model(self, shortcuts):
        model = QStandardItemModel(len(shortcuts), 3)
        model.setHorizontalHeaderLabels(["Key", "Name", "Shortcut"])
        for index, shortcut in enumerate(shortcuts):
            name_item = QStandardItem(shortcut.name())
            name_item.setFlags(name_item.flags() ^ QtCore.Qt.ItemIsEditable)
            model.setItem(index, 0, QStandardItem(shortcut.id()))
            model.setItem(index, 1, name_item)
            model.setItem(index, 2, QStandardItem(shortcut.key()))
        # BUG: Cell changes to row below when editing cell is finished.
        # REQUIREMENT: The cell-selection should not change.
        # WORKAROUND: ???
        model.itemChanged.connect(self._shortcut_changed_event)
        self.setModel(model)
        self.setColumnHidden(0, True)

    def _init_proxy_model(self):
        filter_proxy_model = QSortFilterProxyModel()
        filter_proxy_model.setSourceModel(self.model())
        filter_proxy_model.setFilterKeyColumn(1)
        filter_proxy_model.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setModel(filter_proxy_model)

    def _shortcut_changed_event(self, item):
        key = self.model().sourceModel().item(item.row(), 0).text()
        shortcut = self.model().sourceModel().item(item.row(), 2).text()
        self.shortcutUpdated.emit(key, shortcut)

    def keyPressEvent(self, event):
        # BUG: Using Enter-Key to go into Edit-Mode results an immediate closing of the selected cell.
        # WORKAROUND: ???
        # NOTE: Currently going into Edit-Mode by pressing the Enter-Key is disabled.
        #if event.key() == QtCore.Qt.Key_Return:
        #    self.edit(self.selectionModel().currentIndex())
        super(__class__, self).keyPressEvent(event)