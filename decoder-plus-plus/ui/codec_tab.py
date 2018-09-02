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
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea, QWidget, QFrame, QVBoxLayout, QSplitter, QSizePolicy

from core import Context
from core.plugin.plugins import Plugins
from ui.codec_frame import CodecFrame
from ui.widget.spacer import VSpacer
from ui.widget.status_widget import StatusWidget


class CodecTab(QScrollArea):

    FRAME_HEIGHT = None

    def __init__(self, parent, context: Context, plugins: Plugins):
        super(QWidget, self).__init__(parent)
        self._context = context
        self._logger = context.logger()
        self._plugins = plugins

        self._next_frame_id = 1
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

    def newFrame(self, text, title, previous_frame=None, status=None, msg=None):
             # BUG: Setting complex default values is not possible in python
            # WORKAROUND: Set default value to None and set real default later.
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
                except Exception as e:
                    self._logger.error("Error Resetting Codec Frame: {}".format(str(e)))
            else:
                try:
                    new_frame = CodecFrame(self, self._context, self._next_frame_id, self, self._plugins, previous_frame, text)
                    self._next_frame_id += 1
                    if self._frames.layout().count() > 0:
                        new_frame.flashStatus(status, msg)
                    new_frame.setTitle(title)
                    new_frame.setContentsMargins(0, 0, 0, 0)
                    new_frame.layout().setContentsMargins(0, 0, 0, 0)
                    self._frames_layout.addWidget(new_frame)
                    self._set_frame_content_height(new_frame)

                    if previous_frame:
                        previous_frame.focusInputText()
                    else:
                        new_frame.focusInputText()
                except Exception as e:
                    self._logger.error("Error Initializing New Codec Frame: {}".format(str(e)))

    def _set_frame_content_height(self, new_frame):
        # BUG: Frame height is only calculated correctly for first frame.
        # WORKAROUND: Cache and use frame height of first frame for all other frames.
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

    def getFocussedFrame(self):
        widget = self._frames.focusWidget()
        while widget:
            if isinstance(widget, CodecFrame):
                return widget
            widget = widget.parent()
        return self._frames.widget(0)