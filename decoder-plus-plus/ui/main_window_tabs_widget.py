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
from PyQt5.QtWidgets import QLabel, QTabWidget, QToolButton

from ui import TabBar, CodecTab


class MainWindowTabsWidget(QTabWidget):

    def __init__(self, context, plugins, parent=None):
        super(__class__, self).__init__(parent)
        self._context = context
        self._plugins = plugins
        bar = TabBar()
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
        tab_new_button.setText("+")
        self.addTab(QLabel("Add new Tab"), "")
        self.setTabEnabled(0, False)
        self.tabBar().setTabButton(0, TabBar.RightSide, tab_new_button)

    def newTab(self):
        self.insertTab(self.count() - 1, CodecTab(self, self._context, self._plugins), "Tab")
        self.setCurrentIndex(self.count() - 2)

    def closeTab(self, index=None):
        if not index:
            index = self.currentIndex()
        self.removeTab(index)
        if self.count() <= 1:
            self.newTab()
        else:
            self.setCurrentIndex(index - 1)

    def nextTab(self):
        self.setCurrentIndex((self.currentIndex() + 1) % (self.count() - 1))

    def previousTab(self):
        self.setCurrentIndex((self.currentIndex() - 1) % (self.count() - 1))
