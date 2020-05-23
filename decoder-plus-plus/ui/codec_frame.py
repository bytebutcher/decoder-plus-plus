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
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from qtpy import QtCore

from core import Context
from core.plugin.plugin import PluginType, AbstractPlugin, NullPlugin
from core.plugin.plugin_builder import PluginBuilder
from core.plugin.plugins import Plugins
from ui import VSpacer, IconLabel
from ui.codec_frame_header import CodecFrameHeader
from ui.combo_box_frame import ComboBoxFrame
from ui.view.plain_view import PlainView
from ui.widget.collapsible_frame import CollapsibleFrame
from ui.widget.elided_label import ElidedLabel
from ui.widget.smart_decode_button import SmartDecodeButton
from ui.widget.status_widget import StatusWidget


class CodecFrame(CollapsibleFrame):

    upButtonClicked = pyqtSignal(str)  # frame_id
    downButtonClicked = pyqtSignal(str)  # frame_id
    configButtonClicked = pyqtSignal(str)  # frame_id
    closeButtonClicked = pyqtSignal(str)  # frame_id
    pluginSelected = pyqtSignal(str, str, 'PyQt_PyObject')  # frame_id, input_text, plugin

    def __init__(self, parent, context: Context, tab_id: str, frame_id: str, codec_tab, plugins: Plugins, previous_frame, text):
        super(__class__, self).__init__(parent, context, frame_id, previous_frame, None)
        self._listener = self._context.listener()
        self._context.shortcutUpdated.connect(self._shortcut_updated_event)
        self._init_logger(context, frame_id)
        self._tab_id = tab_id
        self._frame_id = frame_id
        self._codec_tab = codec_tab
        self._plugins = plugins
        self._flash_event = None

        self._status_widget = StatusWidget(self)
        self.addWidget(self._status_widget)
        self.addWidget(self._init_input_frame(text))
        self.addWidget(self._init_button_frame())

        self._init_header()
        self.show()

    def _init_logger(self, context, frame_id):
        """ Initializes the logger. Encapsulates logger-instance to enhance standard-logging with frame-id. """
        self._logger = context.logger()
        # BUG: Using logging with custom field frame_id does not work correctly.
        # FIX: ???
        #self._logger = context.logger(log_format="%(module)s: %(frame_id)d: %(lineno)d: %(msg)s",log_fields={'frame_id': frame_id})

    def _init_header(self):

        codec_frame_header = CodecFrameHeader(self)

        codec_frame_header.addWidget(CodecFrameHeader.TitleHeaderItem(self, codec_frame_header))
        codec_frame_header.addWidget(CodecFrameHeader.ContentPreviewHeaderItem(self, codec_frame_header))
        codec_frame_header.addWidget(CollapsibleFrame.HeaderFrame.HSpacerItem(self))

        codec_frame_header.addWidget(CollapsibleFrame.HeaderFrame.VSepItem(self))
        codec_frame_header.addWidget(CodecFrameHeader.LineCountInfoHeaderItem(self, codec_frame_header))

        codec_frame_header.addWidget(CollapsibleFrame.HeaderFrame.VSepItem(self))
        codec_frame_header.addWidget(CodecFrameHeader.ContentLengthInfoHeaderItem(self, codec_frame_header))
        codec_frame_header.addWidget(CollapsibleFrame.HeaderFrame.VSepItem(self))

        def button_clicked_event(event, signal):
            if event.button() == QtCore.Qt.LeftButton:
                signal.emit(self.id())

        up_button_header_item = CodecFrameHeader.UpButtonHeaderItem(self, codec_frame_header)
        up_button_header_item.clicked.connect(lambda evt: button_clicked_event(evt, self.upButtonClicked))
        codec_frame_header.addWidget(up_button_header_item)

        down_button_header_item = CodecFrameHeader.DownButtonHeaderItem(self, codec_frame_header)
        down_button_header_item.clicked.connect(lambda evt: button_clicked_event(evt, self.downButtonClicked))
        codec_frame_header.addWidget(down_button_header_item)

        config_button_header_item = CodecFrameHeader.ConfigButtonHeaderItem(self, codec_frame_header)
        config_button_header_item.clicked.connect(lambda evt: button_clicked_event(evt, self.configButtonClicked))
        codec_frame_header.addWidget(config_button_header_item)

        close_button_header_item = CodecFrameHeader.CloseButtonHeaderItem(self, codec_frame_header)
        close_button_header_item.clicked.connect(lambda evt: button_clicked_event(evt, self.closeButtonClicked))
        codec_frame_header.addWidget(close_button_header_item)

    def _init_input_frame(self, text):
        input_frame = QFrame(self)
        frame_layout = QVBoxLayout()
        self._plain_view_widget = PlainView(self._tab_id, self._frame_id, text, self._context, self)
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

    def id(self) -> str:
        return self._frame_id

    def getPlugin(self) -> AbstractPlugin:
        """ Returns the currently selected plugin. Might return a NullPlugin when nothing is selected. """
        if hasattr(self, '_combo_box_frame'): # A bit dirty, but might be called before initialization (see Frame::isConfigurable)
            return self._combo_box_frame.selectedPlugin()
        else:
            return NullPlugin(self._context)

    def flashStatus(self, status, message):
        self._header_frame.indicateError(status is "ERROR")
        self._status_widget.setStatus(status, message)

    def selectComboBoxEntryByPlugin(self, plugin, blockSignals=False):
        self._combo_box_frame.selectItem(plugin.type(), plugin.name(), block_signals=True)
        if not blockSignals:
            self.pluginSelected.emit(self.id(), self.getInputText(), plugin)

    def toggleSearchField(self):
        self._plain_view_widget.toggleSearchField()

    def setInputText(self, text):
        self._plain_view_widget.blockSignals(True)
        self._plain_view_widget.setPlainText(text)
        self._plain_view_widget.blockSignals(False)
        self.header().refresh()

    def getInputText(self) -> str:
        return self._plain_view_widget.toPlainText()

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
        return self._plain_view_widget.hasFocus()

    def focusComboBox(self, type):
        self._combo_box_frame.focusType(type)

    def setPlugin(self, plugin: AbstractPlugin, blockSignals=True):
        if plugin:
            self.selectComboBoxEntryByPlugin(plugin, blockSignals=blockSignals)
            self.getPlugin().setup(plugin.config().toDict())
            self.frameChanged.emit(self.id())

    def fromDict(self, frame_config):
        self.setInputText(frame_config["text"])
        self.flashStatus(frame_config["status"]["type"], frame_config["status"]["message"])
        if frame_config["plugin"]["name"] and frame_config["plugin"]["type"]:
            # Configure plugin if any. Last frame does not have a plugin configured, yet.
            self.selectComboBoxEntryByPlugin(PluginBuilder(self._context).build(frame_config["plugin"]), blockSignals=True)
        self.header().refresh()
        self.setCollapsed(frame_config["is_collapsed"])

    def toDict(self):
        status_type, status_message = self._status_widget.status()
        return {
            "text": self.getInputText(),
            "is_collapsed": self.isCollapsed(),
            "status": {
                "type": status_type,
                "message": status_message
            },
            "plugin": self._combo_box_frame.selectedPlugin().toDict()
        }
