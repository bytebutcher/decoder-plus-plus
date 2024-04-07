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
import unittest

from dpp.core.plugin import PluginType
from tests.utils import load_plugin


class TestURLPlusDecoder(unittest.TestCase):
    plugin = load_plugin("URL+", PluginType.DECODER)

    def testPlugin(self):
        self.assertEqual(self.plugin.run(
            'abcdefghijklmnopqrstuvwxyz'
            '%0A%5E%C2%B0%21%22%C2%A7%24%25%26/%28%29%3D%3F%C2%B4%60%3C%3E%7C+%2C.-%3B%3A_%23%2B%27%2A%7E%0A'
            '0123456789'
        ),
            'abcdefghijklmnopqrstuvwxyz\n'
            '^°!"§$%&/()=?´`<>| ,.-;:_#+\'*~\n'
            '0123456789'
        )
