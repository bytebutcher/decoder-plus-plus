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
from qtpy.QtCore import Signal, Slot, QPoint
from qtpy.QtWidgets import QTabBar, QLineEdit, QWidget


class TabBar(QTabBar):
    """QTabBar with double click signal and tab rename behavior."""

    # tabRenamed(index, old_title, new_title)
    tabRenamed = Signal('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')
    tabDoubleClicked = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.__edit_mode_activated = False
        self.setMovable(True)
        self.installEventFilter(self)

    def eventFilter(self, source, event):
        """ Allow moving tabs under certain conditions. """

        if event.type() == QtCore.QEvent.Type.MouseMove:

            if source.currentIndex() == self.count() - 1:
                # Block MouseMove for last tab.
                return True
            else:
                last_tab = self.tabRect(self.count() - 1)
                if event.pos().x() > last_tab.x():
                    # Block movement beyond last tab.
                    return True

                # Retrieve pressed tab.
                # Do not use y-position of event.pos() since mouse may not focus tab all the time.
                pressed_tab_pos = QPoint(event.pos().x(), self.y())
                pressed_tab = self.tabRect(self.tabAt(pressed_tab_pos))
                if (pressed_tab.x() + pressed_tab.width()) >= last_tab.x():
                    # Block movement of pressed tab when reaching beginning of last tab.
                    return True

        return QWidget.eventFilter(self, source, event)

    def mouseDoubleClickEvent(self, event):
        if not self.__edit_mode_activated:
            self.__edit_mode_activated = True
            tab_index = self.tabAt(event.pos())
            self.tabDoubleClicked.emit(tab_index)
            self.start_rename(tab_index)

    def renameTab(self, index=None):
        if not index:
            index = self.currentIndex()
        self.start_rename(index)

    def start_rename(self, tab_index):
        if not self.isTabEnabled(tab_index):
            return
        self.__edited_tab = tab_index
        rect = self.tabRect(tab_index)
        top_margin = 3
        left_margin = 6
        self.__edit = QLineEdit(self)
        self.__edit.show()
        self.__edit.move(rect.left() + left_margin, rect.top() + top_margin)
        self.__edit.resize(rect.width() - 2 * left_margin, rect.height() - 2 * top_margin)
        self.__edit.setText(self.tabText(tab_index))
        self.__edit.selectAll()
        self.__edit.setFocus()
        self.__edit.editingFinished.connect(self.finish_rename)

    @Slot()
    def finish_rename(self):
        old_title = self.tabText(self.__edited_tab)
        new_title = self.__edit.text()
        self.setTabText(self.__edited_tab, self.__edit.text())
        self.__edit.deleteLater()
        self.__edit_mode_activated = False
        self.tabRenamed.emit(self.__edited_tab, old_title, new_title)
