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
    Decodes JSON Web Tokens.

    Example:

        Input:
            eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzb21lIjoicGF5bG9hZCJ9.4twFt5NiznN84AWoo1d7KO1T_yoc0Z6XOpOVswacPZg

        Output:
            {'some': 'payload'}
    """

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies
        super().__init__('JWT', "Thomas Engel", ["jwt"], context)

    def run(self, input_text: str) -> str:
        import jwt
        return str(jwt.decode(input_text.encode('utf-8', errors='surrogateescape'), verify=False))

    def can_decode_input(self, input_text: str) -> bool:
        if input_text and input_text.startswith("ey"):
            try:
                self.run(input_text)
                return True
            except:
                return False
        return False
