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

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QFrame, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QBoxLayout, QSizePolicy

from ui import HSpacer


class CollapsibleFrame(QFrame):
    """
    Frame with ability to un-/collapse content via clickable arrow-handles.
    """

    def __init__(self, parent=None, title=None, content=None, direction=QBoxLayout.LeftToRight):
        """
        Initializes the collapsible frame.
        :param parent: the parent widget of this frame (default=None).
        :param title: the title to be displayed (default=None).
        :param direction: the direction in which content should be aligned (default=QBoxLayout.LeftToRight).
        """
        super(__class__, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._is_collasped = False
        self._title_frame = None
        self._content, self._content_layout = (None, None)

        self._layout = QVBoxLayout()
        self._layout.setAlignment(Qt.AlignTop)

        self._layout.addWidget(self._init_title_frame(title, content, self._is_collasped))
        self._layout.addWidget(self._init_content(direction, self._is_collasped))

        self._init_collapsable()
        self.setLayout(self._layout)

    def _init_title_frame(self, title, content, collapsed):
        self._title_frame = CollapsibleFrame.TitleFrame(self, title=title, content=content, collapsed=collapsed)
        return self._title_frame

    def _init_content(self, direction, collapsed):
        self._content = QFrame(self)
        self._content_layout = QBoxLayout(direction)
        self._content_layout.setAlignment(Qt.AlignTop)
        self._content.setLayout(self._content_layout)
        self._content.setVisible(not collapsed)
        return self._content

    def _init_collapsable(self):
        self._title_frame.clicked.connect(self.toggleCollapsed)

    def addWidget(self, widget):
        """
        Adds an widget to the content.
        :param widget: the widget to be added.
        """
        self._content_layout.addWidget(widget)

    def setContentDirection(self, direction: int):
        """ Sets the direction of the content (e.g. LeftToRight, RightToLeft, TopToBottom, BottomToTop). """
        self._content_layout.setDirection(direction)

    def toggleCollapsed(self):
        """ Toggles collapsing of the frame. """
        self._content.setVisible(self._is_collasped)
        self._is_collasped = not self._is_collasped
        self._title_frame._arrow.setArrow(int(self._is_collasped))

    def setCollapsed(self, status):
        """ Un-/collapses the frame. """
        self._content.setVisible(not status)
        self._is_collasped = status
        self._title_frame._arrow.setArrow(int(self._is_collasped))

    def setTitle(self, title: str=None):
        """ Sets the title of the frame. """
        self._title_frame.setTitle(title)

    def getTitle(self):
        return self._title_frame.getTitle()

    def setMetaData(self, content: str=None):
        self._title_frame.setMetaData(content)

    def indicateError(self, status: bool):
        """ Indicates that there was an error during encoding/decoding/hashing/scripting. """
        self._title_frame.indicateError(status)

    def getContentHeight(self) -> int:
        """ Returns the height of the content when uncollapsed. """
        return self._content.height()

    def setContentHeight(self, height: int):
        """ Sets the height of the content when uncollapsed. """
        self._content.setFixedHeight(height)

    class TitleFrame(QFrame):
        """ Clickable frame with title. """

        clicked = pyqtSignal()

        def __init__(self, parent=None, title="", content="", collapsed=False):
            super(__class__, self).__init__(parent)

            self.setMinimumHeight(26)
            self.setMaximumHeight(26)
            self.indicateError(False)

            self._hlayout = QHBoxLayout()
            self._hlayout.setContentsMargins(0, 0, 0, 0)
            self._hlayout.setSpacing(0)

            self._arrow = None
            self._title = None
            self._content_preview_text = None
            self._line_count_text = None
            self._content_length_text = None

            self._hlayout.addWidget(self._init_arrow(collapsed))
            self._init_title(title, content)


        def _init_arrow(self, collapsed):
            self._arrow = CollapsibleFrame.Arrow(self, collapsed=collapsed)
            self._arrow.setMinimumWidth(24)
            self._arrow.setMaximumWidth(24)
            self._arrow.setStyleSheet("border:0px")
            return self._arrow

        def _init_title(self, title=None, content=None):
            inner_title_frame = QFrame(self)
            inner_title_layout = QHBoxLayout(self)
            inner_title_layout.setContentsMargins(0, 0, 0, 0)
            inner_title_frame.setLayout(inner_title_layout)
            inner_title_frame.setStyleSheet("border:0px")
            inner_title_frame.setMinimumHeight(24)
            inner_title_frame.setMaximumHeight(24)
            self._hlayout.addWidget(inner_title_frame)
            self.setLayout(self._hlayout)

            self._title = QLabel("")
            inner_title_layout.addWidget(self._title)

            content_preview_label = QLabel("")
            inner_title_layout.addWidget(content_preview_label)
            self._content_preview_text = QLabel("")
            self._content_preview_text.setStyleSheet("QLabel { color: gray }");
            inner_title_layout.addWidget(self._content_preview_text)

            inner_title_layout.addWidget(HSpacer(self))

            line_count_label = QLabel("lines: ")
            inner_title_layout.addWidget(line_count_label)

            self._line_count_text = QLabel("0")
            inner_title_layout.addWidget(self._line_count_text)

            content_length_label = QLabel("length: ")
            inner_title_layout.addWidget(content_length_label)
            self._content_length_text = QLabel("0")
            inner_title_layout.addWidget(self._content_length_text)
            inner_title_layout.addWidget(QLabel(""))

            self.setTitle(title)
            self.setMetaData(content)
            return inner_title_frame

        def indicateError(self, status: bool):
            """ Indicates an error by painting the title-border red. Otherweise black. """
            if status:
                self.setStyleSheet("border:1px solid red; ")
            else:
                self.setStyleSheet("border:1px solid rgb(41, 41, 41); ")

        def setTitle(self, title: str=None):
            """ Sets the title of the frame. """
            self._title.setText(title)

        def setMetaData(self, content: str=None):
            if content:
                max_size = 75
                joined_lines = "\\n".join(content.split('\n'))
                data = (joined_lines[:max_size] + ' ..') if len(joined_lines) > max_size else joined_lines
                self._content_preview_text.setText(data)

                length = str(len(content))
                self._content_length_text.setText(length)

                line_count = str(len(content.split('\n')))
                self._line_count_text.setText(line_count)

        def getTitle(self) -> str:
            return self._title.text()

        def mousePressEvent(self, event):
            """ Initiates the un-/collapse event. """
            self.clicked.emit()
            return super(CollapsibleFrame.TitleFrame, self).mousePressEvent(event)

    class Arrow(QFrame):

        def __init__(self, parent=None, collapsed=False):
            super(__class__, self).__init__(parent=parent)

            self.setMaximumSize(24, 24)

            # horizontal == 0
            self._arrow_horizontal = (QtCore.QPointF(7.0, 8.0), QtCore.QPointF(17.0, 8.0), QtCore.QPointF(12.0, 13.0))
            # vertical == 1
            self._arrow_vertical = (QtCore.QPointF(8.0, 7.0), QtCore.QPointF(13.0, 12.0), QtCore.QPointF(8.0, 17.0))
            # arrow
            self._arrow = None
            self.setArrow(int(collapsed))

        def setArrow(self, arrow_direction: int):
            """
            Sets the direction of the arrow.
            :param arrow_direction: the direction of the arrow (0 = horizontal, 1 = vertical).
            """
            if arrow_direction:
                self._arrow = self._arrow_vertical
            else:
                self._arrow = self._arrow_horizontal
            self.repaint()

        def paintEvent(self, event):
            painter = QPainter(self)
            painter.begin(self)
            painter.setBrush(QColor(192, 192, 192))
            painter.setPen(QColor(64, 64, 64))
            painter.drawPolygon(*self._arrow)
            painter.end()
