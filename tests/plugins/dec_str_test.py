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


class TestDecStrDecoder(unittest.TestCase):
    plugin = load_plugin("Dec (str)", PluginType.DECODER)

    def testPlugin(self):
        self.assertEqual(self.plugin.run(
            '97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,'
            '112,113,114,115,116,117,118,119,120,121,122,10,94,176,33,'
            '34,167,36,37,38,47,40,41,61,63,180,96,60,62,124,32,44,46,'
            '45,59,58,95,35,43,39,42,126,10,48,49,50,51,52,53,54,55,56,57'
        ),
            'abcdefghijklmnopqrstuvwxyz\n'
            '^°!"§$%&/()=?´`<>| ,.-;:_#+\'*~\n'
            '0123456789'
        )
