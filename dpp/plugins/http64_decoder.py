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
    Decodes a HTTP64 string.

    HTTP64 is a BASE64 derivation which remaps following characters:

     Location  Base64  Http64
     --------  ------  ------
       62        +       -
       63        /       _
      (pad)      =       $

    Example:

        Input:
            YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXoKXsKwISLCpyQlJi8oKT0_wrRgPD58ICwuLTs6XyMrJyp-CjAxMjM0NTY3ODk$

        Output:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789
    """

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies
        super().__init__('HTTP64', "Thomas Engel", ["base64"], context)

    def run(self, input_text: str) -> str:
        import base64
        encoded = self._add_missing_padding(input_text.encode('utf-8', errors="surrogateescape"))
        encoded = encoded.replace('-', '+')
        encoded = encoded.replace('_', '/')
        encoded = encoded.replace('$', '=')
        return base64.b64decode(encoded).decode('utf-8', errors="surrogateescape")

    def _add_missing_padding(self, input_text: str) -> str:
        missing_padding = len(input_text) % 4
        if missing_padding != 0:
            input_text += '$' * (4 - missing_padding)
        return input_text.decode('utf-8', errors="surrogateescape")

    def can_decode_input(self, input_text: str) -> bool:
        if len(input_text) % 4 == 0:
            if input_text.startswith("0o") and input_text[2:].isdigit():
                # This looks more like an octal encoding.
                return False
            if re.search(r'^(?:[A-Za-z0-9\-_]{4})*(?:[A-Za-z0-9\-_]{2}\$\$|[A-Za-z0-9\-_]{3}\$)?$', input_text):
                return True
        return False
