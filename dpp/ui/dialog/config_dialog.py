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
from datetime import datetime

from qtpy import QtCore
from qtpy.QtCore import QSize
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QDialog, QWidget, QHBoxLayout, QTabWidget, QLabel, QFormLayout, QFrame, QVBoxLayout

from dpp.core.icons import icon, Icon
from dpp.ui import IconLabel, KeyboardShortcutTable, SearchField, HSpacer
from dpp.ui.widget.plugin_tab import PluginTab


class ConfigDialog(QDialog):
    TAB_ABOUT = "About"
    TAB_PLUGINS = "Plugins"
    TAB_KEYBOARD_SHORTCUTS = "Keyboard Shortcuts"

    def __init__(self, parent, context: 'core.context.Context', select_tab_name: str = None):
        """
        Initializes the config dialog.
        :param parent: the widget which is calling the dialog.
        :param context: the context of the application.
        :param select_tab_name: the tab name which should be selcted.
        """
        super().__init__(parent)
        self._context = context
        layout = QHBoxLayout()
        tabs = QTabWidget()

        self._about_tab = self._init_about_tab()
        tabs.insertTab(0, self._about_tab, ConfigDialog.TAB_ABOUT)

        self._plugins_tab = self._init_plugins_tab()
        tabs.insertTab(1, self._plugins_tab, ConfigDialog.TAB_PLUGINS)

        self._keyboard_shortcuts_tab = self._init_keyboard_shortcuts_tab()
        tabs.insertTab(2, self._keyboard_shortcuts_tab, ConfigDialog.TAB_KEYBOARD_SHORTCUTS)

        self._init_tab_selection(tabs, select_tab_name)

        layout.addWidget(tabs)

        self.setLayout(layout)
        self.setMinimumWidth(640)
        self.setWindowTitle("Configuration")

    def _init_tab_selection(self, tabs: QTabWidget, tab_name: str):
        """ Selects the tab with the specified name. """
        for tab_index in range(len(tabs)):
            text = tabs.tabText(tab_index)
            if text == tab_name:
                tabs.setCurrentIndex(tab_index)

    def _init_about_tab(self):
        tab = QWidget(self)
        base_layout = QHBoxLayout()
        base_layout.setAlignment(QtCore.Qt.AlignVCenter)
        if datetime.now().month == 12:
            logo = os.path.join(self._context.getAppPath(), 'images', 'dpp_xmas_stylized.png')
        else:
            logo = os.path.join(self._context.getAppPath(), 'images', 'dpp_stylized.png')
        icon_frame = QFrame()
        icon_layout = QHBoxLayout()
        icon_label = IconLabel(self, QIcon(logo))
        icon_label.mouseDoubleClickEvent = lambda evt: self._context.toggleDebugMode()
        icon_label.setFixedSize(QSize(180, 180))
        icon_layout.setAlignment(QtCore.Qt.AlignLeft)
        icon_layout.setContentsMargins(10, 10, 10, 10)
        icon_layout.addWidget(icon_label)
        icon_frame.setLayout(icon_layout)
        base_layout.addWidget(icon_frame)
        content_frame = QFrame(self)
        frame_layout = QFormLayout()
        frame_layout.setAlignment(QtCore.Qt.AlignTop)
        frame_layout.addRow(QLabel("<font size='18'>Decoder++</font>"))
        frame_layout.addRow(QLabel(f'Version: <i>{self._context.getAppVersion()}</i>'))
        frame_layout.addRow(QLabel("Author: <i>Thomas Engel</i>"))
        frame_layout.addRow(QLabel("Inspired by: <i>PortSwigger's Burp Decoder</i>"))
        frame_layout.addRow(QLabel("Powered by: <i>Qt</i>"))
        authors_label = QLabel('<i>' + ', '.join(
            author for author in self._context.plugins().authors() if author != "Thomas Engel") + '</i>')
        authors_label.setWordWrap(True)
        label = QLabel('Thanks to:')
        label.setAlignment(QtCore.Qt.AlignTop)
        frame_layout.addRow(label, authors_label)
        frame_layout.addRow(QLabel(
            "Website: <a href='https://github.com/bytebutcher/decoder-plus-plus/'>https://github.com/bytebutcher/decoder-plus-plus</a>"))
        content_frame.setLayout(frame_layout)
        base_layout.addWidget(content_frame)
        base_layout.addWidget(HSpacer())
        tab.setLayout(base_layout)
        return tab

    def _init_plugins_tab(self):
        return PluginTab(self._context, self)

    def _init_keyboard_shortcuts_tab(self):

        def on_keyboard_shortcut_table_key_press(text):
            # Focus search bar when alpha numeric key was pressed in shortcut table
            shortcut_filter.setFocus()
            shortcut_filter.setText(text)

        frame = QFrame(self)
        frame_layout = QVBoxLayout(self)
        shortcut_filter = SearchField(self)
        shortcut_filter.setPlaceholderText("Search keyboard shortcut...")
        shortcut_filter.setIcon(icon(Icon.SEARCH))
        frame_layout.addWidget(shortcut_filter)
        shortcut_table = KeyboardShortcutTable(self, self._context)
        shortcut_table.changed.connect(lambda id, shortcut_key: self._context.updateShortcutKey(id, shortcut_key))
        shortcut_table.keyPressed.connect(on_keyboard_shortcut_table_key_press)
        shortcut_filter.textChanged.connect(shortcut_table.model().setFilterRegularExpression)
        frame_layout.addWidget(shortcut_table)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        frame.setLayout(frame_layout)
        return frame
