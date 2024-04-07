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


class TestBase64URL(unittest.TestCase):

    encoder = load_plugin("BASE64 (URL-safe)", PluginType.ENCODER)
    decoder = load_plugin("BASE64 (URL-safe)", PluginType.DECODER)

    def testEncoder(self):
        input_text = 'abcdefghijklmnopqrstuvwxyz'
        output_text = 'YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXo='
        self.assertEqual(self.encoder.run(
            input_text
        ),
            output_text
        )

    def testDecoder(self):
        input_text = 'YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXo='
        output_text = 'abcdefghijklmnopqrstuvwxyz'
        self.assertEqual(self.decoder.run(
            input_text
        ),
            output_text
        )
