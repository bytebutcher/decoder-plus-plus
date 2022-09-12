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
    Decodes a HTML string.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!&quot;§$%&amp;/()=?´`&lt;&gt;| ,.-;:_#+&#x27;*~
            0123456789

        Output:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789
    """

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies
        super().__init__('HTML', "Thomas Engel", ["html"], context)

    def run(self, input_text: str) -> str:
        import html
        return html.unescape(input_text)

    def can_decode_input(self, input_text: str) -> bool:
        """
        Checks whether input can be decoded. When decoded input does not match the initial input some decoding must
        have happened so we return True.
        """
        if input_text:
            try:
                return self.run(input_text) != input_text
            except:
                return False
        return False
