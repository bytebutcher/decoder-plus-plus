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


class TestBase32Encoder(unittest.TestCase):
    encoder = load_plugin("Base32", PluginType.ENCODER)
    decoder = load_plugin("Base32", PluginType.DECODER)

    def testEncoder(self):
        input_text = 'abcdefghijklmnopqrstuvwxyz\n^°!"§$%&/()=?´`<>| ,.-;:_#+\'*~\n0123456789'
        output_text = 'MFRGGZDFMZTWQ2LKNNWG23TPOBYXE43UOV3HO6DZPIFF5QVQEERMFJZEEUTC6KBJHU74FNDAHQ7HYIBMFYWTWOS7EMVSOKT6BIYDCMRTGQ2TMNZYHE======'

        self.assertEqual(self.encoder.run(
            input_text
        ), output_text)


    def testDecoder(self):
        input_text = 'MFRGGZDFMZTWQ2LKNNWG23TPOBYXE43UOV3HO6DZPIFF5QVQEERMFJZEEUTC6KBJHU74FNDAHQ7HYIBMFYWTWOS7EMVSOKT6BIYDCMRTGQ2TMNZYHE======'
        output_text = 'abcdefghijklmnopqrstuvwxyz\n^°!"§$%&/()=?´`<>| ,.-;:_#+\'*~\n0123456789'

        self.assertEqual(self.decoder.run(
            input_text
        ), output_text)
