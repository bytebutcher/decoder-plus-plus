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
    Encodes a string to a comma separated decimal string.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            97,98,99,100,101,102,103,104,\\
            105,106,107,108,109,110,111,112,\\
            ...
            10,48,49,50,51,52,53,54,\\
            55,56,57
    """

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies
        super().__init__('DEC (str)', "Thomas Engel", [], context)

    def run(self, input_text: str) -> str:
        return ",".join(str(ord(c)) for c in input_text)
