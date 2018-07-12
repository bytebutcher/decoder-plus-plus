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

from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QFrame, QComboBox, QVBoxLayout

from core.command import Command
from core.command.command import NullCommand
from ui.widget.combo_box import ComboBox


class ComboBoxFrame(QFrame):

    titleSelected = pyqtSignal()
    commandSelected = pyqtSignal('PyQt_PyObject')

    def __init__(self, parent, context):
        super(ComboBoxFrame, self).__init__(parent)
        self._context = context
        self._commands = context.commands()
        self._logger = context.logger()
        self._command_history = {}
        layout = QVBoxLayout()
        self._decoder_combo = self._init_combo_box("Decode as ...", Command.Type.DECODER)
        self._encoder_combo = self._init_combo_box("Encode as ...", Command.Type.ENCODER)
        self._hasher_combo = self._init_combo_box("Hash ...", Command.Type.HASHER)
        self._script_combo = self._init_combo_box("Script ...", Command.Type.SCRIPT)
        self._combo_boxes = {
            Command.Type.DECODER: self._decoder_combo,
            Command.Type.ENCODER: self._encoder_combo,
            Command.Type.HASHER: self._hasher_combo,
            Command.Type.SCRIPT: self._script_combo
        }
        layout.addWidget(self._decoder_combo)
        layout.addWidget(self._encoder_combo)
        layout.addWidget(self._hasher_combo)
        layout.addWidget(self._script_combo)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def _init_combo_box(self, title, type):
        combo_box = ComboBox()
        combo_box.setEditable(True)
        combo_box.setInsertPolicy(QComboBox.NoInsert)
        model = QStandardItemModel()

        model.setItem(0, 0, QStandardItem(title))
        item_list = self._commands.names(type)
        for index, name in enumerate(item_list):
            model.setItem(index + 1, 0, QStandardItem(name))
        combo_box.lineEdit().returnPressed.connect(lambda: self._combo_box_enter_pressed_event(type))
        # BUG: combo_box.lineEdit().selectAll when focussing lineEdit will be deselected again by general focus-event.
        # WORKAROUND: Delay select-all for a few milliseconds.
        combo_box.focusInEvent = lambda e: QTimer.singleShot(100, lambda: combo_box.lineEdit().selectAll())
        combo_box.setModel(model)
        combo_box.setModelColumn(0)
        combo_box.activated.connect(lambda i: self._combo_box_item_selected_event(type, combo_box.currentIndex()))
        return combo_box

    def _combo_box_enter_pressed_event(self, type):
        combo_box = self._combo_boxes[type]
        current_text = combo_box.currentText()
        self.selectItem(type, current_text, block_signals=False)

    def _combo_box_item_selected_event(self, type, index):
        self.resetExceptType(type)
        # Remove frames below when title element was selected
        if index is 0:
            self.titleSelected.emit()
            return

        command = self.getCommandByTypeAndIndex(type, index)
        if command in self._command_history:
            self._logger.debug("Command in history ...")
            command = self._command_history[command]
        else:
            self._logger.debug("Command added to history ...")
            self._command_history[command] = command
        self.commandSelected.emit(command)

        # BUG: Item gets deselected when running dialogs.
        # WORKAROUND: Reselect Item
        self._reselect_item(index, type)

    def _reselect_item(self, index, type):
        combo_box = self._combo_boxes[type]
        combo_box.blockSignals(True)
        combo_box.setCurrentIndex(index)
        combo_box.blockSignals(False)

    def getCommandByTypeAndIndex(self, type, index):
        try:
            combo_box = self._combo_boxes[type]
            name = combo_box.itemText(index)
            command = self._commands.command(name, type)
            return command
        except Exception as e:
            self._logger.error("Unexpected error. {}".format(e))
            return NullCommand()

    def addCommand(self, command, block_signals=False):
        combo_box = self._combo_boxes[command.type()]
        combo_box.blockSignals(block_signals)
        model = combo_box.model()
        model.setItem(model.rowCount(), 0, QStandardItem(command.name()))
        combo_box.blockSignals(False)
        self._commands.add(command)

    def selectedCommand(self):
        selected_command_types = [command_type for command_type in self._combo_boxes.keys() if self._combo_boxes[command_type].currentIndex() != 0]
        if len(selected_command_types) == 1:
            selected_command_type = selected_command_types[0]
            selected_combo_box = self._combo_boxes[selected_command_type]
            selected_index = selected_combo_box.currentIndex()
            return self.getCommandByTypeAndIndex(selected_command_type, selected_index)

    def selectItem(self, type, command_name, block_signals=False):
        combo_box = self._combo_boxes[type]
        for i in range(combo_box.count()):
            if combo_box.itemText(i) == command_name:
                combo_box.blockSignals(block_signals)
                combo_box.setCurrentIndex(i)
                combo_box.blockSignals(False)
                break

    def focusType(self, type):
        self._combo_boxes[type].setFocus()

    def reset(self, *combo_boxes, **kwargs):
        for combo_box in combo_boxes:
            combo_box.blockSignals(True)
            combo_box.setCurrentIndex(0)
            combo_box.blockSignals(False)

    def resetExceptType(self, type):
        for command_type in self._combo_boxes.keys():
            if command_type is not type:
                self.reset(self._combo_boxes[command_type])

    def resetAll(self):
        self.reset(self._decoder_combo, self._encoder_combo, self._hasher_combo, self._script_combo)

    def setToolTipByCommandType(self, command_type, tooltip):
        # BUG: Tooltip is not setup as expected.
        # WORKAROUND: Use the decoder/encoder/hasher/script method.
        # TODO: Workaround breaks design. Combo-boxes should not leave this object.
        if not command_type in self._combo_boxes.keys():
            self._logger.error("Unknown command type '{}'. Can not set tooltip to {}.".format(command_type, tooltip))
            return
        self._combo_boxes[command_type].setToolTip(tooltip)

    def decoder(self):
        return self._decoder_combo

    def encoder(self):
        return self._encoder_combo

    def hasher(self):
        return self._hasher_combo

    def script(self):
        return self._script_combo