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
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QToolButton, QLabel, QAction

from core import Context
from core.plugin.plugin import PluginType
from ui import *
from ui.dialog.hidden_dialog import HiddenDialog


class MainWindowWidget(QWidget):

    def __init__(self, parent, context):
        super(QWidget, self).__init__(parent)
        self._parent = parent
        self._context = context
        self._plugins = context.plugins()
        self._main_window = parent

        self.layout = QVBoxLayout(self)
        self._tabs = self._init_tabs_widget()
        self._tab_new()
        self._tabs.setCurrentIndex(0)
        self.layout.addWidget(self._tabs)
        self.setLayout(self.layout)
        self._init_shortcuts()


    def _init_shortcuts(self):
        main_menu = self._parent.menuBar()
        self._init_file_menu(main_menu)
        self._init_edit_menu(main_menu)
        self._init_view_menu(main_menu)
        self._init_select_menu(main_menu)
        self._init_tab_menu(main_menu)
        self._init_help_menu(main_menu)

    def _init_help_menu(self, main_menu):
        help_menu = main_menu.addMenu('&Help')
        keyboard_shortcuts_action = QAction("&Keyboard Shortcuts", self)
        keyboard_shortcuts_action.triggered.connect(lambda: self._show_hidden_dialog(HiddenDialog.TAB_KEYBOARD_SHORTCUTS))
        help_menu.addAction(keyboard_shortcuts_action)
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_hidden_dialog)
        help_menu.addAction(about_action)

    def _init_edit_menu(self, main_menu):
        edit_menu = main_menu.addMenu('&Edit')
        self._register_shortcut(Context.Shortcut.TOGGLE_SEARCH_FIELD,
                                "Toggle Search Field",
                                "Ctrl+F",
                                lambda: self._toggle_search_field(),
                                edit_menu)

    def _init_view_menu(self, main_menu):
        view_menu = main_menu.addMenu('&View')
        self._register_shortcut(Context.Shortcut.SELECT_PLAIN_VIEW,
                                "Show Plain View",
                                "Alt+P",
                                lambda: self._select_plain_view(),
                                view_menu)
        self._register_shortcut(Context.Shortcut.SELECT_HEX_VIEW,
                                "Show Hex View",
                                "Alt+X",
                                lambda: self._select_hex_view(),
                                view_menu)

    def _init_select_menu(self, main_menu):
        select_menu = main_menu.addMenu('&Select')
        self._register_shortcut(Context.Shortcut.FOCUS_DECODER,
                                "Select Decoder",
                                "Alt+D",
                                lambda: self._focus_combo_box(PluginType.DECODER),
                                select_menu)
        self._register_shortcut(Context.Shortcut.FOCUS_ENCODER,
                                "Select Encoder",
                                "Alt+E",
                                lambda: self._focus_combo_box(PluginType.ENCODER),
                                select_menu)
        self._register_shortcut(Context.Shortcut.FOCUS_HASHER,
                                "Select Hasher",
                                "Alt+H",
                                lambda: self._focus_combo_box(PluginType.HASHER),
                                select_menu)
        self._register_shortcut(Context.Shortcut.FOCUS_SCRIPT,
                                "Select Script",
                                "Alt+S",
                                lambda: self._focus_combo_box(PluginType.SCRIPT),
                                select_menu)
        self._register_shortcut(Context.Shortcut.FOCUS_INPUT_TEXT,
                                "Select Text Field",
                                "Alt+I",
                                lambda: self._focus_input_text(),
                                select_menu)
        self._register_shortcut(Context.Shortcut.FOCUS_INPUT_TEXT_NEXT,
                                "Select Next Text Field",
                                "Alt+Down",
                                lambda: self._focus_input_text_next(),
                                select_menu)
        self._register_shortcut(Context.Shortcut.FOCUS_INPUT_TEXT_PREVIOUS,
                                "Select Previous Text Field",
                                "Alt+Up",
                                lambda: self._focus_input_text_previous(),
                                select_menu)

    def _init_tab_menu(self, main_menu):
        tab_menu = main_menu.addMenu('&Tabs')
        self._register_shortcut(Context.Shortcut.TAB_RENAME,
                                "Rename Tab",
                                "Alt+Shift+R",
                                self._tabs.tabBar().renameTab,
                                tab_menu)
        self._register_shortcut(Context.Shortcut.TAB_NEXT,
                                "Next Tab",
                                "Ctrl+Tab",
                                self._tab_next,
                                tab_menu)
        self._register_shortcut(Context.Shortcut.TAB_PREVIOUS,
                                "Previous Tab",
                                "Ctrl+Shift+Tab",
                                self._tab_previous,
                                tab_menu)

    def _init_file_menu(self, main_menu):
        file_menu = main_menu.addMenu('&File')
        self._register_shortcut(Context.Shortcut.TAB_NEW,
                                "New Tab", "Ctrl+T",
                                self._tab_new,
                                file_menu)
        self._register_shortcut(Context.Shortcut.TAB_CLOSE,
                                "Close Tab",
                                "Ctrl+W",
                                self._tab_close,
                                file_menu)

    def _register_shortcut(self, id, text, shortcut_key, callback, menu):
        action = self._context.registerShortcut(id, text, shortcut_key, callback, self)
        menu.addAction(action)


    def _call_focussed_frame(self, callback):
        focussed_frame = self._get_focussed_frame()
        if focussed_frame:
            callback(focussed_frame)

    def _get_focussed_frame(self):
        return self._tabs.currentWidget().getFocussedFrame()

    def _focus_combo_box(self, type):
        self._call_focussed_frame(lambda focussed_frame: focussed_frame.focusComboBox(type))

    def _focus_input_text(self):
        self._call_focussed_frame(lambda focussed_frame: focussed_frame.focusInputText())

    def _focus_input_text_next(self):
        focussed_frame = self._get_focussed_frame()
        if focussed_frame:
            if focussed_frame.next():
                focus_frame = focussed_frame.next()
            else:
                focus_frame = focussed_frame
            focus_frame.focusInputText()
            self._tabs.currentWidget().ensureWidgetVisible(focus_frame)

    def _focus_input_text_previous(self):
        focussed_frame = self._get_focussed_frame()
        if focussed_frame:
            if focussed_frame.previous():
                focus_frame = focussed_frame.previous()
            else:
                focus_frame = focussed_frame
            focus_frame.focusInputText()
            self._tabs.currentWidget().ensureWidgetVisible(focus_frame)

    def _select_plain_view(self):
        self._call_focussed_frame(lambda focussed_frame: focussed_frame.selectPlainView())

    def _select_hex_view(self):
        self._call_focussed_frame(lambda focussed_frame: focussed_frame.selectHexView())

    def _toggle_search_field(self):
        self._call_focussed_frame(lambda focussed_frame: focussed_frame.toggleSearchField())

    def _init_tabs_widget(self):
        tabs = QTabWidget()
        bar = TabBar()
        # BUG: Moving tabs beyond last tab breaks program-design (last tab is supposed to be the "add new tab button ('+')").
        # WORKAROUND: ???
        # NOTES:
        # * Currently moving tabs is disabled.
        # * Using an Event-Filter to disable dropping tabs on certain areas did not work.
        bar.setMovable(False)
        tabs.setTabBar(bar)
        tabs.setTabsClosable(True)
        tabs.tabCloseRequested.connect(self._tab_close)
        tab_new_button = QToolButton()
        tab_new_button.clicked.connect(self._tab_new)
        tab_new_button.setText("+")
        tabs.addTab(QLabel("Add new Tab"), "")
        tabs.setTabEnabled(0, False)
        tabs.tabBar().setTabButton(0, TabBar.RightSide, tab_new_button)
        return tabs

    def _tab_new(self):
        self._tabs.insertTab(self._tabs.count() - 1, CodecTab(self, self._context, self._plugins), "Tab")
        self._tabs.setCurrentIndex(self._tabs.count() - 2)

    def _tab_close(self, index=None):
        if not index:
            index = self._tabs.currentIndex()
        self._tabs.removeTab(index)
        if self._tabs.count() <= 1:
            self._tab_new()
        else:
            self._tabs.setCurrentIndex(index - 1)

    def _tab_next(self):
        self._tabs.setCurrentIndex((self._tabs.currentIndex() + 1) % (self._tabs.count() - 1))

    def _tab_previous(self):
        self._tabs.setCurrentIndex((self._tabs.currentIndex() - 1) % (self._tabs.count() - 1))

    def _show_hidden_dialog(self, tab_select: str=None):
        """ Shows the hidden dialog. """
        hidden_dialog = HiddenDialog(self, self._context, tab_select)
        hidden_dialog.exec_()
