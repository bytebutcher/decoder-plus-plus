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
from typing import List

from dpp.core.plugin import DecoderPlugin


class Plugin(DecoderPlugin):
    """
    Decodes an octal string sequence to an ascii string.

    Example:

        Input:
            1411421431441451461471501511521531 \
            5415515615716016116216316416516616 \
            7170171172012136260041042247044045 \
            0460570500510750772641400740761740 \
            4005405605507307213704305304705217 \
            6012060061062063064065066067070071

        Output:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

    """

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies
        super().__init__('OCT (str)', "Thomas Engel", [], context)

    def run(self, input_text: str) -> str:
        return ''.join([chr(int(chunk, 8)) for chunk in self._chunk_string(input_text, 3)])

    def _chunk_string(self, string: str, length: int) -> List[str]:
        return [string[0 + i:length + i] for i in range(0, len(string), length)]