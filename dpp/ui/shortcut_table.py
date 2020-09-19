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
#
from PyQt5.QtCore import QSortFilterProxyModel, pyqtSignal, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QKeyEvent
from PyQt5.QtWidgets import QTableView
from qtpy import QtWidgets

from dpp.ui.dialog.keyboard_shortcut_dialog import KeyboardShortcutDialog


class KeyboardShortcutTable(QTableView):

    changed = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject')
    keyPressed = pyqtSignal(str)

    def __init__(self, parent, context):
        super(KeyboardShortcutTable, self).__init__(parent)
        self._context = context
        self._init_model(context.getShortcuts())
        self._init_headers()
        self._init_proxy_model()
        self.clicked.connect(self.clickEvent)

    def _init_headers(self):
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.verticalHeader().hide()

    def _init_model(self, keyboard_shortcuts):
        model = QStandardItemModel(len(keyboard_shortcuts), 3)
        model.setHorizontalHeaderLabels(["Id", "Name", "Keyboard Shortcut"])
        for index, keyboard_shortcut in enumerate(keyboard_shortcuts):
            model.setItem(index, 0, QStandardItem(keyboard_shortcut.id()))
            model.setItem(index, 1, QStandardItem(keyboard_shortcut.name(remove_anchors=True)))
            model.item(index, 1).setFlags(model.item(index, 1).flags() ^ Qt.ItemIsEditable)
            model.setItem(index, 2, QStandardItem(keyboard_shortcut.key()))
            model.item(index, 2).setFlags(model.item(index, 2).flags() ^ Qt.ItemIsEditable)
        self.setModel(model)
        self.setColumnHidden(0, True)

    def _init_proxy_model(self):
        filter_proxy_model = QSortFilterProxyModel()
        filter_proxy_model.setSourceModel(self.model())
        filter_proxy_model.setFilterKeyColumn(1)
        filter_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.setModel(filter_proxy_model)

    def _edit_keyboard_shortcut(self, item):
        keyboard_shortcut_name = self.model().sourceModel().item(item.row(), 1).text()
        keyboard_shortcut_dialog = KeyboardShortcutDialog(self, self._context, keyboard_shortcut_name)
        keyboard_shortcut_dialog.exec_()
        if keyboard_shortcut_dialog.shouldBeReset():
            self._update_keyboard_shortcut(item, "")
        elif keyboard_shortcut_dialog.keyboardShortcut():
            self._update_keyboard_shortcut(item, keyboard_shortcut_dialog.keyboardShortcut())

    def _update_keyboard_shortcut(self, item, keyboard_shortcut):
        id = self.model().sourceModel().item(item.row(), 0).text()
        self.model().sourceModel().item(item.row(), 2).setText(keyboard_shortcut)
        self.changed.emit(id, keyboard_shortcut)

    def clickEvent(self, item):
        self._edit_keyboard_shortcut(item)

    def keyReleaseEvent(self, event: QKeyEvent):
        item = self.model().sourceModel().item(self.currentIndex().row())
        if event.key() == Qt.Key_Return:
            self._edit_keyboard_shortcut(item)
        elif event.key() == Qt.Key_Backspace:
            self._update_keyboard_shortcut(item, "")
        elif chr(event.key()).isalnum():
            self.keyPressed.emit(chr(event.key()))
