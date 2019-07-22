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

from typing import List

from PyQt5.QtWidgets import QHBoxLayout, QDockWidget, QFrame, QWidget

from core import Context
from core.listener import Listener
from ui.view.hex_view import HexView


class HexDock(QDockWidget):


    def __init__(self, parent: QWidget, context: Context):
        super(HexDock, self).__init__("Hex", parent)
        self._context = Context

        self._selected_frame_id = ""
        self._last_input_text = ""

        self._init_listener(context.listener())
        dock_frame = QFrame()
        dock_layout = QHBoxLayout()
        dock_layout.addWidget(self._init_hex_widget())
        dock_frame.setLayout(dock_layout)
        self.setWidget(dock_frame)

    def _init_listener(self, listener: Listener):
        listener.textChanged.connect(self._update_view)
        listener.textSelectionChanged.connect(self._update_view)
        listener.selectedFrameChanged.connect(self._selected_frame_changed)

    def _init_hex_widget(self):
        self._hex_dock_view = HexView(self, self._context, 0, "")
        return self._hex_dock_view

    def _chunk_string(self, string: str, length: int) -> List[str]:
        """ Breaks the string into a list of chunks with a specified max length. """
        return [string[0 + i:length + i] for i in range(0, len(string), length)]

    def _get_hex_view(self, string: str) -> List[str]:
        def get_hex_char(str_char):
            """ Returns the hex representation of an utf-character while ignoring surrogate special characters. """
            return "{0:02x}".format(ord(str_char))[:2]
        return [get_hex_char(string[i]) for i in range(0, len(string))]

    def _update_view(self, frame_id: str, input_text: str):
        if self._selected_frame_id == frame_id and self._last_input_text != input_text:
            self._last_input_text = input_text
            self._hex_dock_view.setData(input_text)

    def _selected_frame_changed(self, frame_id: str, input_text: str):
        self._selected_frame_id = frame_id
        self._update_view(frame_id, input_text)


    def closeEvent(self, QCloseEvent):
        self.hide()
