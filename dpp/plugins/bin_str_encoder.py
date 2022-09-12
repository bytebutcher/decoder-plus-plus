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
from dpp.core.plugin import EncoderPlugin


class Plugin(EncoderPlugin):
    """
    Encodes a string to a binary string.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            1100001 1100010 1100011 1100100 1100101 \\
            1100110 1100111 1101000 1101001 1101010 \\
            ...
            110100 110101 110110 110111 111000 111001
    """

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies
        super().__init__('BIN (str)', "Thomas Engel", ["codecs"], context)

    def run(self, input_text: str) -> str:
        bits = bin(int.from_bytes(input_text.encode('utf-8', 'surrogateescape'), 'big'))[2:]
        return ' '.join(self._chunk_string(bits.zfill(8 * ((len(bits) + 7) // 8)), 8))

    def _chunk_string(self, string, length):
        return [string[0 + i:length + i] for i in range(0, len(string), length)]
