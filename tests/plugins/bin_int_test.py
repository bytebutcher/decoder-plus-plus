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


class TestBinInt(unittest.TestCase):

    encoder = load_plugin("Bin (int)", PluginType.ENCODER)
    decoder = load_plugin("Bin (int)", PluginType.DECODER)

    def testEncoder(self):
        self.assertEqual(self.encoder.run(
            '123456789'
        ), '111010110111100110100010101')

    def testDecoder(self):
        self.assertEqual(self.decoder.run(
            '111010110111100110100010101'
        ), '123456789')
