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
from typing import Callable

from qtpy.QtWidgets import QFrame

from dpp.ui.builder.widget_builder import LayoutBuilder


class PluginConfigWidgetBuilder:

    def __init__(self, parent, plugin, input_text):
        self._parent = parent
        self._plugin = plugin
        self._input_text = input_text

    def layout(self, callback: Callable) -> 'PluginConfigWidgetBuilder':
        self._layout_callback = callback
        return self

    def build(self) -> QFrame:
        """ Builds the widget based on the layout specification. """
        frame = QFrame(self._parent)
        layout_spec = self._plugin.layout(self._input_text)
        assert layout_spec, 'Illegal layout specification! Expected object, got None!'
        layout = LayoutBuilder().build(self._plugin, self._input_text, layout_spec)
        assert layout, 'Illegal layout! Expected object, got None!'
        layout.setContentsMargins(0, 0, 0, 0)
        frame.setLayout(layout)
        return frame
