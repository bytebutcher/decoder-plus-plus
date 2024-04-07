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

from dpp.core.plugin import EncoderPlugin


class Plugin(EncoderPlugin):
    """
    Encodes ascii characters to hex.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            0x61 0x62 0x63 0x64 0x65 0x66 0x67 0x68 0x69 0x6a 0x6b [...] \\
            0x5e 0xb0 0x21 0x22 0xa7 0x24 0x25 0x26 0x2f 0x28 0x29 [...] \\
            0x30 0x31 0x32 0x33 0x34 0x35 0x36 0x37 0x38 0x39 \\
    """

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies
        super().__init__('Hex (char)', "Thomas Engel", [], context)

    def _run_line(self, line) -> str:
        return ' '.join([hex(ord(char)) for char in line])

    def run(self, input_text: str) -> str:
        return self._run_lines(input_text, self._run_line)
