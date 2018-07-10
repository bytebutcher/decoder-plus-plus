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
from PyQt5.QtCore import QStringListModel, pyqtSignal, QTimer
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QCompleter, QDockWidget, QDialog

from core.command import Command
from ui import SearchField


class CommandRunDialog(QDialog):

    commandRunEvent = pyqtSignal('PyQt_PyObject')

    def __init__(self, parent, commands):
        super().__init__(parent)
        self._commands = commands
        self.setWindowTitle("Run...")
        self.setModal(True)
        self.setParent(parent)
        layout = QHBoxLayout()
        layout.addWidget(self._init_widget())
        self.setLayout(layout)

    def _init_widget(self):
        widget = QWidget(self)
        layout = QHBoxLayout()
        self._search_field = SearchField(self)
        self._search_field.setIcon(qtawesome.icon("fa.search"))
        self._search_field.escapePressed.connect(self.close)
        self._search_field.enterPressed.connect(self._on_enter_press)
        self._search_field.setFocus()
        completer = QCompleter()
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        completer.setFilterMode(QtCore.Qt.MatchContains)
        completer_model = CommandListItemModel(self._commands)
        completer.setModel(completer_model)
        self._search_field.setCompleter(completer)
        layout.addWidget(self._search_field)
        widget.setLayout(layout)
        return widget

    def _on_enter_press(self):
        text, type = self._get_search_term()
        if not text or not type:
            self._search_field.flashBackgroundColor("#f6989d")
            return

        try:
            command = self._commands.command(text, type.upper())
            self._search_field.flashBackgroundColor("#22b14c")
            self.commandRunEvent.emit(command)
            QTimer.singleShot(200, self.close)
        except:
            # Unknown command
            self._search_field.flashBackgroundColor("#f6989d")

    def _get_search_term(self):
        elements = self._search_field.text().split(" ")
        type = elements.pop()
        text = " ".join(elements)
        return text, type


class CommandListItemModel(QStringListModel):

    def __init__(self, commands, parent=None):
        super(CommandListItemModel, self).__init__(parent)
        self._commands = commands
        self.setStringList(self._init_string_list(commands))

    def _init_string_list(self, commands):
        string_list = []
        string_list += self._init_string_list_type(commands, Command.Type.ENCODER)
        string_list += self._init_string_list_type(commands, Command.Type.DECODER)
        string_list += self._init_string_list_type(commands, Command.Type.HASHER)
        string_list += self._init_string_list_type(commands, Command.Type.SCRIPT)
        return sorted(string_list)

    def _init_string_list_type(self, commands, type):
        return [name + " " + type.capitalize() for name in commands.names(type)]

    def data(self, index, role=None):
        if not index.isValid() or not (0 <= index.row() < len(self._commands)):
            return QtCore.QVariant()
        return super(CommandListItemModel, self).data(index, role)

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self._commands)


