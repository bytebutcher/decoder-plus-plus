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
from qtpy import QtCore
from qtpy.QtCore import Signal, Qt
from qtpy.QtGui import QPainter, QColor
from qtpy.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QBoxLayout, QSizePolicy, QWidget

from dpp.core import Context
from dpp.ui import HSpacer
from dpp.ui.widget.separater_widget import VSep
from dpp.ui.widget.status_widget import StatusWidget


class CollapsibleFrame(QFrame):
    """
    Frame with ability to un-/collapse content via clickable arrow-handles.
    """

    arrowClicked = Signal()
    upButtonClicked = Signal()
    downButtonClicked = Signal()
    configButtonClicked = Signal()
    closeButtonClicked = Signal()

    def __init__(self, parent, context: Context, frame_id: str):
        """
        Initializes the collapsible frame.
        :param parent: the parent widget of this frame
        """
        super().__init__(parent)
        self._frame_id = frame_id
        self._context = context
        self._logger = context.logger
        self._listener = self._context.listener()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._is_collasped = False
        self._was_collapse_state_changed_by_user = False
        self.arrowClicked.connect(self._arrow_clicked_event)
        self._header_frame = self._init_header_frame()
        self._content = self._init_content(QBoxLayout.LeftToRight, self._is_collasped)
        self._init_frame_style()

        self._layout = QVBoxLayout()
        self._layout.setAlignment(Qt.AlignTop)

        self._layout.addWidget(self._header_frame)
        self._layout.addWidget(self._content)

        self.setLayout(self._layout)

    def id(self) -> str:
        """ Returns the individual identifier of the frame. """
        return self._frame_id

    def isConfigurable(self) -> bool:
        """
        Returns whether the frame is configurable (always False).
        This method needs to be overridden if other behaviour is required.
        """
        return False

    def _init_frame_style(self):
        background_color = self.palette().color(self.backgroundRole())
        self.setStyleSheet(
            "CollapsibleFrame { border:1px solid " + background_color.lighter(
                90).name() + "; background:" + background_color.lighter(99).name() + "; }")

    def _init_header_frame(self):
        header_frame = CollapsibleFrame.HeaderFrame(self)
        header_frame.arrowClicked.connect(self.arrowClicked.emit)
        return header_frame

    def _init_content(self, direction, collapsed):
        content = QFrame(self)
        content_layout = QBoxLayout(direction)
        content_layout.setAlignment(Qt.AlignTop)
        content.setLayout(content_layout)
        content.setVisible(not collapsed)
        return content

    def _arrow_clicked_event(self):
        self.toggleCollapsed()
        # Remember, when user uncollapses the frame manually. This is used to determine whether the
        # frame should be collapsed automatically under certain conditions.
        self._was_collapse_state_changed_by_user = not self.isCollapsed()

    def addWidget(self, widget):
        """
        Adds an widget to the content.
        :param widget: the widget to be added.
        """
        self._content.layout().addWidget(widget)

    def toggleCollapsed(self):
        """ Toggles collapsing of the frame. """
        self._content.setVisible(self._is_collasped)
        self._is_collasped = not self._is_collasped
        self._header_frame._arrow.setArrow(int(self._is_collasped))

    def setCollapsed(self, status):
        """ Un-/collapses the frame. """
        self._content.setVisible(not status)
        self._is_collasped = status
        self._header_frame._arrow.setArrow(int(self._is_collasped))

    def isCollapsed(self) -> bool:
        return self._is_collasped

    def wasCollapseStateChangedByUser(self):
        """ Returns whether the collapse state was changed by the user. """
        return self._was_collapse_state_changed_by_user

    def header(self) -> 'dpp.ui.collapsible_frame.CollapsibleFrame.HeaderFrame':
        return self._header_frame

    def getContentHeight(self) -> int:
        """ Returns the height of the content when uncollapsed. """
        return self._content.height()

    def setContentHeight(self, height: int):
        """ Sets the height of the content when uncollapsed. """
        self._content.setFixedHeight(height)

    class HeaderFrame(QFrame):
        """ Clickable frame with title. """

        class AbstractHeaderFrameItem(QFrame):

            def __init__(self, parent):
                super(__class__, self).__init__(parent)
                self.setContentsMargins(0, 0, 0, 0)
                self.setLayout(QHBoxLayout())
                self.layout().setContentsMargins(0, 0, 0, 0)
                self.layout().setSpacing(0)

            def clearLayout(self):
                while self.layout().count():
                    child = self.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

            def setCentralWidget(self, widget: QWidget):
                self.clearLayout()
                self.layout().addWidget(widget)

            def centralWidget(self) -> QWidget:
                return self.layout().itemAt(0).widget()

            def setStatus(self, status: str, message: str):
                """ Sets a status.
                :param status: The status to set. Either "DEFAULT", "SUCCESS", or "ERROR".
                :param message: The message to set.
                """
                ...

            def refresh(self):
                """ Refreshes the header item. """
                ...

        class VSepItem(AbstractHeaderFrameItem):

            def __init__(self, parent):
                super(__class__, self).__init__(parent)
                self.setCentralWidget(VSep(self))

        class HSpacerItem(AbstractHeaderFrameItem):

            def __init__(self, parent):
                super(__class__, self).__init__(parent)
                self.setCentralWidget(HSpacer(self))

        arrowClicked = Signal()
        upButtonClicked = Signal()
        downButtonClicked = Signal()
        configButtonClicked = Signal()
        closeButtonClicked = Signal()

        def __init__(self, parent: 'ui.widget.CollapsibleFrame'):
            super(__class__, self).__init__(parent)

            self._parent = parent
            self.setMinimumHeight(26)
            self.setMaximumHeight(26)

            self._hlayout = QHBoxLayout()
            self._hlayout.setContentsMargins(0, 0, 0, 0)
            self._hlayout.setSpacing(0)

            self._arrow = None

            self._hlayout.addWidget(self._init_header_frame(parent.isCollapsed()))
            self.setLayout(self._hlayout)
            self.setStyleSheet("QFrame { border:1px solid rgb(41, 41, 41); }")
            self.setStatus(StatusWidget.DEFAULT, '')

        def _init_header_frame(self, collapsed: bool):
            self._frm_header = QFrame(self)
            self._frm_header.setMinimumHeight(24)
            self._frm_header.setMaximumHeight(24)
            frm_header_layout = QHBoxLayout(self)
            frm_header_layout.setContentsMargins(0, 0, 0, 0)
            frm_header_layout.addWidget(self._init_arrow(collapsed))
            background_color = self._frm_header.palette().color(self._frm_header.backgroundRole())
            self._frm_header.setStyleSheet("QFrame { border:0px; background:" + background_color.darker(96).name() + "; }")
            self._frm_header.setLayout(frm_header_layout)
            return self._frm_header

        def _init_arrow(self, collapsed):
            self._arrow = CollapsibleFrame.Arrow(self, collapsed=collapsed)
            self._arrow.setMinimumWidth(24)
            self._arrow.setMaximumWidth(24)
            self._arrow.setStyleSheet("border:0px")
            return self._arrow

        def addWidget(self, header_item: AbstractHeaderFrameItem):
            self._frm_header.layout().addWidget(header_item)

        def refresh(self):
            """ Refreshes the header model (e.g. line-count, character-count, etc.). """
            for i in range(self._frm_header.layout().count()):
                widget = self._frm_header.layout().itemAt(i).widget()
                if isinstance(widget, CollapsibleFrame.HeaderFrame.AbstractHeaderFrameItem):
                    widget.refresh()

        def setStatus(self, status: str, message: str):
            """ Sets a status in the individual header frames. """
            for i in range(self._frm_header.layout().count()):
                widget = self._frm_header.layout().itemAt(i).widget()
                if isinstance(widget, CollapsibleFrame.HeaderFrame.AbstractHeaderFrameItem):
                    widget.setStatus(status, message)

        def mouseReleaseEvent(self, event):
            if self.underMouse() and event.button() == QtCore.Qt.LeftButton:
                # The arrow (or something non-button like) was clicked
                self.arrowClicked.emit()
            return super(CollapsibleFrame.HeaderFrame, self).mousePressEvent(event)

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
            painter.setBrush(QColor(192, 192, 192))
            painter.setPen(QColor(64, 64, 64))
            painter.drawPolygon(*self._arrow)
