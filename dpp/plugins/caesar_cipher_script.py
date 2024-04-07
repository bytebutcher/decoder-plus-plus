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
import math
import string

from dpp.core.exceptions import CodecException
from dpp.core import plugin
from dpp.core.icons import Icon
from dpp.core.plugin.config import options
from dpp.core.plugin.config.ui import Layout
from dpp.core.plugin.config.ui.layouts import HBoxLayout
from dpp.core.plugin.config.ui.widgets import Button, Option


class Plugin(plugin.ScriptPlugin):
    """ Script to transform text using caesar-cipher. """

    class Option(object):
        Shift = plugin.config.Label("shift", "Shift:")

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies
        super().__init__('Caesar Cipher', "Thomas Engel", [], context, Icon.EDIT)
        self.config.add(plugin.config.options.Slider(
            label=Plugin.Option.Shift,
            value=0,
            description="integer by which the value of the letters should be shifted.",
            is_required=True,
            range=[0, 26]
        ))
        self._codec = CaesarCipher()

    def _create_options_layout(self, input_text: str) -> Layout:
        return HBoxLayout(widgets=[
            Option(Plugin.Option.Shift),
            Button(
                label="Calculate",
                on_click=lambda event: self._calculate_shift(self._config, input_text)
            )
        ])

    def _calculate_shift(self, config, input_text):
        config.update({Plugin.Option.Shift.key: self._codec.calculate_offset(input_text)})

    @property
    def title(self):
        return "{} shift {}".format("Caesar Cipher", self.config.value(Plugin.Option.Shift))

    def run(self, input_text: str):
        return self._codec.run(self.config, input_text)


class CaesarCipher:
    """
    Caesar cipher and offset calculator for Caesar cipher based on known frequency of english letters.
    Based on code from RobSpectre (see https://github.com/RobSpectre/Caesar-Cipher/)
    """

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        # Frequency of letters used in English, taken from Wikipedia.
        # http://en.wikipedia.org/wiki/Letter_frequency
        self.frequency = {
            'a': 0.08167,
            'b': 0.01492,
            'c': 0.02782,
            'd': 0.04253,
            'e': 0.130001,
            'f': 0.02228,
            'g': 0.02015,
            'h': 0.06094,
            'i': 0.06966,
            'j': 0.00153,
            'k': 0.00772,
            'l': 0.04025,
            'm': 0.02406,
            'n': 0.06749,
            'o': 0.07507,
            'p': 0.01929,
            'q': 0.00095,
            'r': 0.05987,
            's': 0.06327,
            't': 0.09056,
            'u': 0.02758,
            'v': 0.00978,
            'w': 0.02360,
            'x': 0.00150,
            'y': 0.01974,
            'z': 0.00074}

    def _calculate_entropy(self, input_text):
        """
        Calculates the entropy of a string based on known frequency.
        :param input_text: the input string.
        :return: a negative float with the total entropy of the input (higher is better).
        """
        total = 0
        for char in input_text:
            if char.isalpha() and char in self.frequency:
                prob = self.frequency[char.lower()]
                total += - math.log(prob) / math.log(2)
        return total

    def _translate(self, _input_text, offset, alphabet):
        shifted_alphabet = alphabet[offset:] + alphabet[:offset]
        table = str.maketrans(alphabet, shifted_alphabet)
        return _input_text.translate(table)

    def _run(self, input_text, offset):

        try:
            return self._translate(
                self._translate(input_text, offset, string.ascii_lowercase), offset, string.ascii_uppercase
            )
        except Exception as err:
            self._logger.debug(err, exc_info=True)
            raise CodecException('Calculating caesar cipher failed!')

    def run(self, config, input_text):
        """
        Applies the caesar cipher.
        :param config: the input parameters.
        :param input_text: the input string.
        :return: String with cipher applied.
        """
        # integer by which the value of the letters should be shifted.
        offset = int(config.value(Plugin.Option.Shift))
        return self._run(input_text, offset)

    def calculate_offset(self, input_text):
        """
        Attempts to calculate offset of ciphertext using frequency of letters in English.
        :param input_text: the input string.
        :return: the most likely offset
        """
        entropy_values = {}
        for i in range(26):
            offset = i * -1
            test_cipher = self._run(input_text, offset)
            entropy_values[i] = self._calculate_entropy(test_cipher)

        sorted_by_entropy = sorted(entropy_values, key=entropy_values.get)
        offset = sorted_by_entropy[0] * -1
        return 26 + offset
