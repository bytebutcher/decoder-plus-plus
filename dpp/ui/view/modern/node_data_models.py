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
from qtpy.QtWidgets import QLineEdit, QWidget
from qtpynodeeditor import NodeDataModel, PortType

import threading

from qtpynodeeditor import NodeData, NodeDataType


class InputNodeData(NodeData):
    """ Node data holding a string. """
    data_type = NodeDataType('string', 'Input')

    def __init__(self, string: str = ''):
        self._string = string
        self._lock = threading.RLock()

    @property
    def lock(self):
        return self._lock

    @property
    def string(self) -> str:
        """ The string data. """
        return self._string



class PluginNodeDataModel(NodeDataModel):
    name = "Input"
    caption_visible = False
    num_ports = {PortType.input: 0,
                 PortType.output: 1,
                 }
    port_caption = {'output': {0: 'Result'}}
    data_type = InputNodeData.data_type

    def __init__(self, plugin, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._input = None
        self._line_edit = QLineEdit(parent)
        self._line_edit.setMaximumSize(self._line_edit.sizeHint())
        self._line_edit.textChanged.connect(self.on_text_edited)
        self._line_edit.setText("")

    @property
    def input(self):
        return self._input

    def save(self) -> dict:
        'Add to the JSON dictionary to save the state of the NumberSource'
        doc = super().save()
        if self._input:
            doc['input'] = self._input.string
        return doc

    def restore(self, state: dict):
        'Restore the number from the JSON dictionary'
        try:
            value = state["input"]
        except Exception:
            ...
        else:
            self._input = InputNodeData(value)
            self._line_edit.setText(self._input.string)

    def out_data(self, port: int) -> NodeData:
        '''
        The data output from this node
        Parameters
        ----------
        port : int
        Returns
        -------
        value : NodeData
        '''
        return self._input

    def embedded_widget(self) -> QWidget:
        'The source has a line edit widget for the user to type in'
        return self._line_edit

    def on_text_edited(self, string: str):
        '''
        Line edit text has changed
        Parameters
        ----------
        string : str
        '''
        try:
            string = self._line_edit.text()
        except ValueError:
            self._data_invalidated.emit(0)
        else:
            self._input = InputNodeData(string)
            self.data_updated.emit(0)


class InputNodeDataModel(NodeDataModel):
    name = "Input"
    caption_visible = False
    num_ports = {PortType.input: 0,
                 PortType.output: 1,
                 }
    port_caption = {'output': {0: 'Result'}}
    data_type = InputNodeData.data_type

    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._input = None
        self._line_edit = QLineEdit(parent)
        self._line_edit.setMaximumSize(self._line_edit.sizeHint())
        self._line_edit.textChanged.connect(self.on_text_edited)
        self._line_edit.setText("")

    @property
    def input(self):
        return self._input

    def save(self) -> dict:
        'Add to the JSON dictionary to save the state of the NumberSource'
        doc = super().save()
        if self._input:
            doc['input'] = self._input.string
        return doc

    def restore(self, state: dict):
        'Restore the number from the JSON dictionary'
        try:
            value = state["input"]
        except Exception:
            ...
        else:
            self._input = InputNodeData(value)
            self._line_edit.setText(self._input.string)

    def out_data(self, port: int) -> NodeData:
        '''
        The data output from this node
        Parameters
        ----------
        port : int
        Returns
        -------
        value : NodeData
        '''
        return self._input

    def embedded_widget(self) -> QWidget:
        'The source has a line edit widget for the user to type in'
        return self._line_edit

    def on_text_edited(self, string: str):
        '''
        Line edit text has changed
        Parameters
        ----------
        string : str
        '''
        try:
            string = self._line_edit.text()
        except ValueError:
            self._data_invalidated.emit(0)
        else:
            self._input = InputNodeData(string)
            self.data_updated.emit(0)