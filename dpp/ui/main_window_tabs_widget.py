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
from typing import List

import qtawesome
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLabel, QTabWidget, QToolButton, QMenu, QFrame, QHBoxLayout

from dpp.core import Context
from dpp.ui import CodecTab, TabBar
from dpp.ui.builder.action_builder import ActionBuilder
from dpp.ui.widget.search_field import SearchField
from dpp.ui.widget.separater_widget import VSep


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

    def __init__(self, context: Context, plugins, parent=None):
        super(__class__, self).__init__(parent)
        self._parent = parent
        self._context = context
        self._current_tab_number = 1
        self._init_listener(context)
        self._plugins = plugins
        bar = TabBar()
        bar.customContextMenuRequested.connect(self._show_context_menu)
        bar.tabRenamed.connect(self.tabRenamed.emit)
        self.setTabBar(bar)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.closeTab)
        tab_new_button = QToolButton()
        tab_new_button.setToolTip("New Tab")
        tab_new_button.clicked.connect(lambda: self.newTab())
        tab_new_button.setIcon(qtawesome.icon("fa.plus"))
        self.addTab(QLabel("Add new Tab"), "")
        self.setTabEnabled(0, False)
        self.tabBar().setTabButton(0, TabBar.RightSide, tab_new_button)

    def _init_search_field(self):
        search_field_frame = QFrame()
        search_field_layout = QHBoxLayout()
        search_field_layout.addWidget(VSep(self))

        self._search_field = SearchField(self)
        self._search_field.setIcon(qtawesome.icon("fa.search"))
        self._search_field.setPlaceholderText("Search codec")
        self._search_field.textChanged.connect(lambda text: {})
        search_field_layout.addWidget(self._search_field)

        self._search_field_button = QToolButton()
        self._search_field_button.setIcon(qtawesome.icon("fa.arrow-circle-right"))
        self._search_field_button.setContentsMargins(0, 0, 0, 0)
        search_field_layout.addWidget(self._search_field_button)

        search_field_frame.setLayout(search_field_layout)
        search_field_frame.setContentsMargins(5, 0, 5, 5) # left, top, right, bottom
        search_field_frame.layout().setContentsMargins(0, 0, 0, 0)
        return search_field_frame

    def _init_listener(self, context):
        self._listener = context.listener()
        self._listener.newTabRequested.connect(self.newTab)

    def _show_context_menu(self, point):
        if not point:
            return

        index = self.tabBar().tabAt(point)
        if index == self.count() - 1:
            # Do not show any context-menu for "Add new tab"-Tab.
            return

        menu = QMenu(self)
        menu.addAction(ActionBuilder(self)
                       .name("New Tab")
                       .callback(self.newTab).build())
        menu.addSeparator()
        menu.addAction(ActionBuilder(self)
                       .name("Rename Tab")
                       .callback(self.tabBar().rename_tab).build())
        menu.addSeparator()
        menu.addAction(ActionBuilder(self)
                       .name("Close Tab")
                       .callback(self.closeTab).build())
        menu.addAction(ActionBuilder(self)
                       .name("Close Other Tabs")
                       .enabled(self.tabCount() > 1)
                       .callback(lambda: self.closeOtherTabs()).build())
        menu.exec(self.tabBar().mapToGlobal(point))

    def newTab(self, input: str=None, title :str=None) -> (int, CodecTab):
        """
        Opens a new tab and writes input into first codec-frame.
        :param input: The input which should be placed into the first codec-frame.
        :param title: The title of the tab.
        """
        codec_tab = CodecTab(self, self._context, self._plugins)
        name = "Tab {}".format(self._current_tab_number) if not title else title
        self._current_tab_number += 1
        self.insertTab(self.count() - 1, codec_tab, name)
        index = self.count() - 2
        self.setCurrentIndex(index)
        self.tabAdded.emit(index, name)
        codec_tab.frames().getFocusedFrame().setInputText(input)
        # BUG: Input-text of newly added codec-tab is not focused correctly.
        # FIX: Refocus input-text.
        codec_tab.frames().getFocusedFrame().focusInputText()
        return index, codec_tab

    def renameTab(self, index, title):
        self.tabBar().setTabText(index, title)
        return self.tab(index)

    def selectTab(self, index):
        if index < 0 or index > self.count() - 2:
            return
        self.setCurrentIndex(index)

    def closeTab(self, index=None):
        if index is None:
            index = self.currentIndex()
        name = self.tabText(index)
        self.removeTab(index)
        if self.count() <= 1:
            self.newTab()
        else:
            self.setCurrentIndex(index - 1)
        self.tabClosed.emit(index, name)

    def closeOtherTabs(self, current_index=None):
        if current_index is None:
            current_index = self.currentIndex()

        # Close every tab ahead of the current one, starting at the end.
        for index in reversed(range(current_index + 1, self.tabCount())):
            self.closeTab(index)

        # Close every tab below the current one, starting at the beginning.
        for index in range(0, current_index):
            self.closeTab(0)

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

    def tab(self, index) -> CodecTab:
        return self.widget(index)

    def tabCount(self):
        # do not count the "Add new Tab"-Tab.
        return self.count() - 1

    def focusCodecSearch(self):
        self._search_field.setFocus()

    def toDict(self) -> List[dict]:
        return [ {
            "name": self.tabBar().tabText(tabIndex),
            "frames": self.tab(tabIndex).toDict()
        } for tabIndex in range(0, self.tabCount()) ]
