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
from dpp.core.icons import Icon
from dpp.core.plugin import IdentifyPlugin


class Plugin(IdentifyPlugin):
    """
    Detects the file type of the input text based on magic bytes.
    """

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies
        super().__init__('Identify File Type (magika)', "Thomas Engel", ["magika"], context, icon=Icon.IDENTIFY_FORMAT)
        self._magika = None

    def _detect_file_type(self, input_text: str) -> str:
        if not self._magika:
            from magika import Magika
            self._magika = Magika()
        return self._magika.identify_bytes(str.encode(input_text)).output.ct_label

    def run(self, input_text: str) -> str:
        return self._detect_file_type(input_text)