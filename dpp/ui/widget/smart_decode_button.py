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

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QPushButton

from dpp.core.plugin import DecoderPlugin


class SmartDecodeButton(QFrame):
    """ A button which provides a smart-decode functionality. """

    clicked = pyqtSignal()

    def __init__(self, parent, plugins: List[DecoderPlugin]):
        super(__class__, self).__init__(parent)
        self._plugins = plugins
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 6, 0, 0)
        self._button = self._init_button()
        layout.addWidget(self._button)
        self.setLayout(layout)

    def _init_button(self):
        button = QPushButton("Smart decode")
        button.clicked.connect(self._button_click_event)
        return button

    def _button_click_event(self):
        """ Forwards the "Smart decode" button click event. """
        self.clicked.emit()

    def _test_decoders(self, input, possible_decoders) -> List[DecoderPlugin]:
        """ Returns a list of decoders which did not threw an error when executing them with the specified input. """
        decoders_without_error = []
        for decoder in possible_decoders:
            try:
                decoder.select(input)
                decoders_without_error.append(decoder)
            except:
                pass
        return decoders_without_error

    def get_possible_decoders(self, input) -> List[DecoderPlugin]:
        """ Returns a list of possible decoders for the specified input. """
        possible_decoders = []
        for plugin in self._plugins:
            if plugin.can_decode_input(input):
                possible_decoders.append(plugin)
        return self._test_decoders(input, possible_decoders)
