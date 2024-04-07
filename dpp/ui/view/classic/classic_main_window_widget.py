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

from qtpy.QtWidgets import QFileDialog, QWidget

from dpp.core.logger import logmethod
from dpp.core.plugin import PluginType
from dpp.ui.view.classic import CodecTab
from dpp.ui.view.classic.codec_frame import CodecFrame
from dpp.ui.view.main_window_widget import MainWindowWidget, menu, MenuItem


class ClassicMainWindowWidget(MainWindowWidget):

    def __init__(self, parent, context: 'dpp.core.context.Context', input_text: str):
        super().__init__(parent, context, input_text)

    #############################################
    # Menu items
    #############################################

    def _init_menu_items(self):
        self._register_shortcuts('&File', [])
        self._register_shortcuts('&Edit', [
            [MenuItem.EDIT_PASTE, MenuItem.EDIT_COPY, MenuItem.EDIT_CUT],
            [MenuItem.TOGGLE_SEARCH_FIELD]
        ])
        self._register_shortcuts('&View', [])
        self._register_shortcuts("&Select", [
            [MenuItem.FOCUS_DECODER, MenuItem.FOCUS_ENCODER, MenuItem.FOCUS_HASHER, MenuItem.FOCUS_SCRIPT],
            [MenuItem.FOCUS_INPUT_TEXT, MenuItem.FOCUS_INPUT_TEXT_NEXT, MenuItem.FOCUS_INPUT_TEXT_PREVIOUS]
        ])
        self._register_shortcuts('&Tabs', [])
        self._register_shortcuts('&Help', [])
        super()._init_menu_items()

    @menu.register_menu_item(id=MenuItem.EDIT_CUT, text="C&ut", shortcut_key="Ctrl+X")
    def _cut_text_action(self):
        self._call_focused_frame(lambda focused_frame: focused_frame.cutSelectedInputText())

    @menu.register_menu_item(id=MenuItem.EDIT_COPY, text="&Copy", shortcut_key="Ctrl+C")
    def _copy_text_action(self):
        self._call_focused_frame(lambda focused_frame: focused_frame.copySelectedInputText())

    @menu.register_menu_item(id=MenuItem.EDIT_PASTE, text="&Paste", shortcut_key="Ctrl+V")
    def _paste_text_action(self):
        self._call_focused_frame(lambda focused_frame: focused_frame.pasteSelectedInputText())

    @menu.register_menu_item(id=MenuItem.TOGGLE_SEARCH_FIELD, text="Toggle &Search Field", shortcut_key="Ctrl+F")
    def _toggle_search_field_action(self):
        self._call_focused_frame(lambda focused_frame: focused_frame.toggleSearchField())

    @menu.register_menu_item(id=MenuItem.FOCUS_DECODER, text="Select &Decoder", shortcut_key="Alt+Shift+D")
    def _focus_decoder_action(self):
        self._call_focused_frame(lambda focused_frame: focused_frame.focusComboBox(PluginType.DECODER))

    @menu.register_menu_item(id=MenuItem.FOCUS_ENCODER, text="Select &Encoder", shortcut_key="Alt+Shift+E")
    def _focus_encoder_action(self):
        self._call_focused_frame(lambda focused_frame: focused_frame.focusComboBox(PluginType.ENCODER))

    @menu.register_menu_item(id=MenuItem.FOCUS_HASHER, text="Select &Hasher", shortcut_key="Alt+Shift+H")
    def _focus_hasher_action(self):
        self._call_focused_frame(lambda focused_frame: focused_frame.focusComboBox(PluginType.HASHER))

    @menu.register_menu_item(id=MenuItem.FOCUS_SCRIPT, text="Select &Script", shortcut_key="Alt+Shift+S")
    def _focus_script_action(self):
        self._call_focused_frame(lambda focused_frame: focused_frame.focusComboBox(PluginType.SCRIPT))

    @menu.register_menu_item(id=MenuItem.FOCUS_INPUT_TEXT, text="Select &Text Field", shortcut_key="Alt+Shift+I")
    def _select_text_field_action(self):
        self._call_focused_frame(lambda focused_frame: focused_frame.focusInputText())

    @menu.register_menu_item(id=MenuItem.FOCUS_INPUT_TEXT_NEXT, text="Select &Next Text Field", shortcut_key="Alt+Down")
    def _focus_next_input_text_action(self):
        focused_frame = self._get_focused_frame()
        if focused_frame and focused_frame.hasNextFrame():
            self._focus_input_text(focused_frame.getNextFrame())

    @menu.register_menu_item(id=MenuItem.FOCUS_INPUT_TEXT_PREVIOUS, text="Select &Previous Text Field",
                             shortcut_key="Alt+Up")
    def _focus_previous_input_text_action(self):
        focused_frame = self._get_focused_frame()
        if focused_frame and focused_frame.hasPreviousFrame():
            self._focus_input_text(focused_frame.getPreviousFrame())

    #############################################
    # Helper functions
    #############################################

    def _call_focused_frame(self, callback):
        focused_frame = self._get_focused_frame()
        if focused_frame:
            callback(focused_frame)

    def _get_focused_frame(self) -> CodecFrame:
        return self.tabsWidget().currentWidget().frames().getFocusedFrame()

    def _focus_input_text(self, future_frame: CodecFrame):
        focused_frame = self._get_focused_frame()
        # Only collapse if frame was not manually collapsed by user and is not first or last frame
        if not focused_frame.wasCollapseStateChangedByUser():
            is_first_or_last_frame = not focused_frame.hasPreviousFrame() or not focused_frame.hasNextFrame()
            if not is_first_or_last_frame:
                focused_frame.setCollapsed(True)

        future_frame.focusInputText()
        future_frame.setCollapsed(False)
        self.tabsWidget().currentWidget().ensureWidgetVisible(future_frame)

    #############################################
    # Connector functions
    #############################################

    @menu.register_menu_item(id=MenuItem.OPEN_FILE, text="&Open File...", shortcut_key="Ctrl+O")
    def _open_file_action(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open File')
        if not filename:
            return

        try:
            with open(filename) as f:
                save_file = json.loads(f.read())
                for tab_config in save_file:
                    index, tab = self.newTab(title=tab_config["name"])
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
                        frame.fromDict(frame_config, safe_mode=True)
                        frame_index = frame_index + 1
            self._context.logger.info("Successfully loaded {}!".format(filename))
        except Exception as e:
            self._context.logger.error("Unexpected error loading file. {}".format(e))

    @menu.register_menu_item(id=MenuItem.SAVE_AS_FILE, text="&Save As...", shortcut_key="Ctrl+S")
    def _save_as_file_action(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'Save As File')
        if not filename:
            return

        try:
            content = str(json.dumps(self.toDict(), default=lambda x: x.__dict__))
            with open(filename, "w") as f:
                f.write(content)
            self._context.logger.info("Successfully saved session in {}!".format(filename))
        except Exception as e:
            self._context.logger.error("Unexpected error saving file. {}".format(e))

    #############################################
    # Public functions
    #############################################

    @logmethod()
    def newTab(self, title: str = None, input_text: str = None, widget: QWidget = None) -> (int, QWidget):
        tab = CodecTab(self, self._context, self._plugins)
        tab.frames().getFocusedFrame().setInputText(input_text)
        # BUG: Input-text of newly added codec-tab is not focused correctly.
        # FIX: Refocus input-text.
        tab.frames().getFocusedFrame().focusInputText()
        return super().newTab(title, input_text, tab)

    @logmethod()
    def duplicateTab(self, title, src_tab):
        tab_index, dst_tab = self.newTab(title=title)
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

    @logmethod()
    def toDict(self):
        return [{
            "name": self.tabsWidget().tabBar().tabText(tabIndex),
            "frames": self.tabsWidget().tab(tabIndex).toDict()
        } for tabIndex in range(0, self.tabsWidget().tabCount())]
