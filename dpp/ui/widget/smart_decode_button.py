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

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QMenu
from PyQt6.QtGui import QAction

from dpp.core.plugin import DecoderPlugin


class SmartDecodeButton(QFrame):
    """ A button which provides a smart-decode functionality. """

    def __init__(self, parent, plugins: List[DecoderPlugin], get_input_callback, select_decoder_callback, logger):
        super(__class__, self).__init__(parent)
        self._plugins = plugins
        self._get_input = get_input_callback
        self._select_decoder = select_decoder_callback
        self._logger = logger
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 6, 0, 0)
        self._button = self._init_button()
        layout.addWidget(self._button)
        self.setLayout(layout)

    def _init_button(self):
        button = QPushButton("Smart decode")
        menu = QMenu(self)
        menu.aboutToShow.connect(lambda: self._populate_button_menu(self._get_input()))
        button.setMenu(menu)
        return button

    def _can_plugin_decode_input(self, decoder: DecoderPlugin, input: str) -> bool:
        """ Returns whether the decoder can decode the specified input. """
        try:
            # Check whether decoder thinks it can decode the input
            if not decoder.can_decode_input(input):
                return False
            # Check whether decoder actually can decode the input without any error
            decoder.select(input)
            return True
        except:
            return False

    def _get_matching_decoders(self, input) -> List[DecoderPlugin]:
        """ Returns a list of matching decoders for the specified input. """
        if not input:
            return []

        return [plugin for plugin in self._plugins if self._can_plugin_decode_input(plugin, input)]

    def _populate_button_menu(self, input):
        """ Populates the button menu with a list of matching decoders for the specified input. """
        menu = self._button.menu()
        menu.clear()
        decoders = self._get_matching_decoders(input)
        if not decoders:
            action = menu.addAction("No matching decoders found ...")
            action.setEnabled(False)
            return

        for decoder in decoders:
            action = QAction(decoder.title(), self)
            action.triggered.connect(lambda chk, item=decoder: self._select_decoder(item))
            menu.addAction(action)
