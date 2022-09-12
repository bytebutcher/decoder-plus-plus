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
from dpp.core.plugin import DecoderPlugin


class Plugin(DecoderPlugin):
    """
    Decodes a binary string.

    Example:

        Input:
            1100001 1100010 1100011 1100100 1100101 \\
            1100110 1100111 1101000 1101001 1101010 \\
            ...
            110100 110101 110110 110111 111000 111001

        Output:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789
    """

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies
        super().__init__('BIN (str)', "Thomas Engel", [], context)

    def run(self, input_text: str) -> str:
        n = int(input_text.replace(' ', ''), 2)
        return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode("utf-8", "surrogateescape") or '\0'
