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
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFrame, QVBoxLayout

from core import Context
from core.plugin.plugin import PluginType
from core.plugin.plugins import Plugins
from ui import VSpacer
from ui.combo_box_frame import ComboBoxFrame
from ui.view.plain_view import PlainView
from ui.widget.collapsible_frame import CollapsibleFrame
from ui.widget.smart_decode_button import SmartDecodeButton
from ui.widget.status_widget import StatusWidget


class CodecFrame(CollapsibleFrame):

    pluginSelected = pyqtSignal(str, str, 'PyQt_PyObject')  # frame_id, input_text, plugin

    def __init__(self, parent, context: Context, frame_id: str, codec_tab, plugins: Plugins, previous_frame, text):
        super(__class__, self).__init__(parent)
        self._context = context
        self._listener = self._context.listener()
        self._context.shortcutUpdated.connect(self._shortcut_updated_event)
        self._init_logger(context, frame_id)
        self._frame_id = frame_id
        self._codec_tab = codec_tab
        self._previous_frame = previous_frame
        if previous_frame:
            previous_frame.setNext(self)
        self._next_frame = None
        self._plugins = plugins
        self._flash_event = None

        self._status_widget = StatusWidget(self)
        input_frame = self._init_input_frame(text)
        button_frame = self._init_button_frame()

        self.addWidget(self._status_widget)
        self.addWidget(input_frame)
        self.addWidget(button_frame)

        self.show()

    def _init_logger(self, context, frame_id):
        """ Initializes the logger. Encapsulates logger-instance to enhance standard-logging with frame-id. """
        self._logger = context.logger()
        # BUG: Using logging with custom field frame_id does not work correctly.
        # FIX: ???
        #self._logger = context.logger(log_format="%(module)s: %(frame_id)d: %(lineno)d: %(msg)s",log_fields={'frame_id': frame_id})

    def _init_input_frame(self, text):
        input_frame = QFrame(self)
        frame_layout = QVBoxLayout()
        self._plain_view_widget = PlainView(self, self._context, self._frame_id, text)
        self.setMetaData(text)
        frame_layout.addWidget(self._plain_view_widget)
        frame_layout.setContentsMargins(0, 6, 6, 6)
        input_frame.setLayout(frame_layout)
        return input_frame

    def _init_button_frame(self):
        button_frame = QFrame(self)
        button_frame_layout = QVBoxLayout()
        self._combo_box_frame = ComboBoxFrame(self, self._context)
        self._combo_box_frame.titleSelected.connect(self._combo_box_title_selected_event)
        self._combo_box_frame.pluginSelected.connect(lambda plugin: self.pluginSelected.emit(self.id(), self.getInputText(), plugin))
        button_frame_layout.addWidget(self._combo_box_frame)
        self._smart_decode_button = SmartDecodeButton(self, self._plugins.filter(type=PluginType.DECODER))
        self._smart_decode_button.clicked.connect(self._smart_decode_button_click_event)
        button_frame_layout.addWidget(self._smart_decode_button)
        button_frame_layout.addWidget(VSpacer(self))
        button_frame.setLayout(button_frame_layout)
        return button_frame

    def _shortcut_updated_event(self, shortcut):
        id = shortcut.id()
        tooltip = self._get_tooltip_by_shortcut(shortcut)
        combo_box_shortcut_map = {
            Context.Shortcut.FOCUS_DECODER: PluginType.DECODER,
            Context.Shortcut.FOCUS_ENCODER: PluginType.ENCODER,
            Context.Shortcut.FOCUS_HASHER: PluginType.HASHER,
            Context.Shortcut.FOCUS_SCRIPT: PluginType.SCRIPT
        }
        if id in combo_box_shortcut_map:
            self._combo_box_frame.setToolTipByPluginType(combo_box_shortcut_map[id], tooltip)
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

    def _smart_decode_button_click_event(self):
        input = self._plain_view_widget.toPlainText()
        # TODO: Split Button and Processing
        decoders = self._smart_decode_button.get_possible_decoders(input)
        if not decoders:
            self._logger.error("No matching decoders detected.")
            return None

        if len(decoders) > 1:
            decoder_titles = [decoder.title() for decoder in decoders]
            self._logger.warning("Multiple matching decoders detected: {}".format(", ".join(decoder_titles)))
            self.selectComboBoxEntryByPlugin(decoders[0])
            return None

        decoder = decoders[0]
        self._logger.info("Possible match: {}".format(decoder.title()))
        self.selectComboBoxEntryByPlugin(decoder)

    def _combo_box_title_selected_event(self):
        self._codec_tab.removeFrames(self._next_frame)
        self.focusInputText()

    def id(self):
        return self._frame_id

    def flashStatus(self, status, message):
        self._title_frame.indicateError(status is "ERROR")
        self._status_widget.setStatus(status, message)

    def selectComboBoxEntryByPlugin(self, plugin):
        self._combo_box_frame.selectItem(plugin.type(), plugin.name(), block_signals=True)
        self.pluginSelected.emit(self.id(), self.getInputText(), plugin)

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

    def setInputText(self, text, blockSignals=False):
        self._plain_view_widget.blockSignals(blockSignals)
        self._plain_view_widget.setPlainText(text)
        self._plain_view_widget.blockSignals(False)
        self.setMetaData(text)

    def getInputText(self):
        return self._plain_view_widget.toPlainText()

    def getTitle(self) -> str:
        return self._title_frame.getTitle()

    def getComboBoxes(self):
        return self._combo_boxes

    def cutSelectedInputText(self):
        self._plain_view_widget.cutSelectedInputText()

    def copySelectedInputText(self):
        self._plain_view_widget.copySelectedInputText()

    def pasteSelectedInputText(self):
        self._plain_view_widget.pasteSelectedInputText()

    def focusInputText(self):
        self._plain_view_widget.setFocus()

    def hasFocus(self):
        # BUG: There is a difference between an active window and a focused window, so when you click on some other
        #      window making it active, the focus is moved with it on Linux but not on Windows.
        # FIX: Always use isActiveWindow instead.
        return self.isActiveWindow()

    def focusComboBox(self, type):
        self._combo_box_frame.focusType(type)

    def toDict(self):
        status_type, status_message = self._status_widget.status()
        return {
            "text": self.getInputText(),
            "title": self.getTitle(),
            "status": {
                "type": status_type,
                "message": status_message
            },
            "plugin": self._combo_box_frame.selectedPlugin().toDict()
        }
