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
from qtpy.QtWidgets import QWidget

from dpp.ui.view.main_window_widget import MainWindowWidget
from dpp.ui.view.modern.node_editor_tab import NodeEditorTab


class ModernMainWindowWidget(MainWindowWidget):

    def __init__(self, parent, context: 'dpp.core.context.Context', input_text: str):
        super().__init__(parent, context, input_text)

    #############################################
    # Menu items
    #############################################

    def _init_menu_items(self):
        self._register_shortcuts('&File', [])
        self._register_shortcuts('&Edit', [])
        self._register_shortcuts('&View', [])
        self._register_shortcuts("&Select", [])
        self._register_shortcuts('&Tabs', [])
        self._register_shortcuts('&Help', [])
        super()._init_menu_items()

    #############################################
    # Connector functions
    #############################################

    def _open_file_action(self) -> str:
        # filename = super()._open_file()
        raise NotImplementedError()

    def _save_as_file_action(self) -> str:
        # filename = super()._save_as_file()
        raise NotImplementedError()

    def _tab_duplicate_action(self, title, src_tab):
        # tab_index, dst_tab = self._new_tab(title=title)
        raise NotImplementedError()

    #############################################
    # Public functions
    #############################################

    def newTab(self, title: str = None, input_text: str = None, widget: QWidget = None) -> (int, QWidget):
        tab = NodeEditorTab(self, self._context, self._plugins, input_text)
        return super().newTab(title, input_text, tab)

    def toDict(self):
        raise NotImplementedError()

