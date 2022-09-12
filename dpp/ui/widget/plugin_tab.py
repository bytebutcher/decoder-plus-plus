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
from typing import List

from qtpy import QtCore
from qtpy.QtCore import Signal, QModelIndex, QEvent
from qtpy.QtGui import QStandardItem, QBrush
from qtpy.QtWidgets import QVBoxLayout, QFrame, QHBoxLayout

from dpp.core import Context
from dpp.core.icons import Icon, icon
from dpp.core.plugin.manager import PluginManager
from dpp.ui.widget import ListWidget, SearchField
from dpp.ui.widget.dyna_frame import DynaFrame
from dpp.ui.widget.plugin_frame import PluginFrame


class PluginSelectionFrame(QFrame):
    """ Encapsulates the SearchField and ListWidget. """

    enterPressed = Signal()
    arrowPressed = Signal()
    selectionChanged = Signal('PyQt_PyObject')
    itemChanged = Signal('PyQt_PyObject')
    textChanged = Signal('PyQt_PyObject')

    def __init__(self, context: Context, plugins: PluginManager, parent=None):
        """
        Initializes the Plugin Selection Frame.
        :param context: the context of the application.
        :param plugins: the plugins to display.
        """
        super(__class__, self).__init__(parent)
        self._context = context
        self._plugins = plugins

        base_layout = QVBoxLayout()

        self._search_field = SearchField(self)
        self._search_field.setPlaceholderText("Search plugin...")
        self._search_field.setIcon(icon(Icon.SEARCH))
        self._search_field.enterPressed.connect(self._on_search_field_enter_key_pressed)
        self._search_field.arrowPressed.connect(self._on_search_field_arrow_pressed)
        self._search_field.textChanged.connect(self._on_search_field_text_changed)

        base_layout.addWidget(self._search_field)

        self._list_widget = ListWidget()
        self._list_widget.clicked.connect(self._show_item)
        self._list_widget.doubleClicked.connect(
            # Signals that user wishes to add this command.
            lambda: self.enterPressed.emit()
        )

        self._list_widget.dataChanged = self._on_list_widget_data_changed
        self._list_widget.selectionModel().selectionChanged.connect(self._show_item)
        self._list_widget.keyPressed.connect(self._on_list_widget_key_pressed)

        self._init_list_items()
        self._list_widget.select_item_by_index(0)

        self.itemChanged.connect(self.__on_list_widget_item_changed)

        base_layout.addWidget(self._list_widget)

        self.setLayout(base_layout)
        self.setMinimumWidth(self._list_widget.sizeHintForColumn(0) + 40)
        self.setMaximumWidth(self._list_widget.sizeHintForColumn(0) + 40)

    def _init_list_items(self):
        """ Add all plugins into a list. """
        for plugin in sorted(self._plugins, key=lambda x: getattr(x, '_name')):
            name = plugin.full_name
            item = QStandardItem(name)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
            dependencies = plugin.check_dependencies()
            if dependencies:
                # Highlight plugins with unresolved dependencies
                item.setForeground(QBrush(QtCore.Qt.red, QtCore.Qt.SolidPattern))
                # Prevent user from enabling plugins with missing dependencies.
                item.setCheckable(False)

            if not dependencies and plugin.is_enabled():
                # Set the checkbox when plugins are enabled
                item.setCheckState(QtCore.Qt.Checked)
            else:
                # Unset the checkbox when plugins are enabled
                item.setCheckState(QtCore.Qt.Unchecked)
            self._list_widget.addItem(item)

    def __on_list_widget_item_changed(self, list_item: QStandardItem):
        """ Catches when items check-box was triggered. Enables/disables plugin. """
        if list_item:
            status = list_item.checkState() == QtCore.Qt.Checked
            name = list_item.text()
            plugin = self._get_item_by_name(name)
            plugin.set_enabled(status)

    def _get_item_by_name(self, name: str):
        """ Returns the plugin matching the name, otherwise None. """
        for plugin in self._plugins:
            if plugin.full_name == name:
                return plugin
        return None

    def _get_item_names(self):
        """ Returns all plugin names in a list. """
        return [plugin.full_name for plugin in self._plugins]

    def setFocus(self):
        """ Overrides the setFocus method to focus the command list widget instead of the meaningless frame. """
        self._list_widget.setFocus()

    def _show_item(self, index):
        """ Triggers the selectionChanged event with the selected command as parameter. """
        if len(self._list_widget.selectedIndexes()) > 0:
            # BUG: When list is filtered by text the emitted index does not correspond to the correct item.
            # NOTE: List uses SortFilterProxyProxyModel to implement search filter.
            # EXAMPLE:
            #   10 items in real list. 3 items in proxy list due to search filter.
            #   1st item in proxy list corresponds to 1st item in real list.
            #   2nd item in proxy list corresponds to 7th item in real list.
            #   3rd item in proxy list corresponds to 9th item in real list.
            #   When clicking the 2nd item in proxy list the text of the 7th item of the real list should be printed.
            # FIX: Map proxy index to controller index.
            item_index = self._list_widget.model().mapToSource(self._list_widget.selectedIndexes()[0]).row()
            item_name = self._list_widget.item(item_index).text()
            item = self._get_item_by_name(item_name)
            self.selectionChanged.emit(item)

    def _on_search_field_enter_key_pressed(self):
        """ When enter is pressed in the search field, the matching item is selected in the list widget. """
        self._list_widget.select_item_by_text(self._search_field.text())

    def _on_search_field_arrow_pressed(self):
        """ When an arrow-key is pressed in the search field, the list widget will gets the focus. """
        self._list_widget.setFocus(True)

    def _on_list_widget_key_pressed(self, evt: QEvent):
        """
        When a key was pressed in the list widget (except enter- and arrow-keys), the focus will be switched
        to the search field to enable the user to enter search terms without manually switching fields.
        """
        self._search_field.setFocus()
        self._search_field.setText("")
        self._search_field.keyPressEvent(evt)

    def _on_list_widget_data_changed(self, topLeft: QModelIndex, bottomRight: QModelIndex, roles: List[int]):
        """ Retriggers the item-changed event containing the corresponding item. """
        self.itemChanged.emit(self._list_widget.item(topLeft.row()))

    def _on_search_field_text_changed(self, text: str):
        """ Filters the text in the list widget based on content of search-field. """
        self._list_widget.model().setFilterRegExp(text)
        self.textChanged.emit(text)


