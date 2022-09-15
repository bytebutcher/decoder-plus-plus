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
from qtpy.QtCore import Signal, Qt
from qtpy.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy
from qtpy import QtCore

from dpp.core.icons import Icon, icon
from dpp.core.math import eta
from dpp.ui import IconLabel
from dpp.ui.widget.collapsible_frame import CollapsibleFrame
from dpp.ui.widget.elided_label import ElidedLabel
from dpp.ui.widget.status_widget import StatusWidget


class CodecFrameHeader(QFrame):
    class AbstractCodecFrameHeaderItem(CollapsibleFrame.HeaderFrame.AbstractHeaderFrameItem):

        def __init__(self, codec_frame: 'dpp.ui.codec_frame.CodecFrame'):
            super(__class__, self).__init__(codec_frame)
            self.codec_frame = codec_frame

    class ClickableCodecFrameHeaderItem(AbstractCodecFrameHeaderItem):
        clicked = Signal('PyQt_PyObject')  # event
        doubleClicked = Signal('PyQt_PyObject')  # event

        def mousePressEvent(self, event):
            # suppress mouse clicks - click signals are used instead
            pass

        def mouseReleaseEvent(self, event):
            # suppress mouse clicks - click signals are used instead
            pass

        def mouseDoubleClickEvent(self, event):
            # suppress mouse clicks - click signals are used instead
            pass

    class IndicatorHeaderItem(AbstractCodecFrameHeaderItem):

        def __init__(self, codec_frame: 'ui.codec_frame.CodecFrame'):
            super(__class__, self).__init__(codec_frame)
            self._indicators = {
                StatusWidget.ERROR: icon(Icon.INDICATOR_ERROR),
                StatusWidget.SUCCESS: icon(Icon.INDICATOR_SUCCESS),
                StatusWidget.DEFAULT: icon(Icon.INDICATOR_DEFAULT)
            }
            self.setCentralWidget(self._init_central_widget())

        def _init_central_widget(self):
            frame = QFrame(self)
            frame_layout = QHBoxLayout()
            frame_layout.setContentsMargins(0, 0, 0, 0)
            frame_layout.addWidget(self._init_indicator())
            frame_layout.addWidget(QLabel(' '))
            frame.setLayout(frame_layout)
            return frame

        def _init_indicator(self):
            self._lbl_indicator = IconLabel(self.codec_frame, self._indicators[StatusWidget.DEFAULT])
            self._lbl_indicator.setMaximumWidth(10)
            self._lbl_indicator.setMaximumHeight(10)
            return self._lbl_indicator

        def setStatus(self, status: str, message: str):
            self._lbl_indicator.setIcon(self._indicators[status])

    class TitleHeaderItem(AbstractCodecFrameHeaderItem):

        def __init__(self, codec_frame: 'ui.codec_frame.CodecFrame'):
            super(__class__, self).__init__(codec_frame)
            self.setCentralWidget(self._init_central_widget())

        def _init_central_widget(self):
            frm = QFrame(self)
            frm_layout = QHBoxLayout()
            frm_layout.setContentsMargins(0, 0, 0, 0)
            lbl_label = QLabel('Codec:')
            frm_layout.addWidget(lbl_label)
            self._lbl_value = QLabel(self.codec_frame.title())
            self._lbl_value.setTextFormat(Qt.PlainText)
            self._lbl_value.setToolTip(self.codec_frame.description())
            frm_layout.addWidget(self._lbl_value)
            frm.setLayout(frm_layout)
            return frm

        def refresh(self):
            title = self.codec_frame.title()
            if title:
                self._lbl_value.setText(title)
                self._lbl_value.setStyleSheet('')
            else:
                # No codec selected.
                self._lbl_value.setText('None')
                self._lbl_value.setStyleSheet('QLabel { color: gray }')

    class ContentPreviewHeaderItem(AbstractCodecFrameHeaderItem):

        def __init__(self, codec_frame: 'ui.codec_frame.CodecFrame'):
            super(__class__, self).__init__(codec_frame)
            self.setCentralWidget(self._init_central_widget())

        def _init_central_widget(self):
            frm = QFrame(self)
            frm_layout = QHBoxLayout()
            frm_layout.setContentsMargins(0, 0, 0, 0)

            self._content_preview_text = ElidedLabel("")
            self._content_preview_text.setTextFormat(Qt.PlainText)
            self._content_preview_text.setStyleSheet("QLabel { color: gray }")
            self._content_preview_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

            frm_layout.addWidget(self._content_preview_text)
            frm_layout.setContentsMargins(0, 0, 0, 0)
            frm.setLayout(frm_layout)

            return frm

        def isascii(self, input_text: str) -> bool:
            try:
                return len(input_text) == len(input_text.encode())
            except UnicodeEncodeError:
                return False

        def refresh(self):
            input_text = self.codec_frame.getInputText()
            if self.isascii(input_text):
                self._content_preview_text.setText(input_text)
            else:
                self._content_preview_text.setText('No Preview Available')

    class LineCountInfoHeaderItem(AbstractCodecFrameHeaderItem):

        def __init__(self, codec_frame: 'ui.codec_frame.CodecFrame'):
            super(__class__, self).__init__(codec_frame)
            self.setCentralWidget(self._init_central_widget())

        def _init_central_widget(self):
            frm = QFrame(self)
            frm_layout = QHBoxLayout()
            frm_layout.setContentsMargins(0, 0, 0, 0)
            lbl_value = QLabel("Lines:")
            frm_layout.addWidget(lbl_value)
            self._txt_value = QLabel("0")
            self._txt_value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            minimum_width = self._txt_value.fontMetrics().boundingRect("000").width()
            self._txt_value.setMinimumWidth(minimum_width)
            frm_layout.addWidget(self._txt_value)
            frm.setLayout(frm_layout)
            return frm

        def refresh(self):
            content = self.codec_frame.getInputText()
            line_count = str((content and len(content.split('\n'))) or 0)
            self._txt_value.setText(line_count)

    class ContentLengthInfoHeaderItem(AbstractCodecFrameHeaderItem):

        def __init__(self, codec_frame: 'ui.codec_frame.CodecFrame'):
            super(__class__, self).__init__(codec_frame)
            self.setCentralWidget(self._init_central_widget())

        def _init_central_widget(self):
            frm = QFrame(self)
            frm_layout = QHBoxLayout()
            frm_layout.setContentsMargins(0, 0, 0, 0)
            lbl_value = QLabel("Length:")
            frm_layout.addWidget(lbl_value)
            self._txt_value = QLabel("0")
            self._txt_value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            minimum_width = self._txt_value.fontMetrics().boundingRect("000").width()
            self._txt_value.setMinimumWidth(minimum_width)
            frm_layout.addWidget(self._txt_value)
            frm.setLayout(frm_layout)
            return frm

        def refresh(self):
            content = self.codec_frame.getInputText()
            length = str((content and len(content)) or 0)
            self._txt_value.setText(length)

    class EntropyInfoHeaderItem(AbstractCodecFrameHeaderItem):

        def __init__(self, codec_frame: 'ui.codec_frame.CodecFrame'):
            super(__class__, self).__init__(codec_frame)
            self.setCentralWidget(self._init_central_widget())

        def _init_central_widget(self):
            frm = QFrame(self)
            frm_layout = QHBoxLayout()
            frm_layout.setContentsMargins(0, 0, 0, 0)
            lbl_text = QLabel('Entropy:')
            frm_layout.addWidget(lbl_text)
            self.txt_value = QLabel('0.00')
            self.txt_value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            minimum_width = self.txt_value.fontMetrics().boundingRect('0.00').width()
            self.txt_value.setMinimumWidth(minimum_width)
            frm_layout.addWidget(self.txt_value)
            frm.setLayout(frm_layout)
            return frm

        def refresh(self):
            content = self.codec_frame.getInputText()
            entropy = eta(content)
            self.txt_value.setText(f'{entropy:.2f}')

    class RefreshButtonHeaderItem(ClickableCodecFrameHeaderItem):

        def __init__(self, codec_frame: 'ui.codec_frame.CodecFrame'):
            super(__class__, self).__init__(codec_frame)
            self.setCentralWidget(self._init_central_widget())

        def _init_central_widget(self):
            self._lbl_icon_up = IconLabel(self, icon(Icon.FRAME_REFRESH))
            self._lbl_icon_up.setHoverEffect(True)
            self._lbl_icon_up.setToolTip("Refresh")
            self._lbl_icon_up.setEnabled(self.codec_frame.hasPreviousFrame())
            self._lbl_icon_up.clicked.connect(self.clicked)
            return self._lbl_icon_up

        def refresh(self):
            status = self.codec_frame.hasStatus(StatusWidget.DEFAULT) and self.codec_frame.hasPreviousFrame()
            self._lbl_icon_up.setEnabled(status)

    class UpButtonHeaderItem(ClickableCodecFrameHeaderItem):

        def __init__(self, codec_frame: 'ui.codec_frame.CodecFrame'):
            super(__class__, self).__init__(codec_frame)
            self.setCentralWidget(self._init_central_widget())

        def _init_central_widget(self):
            self._lbl_icon_up = IconLabel(self, icon(Icon.FRAME_UP))
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
            self._lbl_icon_down = IconLabel(self, icon(Icon.FRAME_DOWN))
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
            self._lbl_icon_config = IconLabel(self, icon(Icon.FRAME_CONFIG))
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
            self._lbl_icon_close = IconLabel(self, icon(Icon.CLOSE))
            self._lbl_icon_close.setHoverEffect(True)
            self._lbl_icon_close.setToolTip("Close")
            self._lbl_icon_close.clicked.connect(self.clicked)
            # First codec frame can not be closed
            self._lbl_icon_close.setEnabled(self.codec_frame.hasPreviousFrame())
            return self._lbl_icon_close

        def refresh(self):
            # First codec frame can not be closed
            self._lbl_icon_close.setEnabled(self.codec_frame.hasPreviousFrame())
