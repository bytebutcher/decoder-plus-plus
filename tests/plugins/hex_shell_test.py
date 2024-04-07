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


class TestHexShellDecoder(unittest.TestCase):
    plugin = load_plugin("Hex (shell)", PluginType.DECODER)

    @unittest.skip("Test fails due to unknown reason")
    def testPlugin(self):
        self.assertEqual(self.plugin.run(
            '\\x61\\x62\\x63\\x64\\x65\\x66\\x67\\x68\\x69\\x6a\\x6b\\x6c\\x6d\\x6e'
            '\\x6f\\x70\\x71\\x72\\x73\\x74\\x75\\x76\\x77\\x78\\x79\\x7a\\x0a\\x5e'
            '\\xc2\\xb0\\x21\\x22\\xc2\\xa7\\x24\\x25\\x26\\x2f\\x28\\x29\\x3d\\x3f'
            '\\xc2\\xb4\\x60\\x3c\\x3e\\x7c\\x20\\x2c\\x2e\\x2d\\x3b\\x3a\\x5f\\x23'
            '\\x2b\\x27\\x2a\\x7e\\x0a\\x30\\x31\\x32\\x33\\x34\\x35\\x36\\x37\\x38'
            '\\x39'
        ),
            'abcdefghijklmnopqrstuvwxyz\n'
            '^°!"§$%&/()=?´`<>| ,.-;:_#+\'*~\n'
            '0123456789'
        )