class PluginTab(QFrame):
    """
    Frame containing a searchable check-list of plugins and a frame displaying info about the currently
    selected plugin.
    """

    enterPressed = Signal()

    def __init__(self, context, parent=None):
        """ Initializes the plugin tab. """
        super(__class__, self).__init__(parent)
        self._context = context
        self._plugins = context.plugins()
        self._plugin_selection_frame = PluginSelectionFrame(context, self._plugins, self)

        base_layout = QVBoxLayout()
        inner_widget = QFrame(self)
        inner_layout = QHBoxLayout()
        self._plugin_selection_frame.enterPressed.connect(self._on_enter_pressed)
        self._plugin_selection_frame.selectionChanged.connect(self._select_frame)

        inner_layout.addWidget(self._plugin_selection_frame)
        self._dynamic_frame = DynaFrame(self, self._get_frame_by_selection(None))
        inner_layout.addWidget(self._dynamic_frame)
        inner_widget.setLayout(inner_layout)
        base_layout.addWidget(inner_widget)

        base_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(base_layout)
        self._plugin_selection_frame.setFocus()

    def _on_enter_pressed(self):
        """ Triggeres the enter-pressed event. """
        self.enterPressed.emit()

    def _select_frame(self, selection):
        """ Sets the widget based on the current selection. """
        self._dynamic_frame.setWidget(self._get_frame_by_selection(selection))

    def _get_frame_by_selection(self, selected_plugin=None) -> PluginFrame:
        """ Returns the frame based on the selected plugin. """
        if selected_plugin is None:
            # There should always be at least one plugin in the list.
            selected_plugin = self._plugins[0]
        return PluginFrame(self._context, selected_plugin)
