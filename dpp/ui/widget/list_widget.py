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
from qtpy import QtCore
from qtpy.QtCore import QSize, QSortFilterProxyModel, Signal
from qtpy.QtGui import QStandardItemModel, QStandardItem
from qtpy.QtWidgets import QListView


class ListWidget(QListView):
    """ Enhanced QListWidget with additional methods for selecting items by name or index. """

    keyPressed = Signal("PyQt_PyObject")

    def __init__(self):
        QListView.__init__(self)
        proxy = QSortFilterProxyModel(self)
        proxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self._model = QStandardItemModel(self)
        proxy.setSourceModel(self._model)
        self.setModel(proxy)

    def select_item_by_text(self, text):
        """ Highligts and selects an item matching the text in the list-widget. """
        if text:
            for index in range(self.count()):
                if str(self.item(index).text()).startswith(text):
                    self.select_item_by_index(index)
                    self.setFocus()
                    break

    def select_item_by_index(self, index):
        """ Highlights and selects an item for the purpose of navigation (e.g. arrow-up, arrow-down). """
        self.setCurrentIndex(self._model.index(index, 0))

    def keyPressEvent(self, evt):
        key = evt.key()
        if key == QtCore.Qt.Key_Down or key == QtCore.Qt.Key_Up:
            # Select item above/below in list view.
            super(ListWidget, self).keyPressEvent(evt)
        elif key == QtCore.Qt.Key_Enter or key == QtCore.Qt.Key_Return:
            # Usually presses ok button and exits dialog.
            super(ListWidget, self).keyPressEvent(evt)
        else:
            # Signal all other events to listeners.
            self.keyPressed.emit(evt)

    def sizeHint(self):
        """ Set a reasonable size for the list widget. """
        s = QSize()
        s.setHeight(super(ListWidget, self).sizeHint().height())
        s.setWidth(self.sizeHintForColumn(0))
        return s

    def setFilterCaseSensitive(self, cs: int):
        """
        Sets the case-sensitivity of the proxy-controller.
        :param cs: the case-sensitivity (QtCore.Qt.CaseSensitive, QtCore.Qt.CaseInsensitive).
        """
        self.model().setFilterCaseSensitivity(cs)

    def addItem(self, item: QStandardItem):
        """ Adds an item to the list. """
        self._model.appendRow(item)

    def item(self, index: int):
        """
        Returns the item at the specified index.
        :raises exception when the index is out of range.
        """
        return self._model.item(index)
