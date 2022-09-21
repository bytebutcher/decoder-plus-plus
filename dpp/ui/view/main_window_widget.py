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
from typing import List, Union

from qtpy.QtCore import QEvent
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QMainWindow, QAction, QVBoxLayout, QMenu, QWidget

from dpp.core.logger import logmethod
from dpp.core.shortcuts import MenuRegistry
from dpp.ui import IconLabel
from dpp.ui.dock.hex_dock import HexDock
from dpp.ui.dock.log_dock import LogDock
from dpp.ui.widget.dock_tabs_widget import DockTabsWidget

from dpp.core import Context
from dpp.ui.dialog.config_dialog import ConfigDialog
from dpp.ui.widget.menu_bar import MenuBar
from dpp.ui.widget.tabs_widget import TabsWidget

menu = MenuRegistry()
MenuItem = Context.Shortcut


class MainWindowWidget(QWidget):

    @logmethod()
    def __init__(self, parent: QMainWindow, context: 'core.context.Context', input_text: str):
        super().__init__(parent)
        self._context = context
        self._plugins = context.plugins()
        self._parent = parent

        # Initialize docks
        self._log_dock_widget = LogDock(self.docksWidget(), context.logger)
        self.docksWidget().registerDockWidget(Context.DockWidget.LOG_DOCK_WIDGET, self._log_dock_widget)
        self.docksWidget().registerDockWidget(Context.DockWidget.HEX_DOCK_WIDGET, HexDock(context, parent))

        # Initialize status bar
        parent.statusBar().addWidget(self._log_dock_widget.logMessageWidget())
        parent.statusBar().addPermanentWidget(self._init_hidden_dialog())

        # Initialize shortcuts
        self._menu_bar = MenuBar(self._parent.menuBar())
        self._init_menu_items()

        # Initialize tabs
        self.tabsWidget().onTabAddButtonClick.connect(self.newTab)
        self.tabsWidget().onTabDuplicateButtonClick.connect(self.duplicateTab)
        self.newTab(input_text=input_text)

    #############################################
    # Menu
    #############################################

    @logmethod()
    def _init_menu_items(self):
        self._register_shortcuts('&File', [
            [Context.Shortcut.TAB_NEW, Context.Shortcut.TAB_CLOSE],
            [Context.Shortcut.OPEN_FILE, Context.Shortcut.SAVE_AS_FILE],
            [Context.Shortcut.SHOW_PLUGINS],
            [Context.Shortcut.FILE_EXIT]
        ])
        self._register_shortcuts('&View', [
            [Context.Shortcut.SELECT_LOG_DOCK, Context.Shortcut.SELECT_HEX_DOCK]
        ])
        self._init_tabs_menu()
        self._register_shortcuts('&Help', [
            [
                Context.Shortcut.SHOW_KEYBOARD_SHORTCUTS, Context.Shortcut.SHOW_ABOUT
            ]
        ])

    @logmethod()
    def _init_tabs_menu(self):
        tab_menu = self._register_shortcuts('&Tabs', [
            [
                Context.Shortcut.TAB_NEW, Context.Shortcut.TAB_RENAME, Context.Shortcut.TAB_DUPLICATE,
                Context.Shortcut.TAB_NEXT, Context.Shortcut.TAB_PREVIOUS
            ]
        ])
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

    @menu.register_menu_item(id=MenuItem.SHOW_KEYBOARD_SHORTCUTS, text="&Keyboard Shortcuts...")
    def _show_keyboard_shortcuts_action(self):
        self._show_hidden_dialog(ConfigDialog.TAB_KEYBOARD_SHORTCUTS)

    @menu.register_menu_item(id=MenuItem.SHOW_ABOUT, text="&About")
    def _show_about_action(self):
        self._show_hidden_dialog()

    @menu.register_menu_item(id=MenuItem.SELECT_LOG_DOCK, text="&Log", shortcut_key="Alt+Shift+L")
    def _toggle_log_dock_widget_action(self):
        self.docksWidget().toggleDockWidget(Context.DockWidget.LOG_DOCK_WIDGET)

    @menu.register_menu_item(id=MenuItem.SELECT_HEX_DOCK, text="He&x", shortcut_key="Alt+Shift+X")
    def _toggle_hex_dock_widget_action(self):
        self.docksWidget().toggleDockWidget(Context.DockWidget.HEX_DOCK_WIDGET)

    @menu.register_menu_item(id=MenuItem.TAB_NEW, text="&New Tab", shortcut_key="Ctrl+T")
    def _new_tab_action(self):
        self.newTab()

    @menu.register_menu_item(id=MenuItem.TAB_RENAME, text="&Rename Tab", shortcut_key="Alt+Shift+R")
    def _rename_tab_action(self):
        self.tabsWidget().tabBar().renameTab()

    @menu.register_menu_item(id=MenuItem.TAB_DUPLICATE, text="&Duplicate Tab", shortcut_key="Ctrl+Shift+D")
    def _duplicate_tab_action(self):
        self.tabsWidget().duplicateTab()

    @menu.register_menu_item(id=MenuItem.TAB_NEXT, text="&Next Tab", shortcut_key="Ctrl+Tab")
    def _next_tab_action(self):
        self.tabsWidget().nextTab()

    @menu.register_menu_item(id=MenuItem.TAB_PREVIOUS, text="&Previous Tab", shortcut_key="Ctrl+Shift+Tab")
    def _previous_tab_action(self):
        self.tabsWidget().previousTab()

    @menu.register_menu_item(id=MenuItem.TAB_CLOSE, text="&Close Tab", shortcut_key="Ctrl+W")
    def _close_tab_action(self):
        self.tabsWidget().closeTab()

    @menu.register_menu_item(id=MenuItem.SHOW_PLUGINS, text="&Plugins...", shortcut_key="Ctrl+Shift+P")
    def _show_plugins_dialog_action(self):
        self._show_hidden_dialog("Plugins")

    @menu.register_menu_item(id=MenuItem.FILE_EXIT, text="E&xit", shortcut_key="Ctrl+Q")
    def _close_application_action(self):
        self._parent.close()

    def _select_classic_gui_action(self):
        pass

    def _select_modern_gui_action(self):
        pass

    #############################################
    # Helpers
    #############################################

    @logmethod()
    def _register_shortcuts(self, menu_item: Union[str, QMenu], items: List[List]):
        def register_shortcut(id, text, shortcut_key, callback, menu_widget):
            """ This method is required in order to get the callback working. """
            self._register_shortcut(id, text, shortcut_key, lambda: callback(self), menu_widget)

        if isinstance(menu_item, str):
            if self.menuBar().hasMenu(menu_item):
                menu_widget = self.menuBar().getMenu(menu_item)
            else:
                menu_widget = self.menuBar().addMenu(menu_item)
        elif isinstance(menu_item, QMenu):
            menu_widget = menu_item
        else:
            raise Exception(f'Invalid type {type(menu)}')

        index = 0
        for shortcut_key_id_list in items:
            index += 1
            for shortcut_key_id in shortcut_key_id_list:
                text, shortcut_key, callback = menu.registry[shortcut_key_id]
                register_shortcut(shortcut_key_id, text, shortcut_key, callback, menu_widget)
            if index < len(items):
                # Add a separator inbetween items
                menu_widget.addSeparator()
        return menu_widget

    @logmethod()
    def _register_shortcut(self, id, text, shortcut_key, callback, menu) -> QAction:
        action = self._context.registerShortcut(id, text, shortcut_key, callback, self)
        menu.addAction(action)
        return action

    @logmethod()
    def _show_hidden_dialog(self, tab_select: str = None):
        """ Shows the hidden dialog. """
        ConfigDialog(self, self._context, tab_select).exec_()

    @logmethod()
    def _tab_added_event(self, index, title, tab, input_text):
        if 0 <= index < len(self._tabs_select_action):
            self._tabs_select_action[index].setVisible(True)

    @logmethod()
    def _tab_closed_event(self, index, title):
        for index in range(0, len(self._tabs_select_action)):
            self._tabs_select_action[index].setVisible(index < self.tabsWidget().tabCount())

    @logmethod()
    def _init_hidden_dialog(self):
        """ Inits the icon which opens the hidden dialog on mouse press. """
        about_label = IconLabel(self, QIcon(os.path.join(self._context.getAppPath(), 'images', 'hidden.png')))
        about_label.mousePressEvent = lambda e: self._show_hidden_dialog()
        return about_label

    #############################################
    # Public functions
    #############################################

    def menuBar(self):
        return self._menu_bar

    def tabsWidget(self):
        if not hasattr(self, '_tabs_widget'):
            layout = QVBoxLayout(self)
            self._tabs_widget = TabsWidget(self._parent, self._context)
            self._tabs_widget.tabAdded.connect(self._tab_added_event)
            self._tabs_widget.tabClosed.connect(self._tab_closed_event)
            layout.addWidget(self._tabs_widget)
        return self._tabs_widget

    def statusBar(self):
        return self._parent.statusBar()

    def docksWidget(self) -> DockTabsWidget:
        if not hasattr(self, '_docks_widget'):
            self._docks_widget = DockTabsWidget(self._parent, self._context)
        return self._docks_widget

    @logmethod()
    def closeEvent(self, e: QEvent):
        """ Closes the main window and saves window-size and -position. """
        self._context.config.setSize(self.size())
        self._context.config.setPosition(self.pos())
        e.accept()

    @logmethod()
    def newTab(self, title: str = None, input_text: str = None, widget: QWidget = None) -> (int, QWidget):
        """
        Opens a new tab and writes input.
        :param title: The title of the tab.
        :param input_text: The input which should be written into the tab.
        """
        index, tab = self.tabsWidget().newTab(widget, title=title, input_text=input_text)
        self.tabsWidget().setCurrentIndex(index)
        return index, tab

    def duplicateTab(self, title, src_tab):
        raise NotImplementedError()
