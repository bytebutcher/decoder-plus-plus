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
    Decodes a hex string.

    Example:

        Input:
            6162636465666768696a6b6c6d6e6f70717273747576777 \\
            8797a0a5ec2b02122c2a72425262f28293d3fc2b4603c3e \\
            7c202c2e2d3b3a5f232b272a7e0a30313233343536373839

        Output:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789
    """

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies
        super().__init__('Hex (str)', "Thomas Engel", [], context)

    def run(self, input_text: str) -> str:
        return self._run_lines(input_text, lambda text_part: bytes.fromhex(text_part).decode('ascii'))

    def can_decode_input(self, input_text: str) -> bool:
        if len(input_text) % 2 == 0:
            hex = re.search(r'^[a-fA-F0-9]+$', input_text)
            if hex:
                return True
        return False
