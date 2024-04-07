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
import sys
import unittest

from qtpy.QtWidgets import QApplication
from qtpy.QtTest import QTest
from qtpy.QtCore import Qt

from dpp.core import Context
from dpp.core.plugin import PluginType
from dpp.ui.decoder_plus_plus_gui import DecoderPlusPlusWindow
from dpp.ui.view.classic import CodecTab
from dpp.ui.view.classic.codec_frames import CodecFrames
from tests.utils import load_plugins, load_plugin
from dpp import app_path

app = QApplication(sys.argv)


class TestClassicMode(unittest.TestCase):

    def setUp(self):
        """Create the GUI"""
        self.context = Context('net.bytebutcher.decoder_plus_plus', app_path)
        self.plugins = load_plugins()
        self.dpp = DecoderPlusPlusWindow(self.context, "")

    def setUpFrames(self) -> CodecFrames:
        idx, codec_tab = self.dpp.newTab("Hello, world!")
        codec_frames = codec_tab.frames()

        plugin = load_plugin("Base64", PluginType.ENCODER)
        codec_frames.frame(0).setPlugin(plugin, block_signals=False)

        plugin = load_plugin("Sha256", PluginType.HASHER)
        codec_frames.frame(1).setPlugin(plugin, block_signals=False)

        return codec_frames

    def testCodecFramesInitialization(self):
        idx, codec_tab = self.dpp.newTab("Hello, world!")
        self.assertIsInstance(codec_tab, CodecTab)
        codec_frames = codec_tab.frames()
        self.assertIsInstance(codec_frames, CodecFrames)
        self.assertEqual(codec_frames.count(), 1)
        self.assertEqual(codec_frames.frame(0).type(), "None")
        self.assertEqual(codec_frames.frame(0).getInputText(), "Hello, world!")
        self.assertEqual(codec_frames.frame(0).status(), ("DEFAULT", None))
        self.assertEqual(codec_frames.frame(0).getOutputText(), "")


    def assertFrame(self, frame, input_text, output_text, status, is_collapsed):
        self.assertEqual(frame.getInputText(), input_text)
        self.assertEqual(frame.getOutputText(), output_text)
        self.assertEqual(frame.status(), status)
        self.assertEqual(frame.isCollapsed(), is_collapsed)

    def testSetUp(self):
        idx, codec_tab = self.dpp.newTab("Hello, world!")
        codec_frames = codec_tab.frames()
        self.assertEqual(codec_frames.count(), 1)
        self.assertFrame(codec_frames.frame(0), "Hello, world!", "", ("DEFAULT", None), False)

        plugin = load_plugin("Base64", PluginType.ENCODER)
        codec_frames.frame(0).setPlugin(plugin, block_signals=False)
        self.assertEqual(codec_frames.count(), 2)
        self.assertFrame(codec_frames.frame(0), "Hello, world!", "SGVsbG8sIHdvcmxkIQ==", ("DEFAULT", None), False)
        self.assertFrame(codec_frames.frame(1), "SGVsbG8sIHdvcmxkIQ==", "", ("SUCCESS", None), False)

        plugin = load_plugin("Sha256", PluginType.HASHER)
        codec_frames.frame(1).setPlugin(plugin, block_signals=False)
        self.assertEqual(codec_frames.count(), 3)
        self.assertFrame(codec_frames.frame(0), "Hello, world!", "SGVsbG8sIHdvcmxkIQ==", ("DEFAULT", None), False)
        self.assertFrame(codec_frames.frame(1), "SGVsbG8sIHdvcmxkIQ==", "f978b1667208cc537def3f71a79f69475474d3f0bd2773f1f2428e73d31dc5ee", ("SUCCESS", None), True)
        self.assertFrame(codec_frames.frame(2), "f978b1667208cc537def3f71a79f69475474d3f0bd2773f1f2428e73d31dc5ee", "", ("SUCCESS", None), False)

    def testChangingCodecDoesExecuteAllCodecsBelow(self):
        # Changing Codec does not execute codecs below #61
        idx, codec_tab = self.dpp.newTab("Hello, world!")
        codec_frames = codec_tab.frames()
        plugin = load_plugin("Base64", PluginType.ENCODER)
        codec_frames.frame(0).setPlugin(plugin, block_signals=False)
        plugin = load_plugin("Base45", PluginType.ENCODER)
        codec_frames.frame(1).setPlugin(plugin, block_signals=False)
        self.assertEqual(codec_frames.count(), 3)
        self.assertFrame(codec_frames.frame(0), "Hello, world!", "SGVsbG8sIHdvcmxkIQ==", ("DEFAULT", None), False)
        self.assertFrame(codec_frames.frame(1), "SGVsbG8sIHdvcmxkIQ==", "YNA -A4JC667+B9NVCSPC2AF4C9HX7", ("SUCCESS", None), True)
        self.assertFrame(codec_frames.frame(2), "YNA -A4JC667+B9NVCSPC2AF4C9HX7", "", ("SUCCESS", None), False)
        plugin = load_plugin("Base45", PluginType.ENCODER)
        codec_frames.frame(0).setPlugin(plugin, block_signals=False)
        self.assertEqual(codec_frames.count(), 3)
        self.assertFrame(codec_frames.frame(0), "Hello, world!", "%69 VDK2EV4404ESVDX0", ("DEFAULT", None), False)
        self.assertFrame(codec_frames.frame(1), "%69 VDK2EV4404ESVDX0", "VV4:97Y+AZM9KY8:Q6A46HY8Y+AV6B", ("SUCCESS", None), True)
        self.assertFrame(codec_frames.frame(2), "VV4:97Y+AZM9KY8:Q6A46HY8Y+AV6B", "", ("SUCCESS", None), False)

    def testMoveCodecUp(self):
        """
        # Example:
        #
        #   1. "Hello, world" - Base64 - open
        #   2. "<base64> of hello world" - Sha256 - collapsed
        #   3. "<sha256> of base64 hello world" - <> - open
        #   4. Press up on Frame 3
        #
        #       Switching the codec of the previous frame with Frame 3 results in:
        #
        #       1. "Hello, world" - Sha256 - open
        #       2. "<sha256> of hello world" - Base64 - collapsed
        #       3. "<base64> of <sha256> of hello world" - open
        #
        #       Note that the text of the first frame is not touched. More precisely any frame which is in default
        #       state should not be touched. However, frames which contain an error can be overwritten.
        #
        """
        codec_frames = self.setUpFrames()

        def clickMoveUpButton(frame_index):
            QTest.mouseClick(codec_frames.frame(frame_index).getMoveUpButton().centralWidget(), Qt.LeftButton)

        def clickMoveDownButton(frame_index):
            QTest.mouseClick(codec_frames.frame(frame_index).getMoveDownButton().centralWidget(), Qt.LeftButton)

        # 1. "Hello, world" - Base64 - open
        idx, codec_tab = self.dpp.newTab("Hello, world!")
        codec_frames = codec_tab.frames()
        # 2. "<base64> of hello world" - Sha256 - collapsed
        plugin = load_plugin("Base64", PluginType.ENCODER)
        codec_frames.frame(0).setPlugin(plugin, block_signals=False)
        # 3. "<sha256> of base64 hello world" - <> - open
        plugin = load_plugin("Sha256", PluginType.HASHER)
        codec_frames.frame(1).setPlugin(plugin, block_signals=False)
        # Assert precondition
        self.assertFrame(codec_frames.frame(0), "Hello, world!", "SGVsbG8sIHdvcmxkIQ==", ("DEFAULT", None), False)
        self.assertFrame(codec_frames.frame(1), "SGVsbG8sIHdvcmxkIQ==", "f978b1667208cc537def3f71a79f69475474d3f0bd2773f1f2428e73d31dc5ee", ("SUCCESS", None), True)
        self.assertFrame(codec_frames.frame(2), "f978b1667208cc537def3f71a79f69475474d3f0bd2773f1f2428e73d31dc5ee", "", ("SUCCESS", None), False)

        # 4. Press up on Frame 3
        clickMoveUpButton(2)
        self.assertEqual(codec_frames.count(), 3)
        self.assertFrame(codec_frames.frame(0), "Hello, world!", "315f5bdb76d078c43b8ac0064e4a0164612b1fce77c869345bfc94c75894edd3", ("DEFAULT", None), False)
        self.assertFrame(codec_frames.frame(1), "315f5bdb76d078c43b8ac0064e4a0164612b1fce77c869345bfc94c75894edd3", "MzE1ZjViZGI3NmQwNzhjNDNiOGFjMDA2NGU0YTAxNjQ2MTJiMWZjZTc3Yzg2OTM0NWJmYzk0Yzc1ODk0ZWRkMw==", ("SUCCESS", None), True)
        self.assertFrame(codec_frames.frame(2), "MzE1ZjViZGI3NmQwNzhjNDNiOGFjMDA2NGU0YTAxNjQ2MTJiMWZjZTc3Yzg2OTM0NWJmYzk0Yzc1ODk0ZWRkMw==", "", ("SUCCESS", None), False)

    def testMoveCodecDown(self):
        """
        # Example:
        #
        #   1. "Hello, world" - Base64 - open
        #   2. "<base64> of hello world" - Sha256 - collapsed
        #   3. "<sha256> of base64 hello world" - <> - open
        #
        #   Case 1. Press down on Frame 1
        #
        #       First frame can not be moved.
        #
        #   Case 2. Press down on Frame 2
        #
        #       Switching the codec of the previous frame with Frame 2 results in:
        #
        #       1. "Hello, world" - Sha256 - open
        #       2. "<sha256> of hello world" - Base64 - collapsed
        #       3. "<base64> of <sha256> of hello world" - open
        #
        #       Note that the text of the first frame is not touched. More precisely any frame which is in default
        #       state should not be touched. However, frames which contain an error can be overwritten.
        #
        #   Case 3. Press down on Frame 3
        #
        #       Last frame can not be moved.
        #
        """
        ...

    def testRefreshCodec(self):
        """
        # Example:
        #
        #   1. "Hello, world" - Base64 - open
        #   2. "<base64> of hello world" - Sha256 - collapsed
        #   3. "<sha256> of base64 hello world" - <> - open
        #   4. Change the text of frame two
        #   - this should change state of frame two from success to default
        #   - this should change content of frame three
        #   5. Press refresh button of frame two
        #   - this should change state of frame two back to success
        #   - this should change content of frame two back to initial value
        #   - this should change content of frame three back to initial value
        """
        ...

    def testCloseCodec(self):
        ...
