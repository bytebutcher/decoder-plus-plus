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


class CollapsibleFrame(QWidget):
    """
    Frame with ability to un-/collapse content via clickable arrow-handles.
    """

    def __init__(self, parent=None, title=None, direction=QBoxLayout.LeftToRight):
        """
        Initializes the collapsible frame.
        :param parent: the parent widget of this frame (default=None).
        :param title: the title to be displayed (default=None).
        :param direction: the direction in which content should be aligned (default=QBoxLayout.LeftToRight).
        """
        super(__class__, self).__init__(parent=parent)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._is_collasped = False
        self._title_frame = None
        self._content, self._content_layout = (None, None)

        self._layout = QVBoxLayout(self)
        self._layout.setAlignment(Qt.AlignTop)
        self._layout.addWidget(self._init_title_frame(title, self._is_collasped))
        self._layout.addWidget(self._init_content(direction, self._is_collasped))

        self._init_collapsable()

    def _init_title_frame(self, title, collapsed):
        self._title_frame = self.TitleFrame(title=title, collapsed=collapsed)
        return self._title_frame

    def _init_content(self, direction, collapsed):
        self._content = QWidget(self)
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

    def setTitle(self, title: str):
        """ Sets the title of the frame. """
        self._title_frame.setTitle(title)

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

        def __init__(self, parent=None, title="", collapsed=False):
            super(__class__, self).__init__(parent=parent)

            self.setMinimumHeight(24)
            self.setMaximumHeight(24)
            self.move(QtCore.QPoint(24, 0))
            self.indicateError(False)

            self._hlayout = QHBoxLayout(self)
            self._hlayout.setContentsMargins(0, 0, 0, 0)
            self._hlayout.setSpacing(0)

            self._arrow = None
            self._title = None

            self._hlayout.addWidget(self._init_arrow(collapsed))
            self._hlayout.addWidget(self._init_title(title))

        def _init_arrow(self, collapsed):
            self._arrow = CollapsibleFrame.Arrow(collapsed=collapsed)
            self._arrow.setStyleSheet("border:0px")
            return self._arrow

        def _init_title(self, title=None):
            self._title = QLabel(title)
            self._title.setMinimumHeight(24)
            self._title.move(QtCore.QPoint(24, 0))
            self._title.setStyleSheet("border:0px")
            return self._title

        def indicateError(self, status: bool):
            """ Indicates an error by painting the title-border red. Otherweise black. """
            if status:
                self.setStyleSheet("border:1px solid red; ")
            else:
                self.setStyleSheet("border:1px solid rgb(41, 41, 41); ")

        def setTitle(self, title: str):
            """ Sets the title of the frame. """
            self._title.setText(title)

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
            painter = QPainter()
            painter.begin(self)
            painter.setBrush(QColor(192, 192, 192))
            painter.setPen(QColor(64, 64, 64))
            painter.drawPolygon(*self._arrow)
            painter.end()
