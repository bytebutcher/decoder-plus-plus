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
import qtawesome
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy
from qtpy import QtCore

from dpp.ui import IconLabel
from dpp.ui.widget.collapsible_frame import CollapsibleFrame
from dpp.ui.widget.elided_label import ElidedLabel


class CodecFrameHeader(QFrame):
    class AbstractCodecFrameHeaderItem(CollapsibleFrame.HeaderFrame.AbstractHeaderFrameItem):

        def __init__(self, codec_frame: 'ui.codec_frame.CodecFrame'):
            super(__class__, self).__init__(codec_frame)
            self.codec_frame = codec_frame

    class ClickableCodecFrameHeaderItem(AbstractCodecFrameHeaderItem):
        clicked = pyqtSignal('PyQt_PyObject')  # event
        doubleClicked = pyqtSignal('PyQt_PyObject')  # event

        def mousePressEvent(self, event):
            # suppress mouse clicks - click signals are used instead
            pass

        def mouseReleaseEvent(self, event):
            # suppress mouse clicks - click signals are used instead
            pass

        def mouseDoubleClickEvent(self, event):
            # suppress mouse clicks - click signals are used instead
            pass

    class TitleHeaderItem(AbstractCodecFrameHeaderItem):

        def __init__(self, codec_frame: 'ui.codec_frame.CodecFrame'):
            super(__class__, self).__init__(codec_frame)
            self.setCentralWidget(self._init_central_widget())

        def _init_central_widget(self):
            frm_title_frame = QFrame(self)
            frm_title_frame_layout = QHBoxLayout()
            frm_title_frame_layout.setContentsMargins(0, 0, 0, 0)
            self._title = QLabel(self.codec_frame.title())
            self._title.setTextFormat(Qt.PlainText)
            self._title.setToolTip(self.codec_frame.description())
            frm_title_frame_layout.addWidget(self._title)
            frm_title_frame.setLayout(frm_title_frame_layout)
            return frm_title_frame

        def refresh(self):
            self._title.setText(self.codec_frame.title())

    class ContentPreviewHeaderItem(AbstractCodecFrameHeaderItem):

        def __init__(self, codec_frame: 'ui.codec_frame.CodecFrame'):
            super(__class__, self).__init__(codec_frame)
            self.setCentralWidget(self._init_central_widget())
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        def _init_central_widget(self):
            frm_content_preview = QFrame(self)
            frm_content_preview_layout = QHBoxLayout()
            frm_content_preview_layout.setContentsMargins(0, 0, 0, 0)
            self._content_preview_text = ElidedLabel("")
            self._content_preview_text.setTextFormat(Qt.PlainText)
            self._content_preview_text.setStyleSheet("QLabel { color: gray }")
            frm_content_preview_layout.addWidget(self._content_preview_text)
            frm_content_preview.setLayout(frm_content_preview_layout)
            return frm_content_preview

        def refresh(self):
            self._content_preview_text.setText(self.codec_frame.getInputText())

    class LineCountInfoHeaderItem(ClickableCodecFrameHeaderItem):

        def __init__(self, codec_frame: 'ui.codec_frame.CodecFrame'):
            super(__class__, self).__init__(codec_frame)
            self.setCentralWidget(self._init_central_widget())

        def _init_central_widget(self):
            frm_line_count = QFrame(self)
            frm_line_count_layout = QHBoxLayout()
            frm_line_count_layout.setContentsMargins(0, 0, 0, 0)
            lbl_line_count = QLabel("Lines:")
            frm_line_count_layout.addWidget(lbl_line_count)
            self._txt_line_count = QLabel("0")
            self._txt_line_count.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            minimum_width = self._txt_line_count.fontMetrics().boundingRect("000").width()
            self._txt_line_count.setMinimumWidth(minimum_width)
            frm_line_count_layout.addWidget(self._txt_line_count)
            frm_line_count.setLayout(frm_line_count_layout)
            return frm_line_count

        def refresh(self):
            content = self.codec_frame.getInputText()
            line_count = str((content and len(content.split('\n'))) or 0)
            self._txt_line_count.setText(line_count)

    class ContentLengthInfoHeaderItem(ClickableCodecFrameHeaderItem):

        def __init__(self, codec_frame: 'ui.codec_frame.CodecFrame'):
            super(__class__, self).__init__(codec_frame)
            self.setCentralWidget(self._init_central_widget())

        def _init_central_widget(self):
            frm_content_length = QFrame(self)
            frm_content_length_layout = QHBoxLayout()
            frm_content_length_layout.setContentsMargins(0, 0, 0, 0)
            lbl_content_length = QLabel("Length:")
            frm_content_length_layout.addWidget(lbl_content_length)
            self._content_length_text = QLabel("0")
            self._content_length_text.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            minimum_width = self._content_length_text.fontMetrics().boundingRect("000").width()
            self._content_length_text.setMinimumWidth(minimum_width)
            frm_content_length_layout.addWidget(self._content_length_text)
            frm_content_length.setLayout(frm_content_length_layout)
            return frm_content_length

        def refresh(self):
            content = self.codec_frame.getInputText()
            length = str((content and len(content)) or 0)
            self._content_length_text.setText(length)

    class UpButtonHeaderItem(ClickableCodecFrameHeaderItem):

        def __init__(self, codec_frame: 'ui.codec_frame.CodecFrame'):
            super(__class__, self).__init__(codec_frame)
            self.setCentralWidget(self._init_central_widget())

        def _init_central_widget(self):
            self._lbl_icon_up = IconLabel(self, qtawesome.icon("fa.chevron-up"))
            self._lbl_icon_up.setHoverEffect(True)
            self._lbl_icon_up.setToolTip("Move up")
            self._lbl_icon_up.setEnabled(self.codec_frame.getFrameIndex() >= 2)
            self._lbl_icon_up.clicked.connect(self.clicked)
            return self._lbl_icon_up

        def refresh(self):
            self._lbl_icon_up.setEnabled(self.codec_frame.getFrameIndex() >= 2)

    class DownButtonHeaderItem(ClickableCodecFrameHeaderItem):

        def __init__(self, codec_frame: 'ui.codec_frame.CodecFrame'):
            super(__class__, self).__init__(codec_frame)
            self.setCentralWidget(self._init_central_widget())

        def _init_central_widget(self):
            self._lbl_icon_down = IconLabel(self, qtawesome.icon("fa.chevron-down"))
            self._lbl_icon_down.setHoverEffect(True)
            self._lbl_icon_down.setToolTip("Move down")
            self._lbl_icon_down.setEnabled(self.codec_frame.hasNextFrame())
            self._lbl_icon_down.clicked.connect(self.clicked)
            return self._lbl_icon_down

        def refresh(self):
            # Only when there is a next codec frame it can be moved down.
            # Note, that the first codec frame can not be moved either.
            self._lbl_icon_down.setEnabled(self.codec_frame.hasNextFrame() and self.codec_frame.hasPreviousFrame())

    class ConfigButtonHeaderItem(ClickableCodecFrameHeaderItem):

        def __init__(self, codec_frame: 'ui.codec_frame.CodecFrame'):
            super(__class__, self).__init__(codec_frame)
            self.setCentralWidget(self._init_central_widget())

        def _init_central_widget(self):
            self._lbl_icon_config = IconLabel(self, qtawesome.icon("fa.cog"))
            self._lbl_icon_config.setHoverEffect(True)
            self._lbl_icon_config.setEnabled(self.codec_frame.isConfigurable())
            self._lbl_icon_config.setToolTip("Configure")
            self._lbl_icon_config.clicked.connect(self.clicked)
            return self._lbl_icon_config

        def refresh(self):
            self._lbl_icon_config.setEnabled(self.codec_frame.isConfigurable())

    class CloseButtonHeaderItem(ClickableCodecFrameHeaderItem):

        def __init__(self, codec_frame: 'ui.codec_frame.CodecFrame'):
            super(__class__, self).__init__(codec_frame)
            self.setCentralWidget(self._init_central_widget())

        def _init_central_widget(self):
            self._lbl_icon_close = IconLabel(self, qtawesome.icon("fa.times"))
            self._lbl_icon_close.setHoverEffect(True)
            self._lbl_icon_close.setToolTip("Close")
            self._lbl_icon_close.clicked.connect(self.clicked)
            # First codec frame can not be closed
            self._lbl_icon_close.setEnabled(self.codec_frame.hasPreviousFrame())
            return self._lbl_icon_close

        def refresh(self):
            # First codec frame can not be closed
            self._lbl_icon_close.setEnabled(self.codec_frame.hasPreviousFrame())
