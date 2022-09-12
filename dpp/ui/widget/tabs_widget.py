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
from qtpy.QtCore import Signal
from qtpy.QtWidgets import QLabel, QTabWidget, QToolButton, QMenu, QWidget

from dpp.core import Context
from dpp.core.icons import Icon, icon
from dpp.ui.view.classic import CodecTab
from dpp.ui.widget.tab_bar import TabBar
from dpp.ui.builder.action_builder import ActionBuilder


class TabsWidget(QTabWidget):
    # onTabAddButtonClick(title, input_text)
    onTabAddButtonClick = Signal('PyQt_PyObject', 'PyQt_PyObject')
    # onTabDuplicateButtonClick(title, src_tab)
    onTabDuplicateButtonClick = Signal('PyQt_PyObject', 'PyQt_PyObject')
    # tabAdded(index, title, tab, input_text)
    tabAdded = Signal('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')
    # tabDuplicated(src_tab, dst_tab)
    tabDuplicated = Signal('PyQt_PyObject', 'PyQt_PyObject')
    # tabClosed(index, title)
    tabClosed = Signal('PyQt_PyObject', 'PyQt_PyObject')
    # tabRenamed(index, old_title, new_title, tab)
    tabRenamed = Signal('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')
    # tabMovedToPrevious(old_index, new_index, title, tab)
    tabMovedToPrevious = Signal('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')
    # tabMovedToNext(old_index, new_index, title, tab)
    tabMovedToNext = Signal('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')

    def __init__(self, parent, context: Context):
        super().__init__(parent)
        self._parent = parent
        self._context = context
        self._current_tab_number = 1
        self._listener = context.listener()
        self._listener.newTabRequested.connect(self.onTabAddButtonClick.emit)
        self._plugins = context.plugins()
        bar = TabBar()
        bar.customContextMenuRequested.connect(self._show_context_menu)
        bar.tabRenamed.connect(
            lambda index, old_title, new_title: self.tabRenamed.emit(index, old_title, new_title, self.tab(index)))
        self.setTabBar(bar)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.closeTab)
        tab_new_button = QToolButton()
        tab_new_button.setToolTip("New Tab")
        tab_new_button.clicked.connect(lambda event: self.onTabAddButtonClick.emit(None, None))
        tab_new_button.setIcon(icon(Icon.TAB_NEW))
        self.addTab(QLabel("Add new Tab"), "")
        self.setTabEnabled(0, False)
        self.tabBar().setTabButton(0, TabBar.RightSide, tab_new_button)

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
                       .callback(lambda checked: self.onTabAddButtonClick.emit(None, None)).build())
        menu.addSeparator()
        menu.addAction(ActionBuilder(self)
                       .name("Rename Tab")
                       .callback(lambda checked: self.tabBar().renameTab()).build())
        menu.addAction(ActionBuilder(self)
                       .name("Duplicate Tab")
                       .callback(lambda checked: self.duplicateTab()).build())
        menu.addSeparator()
        menu.addAction(ActionBuilder(self)
                       .name("Close Tab")
                       .callback(lambda checked: self.closeTab()).build())
        menu.addAction(ActionBuilder(self)
                       .name("Close Other Tabs")
                       .enabled(self.tabCount() > 1)
                       .callback(lambda checked: self.closeOtherTabs()).build())
        menu.exec(self.tabBar().mapToGlobal(point))

    def newTab(self, widget: QWidget, title: str = None, input_text: str = None) -> (int, QWidget):
        """
        Opens a new tab with the specified widget as content.
        :param title: The title of the tab.
        :param input_text: The input for the tab.
        """
        title = "Tab {}".format(self._current_tab_number) if not title else title
        self._current_tab_number += 1
        self.insertTab(self.count() - 1, widget, title)
        index = self.count() - 2
        self.setCurrentIndex(index)
        self.tabAdded.emit(index, title, widget, input_text)
        return index, widget

    def renameTab(self, index, title):
        """ Renames the title of a tab.
        Note: If you require the user to dynamically enter a value checkout the renameTab method in tab_bar.py
        :param index: the index of the tab to be renamed.
        """
        self.tabBar().setTabText(index, title)
        return self.tab(index)

    def duplicateTab(self, src_index=None):
        """
        Duplicates the content of a tab.
        :param src_index: the index of the tab to be duplicated.
        """
        def does_tab_title_already_exist(title):
            for index in range(self.count()):
                if self.tabBar().tabText(index) == title:
                    return True
            return False

        def get_duplicate_tab_title(index):
            count = 1
            while does_tab_title_already_exist(self.tabBar().tabText(index) + " (Copy " + str(count) + ")"):
                count += 1
            return self.tabBar().tabText(index) + " (Copy " + str(count) + ")"

        if src_index is None:
            src_index = self.currentIndex()

        src_tab = self.tab(src_index)
        title = get_duplicate_tab_title(src_index)
        self.onTabDuplicateButtonClick.emit(title, src_tab)

    def selectTab(self, index):
        if index < 0 or index > self.count() - 2:
            return
        self.setCurrentIndex(index)

    def closeTab(self, index=None):
        if index is None:
            index = self.currentIndex()
        title = self.tabText(index)
        self.removeTab(index)
        if self.count() <= 1:
            self.onTabAddButtonClick.emit(None, None)
        else:
            self.setCurrentIndex(index - 1)
        self.tabClosed.emit(index, title)

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
        title = self.tabText(old_index)
        new_index = (old_index + 1) % (self.count() - 1)
        self.setCurrentIndex(new_index)
        self.tabMovedToNext.emit(old_index, new_index, title, self.tab(new_index))

    def previousTab(self):
        old_index = self.currentIndex()
        title = self.tabText(old_index)
        new_index = (old_index - 1) % (self.count() - 1)
        self.setCurrentIndex(new_index)
        self.tabMovedToPrevious.emit(old_index, new_index, title, self.tab(new_index))

    def tab(self, index) -> CodecTab:
        return self.widget(index)

    def tabCount(self):
        # do not count the "Add new Tab"-Tab.
        return self.count() - 1

    def focusCodecSearch(self):
        self._search_field.setFocus()
