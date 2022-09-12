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
    """ Transforms valid JSON- into XML-structure. """

    def __init__(self, context: 'core.context.Context'):
        # Name, Author, Dependencies
        super().__init__('JS to XML', "Thomas Engel", ["json2xml"], context)

    def run(self, input_text: str) -> str:
        from json2xml import json2xml, readfromstring
        return json2xml.Json2xml(readfromstring(input_text)).to_xml()
