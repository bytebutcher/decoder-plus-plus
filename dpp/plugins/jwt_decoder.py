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
from dpp.core.plugin.config import Label
from dpp.core.plugin.config.options import String, ComboBox


class Plugin(DecoderPlugin):
    """
    Decodes JSON Web Tokens.

    Example:

        Input:
            eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzb21lIjoicGF5bG9hZCJ9.4twFt5NiznN84AWoo1d7KO1T_yoc0Z6XOpOVswacPZg

        Options:

            key: secret
            algorithm: HS256

        Output:
            {'some': 'payload'}
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
        self.config.add(ComboBox(
            label=Plugin.Option.Algorithm,
            value="HS256",
            values=[
                "HS256",
                "HS384",
                "HS512",
                "RS256",
                "RS384",
                "RS512",
                "ES256",
                "ES384",
                "ES512",
                "PS256",
                "PS384",
                "PS512",
            ],
            description="allowed algorithm",
            is_required=False,
            is_editable=True
        ))

    def run(self, input_text: str) -> str:
        import jwt
        parameters = {}
        if self.config.value(Plugin.Option.Key):
            parameters['key'] = self.config.value(Plugin.Option.Key)
        if self.config.value(Plugin.Option.Algorithm):
            parameters['algorithms'] = [self.config.value(Plugin.Option.Algorithm)]
        return str(jwt.decode(input_text.encode('utf-8', errors='surrogateescape'), verify=False, **parameters))

    def can_decode_input(self, input_text: str) -> bool:
        if input_text and input_text.startswith("ey"):
            try:
                self.run(input_text)
                return True
            except:
                return False
        return False
