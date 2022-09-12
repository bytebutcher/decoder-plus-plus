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


class Plugin(EncoderPlugin):
    """
    Encodes a string using Base16.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            6162636465666768696A6B6C6D6E6F70717273747576777 \\
            8797A0A5EC2B02122C2A72425262F28293D3FC2B4603C3E \\
            7C202C2E2D3B3A5F232B272A7E0A30313233343536373839
    """

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies
        super().__init__('BASE16', "Thomas Engel", ["base64"], context)

    def run(self, input_text) -> str:
        import base64
        return base64.b16encode(input_text.encode('utf-8', errors='surrogateescape'))\
            .decode('utf-8', errors='surrogateescape')
