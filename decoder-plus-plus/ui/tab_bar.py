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

from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QTabBar, QLineEdit


class TabBar(QTabBar):

    """QTabBar with double click signal and tab rename behavior."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__edit_mode_activated = False

    tabDoubleClicked = pyqtSignal(int)

    def mouseDoubleClickEvent(self, event):
        if not self.__edit_mode_activated:
            self.__edit_mode_activated = True
            tab_index = self.tabAt(event.pos())
            self.tabDoubleClicked.emit(tab_index)
            self.start_rename(tab_index)

    def renameTab(self):
        self.start_rename(self.currentIndex())

    def start_rename(self, tab_index):
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

    @pyqtSlot()
    def finish_rename(self):
        self.setTabText(self.__edited_tab, self.__edit.text())
        self.__edit.deleteLater()
        self.__edit_mode_activated = False

