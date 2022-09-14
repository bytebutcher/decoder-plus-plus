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
from typing import List

from qtpy.QtWidgets import QDialog, QFrame, QVBoxLayout

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
        self._init_listener(context)
        self._focused_frame = None

    # ------------------------------------------------------------------------------------------------------------------

    def _init_listener(self, context):
        self._listener = context.listener()

        def selected_frame_changed(tab_id, frame_id, input_text):
            # Always remember the currently focused frame (e.g. used for finding the currently selected frame when
            # using keyboard-shortcuts)
            if self._tab_id == tab_id:
                self._focused_frame = self.getFrameById(frame_id)

        self._listener.selectedFrameChanged.connect(selected_frame_changed)
        self._listener.textChanged.connect(lambda tab_id, frame_id, text, interactive:
            self._tab_id == tab_id and self._text_changed_event(frame_id, text, interactive))

    # ------------------------------------------------------------------------------------------------------------------

    def _text_changed_event(self, frame_id, text, is_user_action=True, do_preserve_state=False):
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

            input_text = frame.getInputText()
            frame.header().refresh()
            plugin = frame._combo_box_frame.selectedPlugin()
            if not plugin.is_runnable():
                break

            frame = self._execute_plugin_run(frame.id(), input_text, plugin)

    def _on_plugin_selected(self, frame_id: str, input_text: str,
                            combo_box_type: str, combo_box_index: int, plugin: AbstractPlugin):
        frame = self.getFrameById(frame_id)
        if self._show_plugin_config(frame_id, input_text, plugin) != QDialog.Accepted:
            # User clicked the cancel-button within the plugin config dialog.
            # BUG: Item gets selected although dialog was canceled.
            # FIX: Reselect last item prior to current selection.
            frame.getComboBoxes().reselectLastItem(block_signals=True)
        else:
            # BUG: Item gets deselected when running dialogs.
            # FIX: Reselect Item
            frame.getComboBoxes().reselectItem(combo_box_index, combo_box_type)

        # ------------------------------------------------------------------------------------------------------------------

    def _execute_plugin_run(self, frame_id, input_text, plugin) -> CodecFrame:
        frame_index = self.getFrameIndex(frame_id) + 1
        output_text = ""
        status = StatusWidget.SUCCESS
        error = None
        try:
            output_text = plugin.run(input_text)
        except BaseException as e:
            status = StatusWidget.ERROR
            error = str(e)
            self._context.logger.error('{} {}: {}'.format(plugin.name, plugin.type, error))

        return self.newFrame(output_text, plugin.title, frame_index, status=status, msg=error)

    def _show_plugin_config(self, frame_id, input_text, plugin) -> int:
        new_frame_index = self.getFrameIndex(frame_id) + 1
        output = ""
        error = None
        try:
            if plugin.is_configurable():
                result = PluginConfigDialog(self._context, plugin, input_text).exec_()
                if result != QDialog.Accepted:
                    return result
            output = plugin.run(input_text)
            status = StatusWidget.SUCCESS
        except BaseException as err:
            status = StatusWidget.ERROR
            self._context.logger.error(f'{plugin.name} {plugin.type}: {str(err)}')
            self._context.logger.debug(str(err), exc_info=True)

        self.newFrame(output, plugin.title, new_frame_index, status=status, msg=error).focusInputText()
        return QDialog.Accepted

    def _refill_frame(self, text, title, frame_index, status, msg=None):
        self._context.logger.trace(f'Refill frame at index {frame_index}')
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
            # Display status and insert text into frame when there was no error.
            # Note that setInputText may result into another call to newFrame with frame_index + 1.
            frame = self.getFrameByIndex(frame_index)
            frame.setInputText(text)
            frame.header().refresh()
            frame.setStatus(status, msg)

        return frame

    def _on_plugin_deselected(self, frame_id):
        _frame_index = self.getFrameIndex(frame_id)
        self._context.logger.debug(f'Reset frames after index {_frame_index} up until {self.getFramesCount() - 1}')
        for frame_index in range(self.getFramesCount() - 1, _frame_index, -1):
            self._context.logger.debug(f'Reset frame with index {frame_index}')
            self.getFrameByIndex(frame_index).deleteLater()

    # ------------------------------------------------------------------------------------------------------------------

    def getFrameIndex(self, frame_id) -> int:
        frame = None
        index = 0
        for current_frame in self.getFrames():
            if current_frame.id() == frame_id:
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

    # ------------------------------------------------------------------------------------------------------------------

    def newFrame(self, text, title, frame_index, status, msg=None) -> CodecFrame:
        if frame_index < self.getFramesCount():
            return self._refill_frame(text, title, frame_index, status, msg)

        self._context.logger.debug(f'Adding new codec frame {title} at {frame_index} ...')
        previous_frame = self.getFrameByIndex(frame_index - 1)
        new_frame = CodecFrame(self, self._context, self._tab_id, self, self._plugins, text)
        self.layout().addWidget(new_frame)

        new_frame.pluginSelected.connect(self._on_plugin_selected)
        new_frame.pluginDeselected.connect(self._on_plugin_deselected)
        new_frame.configButtonClicked.connect(self._on_frame_config_button_clicked)
        new_frame.refreshButtonClicked.connect(self._on_frame_refresh_button_clicked)
        new_frame.upButtonClicked.connect(self._on_frame_up_button_clicked)
        new_frame.downButtonClicked.connect(self._on_frame_down_button_clicked)
        new_frame.closeButtonClicked.connect(self._on_frame_close_button_clicked)

        if frame_index > 0:
            # Every new frame (except the first frame) should signal success/error.
            new_frame.setStatus(status, msg)

        if previous_frame and frame_index > 1:
            # Auto-collapse frame where plugin was selected (except first frame and when this frame had focus).
            previous_frame.setCollapsed(not (self._focused_frame and self._focused_frame == previous_frame))

        new_frame.setContentsMargins(0, 0, 0, 0)
        new_frame.layout().setContentsMargins(0, 0, 0, 0)
        new_frame.header().refresh()
        if previous_frame: previous_frame.header().refresh()
        return new_frame

    def _on_frame_close_button_clicked(self, frame_id):
        """ Closes/Removes the frame with the specified frame-id. """
        _frame_index = self.getFrameIndex(frame_id)
        self._context.logger.debug(f'Close frame {_frame_index}:{frame_id}')
        assert _frame_index > 0, 'Illegal operation! Can not close first or invalid frame!'
        frame = self.getFrameByIndex(_frame_index)
        previous_frame = self.getFrameByIndex(_frame_index - 1)

        if not self.hasNextFrame(_frame_index):
            # If this is the last frame the combo-boxes of the previous frame needs to reset.
            self.layout().removeWidget(frame) # remove frame from layout to avoid side-effects with header refresh
            frame.deleteLater()
            previous_frame.getComboBoxes().resetAll()
            # Usability: Always show the content of the last frame.
            previous_frame.setCollapsed(False)
            # Update headings since some buttons may need to be en-/disabled.
            previous_frame.header().refresh()
        else:
            # Otherwise the selected plugin of the previous frame needs to be executed.
            next_frame = self.getFrameByIndex(_frame_index + 1)
            self.layout().removeWidget(frame) # remove frame from layout to avoid side-effects with header refresh
            frame.deleteLater()
            self._execute_plugin_run(previous_frame.id(), previous_frame.getInputText(), previous_frame.getPlugin())
            # Update headings since some buttons may need to be en-/disabled.
            next_frame.header().refresh()
            previous_frame.header().refresh()

    def _on_frame_refresh_button_clicked(self, frame_id: str):
        _frame_index = self.getFrameIndex(frame_id)
        self._context.logger.debug(f'Refreshing frame {_frame_index}:{frame_id}')
        assert self.hasPreviousFrame(_frame_index), 'Illegal operation! No previous frame!'
        previous_frame = self.getFrameByIndex(_frame_index - 1)
        self._context.listener().textChanged.emit(
            self._tab_id, previous_frame.getFrameId(), previous_frame.getInputText(), False)

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
        assert not codec_frame or frame_index < 2, f'Illegal operation! moveFrameUp({frame_index}:{frame_id})'
        self._switch_frames(frame_index - 2, frame_index - 1)
        codec_frame = self.getFrameByIndex(frame_index - 2)
        self._text_changed_event(codec_frame.id(), codec_frame.getInputText(), is_user_action=False, do_preserve_state=True)

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
        assert not codec_frame or frame_index == 0 or frame_index == self.getFramesCount() - 1, \
            f'Illegal operation! moveFrameDown({frame_index}:{frame_id})'
        self._switch_frames(frame_index - 1, frame_index)
        codec_frame = self.getFrameByIndex(frame_index - 1)
        self._text_changed_event(codec_frame.id(), codec_frame.getInputText(), is_user_action=False, do_preserve_state=True)

    def _switch_frames(self, index1, index2):
        frame1 = self.getFrameByIndex(index1)
        plugin1 = frame1.getPlugin()
        frame2 = self.getFrameByIndex(index2)
        plugin2 = frame2.getPlugin()
        frame2.setPlugin(plugin1)
        frame1.setPlugin(plugin2)

    def _on_frame_config_button_clicked(self, frame_id: str):
        # Remember: We press the config-button of a frame, but want to show the plugin-config of the previous frame ...
        frame_index = self.getFrameIndex(frame_id)
        previous_frame = self.getFrameByIndex(frame_index - 1)
        if previous_frame:
            plugin = previous_frame.getPlugin()
            input_text = previous_frame.getInputText()
            self._show_plugin_config(previous_frame.id(), input_text, plugin)

    # ------------------------------------------------------------------------------------------------------------------

    def toDict(self) -> List[dict]:
        return [frame.toDict() for frame in self.getFrames()]
