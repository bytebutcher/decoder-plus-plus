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
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget
from qtpy import QtCore

from core.plugin.plugin import NullPlugin
from ui import IconLabel
from ui.widget.collapsible_frame import CollapsibleFrame
from ui.widget.elided_label import ElidedLabel


class CodecFrameHeader(QFrame):

    class AbstractCodecFrameHeaderItem(CollapsibleFrame.HeaderFrame.AbstractHeaderFrameItem):

        def __init__(self, codec_frame: 'ui.codec_frame.CodecFrame', header: 'ui.codec_frame_header.CodecFrameHeader'):
            super(__class__, self).__init__(codec_frame)
            self.header = header
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

        def __init__(self, codec_frame: 'ui.codec_frame.CodecFrame', header: 'ui.codec_frame_header.CodecFrameHeader'):
            super(__class__, self).__init__(codec_frame, header)
            self.setCentralWidget(self._init_central_widget())

        def _init_central_widget(self):
            frm_title_frame = QFrame(self)
            frm_title_frame_layout = QHBoxLayout()
            frm_title_frame_layout.setContentsMargins(0, 0, 0, 0)
            self._title = QLabel(self.header.title())
            self._title.setTextFormat(Qt.PlainText)
            self._title.setToolTip(self.header.description())
            frm_title_frame_layout.addWidget(self._title)
            frm_title_frame.setLayout(frm_title_frame_layout)
            return frm_title_frame

        def refresh(self):
            self._title.setText(self.header.title())

    class ContentPreviewHeaderItem(AbstractCodecFrameHeaderItem):

        def __init__(self, codec_frame: 'ui.codec_frame.CodecFrame', header: 'ui.codec_frame_header.CodecFrameHeader'):
            super(__class__, self).__init__(codec_frame, header)
            self.setCentralWidget(self._init_central_widget())

        def _init_central_widget(self):
            frm_content_preview = QFrame(self)
            frm_content_preview_layout = QHBoxLayout()
            frm_content_preview_layout.setContentsMargins(0, 0, 0, 0)
            txt_content_preview = QLabel("")
            frm_content_preview_layout.addWidget(txt_content_preview)
            self._content_preview_text = ElidedLabel("")
            self._content_preview_text.setTextFormat(Qt.PlainText)
            self._content_preview_text.setStyleSheet("QLabel { color: gray }");
            frm_content_preview_layout.addWidget(self._content_preview_text)
            frm_content_preview.setLayout(frm_content_preview_layout)
            return frm_content_preview

        def refresh(self):
            self._content_preview_text.setText(self.codec_frame.getInputText())

    class LineCountInfoHeaderItem(ClickableCodecFrameHeaderItem):

        def __init__(self, codec_frame: 'ui.codec_frame.CodecFrame', header: 'ui.codec_frame_header.CodecFrameHeader'):
            super(__class__, self).__init__(codec_frame, header)
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

        def __init__(self, codec_frame: 'ui.codec_frame.CodecFrame', header: 'ui.codec_frame_header.CodecFrameHeader'):
            super(__class__, self).__init__(codec_frame, header)
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

        def __init__(self, codec_frame: 'ui.codec_frame.CodecFrame', header: 'ui.codec_frame_header.CodecFrameHeader'):
            super(__class__, self).__init__(codec_frame, header)
            self.setCentralWidget(self._init_central_widget())

        def _init_central_widget(self):
            self._lbl_icon_up = IconLabel(self, qtawesome.icon("fa.chevron-up"))
            self._lbl_icon_up.setHoverEffect(True)
            self._lbl_icon_up.setToolTip("Move up")
            self._lbl_icon_up.setEnabled(self.codec_frame.hasPrevious() and self.codec_frame.previous().hasPrevious())
            self._lbl_icon_up.clicked.connect(self.clicked)
            return self._lbl_icon_up

        def refresh(self):
            self._lbl_icon_up.setEnabled(self.codec_frame.hasPrevious() and self.codec_frame.previous().hasPrevious())

    class DownButtonHeaderItem(ClickableCodecFrameHeaderItem):

        def __init__(self, codec_frame: 'ui.codec_frame.CodecFrame', header: 'ui.codec_frame_header.CodecFrameHeader'):
            super(__class__, self).__init__(codec_frame, header)
            self.setCentralWidget(self._init_central_widget())

        def _init_central_widget(self):
            self._lbl_icon_down = IconLabel(self, qtawesome.icon("fa.chevron-down"))
            self._lbl_icon_down.setHoverEffect(True)
            self._lbl_icon_down.setToolTip("Move down")
            self._lbl_icon_down.setEnabled(self.codec_frame.hasNext())
            self._lbl_icon_down.clicked.connect(self.clicked)
            return self._lbl_icon_down

        def refresh(self):
            self._lbl_icon_down.setEnabled(self.codec_frame.hasNext())

    class ConfigButtonHeaderItem(ClickableCodecFrameHeaderItem):

        def __init__(self, codec_frame: 'ui.codec_frame.CodecFrame', header: 'ui.codec_frame_header.CodecFrameHeader'):
            super(__class__, self).__init__(codec_frame, header)
            self.setCentralWidget(self._init_central_widget())

        def _init_central_widget(self):
            self._lbl_icon_config = IconLabel(self, qtawesome.icon("fa.cog"))
            self._lbl_icon_config.setHoverEffect(True)
            self._lbl_icon_config.setEnabled(self.header.isConfigurable())
            self._lbl_icon_config.setToolTip("Configure")
            self._lbl_icon_config.clicked.connect(self.clicked)
            return self._lbl_icon_config

        def refresh(self):
            self._lbl_icon_config.setEnabled(self.header.isConfigurable())

    class CloseButtonHeaderItem(ClickableCodecFrameHeaderItem):

        def __init__(self, codec_frame: 'ui.codec_frame.CodecFrame', header: 'ui.codec_frame_header.CodecFrameHeader'):
            super(__class__, self).__init__(codec_frame, header)
            self.setCentralWidget(self._init_central_widget())

        def _init_central_widget(self):
            self._lbl_icon_close = IconLabel(self, qtawesome.icon("fa.times"))
            self._lbl_icon_close.setHoverEffect(True)
            self._lbl_icon_close.setToolTip("Close")
            self._lbl_icon_close.clicked.connect(self.clicked)
            return self._lbl_icon_close


    def __init__(self, codec_frame):
        super(__class__, self).__init__()
        self._codec_frame = codec_frame
        self._context = codec_frame._context

    def addWidget(self, widget: QWidget):
        """ Adds a widget to the header. """
        self._codec_frame.header().addWidget(widget)

    def title(self) -> str:
        """ Returns the title of the current frame which is either the title of the previous plugin or None. """
        if self._codec_frame.hasPrevious():
            return self._codec_frame.previous().getPlugin().title()
        return None

    def description(self) -> str:
        """
        Returns the description of the current frame which is either the description of the previous plugin or None.
        """
        if self._codec_frame.hasPrevious():
            if not isinstance(self._codec_frame.previous().getPlugin(), NullPlugin):
                return self._codec_frame.previous().getPlugin().__doc__

    def isConfigurable(self):
        """ Checks whether the plugin which computes the input is configurable. """
        if self._codec_frame.hasPrevious():
            plugin = self._codec_frame.previous().getPlugin()
            return plugin and plugin.is_configurable()
        return False
