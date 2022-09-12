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
    Decodes a Base54 string.

    Example:

        Input:
            0ECJPC% CC3DVED5QDO$D/3EHFE QEA%ET4F3GF:D1PROM84GROSP4A$4L35JX7TROL7CL+7134V$5.L7A1CMK5XG5/C1*96DL6WW66:6C1

        Output:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789
    """

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies
        super().__init__('BASE45', "Thomas Engel", ["base45"], context)

    def run(self, input_text: str) -> str:
        import base45
        return base45.b45decode(str.encode(input_text)).decode('utf-8', errors="surrogateescape")

    def can_decode_input(self, input_text: str) -> bool:
        if input_text.startswith("0o") and input_text[2:].isdigit():
            # This looks more like an octal encoding.
            return False
        if re.search(r'^[A-Z0-9 $%*+-./:]*$', input_text):
            return True
        return False

