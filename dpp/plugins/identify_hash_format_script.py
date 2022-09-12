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
from dpp.core.plugin import IdentifyPlugin


class Plugin(IdentifyPlugin):
    """
    Identifies the hash format of the input text based on structure.
    """

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies
        super().__init__('Identify Hash Format', "Thomas Engel", ["hashid"], context)

    def _detect_hash_format(self, input_text: str) -> str:
        from hashid import HashID
        return "\n".join(sorted([item.name for item in HashID().identifyHash(input_text)]))

    def run(self, input_text: str) -> str:
        return self._detect_hash_format(input_text)
