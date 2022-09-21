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
import logging
from typing import List, Dict

from qtpy.QtWidgets import QAction, QFrame, QHBoxLayout, QPushButton, QMenu

from dpp.core.exceptions import CodecException
from dpp.core.math import eta
from dpp.core.plugin import DecoderPlugin


class SmartDecodeButton(QFrame):
    """ A button which provides a smart-decode functionality. """

    def __init__(self, parent, plugins: List[DecoderPlugin], get_input_callback, select_decoder_callback):
        super(__class__, self).__init__(parent)
        self._logger = logging.getLogger(__name__)
        self._plugins = plugins
        self._get_input = get_input_callback
        self._select_decoder = select_decoder_callback
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

    def _decode_input(self, decoder: DecoderPlugin, input_text: str) -> bool:
        """ Returns the decoded input. Raises an CodecException when decoding fails. """
        try:
            self._logger.debug(f'Trying to decode input using {decoder.name} ...')
            # Check whether decoder thinks it can decode the input
            if not decoder.can_decode_input(input_text):
                raise CodecException(f'Invalid input for {decoder.name}!')
            # Check whether decoder actually can decode the input without any error
            return decoder.run(input_text)
        except Exception as err:
            self._logger.debug(err)
            raise CodecException(f'Decoding input with {decoder.name} failed!')

    def _get_matching_decoders(self, input_text) -> Dict[float, DecoderPlugin]:
        """ Returns a dict of matching decoders with the associated entropy of the decoded output. """
        self._logger.debug(f'Looking for matching decoders for "{input_text}" ...')
        result = {}
        if not input_text:
            return result
        for plugin in self._plugins:
            try:
                output_text = self._decode_input(plugin, input_text)
                output_text_entropy = eta(output_text)
                result[output_text_entropy] = plugin
            except CodecException as err:
                # Expected exception when decoding input fails.
                self._logger.debug(err)
        return result

    def _populate_button_menu(self, input_text):
        """ Populates the button menu with a list of matching decoders for the specified input. """
        menu = self._button.menu()
        menu.clear()
        decoders = self._get_matching_decoders(input_text)
        if not decoders:
            action = menu.addAction("No matching decoders found ...")
            action.setEnabled(False)
            return

        entropy_orders = sorted(decoders, key=lambda x: float(x))
        for entropy in entropy_orders:
            decoder = decoders[entropy]
            action = QAction(f'{decoder.title} [{entropy:.2f}]', self)
            action.triggered.connect(lambda chk, item=decoder: self._select_decoder(item))
            menu.addAction(action)
