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
import re

from dpp.core.plugin import DecoderPlugin


class Plugin(DecoderPlugin):
    """
    Decodes a Base32 string.

    Example:

        Input:
            MFRGGZDFMZTWQ2LKNNWG23TPOBYXE43UOV3HO6DZPIFF5Q \\
            VQEERMFJZEEUTC6KBJHU74FNDAHQ7HYIBMFYWTWOS7EMVS \\
            OKT6BIYDCMRTGQ2TMNZYHE======

        Output:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789
    """

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies
        super().__init__('BASE32', "Thomas Engel", ["base64"], context)

    def run(self, input_text) -> str:
        import base64
        return base64.b32decode(input_text.encode('utf-8', errors='surrogateescape')) \
            .decode('utf-8', errors='surrogateescape')

    def can_decode_input(self, input_text: str) -> bool:
        if len(input_text) % 4 == 0:
            if re.search(r'^(?:[A-Z2-7]{8})*(?:[A-Z2-7]{2}={6}|[A-Z2-7]{4}={4}|[A-Z2-7]{5}={3}|[A-Z2-7]{7}=)?$',
                         input_text):
                return True
        return False
