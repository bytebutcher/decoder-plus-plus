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
from dpp.core.plugin.config import Label
from dpp.core.plugin.config.options import String


class Plugin(EncoderPlugin):
    """
    Encodes JSON Web Tokens.

    Example:

        Input:
            {"some": "payload"}

        Options:

            key: secret
            algorithm: HS256

        Output:
            eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzb21lIjoicGF5bG9hZCJ9.4twFt5NiznN84AWoo1d7KO1T_yoc0Z6XOpOVswacPZg
    """

    class Option(object):
        Key = Label("key", "Key")
        Algorithm = Label("algorithm", "Algorithm")

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies
        super().__init__('JWT', "Thomas Engel", ["jwt"], context)
        self.config.add(String(
            label=Plugin.Option.Key,
            value="",
            description="the key suitable for the allowed algorithm",
            is_required=False
        ))
        self.config.add(String(
            label=Plugin.Option.Algorithm,
            value="",
            description="allowed algorithm",
            is_required=False
        ))

    def run(self, input_text: str) -> str:
        import jwt
        import json
        payload = json.loads(input_text.encode('utf-8', errors='surrogateescape'))
        parameters = {}
        if self.config.value(Plugin.Option.Key):
            parameters['key'] = self.config.value(Plugin.Option.Key)
        if self.config.value(Plugin.Option.Algorithm):
            parameters['algorithm'] = self.config.value(Plugin.Option.Algorithm)
        return str(jwt.encode(payload, **parameters))

