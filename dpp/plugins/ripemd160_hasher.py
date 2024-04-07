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
#
# Changelog:
#   2018-07-09 - Initial implementation by Tim Menapace using the hashlib library.
#   2024-04-06 - Replaced hashlib library with pycryptodome since the availability of RIPEMD160 in hashlib
#                is not guaranteed and depends on the SSL library used on the platform.
#
from dpp.core.plugin import HasherPlugin


class Plugin(HasherPlugin):
    """
    Hashes a string using RIPEMD160.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            1b63bae30eb8be665459c3f2021293811ac2d63b
    """

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies
        super().__init__('RIPEMD160', "Tim Menapace", ["pycryptodome"], context)

    def run(self, input_text: str) -> str:
        from Crypto.Hash import RIPEMD160
        return RIPEMD160.new(input_text.encode('utf-8', errors='surrogateescape')).hexdigest()
