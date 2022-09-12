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
    Hashes a string using KECCAK 512.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            e7eb5bc85e3d05ccab9863189ce1a34ef2a3feda8ce633b690dd133242a43e90 \
            44bd36c27cb30d66a5eef8b4cb917c609f6983e2c2b8625c0aedb3f87f364172
    """

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies
        super().__init__('KECCAK 512', "Thomas Engel", ["pycryptodome"], context)

    def run(self, input_text: str) -> str:
        from Crypto.Hash import keccak
        return keccak.new(digest_bits=512, data=input_text.encode('utf-8', errors='surrogateescape')).hexdigest()
