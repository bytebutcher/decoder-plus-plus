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
    Encodes a text using Base64.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            0ECJPC% CC3DVED5QDO$D/3EHFE QEA%ET4F3GF:D1PROM84GROSP4A$4L35JX7TROL7CL+7134V$5.L7A1CMK5XG5/C1*96DL6WW66:6C1
    """

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies
        super().__init__('BASE45', "Thomas Engel", ["base45"], context)

    def run(self, input_text: str) -> str:
        import base45
        return base45.b45encode(input_text.encode('utf-8', errors="surrogateescape")) \
            .decode('utf-8', errors="surrogateescape")
