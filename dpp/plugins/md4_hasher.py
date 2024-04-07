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
from dpp.core.plugin import HasherPlugin


class Plugin(HasherPlugin):
    """
    Hashes a string using MD4.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            872e3f347295c197822d6dc7a6bbb94e
    """

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies
        super().__init__('MD4', "Thomas Engel", ["pycryptodome"], context)

    def run(self, input_text: str) -> str:
        from Crypto.Hash import MD4
        return MD4.new(input_text.encode('utf-8', errors='surrogateescape')).hexdigest()
