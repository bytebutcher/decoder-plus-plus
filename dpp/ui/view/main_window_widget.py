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
import os

from qtpy.QtCore import QEvent
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QMainWindow, QAction, QVBoxLayout, QFileDialog, QMenu, QWidget

from dpp.ui import IconLabel
from dpp.ui.dock.hex_dock import HexDock
from dpp.ui.dock.log_dock import LogDock
from dpp.ui.widget.dock_tabs_widget import DockTabsWidget

from dpp.core import Context
from dpp.ui.view.classic import CodecTab
from dpp.ui.dialog.config_dialog import ConfigDialog
from dpp.ui.widget.tabs_widget import TabsWidget


class MainWindowWidget(QWidget):

    def __init__(self, parent: QMainWindow, context: 'core.context.Context'):
        super().__init__(parent)
        self._context = context
        self._logger = context.logger()
        self._plugins = context.plugins()
        self._parent = parent

        #############################################
        #   Initialize docks
        #############################################

        # Initialize log dock widget
        self._log_dock_widget = LogDock(self.docksWidget(), self._logger)
        self.docksWidget().registerDockWidget(Context.DockWidget.LOG_DOCK_WIDGET, self._log_dock_widget)
        self.docksWidget().registerDockWidget(Context.DockWidget.HEX_DOCK_WIDGET, HexDock(context, parent))

        #############################################
        #   Initialize status bar
        #############################################

        parent.statusBar().addWidget(self._log_dock_widget.logMessageWidget())
        parent.statusBar().addPermanentWidget(self._init_hidden_dialog())

        #############################################
        #   Initialize shortcuts
        #############################################
        self._init_shortcuts()

    def menuBar(self):
        return self._parent.menuBar()

    def _init_shortcuts(self):
        self._file_menu = self._init_file_menu()
        self._edit_menu = self._init_edit_menu()
        self._view_menu = self._init_view_menu()
        self._select_menu = self._init_select_menu()
        self._tab_menu = self._init_tab_menu()
        self._help_menu = self._init_help_menu()

    def _init_help_menu(self) -> QMenu:
        help_menu = self.menuBar().addMenu('&Help')
        keyboard_shortcuts_action = QAction("&Keyboard Shortcuts...", self)
        keyboard_shortcuts_action.triggered.connect(
            lambda: self._show_hidden_dialog(ConfigDialog.TAB_KEYBOARD_SHORTCUTS))
        help_menu.addAction(keyboard_shortcuts_action)
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_hidden_dialog)
        help_menu.addAction(about_action)
        return help_menu

    def _init_edit_menu(self) -> QMenu:
        return self.menuBar().addMenu('&Edit')

    def _init_view_menu(self) -> QMenu:
        view_menu = self.menuBar().addMenu('&View')
        # self._register_shortcut(Context.Shortcut.SELECT_CLASSIC_GUI,
        #                        "&Classic",
        #                        "Alt+Shift+C",
        #                        lambda: self._select_classic_gui(),
        #                        view_menu)
        # self._register_shortcut(Context.Shortcut.SELECT_MODERN_GUI,
        #                        "&Modern",
        #                        "Alt+Shift+M",
        #                        lambda: self._select_modern_gui(),
        #                        view_menu)
        # view_menu.addSeparator()
        self._register_shortcut(Context.Shortcut.SELECT_LOG_DOCK,
                                "&Log",
                                "Alt+Shift+L",
                                lambda: self.docksWidget().toggleDockWidget(Context.DockWidget.LOG_DOCK_WIDGET),
                                view_menu)
        self._register_shortcut(Context.Shortcut.SELECT_HEX_DOCK,
                                "He&x",
                                "Alt+Shift+X",
                                lambda: self.docksWidget().toggleDockWidget(Context.DockWidget.HEX_DOCK_WIDGET),
                                view_menu)
        return view_menu

    def _init_select_menu(self) -> QMenu:
        return self.menuBar().addMenu('&Select')

    def _init_tab_menu(self) -> QMenu:
        tab_menu = self.menuBar().addMenu('&Tabs')
        self._register_shortcut(Context.Shortcut.TAB_NEW,
                                "&New Tab",
                                "Ctrl+T",
                                lambda: self.tabsWidget().onTabAddButtonClick.emit(None, None),
                                tab_menu)
        self._register_shortcut(Context.Shortcut.TAB_RENAME,
                                "&Rename Tab",
                                "Alt+Shift+R",
                                lambda: self.tabsWidget().tabBar().renameTab(),
                                tab_menu)
        self._register_shortcut(Context.Shortcut.TAB_DUPLICATE,
                                "&Duplicate Tab",
                                "Ctrl+Shift+D",
                                lambda: self.tabsWidget().duplicateTab(),
                                tab_menu)
        self._register_shortcut(Context.Shortcut.TAB_NEXT,
                                "&Next Tab",
                                "Ctrl+Tab",
                                lambda: self.tabsWidget().nextTab(),
                                tab_menu)
        self._register_shortcut(Context.Shortcut.TAB_PREVIOUS,
                                "&Previous Tab",
                                "Ctrl+Shift+Tab",
                                lambda: self.tabsWidget().previousTab(),
                                tab_menu)

        tab_menu.addSeparator()
        self._tabs_select_action = []

        def select_tab(index):
            return lambda: self.tabsWidget().selectTab(index)

        for tab_num in range(1, 10):
            action = self._register_shortcut(Context.Shortcut.TAB_SELECT_.format(tab_num),
                                             "Select Tab &{}".format(tab_num),
                                             "Alt+{}".format(tab_num),
                                             select_tab(tab_num - 1),
                                             tab_menu)
            action.setVisible(False)
            self._tabs_select_action.append(action)
        return tab_menu

    def _init_file_menu(self) -> QMenu:
        file_menu = self.menuBar().addMenu('&File')
        self._register_shortcut(Context.Shortcut.TAB_NEW,
                                "&New Tab", "Ctrl+T",
                                lambda: self.tabsWidget().onTabAddButtonClick.emit(None, None),
                                file_menu)
        self._register_shortcut(Context.Shortcut.TAB_CLOSE,
                                "&Close Tab",
                                "Ctrl+W",
                                lambda: self.tabsWidget().closeTab(),
                                file_menu)
        file_menu.addSeparator()
        self._register_shortcut(Context.Shortcut.OPEN_FILE,
                                "&Open File...", "Ctrl+O",
                                lambda: self._open_file(),
                                file_menu)
        self._register_shortcut(Context.Shortcut.SAVE_AS_FILE,
                                "&Save As...", "Ctrl+S",
                                lambda: self._save_as_file(),
                                file_menu)
        file_menu.addSeparator()
        self._register_shortcut(Context.Shortcut.SHOW_PLUGINS,
                                "&Plugins...", "Ctrl+Shift+P",
                                lambda: self._show_plugins_dialog(),
                                file_menu)
        file_menu.addSeparator()
        self._register_shortcut(Context.Shortcut.FILE_EXIT,
                                "E&xit",
                                "Ctrl+Q",
                                lambda: self._parent.close(),
                                file_menu)
        return file_menu

    def _register_shortcut(self, id, text, shortcut_key, callback, menu) -> QAction:
        action = self._context.registerShortcut(id, text, shortcut_key, callback, self)
        menu.addAction(action)
        return action

    def _select_classic_gui(self):
        pass

    def _select_modern_gui(self):
        pass

    def _open_file(self) -> str:
        filename, _ = QFileDialog.getOpenFileName(self, 'Open File')
        return filename

    def _save_as_file(self) -> str:
        filename, _ = QFileDialog.getSaveFileName(self, 'Save As File')
        return filename

    def _show_plugins_dialog(self):
        self._show_hidden_dialog("Plugins")

    def _show_hidden_dialog(self, tab_select: str = None):
        """ Shows the hidden dialog. """
        hidden_dialog = ConfigDialog(self, self._context, tab_select)
        hidden_dialog.exec_()

    def _tab_added_event(self, index, title, tab, input):
        if 0 <= index < len(self._tabs_select_action):
            self._tabs_select_action[index].setVisible(True)

    def _tab_closed_event(self, index, title):
        for index in range(0, len(self._tabs_select_action)):
            self._tabs_select_action[index].setVisible(index < self.tabsWidget().tabCount())

    def _init_hidden_dialog(self):
        """ Inits the icon which opens the hidden dialog on mouse press. """
        about_label = IconLabel(self, QIcon(os.path.join(self._context.getAppPath(), 'images', 'hidden.png')))
        about_label.mousePressEvent = lambda e: self._show_hidden_dialog()
        return about_label

    def tabsWidget(self):
        if not hasattr(self, '_tabs_widget'):
            layout = QVBoxLayout(self)
            self._tabs_widget = TabsWidget(self._parent, self._context)
            self._tabs_widget.tabAdded.connect(self._tab_added_event)
            self._tabs_widget.tabClosed.connect(self._tab_closed_event)
            layout.addWidget(self._tabs_widget)
            self._parent.setLayout(layout)
        return self._tabs_widget

    def statusBar(self):
        return self._parent.statusBar()

    def docksWidget(self) -> DockTabsWidget:
        if not hasattr(self, '_docks_widget'):
            self._docks_widget = DockTabsWidget(self._parent, self._context)
        return self._docks_widget

    def closeEvent(self, e: QEvent):
        """ Closes the main window and saves window-size and -position. """
        self._context.config.setSize(self.size())
        self._context.config.setPosition(self.pos())
        e.accept()

    def newTab(self, widget, title: str = None, input: str = None) -> (int, CodecTab):
        """
        Opens a new tab and writes input.
        :param title: The title of the tab.
        :param input: The input which should be written into the tab.
        """
        index, tab = self.tabsWidget().newTab(widget, title=title, input=input)
        self.tabsWidget().setCurrentIndex(index)
        return index, tab
