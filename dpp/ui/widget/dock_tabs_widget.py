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
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QDockWidget, QTabBar, QMainWindow, QWidget


class DockTabsWidget(QWidget):
    """ A helper widget which allows managing multiple dock widgets in tabs. """

    def __init__(self, parent: QMainWindow, context: 'core.context.Context'):
        super().__init__(parent)
        self._context = context
        self._plugins = context.plugins()
        self._parent = parent

        self._dock_widgets = {}

        # Initialize empty dock
        self._empty_dock = QDockWidget("", self._parent)
        self._empty_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self._parent.addDockWidget(Qt.BottomDockWidgetArea, self._empty_dock)
        self._empty_dock.visibilityChanged.connect(lambda event: self.toggleDockWidget())

        # Initialize dock tab bar
        self._dock_tab_bar = self.tabBar()
        self._dock_tab_bar.tabBarDoubleClicked.connect(lambda e: self._empty_dock.raise_())
        # Do only dock tab bar on startup
        self._empty_dock.raise_()

    def tabBar(self) -> QTabBar:
        """
        Returns the tab bar of the docks widget.

        Note, that QMainWindow does not provide a public interface to access the tab bar and that the tab bar is only
        accessible when more than two dock widgets were added and tabified. Since initially there is only have one dock
        widget present we temporarily add another dock widget (shadow dock) and remove it after retrieving the tab bar.
        """
        shadow_dock = QDockWidget("", self._parent)
        self._parent.addDockWidget(Qt.BottomDockWidgetArea, shadow_dock)
        self._parent.tabifyDockWidget(self._empty_dock, shadow_dock)
        tabBar = self._parent.findChild(QTabBar, "")
        self._parent.removeDockWidget(shadow_dock)
        return tabBar

    def registerDockWidget(self, name, dock_widget):
        """ Registers a new dock widget by name. """
        if name in self._dock_widgets:
            raise Exception(f'Dock {name} is already registered!')
        dock_widget.setFeatures(QDockWidget.DockWidgetFloatable)
        self._parent.addDockWidget(Qt.BottomDockWidgetArea, dock_widget)
        self._parent.tabifyDockWidget(self._empty_dock, dock_widget)
        dock_widget.visibilityChanged.connect(lambda event: self.toggleDockWidget())
        self._empty_dock.raise_()
        self._dock_widgets[name] = dock_widget

    def dockWidget(self, name) -> QWidget:
        """ Returns the dock widget matching the name. """
        if name not in self._dock_widgets:
            raise Exception(f'Dock widget "{name}" was never registered!')
        return self._dock_widgets[name]

    def toggleDockWidget(self, name: str = None):
        """ Toggles a single dock widget or all dock widgets if no name is specified. """
        if name:
            self._toggle_dock_widget(name)
        else:
            self._toggle_dock_widgets()

    def _toggle_dock_widget(self, name):
        """ Toggles a single dock widget. """
        dock_widget = self.dockWidget(name)
        if not self.isDockWidgetVisible(name):
            dock_widget.raise_()
        else:
            self._empty_dock.raise_()

    def _toggle_dock_widgets(self):
        """
        Shows/Hides the docks so either only the tab bar or the dock widget area and the tab bar are visible.
        This function ensures that the central widget is resized accordingly when the empty_dock gets selected
        by hiding all (other) widgets.
        """
        is_empty_dock_visible = not self._empty_dock.visibleRegion().isEmpty()
        for dock in self._dock_widgets.values():
            if is_empty_dock_visible:
                if not dock.isFloating():
                    dock.hide()
            else:
                dock.show()

    def isDockWidgetVisible(self, name) -> bool:
        """ Returns whether the specified dock widget is visible. """
        return not self.dockWidget(name).visibleRegion().isEmpty()
