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
from typing import List, Tuple, Dict

from qtpy.QtWidgets import QDialog, QFrame, QVBoxLayout

from dpp.core.logger import logmethod
from dpp.core.plugin import AbstractPlugin
from dpp.ui.dialog.plugin_config_dialog import PluginConfigDialog
from dpp.ui.view.classic.codec_frame import CodecFrame
from dpp.ui.widget.status_widget import StatusWidget


class CodecFrames(QFrame):

    def __init__(self, parent, context, tab_id, plugins):
        super(__class__, self).__init__(parent)
        self._context = context
        self._tab_id = tab_id
        self._plugins = plugins
        self._frames_layout = QVBoxLayout()
        self.setLayout(self._frames_layout)
        self._frames_layout.setContentsMargins(0, 0, 0, 0)
        self._focused_frame = None

    # ------------------------------------------------------------------------------------------------------------------
    # Private helper functions
    # ------------------------------------------------------------------------------------------------------------------

    @logmethod()
    def _configure_plugin(self, frame_id, input_text, plugin) -> bool:
        if plugin.is_configurable():
            if PluginConfigDialog(self._context, plugin, input_text).exec_() != QDialog.Accepted:
                # User clicked the cancel-button within the plugin config dialog.
                # BUG: Item gets selected although dialog was canceled.
                # FIX: Reselect last item prior to current selection.
                self.getFrameById(frame_id).getComboBoxes().reselectLastItem(block_signals=True)
                return False
        return True

    @logmethod()
    def _run_plugin(self, frame: CodecFrame) -> Tuple[str, str, str]:
        """
        Runs the plugin using the input text on the frame.
        @param frame: the frame to run.
        @return: the new CodecFrame or None if plugin configuration failed.
        """
        output = ""
        error = None
        plugin = frame.getPlugin()
        try:
            if frame.hasTextSelected():
                start_text, input_text, end_text = frame.getSelectedText()
                output = start_text + plugin.run(input_text) + end_text
            else:
                input_text = frame.getInputText()
                output = plugin.run(input_text)
            status = StatusWidget.SUCCESS
        except BaseException as err:
            status = StatusWidget.ERROR
            error = str(err)
            self._context.logger.error(f'{plugin.name} {plugin.type}: {error}')
            self._context.logger.debug(str(err), exc_info=True)
        return output, status, error

    @logmethod()
    def _refill_frame(self, text, title, frame_index, status, msg=None):
        if status == StatusWidget.ERROR:
            # ERROR usually indicates that codec execution failed and there is no text to display.
            # However, we indicate to the user that there is an error (setStatus) for this frame and any
            # following frame.
            frame = self.getFrameByIndex(frame_index)
            while frame_index < self.getFramesCount():
                _frame = self.getFrameByIndex(frame_index)
                _frame.setStatus(status, msg)
                _frame.header().refresh()
                # Display error only for the first frame.
                msg = None
                frame_index = frame_index + 1
        else:
            frame = self.getFrameByIndex(frame_index)
            frame.setInputText(text)
            frame.header().refresh()
            frame.setStatus(status, msg)

        return frame

    @logmethod()
    def _deselect_plugin(self, frame_id: str):
        """ When the first combo box entry gets selected all further frames are going to be removed. """
        _frame_index = self.getFrameIndex(frame_id)
        self._context.logger.debug(f'Reset frames after index {_frame_index} up until {self.getFramesCount() - 1}')
        for frame_index in range(self.getFramesCount() - 1, _frame_index, -1):
            self._context.logger.debug(f'Reset frame with index {frame_index}')
            self.getFrameByIndex(frame_index).deleteLater()

    @logmethod()
    def _new_frame(self, frame: CodecFrame) -> CodecFrame:
        plugin = frame.getPlugin()
        output, status, error = self._run_plugin(frame)
        new_frame_index = frame.getFrameIndex() + 1
        return self.newFrame(output, plugin.title, new_frame_index, status=status, msg=error)

    @logmethod()
    def _update_frames(self, frame_id, is_user_action=True, do_preserve_state=False):
        """
        Updates all frames starting from the given frame_id.
        @param frame_id: the frame id to start updating from.
        @param is_user_action: defines whether the update was triggered by a user action.
                               If True, the method marks the starting frame with a "DEFAULT" status to denote
                               that the user has modified the input. Defaults to True.
        @param do_preserve_state: defines whether the state of the frame should be preserved or not.
        """
        frame_index = self.getFrameIndex(frame_id)
        frame = self.getFrameById(frame_id)
        if is_user_action:
            frame.setStatus(StatusWidget.DEFAULT, '')
        while frame:
            if do_preserve_state and self.hasNextFrame(frame_index) and \
                    self.getFrameByIndex(frame_index + 1).status() == StatusWidget.DEFAULT:
                # Do not overwrite content of frames which are in default-state.
                # Usually done when moving frames to a new position whereby custom user-input should not be
                # overwritten.
                frame = self.getFrameByIndex(frame_index + 1)
                continue

            frame.header().refresh()
            plugin = frame.getPlugin()
            if not plugin.is_runnable():
                break

            frame = self._update_frame(frame)

    @logmethod()
    def _replace_input_text(self, input_text: str, replacements: Dict[str, Tuple[str, str, str]]) -> str:
        """
        Replaces text at the specified positions in the input text.
        @param input_text: a string.
        @param replacements: a dictionary of tuples. key contains the starting index, value/tuple contains the
                             starting position (duplicate), ending position and replacement text.
        @return: The output text with the specified replacements.
        """
        output_text = []
        end_index = -1
        for index, element in enumerate(input_text):
            if index in replacements:
                start_index, end_index, replacement_text = replacements[index]
                output_text.extend(list(replacement_text))
                continue
            if index >= end_index:
                output_text.append(element)
        return ''.join(output_text)

    @logmethod()
    def _switch_frames(self, index1, index2):
        frame1 = self.getFrameByIndex(index1)
        plugin1 = frame1.getPlugin()
        frame2 = self.getFrameByIndex(index2)
        plugin2 = frame2.getPlugin()
        frame2.setPlugin(plugin1)
        frame1.setPlugin(plugin2)

    @logmethod()
    def _update_frame(self, frame: CodecFrame) -> CodecFrame:
        plugin = frame.getPlugin()
        output, status, error = self._run_plugin(frame)
        new_frame_index = frame.getFrameIndex() + 1
        return self.newFrame(output, plugin.title, new_frame_index, status=status, msg=error)

    # ------------------------------------------------------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------------------------------------------------------

    @logmethod()
    def _on_plugin_selected(self, frame_id: str, plugin: AbstractPlugin):
        if plugin:
            frame = self.getFrameById(frame_id)
            if not self._configure_plugin(frame_id, frame.getInputText(), plugin):
                # Abort if user cancels configuration.
                return

            # Do only auto-collapse, when we are creating a new frame. But never auto-collapse the first frame.
            if frame.getFrameIndex() == self.getFramesCount() - 1 and frame.getFrameIndex() > 0:
                frame.setCollapsed(True)

            # Iteratively execute codecs starting with the current frame and continuing to the last frame,
            # stopping if any codec encounters a failure.
            self._update_frames(frame.id(), is_user_action=False)

            # Focus input text of next frame which is not collapsed.
            next_frame = frame
            while next_frame.hasNextFrame():
                next_frame: CodecFrame = next_frame.getNextFrame()
                if not next_frame.isCollapsed():
                    next_frame.focusInputText()
                    break
        else:
            self._deselect_plugin(frame_id)

    @logmethod()
    def _on_frame_close_button_clicked(self, frame_id):
        """ Closes/Removes the frame with the specified frame-id. """
        _frame_index = self.getFrameIndex(frame_id)
        self._context.logger.debug(f'Close frame {_frame_index}:{frame_id}')
        assert _frame_index > 0, 'Illegal operation! Can not close first or invalid frame!'
        frame = self.getFrameByIndex(_frame_index)
        previous_frame = self.getFrameByIndex(_frame_index - 1)

        if not self.hasNextFrame(_frame_index):
            # If this is the last frame the combo-boxes of the previous frame needs to reset.
            self.layout().removeWidget(frame)  # remove frame from layout to avoid side-effects with header refresh
            frame.deleteLater()
            previous_frame.getComboBoxes().resetAll()
            # Usability: Always show the content of the last frame.
            previous_frame.setCollapsed(False)
            # Update headings since some buttons may need to be en-/disabled.
            previous_frame.header().refresh()
        else:
            # Otherwise the selected plugin of the previous frame needs to be executed.
            next_frame = self.getFrameByIndex(_frame_index + 1)
            self.layout().removeWidget(frame)  # remove frame from layout to avoid side-effects with header refresh
            frame.deleteLater()
            self._update_frame(previous_frame)

            # Update headings since some buttons may need to be en-/disabled.
            next_frame.header().refresh()
            previous_frame.header().refresh()

    @logmethod()
    def _on_frame_refresh_button_clicked(self, frame_id: str):
        _frame_index = self.getFrameIndex(frame_id)
        self._context.logger.debug(f'Refreshing frame {_frame_index}:{frame_id}')
        self._update_frames(frame_id, is_user_action=False)

    @logmethod()
    def _on_frame_up_button_clicked(self, frame_id: str):
        # Example:
        #
        #   1. "Hello, world" - Base64 - open
        #   2. "<base64> of hello world" - Sha256 - collapsed
        #   3. "<sha256> of base64 hello world" - <> - open
        #
        #   Case 1. Press up on Frame 1
        #
        #       First frame can not be moved.
        #
        #   Case 2. Press down on Frame 2
        #
        #       Second frame can not be moved.
        #
        #   Case 3. Press down on Frame 3
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
        frame_index = self.getFrameIndex(frame_id)
        codec_frame = self.getFrameByIndex(frame_index)
        assert codec_frame and frame_index > 1, f'Illegal operation! moveFrameUp({frame_index}:{frame_id})'
        self._switch_frames(frame_index - 2, frame_index - 1)
        codec_frame = self.getFrameByIndex(frame_index - 2)
        self._update_frames(codec_frame.id(), is_user_action=False, do_preserve_state=True)

    @logmethod()
    def _on_frame_down_button_clicked(self, frame_id: str):
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
        frame_index = self.getFrameIndex(frame_id)
        codec_frame = self.getFrameByIndex(frame_index)
        assert codec_frame and frame_index > 0 or frame_index < self.getFramesCount() - 1, \
            f'Illegal operation! moveFrameDown({frame_index}:{frame_id}) with {self.getFramesCount()} frames'
        self._switch_frames(frame_index - 1, frame_index)
        codec_frame = self.getFrameByIndex(frame_index - 1)
        self._update_frames(codec_frame.id(), is_user_action=False, do_preserve_state=True)

    @logmethod()
    def _on_frame_config_button_clicked(self, frame_id: str):
        # Remember: We press the config-button of a frame, but want to show the plugin-config of the previous frame ...
        frame_index = self.getFrameIndex(frame_id)
        previous_frame = self.getFrameByIndex(frame_index - 1)
        if previous_frame:
            if not self._configure_plugin(frame_id, previous_frame.getInputText(), previous_frame.getPlugin()):
                # Abort if the user cancels the configuration
                return
            self._new_frame(previous_frame)

    # ------------------------------------------------------------------------------------------------------------------
    # Public functions
    # ------------------------------------------------------------------------------------------------------------------

    def getFrameIndex(self, frame_id) -> int:
        frame = None
        index = 0
        for current_frame in self.getFrames():
            if current_frame.getFrameId() == frame_id:
                frame = current_frame
                break
            index = index + 1
        return index if frame else -1

    def getFrameById(self, frame_id) -> CodecFrame:
        for frame in self.getFrames():
            if frame.id() == frame_id:
                return frame

    def getFrameByIndex(self, index) -> CodecFrame:
        if self.layout().itemAt(index):
            return self.layout().itemAt(index).widget()

    def getFramesCount(self) -> int:
        return self.layout().count()

    def getFocusedFrame(self) -> CodecFrame:
        widget = self.focusWidget()
        while widget:
            if isinstance(widget, CodecFrame):
                return widget
            widget = widget.parent()
        return self.layout().itemAt(0).widget()

    def getFrames(self) -> List[CodecFrame]:
        frames = []
        for frameIndex in range(0, self.layout().count()):
            frames.append(self.layout().itemAt(frameIndex).widget())
        return frames

    def hasNextFrame(self, frame_index: int, frame_id: str = None) -> bool:
        assert frame_index is not None or frame_id is not None, \
            'Illegal operation! Expected either frame_index or frame_id!'
        if frame_index is not None:
            return frame_index < (self.getFramesCount() - 1)
        if frame_id is not None:
            return self.hasNextFrame(frame_index=self.getFrameIndex(frame_id))

    def hasPreviousFrame(self, frame_index: int = None, frame_id: str = None) -> bool:
        assert frame_index is not None or frame_id is not None, \
            'Illegal operation! Expected either frame_index or frame_id!'
        if frame_index is not None:
            return frame_index > 0
        if frame_id is not None:
            return self.hasPreviousFrame(frame_index=self.getFrameIndex(frame_id))

    @logmethod()
    def newFrame(self, input_text: str, title: str, frame_index: int, status, msg=None) -> CodecFrame:
        if frame_index < self.getFramesCount():
            # if frame already exists, refill frame.
            return self._refill_frame(input_text, title, frame_index, status, msg)

        self._context.logger.debug(f'Adding new codec frame {title} at {frame_index} ...')
        previous_frame = self.getFrameByIndex(frame_index - 1)
        new_frame = CodecFrame(self, self._context, self._tab_id, self, self._plugins, input_text)
        self.layout().addWidget(new_frame)

        new_frame.pluginSelected.connect(self._on_plugin_selected)
        new_frame.configButtonClicked.connect(self._on_frame_config_button_clicked)
        new_frame.refreshButtonClicked.connect(self._on_frame_refresh_button_clicked)
        new_frame.upButtonClicked.connect(self._on_frame_up_button_clicked)
        new_frame.downButtonClicked.connect(self._on_frame_down_button_clicked)
        new_frame.closeButtonClicked.connect(self._on_frame_close_button_clicked)

        def on_text_selection_changed(tab_id, frame_id, input_text):
            if self._tab_id == tab_id:
                self._context.listener().textSelectionChanged.emit(tab_id, frame_id, input_text)

        new_frame.textSelectionChanged.connect(on_text_selection_changed)

        def selected_frame_changed(tab_id, frame_id, input_text):
            # Always remember the currently focused frame (e.g. used for finding the currently selected frame when
            # using keyboard-shortcuts)
            if self._tab_id == tab_id:
                self._focused_frame = self.getFrameById(frame_id)
                self._context.listener().selectedFrameChanged.emit(tab_id, frame_id, input_text)

        new_frame.selectedFrameChanged.connect(selected_frame_changed)

        def textChanged(tab_id, frame_id, text):
            if self._tab_id == tab_id:
                self._update_frames(frame_id)
                self._context.listener().textChanged.emit(tab_id, frame_id, text)

        new_frame.textChanged.connect(textChanged)
        if frame_index > 0:
            # Every new frame (except the first frame) should signal success/error.
            new_frame.setStatus(status, msg)

        def on_text_submitted(tab_id: str, frame_id: str, text: str):
            if tab_id == self._tab_id and frame_id == new_frame.id():
                new_frame.setInputText(text)

        self._context.listener().textSubmitted.connect(on_text_submitted)

        new_frame.setContentsMargins(0, 0, 0, 0)
        new_frame.layout().setContentsMargins(0, 0, 0, 0)
        new_frame.header().refresh()
        if previous_frame: previous_frame.header().refresh()
        return new_frame

    def frame(self, index: int) -> CodecFrame:
        return self.layout().itemAt(index).widget()

    def count(self) -> int:
        return self.layout().count()

    @logmethod()
    def toDict(self) -> List[dict]:
        return [frame.toDict() for frame in self.getFrames()]
