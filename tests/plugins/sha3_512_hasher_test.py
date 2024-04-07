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


class TestSHA3_512Hasher(unittest.TestCase):

    plugin = load_plugin("SHA3 512", PluginType.HASHER)

    def testPlugin(self):
        self.assertEqual(self.plugin.run(
            'abcdefghijklmnopqrstuvwxyz\n'
            '^°!"§$%&/()=?´`<>| ,.-;:_#+\'*~\n'
            '0123456789'
        ),
            '82ca87f576cadb05d4c911f36c98ed2735f45cad359d6ef5f6d544f5a3210e3e'
            'cf080be15e539e23c15e2eb23054677d8a015ee56be2d9673c9f187d290906ed'
        )
