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
from qtpy.QtWidgets import QFrame, QVBoxLayout

from qtpynodeeditor import FlowScene, DataModelRegistry, FlowView

from dpp.ui.view.modern.node_data_models import InputNodeDataModel
from dpp.ui.view.modern.node_data_models_builder import NodeDataModelsBuilder


class NodeEditor(QFrame):

    def __init__(self, parent, context, tab_id, plugins, input_text: str):
        super(__class__, self).__init__(parent)
        self._context = context
        self._tab_id = tab_id
        self._plugins = plugins
        self._layout = QVBoxLayout()
        self._node_data_models_builder = NodeDataModelsBuilder(context)
        node_editor_view = self._init_node_editor_view(input_text)
        self._layout.addWidget(node_editor_view)
        self.setLayout(self._layout)
        self._layout.setContentsMargins(0, 0, 0, 0)

    def _init_node_editor_view(self, input: str):

        #data_models = .build()
        registry = DataModelRegistry()
        registry.register_model(InputNodeDataModel, style=None)


        scene = FlowScene(registry=registry)
        view = FlowView(scene)

        inputs = []
        input = scene.create_node(InputNodeDataModel)
        input.input = input


        try:
            scene.auto_arrange(nodes=inputs, layout='bipartite')
        except ImportError:
            ...

        return view
