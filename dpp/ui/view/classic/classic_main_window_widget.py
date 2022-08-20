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
#
import json

from qtpy.QtWidgets import QMenu

from dpp.core import Context
from dpp.core.plugin import PluginType
from dpp.ui.view.classic import CodecTab
from dpp.ui.view.classic.codec_frame import CodecFrame
from dpp.ui.view.main_window_widget import MainWindowWidget


class ClassicMainWindowWidget(MainWindowWidget):

    def __init__(self, parent, context: 'dpp.core.context.Context', input: str):
        super().__init__(parent, context)
        self.tabsWidget().onTabAddButtonClick.connect(self._new_codec_tab)
        self.tabsWidget().onTabDuplicateButtonClick.connect(self._tab_duplicate)
        self._new_codec_tab(input=input)

    def _new_codec_tab(self, title: str = None, input: str = None) -> (int, CodecTab):
        tab = CodecTab(self, self._context, self._plugins)
        tab.frames().getFocusedFrame().setInputText(input)
        # BUG: Input-text of newly added codec-tab is not focused correctly.
        # FIX: Refocus input-text.
        tab.frames().getFocusedFrame().focusInputText()
        return self.newTab(tab, title, input)

    def _open_file(self) -> str:
        filename = super()._open_file()
        if filename:
            try:
                with open(filename) as f:
                    save_file = json.loads(f.read())
                    for tab_config in save_file:
                        index, tab = self._new_codec_tab(title=tab_config["name"])
                        frame_index = 0
                        for frame_config in tab_config["frames"]:
                            if frame_index == 0:
                                # New tabs already contain one empty frame
                                frame = tab.frames().getFrames()[0]
                                frame.setInputText(frame_config["text"])
                                frame.setStatus(frame_config["status"]["type"], frame_config["status"]["message"])
                            else:
                                frame = tab.frames().newFrame(frame_config["text"],
                                                              frame_config["title"],
                                                              frame_index,
                                                              frame_config["status"]["type"],
                                                              frame_config["status"]["message"])
                            frame.fromDict(frame_config)
                            frame_index = frame_index + 1
                self._context.logger().info("Successfully loaded {}!".format(filename))
            except Exception as e:
                self._context.logger().error("Unexpected error loading file. {}".format(e))

    def _save_as_file(self) -> str:
        filename = super()._save_as_file()
        if filename:
            try:
                self._context.saveAsFile(filename, str(json.dumps(self.toDict(), default=lambda x: x.__dict__)))
                self._context.logger().info("Successfully saved session in {}!".format(filename))
            except Exception as e:
                self._context.logger().error("Unexpected error saving file. {}".format(e))

    def _tab_duplicate(self, title, src_tab):
        tab_index, dst_tab = self._new_codec_tab(title=title)
        frame_index = 0
        for src_frame in src_tab.frames().getFrames():
            status_type, status_message = src_frame.status()
            if frame_index == 0:
                # New tabs already contain one empty frame
                frame = dst_tab.frames().getFrames()[0]
                frame.setInputText(src_frame.getInputText())
                frame.setStatus(status_type, status_message)
            else:
                dst_tab.frames().newFrame(src_frame.getInputText(),
                                          src_frame.title(),
                                          frame_index,
                                          status_type,
                                          status_message)
            dst_tab.frames().getFrameByIndex(frame_index).fromDict(src_frame.toDict())
            frame_index = frame_index + 1

    def _init_edit_menu(self) -> QMenu:
        edit_menu = super()._init_edit_menu()
        self._register_shortcut(Context.Shortcut.EDIT_CUT,
                                "C&ut",
                                "Ctrl+X",
                                lambda: self._call_focused_frame(
                                    lambda focused_frame: focused_frame.cutSelectedInputText()),
                                edit_menu)
        self._register_shortcut(Context.Shortcut.EDIT_COPY,
                                "&Copy",
                                "Ctrl+C",
                                lambda: self._call_focused_frame(
                                    lambda focused_frame: focused_frame.copySelectedInputText()),
                                edit_menu)
        self._register_shortcut(Context.Shortcut.EDIT_PASTE,
                                "&Paste",
                                "Ctrl+P",
                                lambda: self._call_focused_frame(
                                    lambda focused_frame: focused_frame.pasteSelectedInputText()),
                                edit_menu)
        edit_menu.addSeparator()
        self._register_shortcut(Context.Shortcut.TOGGLE_SEARCH_FIELD,
                                "Toggle &Search Field",
                                "Ctrl+F",
                                lambda: self._call_focused_frame(
                                    lambda focused_frame: focused_frame.toggleSearchField()),
                                edit_menu)
        return edit_menu

    def _init_select_menu(self):
        select_menu = super()._init_select_menu()
        # self._register_shortcut(Context.Shortcut.FOCUS_CODEC_SEARCH,
        #                        "Select Codec Search",
        #                        "Ctrl+Space",
        #                        lambda: self._tabs.focusCodecSearch(),
        #                        select_menu)
        self._register_shortcut(Context.Shortcut.FOCUS_DECODER,
                                "Select &Decoder",
                                "Alt+Shift+D",
                                lambda: self._call_focused_frame(
                                    lambda focused_frame: focused_frame.focusComboBox(PluginType.DECODER)),
                                select_menu)
        self._register_shortcut(Context.Shortcut.FOCUS_ENCODER,
                                "Select &Encoder",
                                "Alt+Shift+E",
                                lambda: self._call_focused_frame(
                                    lambda focused_frame: focused_frame.focusComboBox(PluginType.ENCODER)),
                                select_menu)
        self._register_shortcut(Context.Shortcut.FOCUS_HASHER,
                                "Select &Hasher",
                                "Alt+Shift+H",
                                lambda: self._call_focused_frame(
                                    lambda focused_frame: focused_frame.focusComboBox(PluginType.HASHER)),
                                select_menu)
        self._register_shortcut(Context.Shortcut.FOCUS_SCRIPT,
                                "Select &Script",
                                "Alt+Shift+S",
                                lambda: self._call_focused_frame(
                                    lambda focused_frame: focused_frame.focusComboBox(PluginType.SCRIPT)),
                                select_menu)

        select_menu.addSeparator()

        self._register_shortcut(Context.Shortcut.FOCUS_INPUT_TEXT,
                                "Select &Text Field",
                                "Alt+Shift+I",
                                lambda: self._call_focused_frame(lambda focused_frame: focused_frame.focusInputText()),
                                select_menu)
        self._register_shortcut(Context.Shortcut.FOCUS_INPUT_TEXT_NEXT,
                                "Select &Next Text Field",
                                "Alt+Down",
                                lambda: self._focus_input_text(lambda frame: frame.getNextFrame()),
                                select_menu)
        self._register_shortcut(Context.Shortcut.FOCUS_INPUT_TEXT_PREVIOUS,
                                "Select &Previous Text Field",
                                "Alt+Up",
                                lambda: self._focus_input_text(lambda frame: frame.getPreviousFrame()),
                                select_menu)
        return select_menu

    def _call_focused_frame(self, callback):
        focused_frame = self._get_focused_frame()
        if focused_frame:
            callback(focused_frame)

    def _get_focused_frame(self) -> CodecFrame:
        return self.tabsWidget().currentWidget().frames().getFocusedFrame()

    def _focus_input_text(self, callback):
        frame = self._get_focused_frame()
        if frame:
            future_frame = callback(frame) or frame
            future_frame.focusInputText()
            # Collapse/Uncollapse frames automatically.
            if self.tabsWidget().currentWidget().frames().getFramesCount() > 2:
                if frame != future_frame:
                    if future_frame.isCollapsed():
                        if future_frame.hasPreviousFrame():
                            # Toggle frame, except the first frame which does not have a header
                            future_frame.toggleCollapsed()
                    if not frame.wasCollapseStateChangedByUser():
                        if frame.hasPreviousFrame():
                            # Collapse frame, except the first frame which does not have a header
                            frame.toggleCollapsed()

            self.tabsWidget().currentWidget().ensureWidgetVisible(future_frame)

    def toDict(self):
        return [{
            "name": self.tabsWidget().tabBar().tabText(tabIndex),
            "frames": self.tabsWidget().tab(tabIndex).toDict()
        } for tabIndex in range(0, self.tabsWidget().tabCount())]
