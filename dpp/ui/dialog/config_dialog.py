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

import qtawesome
from PyQt5 import QtCore
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QWidget, QHBoxLayout, QTabWidget, QLabel, QFormLayout, QFrame, QVBoxLayout

from dpp.ui import IconLabel, KeyboardShortcutTable, SearchField, HSpacer
from dpp.ui.widget.plugin_tab import PluginTab


class ConfigDialog(QDialog):

    TAB_ABOUT = "About"
    TAB_PLUGINS = "Plugins"
    TAB_KEYBOARD_SHORTCUTS = "Keyboard Shortcuts"

    def __init__(self, parent, context: 'core.context.Context', select_tab_name: str=None):
        """
        Initializes the hidden dialog.
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
        self.setWindowTitle(" ")

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
        logo = os.path.join(self._context.getAppPath(), 'images', 'dpp.png')

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
        form_frame = QFrame(self)
        form_layout = QFormLayout()
        form_layout.setAlignment(QtCore.Qt.AlignLeft)
        form_layout.addRow(QLabel("<font size='18'>Decoder++</font>"), QLabel(""))
        form_layout.addRow(QLabel(""), QLabel(""))
        form_layout.addRow(QLabel("Core-Development: "), QLabel(""))
        form_layout.addRow(QLabel(""), QLabel("Thomas Engel"))
        form_layout.addRow(QLabel("Plugin-Development: "), QLabel(""))
        plugin_authors = self._context.plugins().authors()
        for plugin_author in plugin_authors:
            plugin_author_label = QLabel(plugin_author)
            # Show tooltip with all plugin names.
            # Enable automatic text wrapping of tooltip by using rich-text.
            plugin_author_label.setToolTip("<font>{}</font>".format(", ".join(sorted(set(self._context.plugins().names(author=plugin_author))))))
            form_layout.addRow(QLabel(""), plugin_author_label)
        form_layout.addRow(QLabel("Inspired By: "), QLabel(""))
        form_layout.addRow(QLabel(""), QLabel("PortSwigger's Burp Decoder"))
        form_layout.addRow(QLabel("Powered By: "), QLabel(""))
        form_layout.addRow(QLabel(""), QLabel("PyQt5"))
        form_layout.addRow(QLabel(""), QLabel("QtAwesome"))
        form_layout.addRow(QLabel(""), QLabel("QScintilla"))
        form_layout.addRow(QLabel("Website: "), QLabel(""))
        form_layout.addRow(QLabel(""), QLabel("<a href='https://github.com/bytebutcher/decoder-plus-plus/'>https://github.com/bytebutcher/decoder-plus-plus</a>"))
        form_frame.setLayout(form_layout)
        base_layout.addWidget(form_frame)
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
        shortcut_filter.setIcon(qtawesome.icon("fa.search"))
        frame_layout.addWidget(shortcut_filter)
        shortcut_table = KeyboardShortcutTable(self, self._context)
        shortcut_table.changed.connect(lambda id, shortcut_key: self._context.updateShortcutKey(id, shortcut_key))
        shortcut_table.keyPressed.connect(on_keyboard_shortcut_table_key_press)
        shortcut_filter.textChanged.connect(shortcut_table.model().setFilterRegExp)
        frame_layout.addWidget(shortcut_table)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        frame.setLayout(frame_layout)
        return frame
