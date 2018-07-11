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

import qtawesome
from PyQt5 import QtCore
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QWidget, QHBoxLayout, QTabWidget, QLabel, QFormLayout, QFrame, QVBoxLayout

from ui import IconLabel, ShortcutTable, SearchField


class HiddenDialog(QDialog):

    def __init__(self, parent, context):
        super().__init__(parent)
        self._context = context
        layout = QHBoxLayout()
        tabs = QTabWidget()
        tabs.insertTab(0, self._init_about_tab(), "About")
        tabs.insertTab(1, self._init_keyboard_shortcuts_tab(), "Keyboard Shortcuts")
        layout.addWidget(tabs)
        self.setLayout(layout)
        self.setWindowTitle(" ")

    def _init_about_tab(self):
        tab = QWidget(self)
        base_layout = QHBoxLayout()
        base_layout.setAlignment(QtCore.Qt.AlignCenter)
        icon_label = IconLabel(self, QIcon("dpp.png"))
        icon_label.setFixedSize(QSize(180, 180))
        base_layout.addWidget(icon_label)
        form_frame = QFrame(self)
        form_layout = QFormLayout()
        form_layout.addRow(QLabel("Decoder++"), QLabel(""))
        form_layout.addRow(QLabel("Core-Development: "), QLabel(""))
        form_layout.addRow(QLabel(""), QLabel("Thomas Engel"))
        form_layout.addRow(QLabel("Plugin-Development: "), QLabel(""))
        plugin_authors = self._context.commands().authors()
        for plugin_author in plugin_authors:
            plugin_author_label = QLabel(plugin_author)
            plugin_author_label.setToolTip(", ".join(sorted(set(self._context.commands().names(author=plugin_author)))))
            form_layout.addRow(QLabel(""), plugin_author_label)
        form_frame.setLayout(form_layout)
        base_layout.addWidget(form_frame)
        tab.setLayout(base_layout)
        return tab

    def _init_keyboard_shortcuts_tab(self):
        frame = QFrame(self)
        frame_layout = QVBoxLayout(self)
        shortcut_filter = SearchField()
        shortcut_filter.setIcon(qtawesome.icon("fa.search"))
        frame_layout.addWidget(shortcut_filter)
        shortcut_table = ShortcutTable(self, self._context.getShortcuts())
        shortcut_table.shortcutUpdated.connect(lambda id, shortcut_key: self._context.updateShortcutKey(id, shortcut_key))
        shortcut_filter.textChanged.connect(shortcut_table.model().setFilterRegExp)
        frame_layout.addWidget(shortcut_table)
        frame.setLayout(frame_layout)
        return frame
