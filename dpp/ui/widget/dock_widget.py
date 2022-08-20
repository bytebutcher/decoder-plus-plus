# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of Decoder++
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# The code is based on https://github.com/obdasystems/eddy/blob/master/eddy/ui/dock.py
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets
from qtpy.QtGui import QIcon, QCloseEvent
from qtpy.QtWidgets import QTabBar, QDockWidget, QStyle, QApplication, QToolButton, QHBoxLayout, QFrame, QWidget


class DockWidget(QtWidgets.QDockWidget):
    """
    This class implements the container for docking area widgets.
    """

    def __init__(self, title: str, icon: QIcon, parent):
        """
        Initialize the dock widget.
        """
        super().__init__(title, parent, QtCore.Qt.Widget)
        self.icon = icon

        # Add customized title bar widget
        self.title_bar_widget = TitleBarWidget(title, icon, self)
        self.setTitleBarWidget(self.title_bar_widget)

        # Configure main layout
        self._dock_frame = QFrame()
        self._dock_layout = QHBoxLayout()
        self._dock_frame.setLayout(self._dock_layout)
        self.setWidget(self._dock_frame)

        # Setup event listeners
        self.dockLocationChanged.connect(lambda area: self.updateTabBarIcon())
        self.featuresChanged.connect(lambda features: self.title_bar_widget.featuresChangedEvent(features))

    #############################################
    #   Interface
    #############################################

    def addWidget(self, widget: QWidget):
        self._dock_layout.addWidget(widget)

    def addTitleBarButton(self, button):
        """
        Add a button to the right side of the titlebar of this widget.
        :type button: T <= QPushButton|QToolButton
        """
        widget = self.titleBarWidget()
        widget.addButton(button)
        widget.updateLayout()

    def updateTabBarIcon(self):
        """
        Updates the tab bar icon.
        """
        tab_bar = self.parent().findChild(QTabBar, "")
        if tab_bar:
            for index in range(0, tab_bar.count()):
                if self.windowTitle() == tab_bar.tabText(index):
                    tab_bar.setTabIcon(index, self.icon)
                    break

    def hide(self):
        """ Hides the dock. """
        self._dock_frame.setVisible(False)

    def show(self):
        """ Shows the dock. """
        self._dock_frame.setVisible(True)

    #############################################
    #   Events
    #############################################

    def closeEvent(self, event: QCloseEvent):
        """ Closes the dock. """
        self.hide()


class TitleBarWidget(QtWidgets.QWidget):
    """
    This class implements the title area of docking area widgets.
    """
    def __init__(self, title: str, icon: QIcon, parent):
        """ Initialize the widget. """
        super().__init__(parent)

        # Create title bar icon and title
        self.imageLabel = QtWidgets.QLabel(self)
        self.imageLabel.setPixmap(icon.pixmap(18))
        self.imageLabel.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.imageLabel.setContentsMargins(0, 0, 0, 0)
        self.imageLabel.setFixedSize(18, 18)
        self.titleLabel = QtWidgets.QLabel(title, self)
        self.titleLabel.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.titleLabel.setContentsMargins(4, 0, 0, 0)

        # Create standard buttons
        iconSize = QApplication.style().standardIcon(
            QStyle.SP_TitleBarNormalButton).actualSize(
            QtCore.QSize(100, 100))
        buttonSize = iconSize + QtCore.QSize(4, 4)

        self.dockButton = QToolButton(self)
        self.dockButton.setIcon(QApplication.style().standardIcon(
            QStyle.SP_TitleBarNormalButton))
        self.dockButton.setMaximumSize(buttonSize)
        self.dockButton.setAutoRaise(True)
        self.dockButton.clicked.connect(self.toggleFloating)

        self.closeButton = QToolButton(self)
        self.closeButton.setMaximumSize(buttonSize)
        self.closeButton.setAutoRaise(True)
        self.closeButton.setIcon(QApplication.style().standardIcon(
            QStyle.SP_DockWidgetCloseButton))
        self.closeButton.clicked.connect(self.parent().close)
        self.buttons = [self.dockButton, self.closeButton]

        # Configure layout
        self.mainLayout = QtWidgets.QHBoxLayout(self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)
        self.setContentsMargins(6, 4, 6, 4)
        self.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)
        self.updateLayout()

    #############################################
    #   Interface
    #############################################

    def addButton(self, button):
        """
        Add a button to the right side of the titlebar, before the close button.
        :type button: T <= QPushButton|QToolButton
        """
        self.buttons.insert(0, button)

    def toggleFloating(self):
        """
        Toggles floating.
        """
        self.parent().setFloating(not self.parent().isFloating())

    def updateLayout(self):
        """
        Redraw the widget by updating its layout.
        """
        # CLEAR CURRENT LAYOUT
        for i in reversed(range(self.mainLayout.count())):
            item = self.mainLayout.itemAt(i)
            self.mainLayout.removeItem(item)
        # DISPOSE NEW ELEMENTS
        self.mainLayout.addWidget(self.imageLabel, 0, QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.mainLayout.addWidget(self.titleLabel, 1, QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        for button in self.buttons:
            self.mainLayout.addWidget(button, 0, QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)

    #############################################
    #   Events
    #############################################

    def featuresChangedEvent(self, features):
        """
        Updates the features of the title bar widget.
        :param features: const
        """

        def _value(item):
            # BUG: In PyQt6 QDockWidget.DockWidgetFeature(s) need to be accessed via value attribute.
            # SOLUTION: Handle access to QDockWidget.DockWidgetFeatures according to current PyQt version.
            return item.value if hasattr(item, 'value') else item

        self.dockButton.setVisible(_value(features) & _value(QDockWidget.DockWidgetFloatable))
        self.closeButton.setVisible(_value(features) & _value(QDockWidget.DockWidgetClosable))

    def mouseDoubleClickEvent(self, mouseEvent):
        """
        Executed when the mouse is double-clicked on the widget.
        :type mouseEvent: QMouseEvent
        """
        pass

    def paintEvent(self, paintEvent):
        """
        This is needed for the widget to pick the stylesheet.
        :type paintEvent: QPaintEvent
        """
        option = QtWidgets.QStyleOption()
        option.initFrom(self)
        painter = QtGui.QPainter(self)
        style = self.style()
        style.drawPrimitive(QtWidgets.QStyle.PE_Widget, option, painter, self)
