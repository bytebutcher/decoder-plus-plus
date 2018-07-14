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
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QGroupBox, QRadioButton

from core import Context
from core.exception import AbortedException
from ui.combo_box_frame import ComboBoxFrame
from ui.view.plain_view import PlainView
from ui.view.hex_view import HexView
from ui.widget.status_widget import StatusWidget


class CodecFrame(QFrame):

    def __init__(self, parent, context, frame_id, codec_tab, commands, previous_frame, text):
        super(CodecFrame, self).__init__(parent)
        self._context = context
        self._context.shortcutUpdated.connect(self._shortcut_updated_event)
        self._init_logger(context, frame_id)
        self._frame_id = frame_id
        self._codec_tab = codec_tab
        self._previous_frame = previous_frame
        if previous_frame:
            previous_frame.setNext(self)
        self._next_frame = None
        self._commands = commands
        self._flash_event = None

        self._layout = QHBoxLayout(self)
        self._status_widget = StatusWidget(self)
        input_frame = self._init_input_frame(text)
        button_frame = self._init_button_frame()

        self._group_box = QGroupBox()
        group_box_layout = QHBoxLayout()
        group_box_layout.addWidget(self._status_widget)
        group_box_layout.addWidget(input_frame)
        group_box_layout.addWidget(button_frame, 0, Qt.AlignTop)
        self._group_box.setLayout(group_box_layout)

        _, top, _, bottom = self._layout.getContentsMargins()
        self._layout.addWidget(self._group_box)
        self.setLayout(self._layout)

    """
    Initializes the logger. Encapsulates logger-instance to enhance standard-logging with frame-id.
    """
    def _init_logger(self, context, frame_id):
        self._logger = context.logger()
        # BUG: Using logging with custom field frame_id does not work correctly.
        # WORKAROUND: ???
        #self._logger = context.logger(log_format="%(module)s: %(frame_id)d: %(lineno)d: %(msg)s",log_fields={'frame_id': frame_id})

    def _init_input_frame(self, text):
        input_frame = QFrame()
        frame_layout = QVBoxLayout()
        self._plain_view_widget = PlainView(text)
        self._plain_view_widget.textChanged.connect(self._text_changed_event)
        self._plain_view_widget = self._plain_view_widget
        frame_layout.addWidget(self._plain_view_widget)
        frame_layout.setContentsMargins(0, 6, 6, 6)

        self._hex_view_widget = HexView(self, self._context, self._frame_id, self.getInputText())
        self._hex_view_widget.textChanged.connect(self._hex_view_text_changed_event)
        self._hex_view_widget.setHidden(True)
        frame_layout.addWidget(self._hex_view_widget)
        input_frame.setLayout(frame_layout)
        return input_frame

    def _init_button_frame(self):
        button_frame = QFrame()
        button_frame_layout = QVBoxLayout()
        self._combo_box_frame = ComboBoxFrame(self, self._context)
        self._combo_box_frame.titleSelected.connect(self._combo_box_title_selected_event)
        self._combo_box_frame.commandSelected.connect(self._execute_command_select)
        button_frame_layout.addWidget(self._combo_box_frame)
        button_frame_layout.addWidget(self._init_radio_frame())
        button_frame.setLayout(button_frame_layout)
        return button_frame

    def _init_radio_frame(self):
        radio_frame = QFrame()
        radio_frame_layout = QHBoxLayout()
        self._plain_radio = QRadioButton("Plain")
        self._plain_radio.setChecked(True)
        self._plain_radio.toggled.connect(self._view_radio_button_toggle_event)
        self._hex_radio = QRadioButton("Hex")
        self._hex_radio.toggled.connect(self._view_radio_button_toggle_event)
        radio_frame_layout.addWidget(self._plain_radio)
        radio_frame_layout.addWidget(self._hex_radio)
        radio_frame.setLayout(radio_frame_layout)
        return radio_frame

    def _shortcut_updated_event(self, shortcut):
        id = shortcut.id()
        tooltip = self._get_tooltip_by_shortcut(shortcut)
        if id == Context.Shortcut.FOCUS_DECODER:
            self._combo_box_frame.decoder().setToolTip(tooltip)
        elif id == Context.Shortcut.FOCUS_ENCODER:
            self._combo_box_frame.encoder().setToolTip(tooltip)
        elif id == Context.Shortcut.FOCUS_HASHER:
            self._combo_box_frame.hasher().setToolTip(tooltip)
        elif id == Context.Shortcut.FOCUS_SCRIPT:
            self._combo_box_frame.script().setToolTip(tooltip)
        elif id == Context.Shortcut.SELECT_PLAIN_VIEW:
            self._plain_radio.setToolTip(tooltip)
        elif id == Context.Shortcut.SELECT_HEX_VIEW:
            self._hex_radio.setToolTip(tooltip)
        else:
            return
        self._logger.debug("Updated tooltip within codec-frame for {id} to {tooltip}".format(id=id, tooltip=tooltip))

    def _update_tooltip(self, the_widget, the_shortcut_id):
        tooltip = self._get_tooltip_by_shortcut_id(the_shortcut_id)
        the_widget.setToolTip(tooltip)

    def _get_tooltip_by_shortcut_id(self, the_shortcut_id):
        shortcut = self._context.getShortcutById(the_shortcut_id)
        return self._get_tooltip_by_shortcut(shortcut)

    def _get_tooltip_by_shortcut(self, shortcut):
        return "{description} ({shortcut_key})".format(description=shortcut.name(), shortcut_key=shortcut.key())

    def _combo_box_title_selected_event(self):
        self._codec_tab.removeFrames(self._next_frame)
        self.focusInputText()

    def _view_radio_button_toggle_event(self):
        self._plain_view_widget.setVisible(self._plain_radio.isChecked())
        self._hex_view_widget.setVisible(self._hex_radio.isChecked())
        # BUG: Performance Issue When Updating Multiple HexView-Frames During Input Text Changes
        # WORKAROUND: Do only update HexView when it's visible
        if self._hex_radio.isChecked():
            input = self._plain_view_widget.toPlainText()
            self._hex_view_widget.blockSignals(True)
            self._hex_view_widget.setData(input)
            self._hex_view_widget.blockSignals(False)

    def _text_changed_event(self):
        # BUG: Performance Issue When Updating Multiple HexView-Frames When Input Text Changes
        # WORKAROUND: Do only update HexView when it's visible
        if self._hex_view_widget.isVisible():
            input = self._plain_view_widget.toPlainText()
            self._hex_view_widget.blockSignals(True)
            self._hex_view_widget.setData(input)
            self._hex_view_widget.blockSignals(False)
        self._status_widget.setStatus("DEFAULT")
        self._execute()

    def _hex_view_text_changed_event(self, new_text):
        input = new_text
        self._plain_view_widget.blockSignals(True)
        self._plain_view_widget.setPlainText(input)
        self._plain_view_widget.blockSignals(False)
        self._status_widget.setStatus("DEFAULT")
        self._execute()

    def _execute(self):
        command = self._combo_box_frame.selectedCommand()
        if command:
            self._execute_command_run(command)

    def _execute_command_run(self, command):
        input = self.getInputText()
        output = ""
        try:
            output = command.run(input)
            self._codec_tab.newFrame(output, command.title(), self, status=StatusWidget.SUCCESS)
        except Exception as e:
            error = str(e)
            self._logger.error('{} {}: {}'.format(command.name(), command.type(), str(e)))
            self._codec_tab.newFrame(output, command.title(), self, status=StatusWidget.ERROR, msg=error)

    def _execute_command_select(self, command):
        output = ""
        try:
            input = self.getInputText()
            output = command.select(input)
            self._codec_tab.newFrame(output, command.title(), self, status=StatusWidget.SUCCESS)
        except AbortedException as e:
            # User aborted selection. This usually happens when a user clicks the cancel-button within a codec-dialog.
            self._logger.debug(str(e))
        except Exception as e:
            error = str(e)
            self._logger.error('{} {}: {}'.format(command.name(), command.type(), error))
            self._codec_tab.newFrame(output, command.title(), self, status=StatusWidget.ERROR, msg=error)

    def flashStatus(self, status, message):
        self._status_widget.setStatus(status, message)

    def selectComboBoxEntryByCommand(self, command):
        self._combo_box_frame.selectItem(command.type(), command.name(), block_signals=True)
        self._execute_command_run(command)

    def selectPlainView(self):
        self._plain_radio.setChecked(True)

    def selectHexView(self):
        self._hex_radio.setChecked(True)

    def toggleSearchField(self):
        self._plain_view_widget.toggleSearchField()

    def hasNext(self):
        return self._next_frame is not None

    def hasPrevious(self):
        return self._previous_frame is not None

    def setNext(self, next_frame):
        self._next_frame = next_frame

    def setPrevious(self, previous_frame):
        self._previous_frame = previous_frame

    def next(self):
        return self._next_frame

    def previous(self):
        return self._previous_frame

    def setTitle(self, title):
        self._group_box.setTitle(title)

    def setInputText(self, text, blockSignals=False):
        self._plain_view_widget.blockSignals(blockSignals)
        self._plain_view_widget.setPlainText(text)
        self._plain_view_widget.blockSignals(False)

    def getInputText(self):
        return self._plain_view_widget.toPlainText()

    def getComboBoxes(self):
        return self._combo_boxes

    def focusInputText(self):
        self._plain_view_widget.setFocus()

    def focusComboBox(self, type):
        self._combo_box_frame.focusType(type)
