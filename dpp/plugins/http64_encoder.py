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
    Encodes a text using HTTP64.

    HTTP64 is a BASE64 derivation which remaps following characters:

     Location  Base64  Http64
     --------  ------  ------
       62        +       -
       63        /       _
      (pad)      =       $

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXoKXsKwISLCpyQlJi8oKT0_wrRgPD58ICwuLTs6XyMrJyp-CjAxMjM0NTY3ODk$
    """

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies
        super().__init__('HTTP64', "Thomas Engel", ["base64"], context)

    def run(self, input_text: str) -> str:
        import base64
        encoded = base64.b64encode(input_text.encode('utf-8', errors="surrogateescape")) \
            .decode('utf-8', errors="surrogateescape")
        encoded = encoded.replace('+', '-')
        encoded = encoded.replace('/', '_')
        encoded = encoded.replace('=', '$')
        return encoded
