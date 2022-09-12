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
from dpp.core.plugin import ScriptPlugin


class Plugin(ScriptPlugin):
    """
    Transforms a hex string from little to big endian vice versa.

    Example:

        Input:
            0002000A

        Output:
            0A000200
    """

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies
        super().__init__('Little/Big Endian', "Thomas Engel", [], context)

    @property
    def title(self):
        return "Little/Big Endian Transform"

    def run(self, input_text: str) -> str:
        return ''.join(list(reversed(self._chunk_string(input_text, 2))))

    def _chunk_string(self, string, length):
        return [string[0 + i:length + i] for i in range(0, len(string), length)]