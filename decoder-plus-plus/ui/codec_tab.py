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
import uuid
from typing import List

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QScrollArea, QWidget, QFrame, QVBoxLayout, QSplitter, QSizePolicy

from core import Context
from core.exception import AbortedException
from core.plugin.plugin_builder import PluginBuilder
from core.plugin.plugins import Plugins
from ui.codec_frame import CodecFrame
from ui.widget.spacer import VSpacer
from ui.widget.status_widget import StatusWidget


class CodecTab(QScrollArea):

    FRAME_HEIGHT = None

    def __init__(self, parent, context: Context, plugins: Plugins):
        super(QWidget, self).__init__(parent)
        self._tab_id = uuid.uuid4().hex
        self._context = context
        self._init_listener(context)
        self._logger = context.logger()
        self._plugins = plugins

        self._focused_frame = None
        self._next_frame_id = uuid.uuid4().hex
        self._frames = QFrame()
        self._frames_layout = QVBoxLayout()
        self._frames.setLayout(self._frames_layout)
        self._frames_layout.setContentsMargins(0, 0, 0, 0)

        self._main_frame = QFrame(self)
        self._main_frame_layout = QVBoxLayout()
        self._main_frame_layout.setAlignment(Qt.AlignTop)
        self._main_frame_layout.addWidget(self._frames)
        self._main_frame_layout.addWidget(VSpacer(self))
        self._main_frame.setLayout(self._main_frame_layout)
        self.newFrame("", "")

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setWidgetResizable(True)
        self.setWidget(self._main_frame)

    def _init_listener(self, context):
        self._listener = context.listener()

        def selected_frame_changed(tab_id, frame_id, input_text):
            # Always remember the currently focused frame (e.g. used for finding the currently selected frame when
            # using keyboard-shortcuts)
            if self.id() == tab_id:
                self._focused_frame = self.getFrameById(frame_id)

        self._listener.selectedFrameChanged.connect(selected_frame_changed)
        self._listener.textChanged.connect(lambda tab_id, frame_id, text: self.id() == tab_id and self._text_changed_event(frame_id, text))

    # ------------------------------------------------------------------------------------------------------------------

    def _set_frame_content_height(self, new_frame):
        # BUG: Frame height is only calculated correctly for first frame.
        # FIX: Cache and use frame height of first frame for all other frames.
        if not self.FRAME_HEIGHT:
            new_frame.show()
            self.FRAME_HEIGHT = new_frame.getContentHeight()
        new_frame.setContentHeight(self.FRAME_HEIGHT)

    # ------------------------------------------------------------------------------------------------------------------
    # TODO: Move the following code into the codec-frame
    # ------------------------------------------------------------------------------------------------------------------

    def _text_changed_event(self, frame_id, text, is_user_action=True, do_preserve_state=False):
        frame = self.getFrameById(frame_id)
        if is_user_action:
            frame._status_widget.setStatus("DEFAULT")
        while frame:
            if do_preserve_state and frame.hasNext() and frame.next()._status_widget.hasStatus("DEFAULT"):
                # Do not overwrite content of frames which are in default-state.
                # Usually done when moving frames to a new position whereby custom user-input should not be
                # overwritten.
                frame = frame.next()
                continue

            input_text = frame.getInputText()
            frame.header().refresh()
            plugin = frame._combo_box_frame.selectedPlugin()
            if not plugin.is_runnable():
                break

            frame = self._execute_plugin_run(frame.id(), input_text, plugin)

    def _execute_plugin_run(self, frame_id, input_text, plugin) -> CodecFrame:
        frame = self.getFrameById(frame_id)
        output_text = ""
        try:
            output_text = plugin.run(input_text)
            return self.newFrame(output_text, plugin.title(), frame, status=StatusWidget.SUCCESS)
        except BaseException as e:
            error = str(e)
            self._logger.error('{} {}: {}'.format(plugin.name(), plugin.type(), error))
            return self.newFrame(output_text, plugin.title(), frame, status=StatusWidget.ERROR, msg=error)


    def _execute_plugin_select(self, frame_id, input_text, plugin):
        frame = self.getFrameById(frame_id)
        output = ""
        try:
            plugin.set_aborted(False)
            output = plugin.select(input_text)
            self.newFrame(output, plugin.title(), frame, status=StatusWidget.SUCCESS).focusInputText()
        except AbortedException as e:
            # User aborted selection. This usually happens when a user clicks the cancel-button within a codec-dialog.
            self._logger.debug(str(e))
            plugin.set_aborted(True)
        except BaseException as e:
            error = str(e)
            self._logger.error('{} {}: {}'.format(plugin.name(), plugin.type(), error))
            self.newFrame(output, plugin.title(), frame, status=StatusWidget.ERROR, msg=error)

    def _get_plugin_config(self, frame_id: str):
        # Remember: We press the config-button of a frame, but want the plugin-config of the previous frame ...
        frame = self.getFrameById(frame_id).previous()
        if frame:
            plugin = frame.getPlugin()
            input_text = frame.getInputText()
            self._execute_plugin_select(frame.id(), input_text, plugin)

    # ------------------------------------------------------------------------------------------------------------------

    def id(self):
        return self._tab_id

    # ------------------------------------------------------------------------------------------------------------------

    def newFrame(self, text, title, previous_frame=None, status=None, msg=None) -> CodecFrame:
        # BUG: Setting complex default values is not possible in python
        # FIX: Set default value to None and set real default later.
        if status is None:
            status = StatusWidget.DEFAULT

        if previous_frame and previous_frame.hasNext():
            next_frame = previous_frame.next()
            if status == StatusWidget.ERROR:
                finished = False
                while not finished:
                    next_frame.flashStatus(status, msg)
                    next_frame.header().refresh()
                    # Display error only for the first frame.
                    msg = None
                    finished = not next_frame.hasNext()
                    next_frame = next_frame.next()
            else:
                next_frame.setInputText(text)
                next_frame.header().refresh()
                next_frame.flashStatus(status, msg)

            return next_frame
        else:
            new_frame = CodecFrame(self, self._context, self._tab_id, self._next_frame_id, self, self._plugins, previous_frame, text)
            new_frame.pluginSelected.connect(self._execute_plugin_select)
            new_frame.configButtonClicked.connect(lambda frame_id: self._get_plugin_config(frame_id))
            self._next_frame_id = uuid.uuid4().hex
            if self._frames.layout().count() > 0:
                # Every frame (except the first frame) should signal success/error.
                new_frame.flashStatus(status, msg)
            if self._frames.layout().count() > 1:
                # Auto-collapse previous frames (except first frame and when previous frame had focus).
                previous_frame.setCollapsed(not (self._focused_frame and self._focused_frame == previous_frame))
            new_frame.header().refresh()
            new_frame.setContentsMargins(0, 0, 0, 0)
            new_frame.layout().setContentsMargins(0, 0, 0, 0)
            new_frame.upButtonClicked.connect(self.moveFrameUp)
            new_frame.downButtonClicked.connect(self.moveFrameDown)
            new_frame.closeButtonClicked.connect(self.closeFrame)
            self._frames_layout.addWidget(new_frame)
            self._set_frame_content_height(new_frame)
            if previous_frame: previous_frame.header().refresh()
            return new_frame

    # ------------------------------------------------------------------------------------------------------------------

    def getFrameById(self, frame_id):
        frame = None
        for current_frame in self.getFrames():
            if current_frame.id() == frame_id:
                frame = current_frame
                break
        return frame

    def getFocusedFrame(self) -> CodecFrame:
        widget = self._frames.focusWidget()
        while widget:
            if isinstance(widget, CodecFrame):
                return widget
            widget = widget.parent()
        return self._frames_layout.itemAt(0).widget()

    def getFrames(self) -> List[CodecFrame]:
        frames = []
        for frameIndex in range(0, self._frames_layout.count()):
            frames.append(self._frames_layout.itemAt(frameIndex).widget())
        return frames

    def getFramesCount(self) -> int:
        return self._frames_layout.count()

    # ------------------------------------------------------------------------------------------------------------------

    def closeFrame(self, frame_id):
        """
        Closes/Removes the frame with the specified frame-id.

        This is done by caching the config of all frames (except the frame specified), removing the last frame and
        rebuilding everything from scratch (top to bottom).

        There might be better ways removing a frame but this one works as expected.
        """

        # Caching the config of all frames (except the frame specified)
        frame_config_list = []
        frames = self.getFrames()
        uncollapse_last_frame = False
        for frame in frames:
            if frame.id() != frame_id:
                frame_config_list.append(frame.toDict())
            else:
                # We need to move the plugin of the to-be-removed frame to the previous frame.
                frame_config_list[-1]["plugin"] = frame.toDict()["plugin"]
                if not frame.hasNext(): # it is the last frame
                    uncollapse_last_frame = not frame.isCollapsed()

        # Remove the last frame
        self.removeFrames(frames[-1])

        # Rebuilding everything from scratch (starting at frame 1)
        frame = frames[0]
        for frame_config in frame_config_list:
            frame.fromDict(frame_config)
            frame = frame.next()

        if uncollapse_last_frame:
            frames[-2].setCollapsed(False)

    def removeFrames(self, frame):
        """ Remove all frames below the frame specified """
        if frame:
            if frame.hasPrevious():
                frame.previous().setNext(None)

            frames_to_remove = [frame]
            while frame.hasNext():
                frames_to_remove.append(frame.next())
                frame = frame.next()
            for frame_to_remove in reversed(frames_to_remove):
                frame_to_remove.deleteLater()

    # ------------------------------------------------------------------------------------------------------------------

    def moveFrameUp(self, frame_id: str):
        codec_frame = self.getFrameById(frame_id)
        if not codec_frame or not codec_frame.previous() or not codec_frame.previous().previous():
            self._logger.debug('moveFrameUp({}): invalid move'.format(frame_id))
            return

        self.switchFrames(codec_frame.previous().previous(), codec_frame.previous())
        self._text_changed_event(codec_frame.previous().previous().id(), codec_frame.previous().previous().getInputText(), is_user_action=False, do_preserve_state=True)

    def moveFrameDown(self, frame_id: str):
        codec_frame = self.getFrameById(frame_id)
        if not codec_frame or not codec_frame.previous() or not codec_frame.next():
            self._logger.debug('moveFrameDown({}): invalid move'.format(frame_id))
            return

        self.switchFrames(codec_frame.previous(), codec_frame)
        self._text_changed_event(codec_frame.previous().id(), codec_frame.previous().getInputText(), is_user_action=False, do_preserve_state=True)


    def switchFrames(self, frame: CodecFrame, another_frame: CodecFrame):
        temp_frame_plugin = frame.getPlugin()
        frame.setPlugin(another_frame.getPlugin())
        another_frame.setPlugin(temp_frame_plugin)

    # ------------------------------------------------------------------------------------------------------------------

    def toDict(self) -> List[dict]:
        return [ frame.toDict() for frame in self.getFrames() ]
