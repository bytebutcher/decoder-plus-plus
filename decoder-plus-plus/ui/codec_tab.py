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

from ui import CodecFrame
from ui.widget.spacer import VSpacer
from ui.widget.status_widget import StatusWidget


class CodecTab(QScrollArea):

    # BUG: codec_frame should have height 210 but has 480.
    # WORKAROUND: manually set height to 210 height.
    # SEE: https://forum.qt.io/topic/42055/qwidget-height-returns-incorrect-value-in-5-3/7
    FRAME_HEIGHT = 210

    def __init__(self, parent, context, commands):
        super(QWidget, self).__init__(parent)
        self._context = context
        self._logger = context.logger()
        self._commands = commands

        self._next_frame_id = 1
        self._frames = QSplitter(Qt.Vertical)
        self._frames.setChildrenCollapsible(False)
        self._frames.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self._frames.setContentsMargins(0, 0, 0, 0)

        self._main_frame = QFrame(self)
        self._main_frame_layout = QVBoxLayout()
        self._main_frame_layout.addWidget(self._frames)
        self._main_frame_layout.addWidget(VSpacer(self))
        self._main_frame.setLayout(self._main_frame_layout)
        self.newFrame("", "")

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setWidgetResizable(True)
        self.setWidget(self._main_frame)

    def newFrame(self, text, title, previous_frame=None, status=None, msg=None):
        try:
            # BUG: Setting complex default values is not possible in python
            # WORKAROUND: Set default value to None and set real default later.
            if status is None:
                status = StatusWidget.DEFAULT

            if previous_frame and previous_frame.hasNext():
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
            else:
                new_frame = CodecFrame(self, self._context, self._next_frame_id, self, self._commands, previous_frame, text)
                self._next_frame_id += 1
                if self._frames.count() > 0:
                    new_frame.flashStatus(status, msg)
                new_frame.setTitle(title)
                new_frame.setContentsMargins(0, 0, 0, 0)
                new_frame.layout().setContentsMargins(0, 0, 0, 0)
                self._frames.addWidget(new_frame)

                # BUG: QSplitter does not allow frames to be wider than the surrounding area (here: QScrollArea).
                # WORKAROUND: Set a fixed size for codec frames and disable handles which prevents users from
                #             trying to resize the codec frames.
                new_frame.setFixedHeight(self.FRAME_HEIGHT)
                self._frames.handle(self._frames.count() - 1).setEnabled(False)

                if previous_frame:
                    previous_frame.focusInputText()
                else:
                    new_frame.focusInputText()
        except Exception as e:
            self._logger.error("Unknown error: {}".format(str(e)))

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