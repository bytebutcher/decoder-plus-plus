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
import qtawesome
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLabel, QTabWidget, QToolButton

from ui import TabBar, CodecTab


class MainWindowTabsWidget(QTabWidget):

    # tabAdded(index, name)
    tabAdded = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject')
    # tabClosed(index, name)
    tabClosed = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject')
    # tabRenamed(index, old_name, new_name)
    tabRenamed = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')
    # tabMovedToPrevious(old_index, new_index, name)
    tabMovedToPrevious = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')
    # tabMovedToNext(old_index, new_index, name)
    tabMovedToNext = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')

    def __init__(self, context, plugins, parent=None):
        super(__class__, self).__init__(parent)
        self._context = context
        self._plugins = plugins
        bar = TabBar()
        bar.tabRenamed.connect(self.tabRenamed.emit)
        # BUG: Moving tabs beyond last tab breaks program-design (last tab is supposed to be the "add new tab button ('+')").
        # WORKAROUND: ???
        # NOTES:
        # * Currently moving tabs is disabled.
        # * Using an Event-Filter to disable dropping tabs on certain areas did not work.
        bar.setMovable(False)
        self.setTabBar(bar)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.closeTab)
        tab_new_button = QToolButton()
        tab_new_button.clicked.connect(self.newTab)
        tab_new_button.setIcon(qtawesome.icon("fa.plus"))
        self.addTab(QLabel("Add new Tab"), "")
        self.setTabEnabled(0, False)
        self.tabBar().setTabButton(0, TabBar.RightSide, tab_new_button)

    def newTab(self):
        name = "Tab {}".format(self.count())
        self.insertTab(self.count() - 1, CodecTab(self, self._context, self._plugins), name)
        index = self.count() - 2
        self.setCurrentIndex(index)
        self.tabAdded.emit(index, name)

    def selectTab(self, index):
        if index < 0 or index > self.count() - 2:
            return
        self.setCurrentIndex(index)

    def closeTab(self, index=None):
        if not index:
            index = self.currentIndex()
        name = self.tabText(index)
        self.removeTab(index)
        if self.count() <= 1:
            self.newTab()
        else:
            self.setCurrentIndex(index - 1)
        self.tabClosed.emit(index, name)

    def nextTab(self):
        old_index = self.currentIndex()
        name = self.tabText(old_index)
        new_index = (old_index + 1) % (self.count() - 1)
        self.setCurrentIndex(new_index)
        self.tabMovedToNext.emit(old_index, new_index, name)

    def previousTab(self):
        old_index = self.currentIndex()
        name = self.tabText(old_index)
        new_index = (old_index - 1) % (self.count() - 1)
        self.setCurrentIndex(new_index)
        self.tabMovedToPrevious.emit(old_index, new_index, name)

    def tabCount(self):
        # do not count the "Add new Tab"-Tab.
        return self.count() - 1