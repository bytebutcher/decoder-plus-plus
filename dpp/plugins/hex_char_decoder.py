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
    Decodes hex to ascii chars.

    Example:

        Input:
            0x61 0x62 0x63 0x64 0x65 0x66 0x67 0x68 0x69 0x6a 0x6b [...] \\
            0x5e 0xb0 0x21 0x22 0xa7 0x24 0x25 0x26 0x2f 0x28 0x29 [...] \\
            0x30 0x31 0x32 0x33 0x34 0x35 0x36 0x37 0x38 0x39 \\

        Output:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789
    """

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies
        super().__init__('Hex (char)', "Thomas Engel", [], context)

    def run(self, input_text: str) -> str:
        if input_text:
            import re
            output = input_text
            for hex_code in set(sorted(re.findall(r'0[Xx][0-9a-fA-F][0-9a-fA-F][ ]?', input_text))):
                try:
                    output = output.replace(hex_code, chr(int(hex_code.strip(), 16)))
                except:
                    # Hex codes which can not be transformed to ascii are not replaced.
                    pass
            return output
        else:
            return ""

    def can_decode_input(self, input_text: str) -> bool:
        contains_hex = re.findall(r'0[Xx][0-9a-fA-F][0-9a-fA-F]', input_text)
        if contains_hex:
            return True
        return False
