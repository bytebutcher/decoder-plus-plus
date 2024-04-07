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
import re

from dpp.core.plugin import DecoderPlugin


class Plugin(DecoderPlugin):
    """
    Decodes a hex string to an integer.

    Example:

        Input:
            0x75bcd15

        Output:
            123456789
    """

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies
        super().__init__('Hex (int)', "Thomas Engel", [], context)

    def run(self, input_text: str) -> str:
        return self._run_lines(input_text, lambda text_part: str(int(text_part, 16)))

    def can_decode_input(self, input_text):
        if len(input_text) % 2 == 0:
            hex = re.search(r'^(0x|0X)[a-fA-F0-9]+$', input_text)
            if hex:
                return True
        return False