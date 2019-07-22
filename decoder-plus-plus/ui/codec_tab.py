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
from core.plugin.plugins import Plugins
from ui.codec_frame import CodecFrame
from ui.widget.spacer import VSpacer
from ui.widget.status_widget import StatusWidget


class CodecTab(QScrollArea):

    FRAME_HEIGHT = None

    def __init__(self, parent, context: Context, plugins: Plugins):
        super(QWidget, self).__init__(parent)
        self._context = context
        self._init_listener(context)
        self._logger = context.logger()
        self._plugins = plugins

        self._focussed_frame = None
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
        def selected_frame_changed(frame_id, input_text):
            self._focussed_frame = self.getFrameById(frame_id)

        # Always remember the currently focussed frame
        self._listener.selectedFrameChanged.connect(selected_frame_changed)

        def text_changed_event(frame_id, input_text):
            frame = self.getFrameById(frame_id)
            if frame:
                frame._status_widget.setStatus("DEFAULT")
                frame.setMetaData(input_text)
                plugin = frame._combo_box_frame.selectedPlugin()
                if plugin.is_runnable():
                    self._execute_plugin_run(frame.id(), input_text, plugin)

        self._listener.textChanged.connect(text_changed_event)


    def _execute_plugin_run(self, frame_id, input_text, plugin):
        frame = self.getFrameById(frame_id)
        output_text = ""
        try:
            output_text = plugin.run(input_text)
            self.newFrame(output_text, plugin.title(), frame, status=StatusWidget.SUCCESS)
        except Exception as e:
            error = str(e)
            self._logger.error('{} {}: {}'.format(plugin.name(), plugin.type(), str(e)))
            self.newFrame(output_text, plugin.title(), frame, status=StatusWidget.ERROR, msg=error)

    def _execute_plugin_select(self, frame_id, input_text, plugin):
        frame = self.getFrameById(frame_id)
        output = ""
        try:
            plugin.set_aborted(False)
            output = plugin.select(input_text)
            self.newFrame(output, plugin.title(), frame, status=StatusWidget.SUCCESS)
        except AbortedException as e:
            # User aborted selection. This usually happens when a user clicks the cancel-button within a codec-dialog.
            self._logger.debug(str(e))
            plugin.set_aborted(True)
        except Exception as e:
            error = str(e)
            self._logger.error('{} {}: {}'.format(plugin.name(), plugin.type(), error))
            self.newFrame(output, plugin.title(), frame, status=StatusWidget.ERROR, msg=error)

    def newFrame(self, text, title, previous_frame=None, status=None, msg=None) -> CodecFrame:
        # BUG: Setting complex default values is not possible in python
        # FIX: Set default value to None and set real default later.
        if status is None:
            status = StatusWidget.DEFAULT

        if previous_frame and previous_frame.hasNext():
            try:
                next_frame = previous_frame.next()
                next_frame.setTitle(title)
                finished = False
                if status == StatusWidget.ERROR:
                    while not finished:
                        next_frame.flashStatus(status, msg)
                        # Display error only for the first frame.
                        msg = None
                        finished = not next_frame.hasNext()
                        next_frame = next_frame.next()
                else:
                    next_frame.setInputText(text, msg is not None and len(msg) > 0)
                    next_frame.flashStatus(status, msg)

                previous_frame.focusInputText()
                return next_frame
            except Exception as e:
                self._logger.error("Error Resetting Codec Frame: {}".format(str(e)))
        else:
            try:
                new_frame = CodecFrame(self, self._context, self._next_frame_id, self, self._plugins, previous_frame, text)
                new_frame.pluginSelected.connect(self._execute_plugin_select)
                self._next_frame_id = uuid.uuid4().hex
                if self._frames.layout().count() == 0:
                    # First frame has no title and should not be collapsible.
                    new_frame._title_frame.setHidden(True)
                if self._frames.layout().count() > 0:
                    # Every frame (except the first frame) should signal success/error.
                    new_frame.flashStatus(status, msg)
                if self._frames.layout().count() > 1:
                    # Auto-collapse previous frames (except first frame and when previous frame had focus).
                    previous_frame.setCollapsed(not (self._focussed_frame and self._focussed_frame == previous_frame))
                new_frame.setTitle(title)
                new_frame.setContentsMargins(0, 0, 0, 0)
                new_frame.layout().setContentsMargins(0, 0, 0, 0)
                self._frames_layout.addWidget(new_frame)
                self._set_frame_content_height(new_frame)
                return new_frame
            except Exception as e:
                self._logger.error("Error Initializing New Codec Frame: {}".format(str(e)))

    def getFrames(self) -> List[CodecFrame]:
        frames = []
        for frameIndex in range(0, self._frames_layout.count()):
            frames.append(self._frames_layout.itemAt(frameIndex).widget())
        return frames

    def getFrameById(self, frame_id):
        frame = None
        for current_frame in self.getFrames():
            if current_frame.id() == frame_id:
                frame = current_frame
                break
        return frame

    def _set_frame_content_height(self, new_frame):
        # BUG: Frame height is only calculated correctly for first frame.
        # FIX: Cache and use frame height of first frame for all other frames.
        if not self.FRAME_HEIGHT:
            new_frame.show()
            self.FRAME_HEIGHT = new_frame.getContentHeight()
        new_frame.setContentHeight(self.FRAME_HEIGHT)

    def removeFrames(self, frame):
        if frame:
            if frame.previous():
                frame.previous().setNext(None)

            frames_to_remove = [frame]
            while frame.next():
                frames_to_remove.append(frame.next())
                frame = frame.next()
            for frame_to_remove in reversed(frames_to_remove):
                frame_to_remove.deleteLater()

    def getFocussedFrame(self) -> CodecFrame:
        widget = self._frames.focusWidget()
        while widget:
            if isinstance(widget, CodecFrame):
                return widget
            widget = widget.parent()
        return self._frames_layout.itemAt(0).widget()

    def toDict(self) -> List[dict]:
        return [ frame.toDict() for frame in self.getFrames() ]
