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
import uuid
from typing import List

from qtpy.QtWidgets import QVBoxLayout, QWidget


from dpp.core import Context
from dpp.core.plugin.manager import PluginManager
from dpp.ui.view.modern.node_editor import NodeEditor


class NodeEditorTab(QWidget):

    def __init__(self, parent, context: Context, plugin_manager: PluginManager, input_text: str):
        super(__class__, self).__init__(parent)
        self._tab_id = uuid.uuid4().hex
        self._layout = QVBoxLayout()
        self._node_editor = NodeEditor(parent, context, self._tab_id, plugin_manager, input_text)
        self._layout.addWidget(self._node_editor)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)

    # ------------------------------------------------------------------------------------------------------------------

    def id(self):
        return self._tab_id

    # ------------------------------------------------------------------------------------------------------------------

    def toDict(self) -> List[dict]:
        raise NotImplementedError()
