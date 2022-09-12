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
import copy

from qtpy.QtCore import QTimer, Signal
from qtpy.QtGui import QStandardItemModel, QStandardItem
from qtpy.QtWidgets import QFrame, QComboBox, QVBoxLayout

import dpp
from dpp.core.plugin import NullPlugin
from dpp.core.plugin import PluginType
from dpp.ui.widget.combo_box import ComboBox


class ComboBoxFrame(QFrame):
    pluginDeselected = Signal(str)  # combo_box_type
    pluginSelected = Signal(str, int, 'PyQt_PyObject')  # combo_box_type, combo_box_index, plugin

    def __init__(self, parent, context):
        super(ComboBoxFrame, self).__init__(parent)
        self._context = context
        self._plugins = context.plugins()
        self._plugin_history = {}
        layout = QVBoxLayout()
        self._decoder_combo = self._init_combo_box("Decode as ...", PluginType.DECODER)
        self._encoder_combo = self._init_combo_box("Encode as ...", PluginType.ENCODER)
        self._hasher_combo = self._init_combo_box("Hash ...", PluginType.HASHER)
        self._script_combo = self._init_combo_box("Script ...", PluginType.SCRIPT)
        self._combo_boxes = {
            PluginType.DECODER: self._decoder_combo,
            PluginType.ENCODER: self._encoder_combo,
            PluginType.HASHER: self._hasher_combo,
            PluginType.SCRIPT: self._script_combo
        }
        layout.addWidget(self._decoder_combo)
        layout.addWidget(self._encoder_combo)
        layout.addWidget(self._hasher_combo)
        layout.addWidget(self._script_combo)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self._combo_box_selection_history = []

    def _init_combo_box(self, plugin_title: str, plugin_type: str):
        combo_box = ComboBox()
        combo_box.setEditable(True)
        combo_box.setInsertPolicy(QComboBox.NoInsert)
        model = QStandardItemModel()

        model.setItem(0, 0, QStandardItem(plugin_title))
        # Do not load disabled plugins and plugins with unresolved dependencies into the combobox.
        plugin_list = [plugin for plugin in self._plugins.filter(type=plugin_type) if plugin.is_enabled() and not plugin.check_dependencies()]
        for index, plugin in enumerate(plugin_list):
            item = QStandardItem(plugin.name)
            item.setToolTip(plugin.__doc__)
            model.setItem(index + 1, 0, item)
        combo_box.lineEdit().returnPressed.connect(lambda: self._combo_box_enter_pressed_event(plugin_type))
        # BUG: combo_box.lineEdit().selectAll when focussing lineEdit will be deselected again by general focus-event.
        # FIX: Delay select-all for a few milliseconds.
        combo_box.focusInEvent = lambda e: QTimer.singleShot(100, lambda: combo_box.lineEdit().selectAll())
        # BUG: combo_box.lineEdit().deselect does not work correctly when loosing focus.
        # FIX: Delay deselect for a few milliseconds.
        combo_box.focusOutEvent = lambda e: QTimer.singleShot(100, lambda: combo_box.lineEdit().deselect())
        combo_box.setModel(model)
        combo_box.setModelColumn(0)
        combo_box.activated.connect(lambda i: self._combo_box_item_selected_event(plugin_type, combo_box.currentIndex()))
        return combo_box

    def _combo_box_enter_pressed_event(self, combo_box_type: str):
        combo_box = self._combo_boxes[combo_box_type]
        current_text = combo_box.currentText()
        self._combo_box_selection_history.append([combo_box_type, combo_box.index()])
        self.selectItem(combo_box_type, current_text, block_signals=False)

    def _combo_box_item_selected_event(self, combo_box_type: str, combo_box_index: int):
        self.resetExceptType(combo_box_type)
        if combo_box_index == 0:
            # Remove frames below when title element was selected
            # Note: It does not matter which combo box is the source, since all combo boxes are going to reset
            # to index 0.
            self.pluginDeselected.emit(combo_box_type)
            return

        self._combo_box_selection_history.append([combo_box_type, combo_box_index])
        plugin = self.getPluginByTypeAndIndex(combo_box_type, combo_box_index)
        self.pluginSelected.emit(combo_box_type, combo_box_index, plugin)

    def reselectLastItem(self, block_signals=True):
        # Always reset everything first.
        self.resetAll()
        if len(self._combo_box_selection_history) > 1:
            # Reselect previous item if any.
            type, index = self._combo_box_selection_history[-2]
            self.reselectItem(index, type, block_signals)

    def reselectItem(self, index: int, plugin_type: str, block_signals=True):
        combo_box = self._combo_boxes[plugin_type]
        combo_box.blockSignals(block_signals)
        combo_box.setCurrentIndex(index)
        combo_box.blockSignals(False)

    def getPluginByTypeAndIndex(self, plugin_type: str, index: int) -> dpp.core.plugin.AbstractPlugin:
        try:
            combo_box = self._combo_boxes[plugin_type]
            name = combo_box.itemText(index)
            plugin = copy.deepcopy(self._plugins.plugin(name, plugin_type))
            if plugin in self._plugin_history:
                plugin = self._plugin_history[plugin]
            else:
                self._plugin_history[plugin] = plugin
            return plugin
        except Exception as e:
            self._context.logger.error("Unexpected error. {}".format(e))
            return NullPlugin(self._context)

    def selectedPlugin(self) -> dpp.core.plugin.AbstractPlugin:
        selected_plugin_types = [plugin_type for plugin_type in self._combo_boxes.keys() if self._combo_boxes[plugin_type].currentIndex() != 0]
        if len(selected_plugin_types) == 1:
            selected_plugin_type = selected_plugin_types[0]
            selected_combo_box = self._combo_boxes[selected_plugin_type]
            selected_index = selected_combo_box.currentIndex()
            return self.getPluginByTypeAndIndex(selected_plugin_type, selected_index)
        else:
            return NullPlugin(self._context)

    def selectItem(self, plugin_type: str, plugin_name: str, block_signals=False):
        if not plugin_type and not plugin_name:
            self.resetAll()
            return

        self.resetExceptType(plugin_type)
        combo_box = self._combo_boxes[plugin_type]
        for i in range(combo_box.count()):
            if combo_box.itemText(i) == plugin_name:
                combo_box.blockSignals(block_signals)
                combo_box.setCurrentIndex(i)
                combo_box.blockSignals(False)
                break

    def focusType(self, combo_box_type: str):
        """ Focues the combo-box associated with the specified type (e.g. PluginType.DECODER, ...). """
        self._combo_boxes[combo_box_type].setFocus()

    def _reset(self, *combo_boxes, **kwargs):
        """ Resets a list of combo-boxes. """
        for combo_box in combo_boxes:
            combo_box.blockSignals(True)
            combo_box.setCurrentIndex(0)
            combo_box.blockSignals(False)

    def resetExceptType(self, combo_box_type: str):
        """ Resets all combo-boxes except the specified type (e.g. PluginType.DECODER, ...). """
        for _combo_box_type in self._combo_boxes.keys():
            if _combo_box_type != combo_box_type:
                self._reset(self._combo_boxes[_combo_box_type])

    def resetAll(self):
        """ Resets all combo-boxes to show the first element. """
        self._context.logger.debug("ComboBoxFrame:ResetAll")
        self._reset(self._decoder_combo, self._encoder_combo, self._hasher_combo, self._script_combo)

    def setToolTip(self, tooltip: str, combo_box_type: str = None):
        """ Setup's the tooltip of the combo-box associated with the specified plugin-type.
        :param tooltip: the tooltip to show.
        :param combo_box_type: the plugin-type which is associated with the combo-box (e.g. PluginType.DECODER, ...).
        """
        assert combo_box_type is not None, 'No combo box type was specified!'
        assert combo_box_type in self._combo_boxes.keys(), 'Illegal combo box type!'
        self._combo_boxes[combo_box_type].setToolTip(tooltip)
