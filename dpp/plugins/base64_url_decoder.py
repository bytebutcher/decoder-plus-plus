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
    Decodes a URL-safe BASE64 string.

    URL-safe BASE64 is a BASE64 derivation which remaps following characters:

     Location  Base64  Http64
     --------  ------  ------
       62        +       -
       63        /       _

    Example:

        Input:
            YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXoKXsKwISLCpyQlJi8oKT0_wrRgPD58ICwuLTs6XyMrJyp-CjAxMjM0NTY3ODk=

        Output:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789
    """

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies
        super().__init__('BASE64 (URL-safe)', "Thomas Engel", ["base64"], context)

    def run(self, input_text: str) -> str:
        import base64
        input_text = self._add_missing_padding(input_text.encode('utf-8', errors="surrogateescape"))
        return base64.urlsafe_b64decode(input_text).decode('utf-8', errors="surrogateescape")

    def _add_missing_padding(self, input_text: str) -> str:
        missing_padding = len(input_text) % 4
        if missing_padding != 0:
            input_text += b'=' * (4 - missing_padding)
        return input_text

    def can_decode_input(self, input_text: str) -> bool:
        if len(input_text) % 4 == 0:
            if input_text.startswith("0o") and input_text[2:].isdigit():
                # This looks more like an octal encoding.
                return False
            if not ("-" in input_text or "_" in input_text):
                # The urlsafe b64 encoder substitutes - instead of + and _ instead of /.
                # If these characters are not found in the input string it might be b64, but it is not the urlsafe b64.
                return False
            if re.search(r'^(?:[A-Za-z0-9\-_]{4})*(?:[A-Za-z0-9\-_]{2}==|[A-Za-z0-9\-_]{3}=)?$', input_text):
                return True
        return False
