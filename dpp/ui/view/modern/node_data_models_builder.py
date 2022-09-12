from typing import List

from qtpynodeeditor import NodeDataModel


class NodeDataModelsBuilder:

    def __init__(self, context: 'dpp.core.context.Context'):
        self._context = context

    def build(self) -> List[NodeDataModel]:
        node_data_models = []
        for plugin in self._context.plugins():
            node_data_models.append(PluginNodeDataModel(plugin))
        return node_data_models