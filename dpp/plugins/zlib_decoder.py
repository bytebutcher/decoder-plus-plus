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
    Decodes bytes using ZLib.

    Example:

        Input:
            [bytes]

        Output:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789
    """

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies
        super().__init__('Zlib', "Thomas Engel", ["zlib"], context)

    def run(self, input_text: str) -> str:
        import zlib
        return zlib.decompress(input_text.encode('utf-8', errors='surrogateescape'))\
            .decode('utf-8', errors='surrogateescape')

    def can_decode_input(self, input_text: str) -> bool:
        if input_text:
            input_bytes = input_text.encode('utf-8', errors='surrogateescape')
            if len(input_bytes) > 2:
                return (input_bytes[0] == 0x78) and (input_bytes[1] in (
                    0x01, # No Compression/Low
                    0x9c, # Default Compression
                    0xda  # Best Compression
                ))
        return False
