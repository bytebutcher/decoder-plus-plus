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
from ui.combo_box_frame import ComboBoxFrame
from ui.view.plain_view import PlainView
from ui.widget.collapsible_frame import CollapsibleFrame
from ui.widget.elided_label import ElidedLabel
from ui.widget.smart_decode_button import SmartDecodeButton
from ui.widget.status_widget import StatusWidget


class CodecFrame(CollapsibleFrame):

    pluginSelected = pyqtSignal(str, str, 'PyQt_PyObject')  # frame_id, input_text, plugin
    upButtonClicked = pyqtSignal(str) # frame_id
    downButtonClicked = pyqtSignal(str) # frame_id
    configButtonClicked = pyqtSignal(str) # frame_id
    closeButtonClicked = pyqtSignal(str) # frame_id

    class AbstractCodecFrameHeaderItem(CollapsibleFrame.HeaderFrame.AbstractHeaderFrameItem):

        def __init__(self, parent: 'ui.codec_frame.CodecFrame'):
            super(__class__, self).__init__(parent)

    class TitleHeaderItem(AbstractCodecFrameHeaderItem):

        def __init__(self, parent: 'ui.codec_frame.CodecFrame'):
            super(__class__, self).__init__(parent)
            self.setCentralWidget(self._init_central_widget())

        def _init_central_widget(self):
            frm_title_frame = QFrame(self)
            frm_title_frame_layout = QHBoxLayout()
            frm_title_frame_layout.setContentsMargins(0, 0, 0, 0)
            self._title = QLabel(self._parent.getTitle())
            self._title.setTextFormat(Qt.PlainText)
            self._title.setToolTip(self._parent.getDescription())
            frm_title_frame_layout.addWidget(self._title)
            frm_title_frame.setLayout(frm_title_frame_layout)
            return frm_title_frame

        def refresh(self):
            self._title.setText(self._parent.getTitle())

    class ContentPreviewHeaderItem(AbstractCodecFrameHeaderItem):

        def __init__(self, parent: 'ui.codec_frame.CodecFrame'):
            super(__class__, self).__init__(parent)
            self.setCentralWidget(self._init_central_widget())

        def _init_central_widget(self):
            frm_content_preview = QFrame(self)
            frm_content_preview_layout = QHBoxLayout()
            frm_content_preview_layout.setContentsMargins(0, 0, 0, 0)
            txt_content_preview = QLabel("")
            frm_content_preview_layout.addWidget(txt_content_preview)
            self._content_preview_text = ElidedLabel("")
            self._content_preview_text.setTextFormat(Qt.PlainText)
            self._content_preview_text.setStyleSheet("QLabel { color: gray }");
            frm_content_preview_layout.addWidget(self._content_preview_text)
            frm_content_preview.setLayout(frm_content_preview_layout)
            return frm_content_preview

        def refresh(self):
            self._content_preview_text.setText(self._parent.getInputText())

    class LineCountInfoHeaderItem(AbstractCodecFrameHeaderItem):

        def __init__(self, parent: 'ui.codec_frame.CodecFrame'):
            super(__class__, self).__init__(parent)
            self.setCentralWidget(self._init_central_widget())

        def _init_central_widget(self):
            frm_line_count = QFrame(self)
            frm_line_count_layout = QHBoxLayout()
            frm_line_count_layout.setContentsMargins(0, 0, 0, 0)
            lbl_line_count = QLabel("Lines:")
            frm_line_count_layout.addWidget(lbl_line_count)
            self._txt_line_count = QLabel("0")
            self._txt_line_count.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            minimum_width = self._txt_line_count.fontMetrics().boundingRect("000").width()
            self._txt_line_count.setMinimumWidth(minimum_width)
            frm_line_count_layout.addWidget(self._txt_line_count)
            frm_line_count.setLayout(frm_line_count_layout)
            return frm_line_count

        def refresh(self):
            content = self._parent.getInputText()
            line_count = str((content and len(content.split('\n'))) or 0)
            self._txt_line_count.setText(line_count)

    class ContentLengthInfoHeaderItem(AbstractCodecFrameHeaderItem):

        def __init__(self, parent: 'ui.codec_frame.CodecFrame'):
            super(__class__, self).__init__(parent)
            self.setCentralWidget(self._init_central_widget())

        def _init_central_widget(self):
            frm_content_length = QFrame(self)
            frm_content_length_layout = QHBoxLayout()
            frm_content_length_layout.setContentsMargins(0, 0, 0, 0)
            lbl_content_length = QLabel("Length:")
            frm_content_length_layout.addWidget(lbl_content_length)
            self._content_length_text = QLabel("0")
            self._content_length_text.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            minimum_width = self._content_length_text.fontMetrics().boundingRect("000").width()
            self._content_length_text.setMinimumWidth(minimum_width)
            frm_content_length_layout.addWidget(self._content_length_text)
            frm_content_length.setLayout(frm_content_length_layout)
            return frm_content_length

        def refresh(self):
            content = self._parent.getInputText()
            length = str((content and len(content)) or 0)
            self._content_length_text.setText(length)

    class UpButtonHeaderItem(AbstractCodecFrameHeaderItem):

        def __init__(self, parent: 'ui.codec_frame.CodecFrame'):
            super(__class__, self).__init__(parent)
            self.setCentralWidget(self._init_central_widget())

        def _init_central_widget(self):
            self._lbl_icon_up = IconLabel(self, qtawesome.icon("fa.chevron-up"))
            self._lbl_icon_up.setHoverEffect(True)
            self._lbl_icon_up.setToolTip("Move up")
            self._lbl_icon_up.setEnabled(self._parent.hasPrevious() and self._parent.previous().hasPrevious())
            return self._lbl_icon_up

        def refresh(self):
            self._lbl_icon_up.setEnabled(self._parent.hasPrevious() and self._parent.previous().hasPrevious())

    class DownButtonHeaderItem(AbstractCodecFrameHeaderItem):

        def __init__(self, parent: 'ui.codec_frame.CodecFrame'):
            super(__class__, self).__init__(parent)
            self.setCentralWidget(self._init_central_widget())

        def _init_central_widget(self):
            self._lbl_icon_down = IconLabel(self, qtawesome.icon("fa.chevron-down"))
            self._lbl_icon_down.setHoverEffect(True)
            self._lbl_icon_down.setToolTip("Move down")
            self._lbl_icon_down.setEnabled(self._parent.hasNext())
            return self._lbl_icon_down

        def refresh(self):
            self._lbl_icon_down.setEnabled(self._parent.hasNext())

    class ConfigButtonHeaderItem(AbstractCodecFrameHeaderItem):

        def __init__(self, parent: 'ui.codec_frame.CodecFrame'):
            super(__class__, self).__init__(parent)
            self.setCentralWidget(self._init_central_widget())

        def _init_central_widget(self):
            self._lbl_icon_config = IconLabel(self, qtawesome.icon("fa.cog"))
            self._lbl_icon_config.setHoverEffect(True)
            self._lbl_icon_config.setEnabled(self._parent.isConfigurable())
            self._lbl_icon_config.setToolTip("Configure")
            return self._lbl_icon_config

        def refresh(self):
            self._lbl_icon_config.setEnabled(self._parent.isConfigurable())

    class CloseButtonHeaderItem(AbstractCodecFrameHeaderItem):

        def __init__(self, parent: 'ui.codec_frame.CodecFrame'):
            super(__class__, self).__init__(parent)
            self.setCentralWidget(self._init_central_widget())

        def _init_central_widget(self):
            self._lbl_icon_close = IconLabel(self, qtawesome.icon("fa.times"))
            self._lbl_icon_close.setHoverEffect(True)
            self._lbl_icon_close.setToolTip("Close")
            return self._lbl_icon_close

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
        self._init_header_frame_items()

        self.show()

    def _init_header_frame_items(self):
        header = self.header()
        header.addWidget(CodecFrame.TitleHeaderItem(self))
        header.addWidget(CodecFrame.ContentPreviewHeaderItem(self))
        header.addWidget(CollapsibleFrame.HeaderFrame.HSpacerItem(self))

        header.addWidget(CollapsibleFrame.HeaderFrame.VSepItem(self))
        header.addWidget(CodecFrame.LineCountInfoHeaderItem(self))

        header.addWidget(CollapsibleFrame.HeaderFrame.VSepItem(self))
        header.addWidget(CodecFrame.ContentLengthInfoHeaderItem(self))
        header.addWidget(CollapsibleFrame.HeaderFrame.VSepItem(self))

        up_button_header_item = CodecFrame.UpButtonHeaderItem(self)
        up_button_header_item.mouseReleaseEvent = lambda evt: self.upButtonClicked.emit(self.id())
        header.addWidget(up_button_header_item)

        down_button_header_item = CodecFrame.DownButtonHeaderItem(self)
        down_button_header_item.mouseReleaseEvent = lambda evt: self.downButtonClicked.emit(self.id())
        header.addWidget(down_button_header_item)

        config_button_header_item = CodecFrame.ConfigButtonHeaderItem(self)
        config_button_header_item.mouseReleaseEvent = lambda evt: self.configButtonClicked.emit(self.id())
        header.addWidget(config_button_header_item)

        close_button_header_item = CodecFrame.CloseButtonHeaderItem(self)
        close_button_header_item.mouseReleaseEvent = lambda evt: self.closeButtonClicked.emit(self.id())
        header.addWidget(close_button_header_item)

    def _init_logger(self, context, frame_id):
        """ Initializes the logger. Encapsulates logger-instance to enhance standard-logging with frame-id. """
        self._logger = context.logger()
        # BUG: Using logging with custom field frame_id does not work correctly.
        # FIX: ???
        #self._logger = context.logger(log_format="%(module)s: %(frame_id)d: %(lineno)d: %(msg)s",log_fields={'frame_id': frame_id})

    def _init_input_frame(self, text):
        input_frame = QFrame(self)
        frame_layout = QVBoxLayout()
        self._plain_view_widget = PlainView(self, self._context, self._tab_id, self._frame_id, text)
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

    def getTitle(self) -> str:
        """ Returns the title of the current frame which is either the title of the previous plugin or None. """
        if self.hasPrevious():
            return self.previous().getPlugin().title()
        return None

    def getDescription(self) -> str:
        """
        Returns the description of the current frame which is either the description of the previous plugin or None.
        """
        if self.hasPrevious():
            if not isinstance(self.previous().getPlugin(), NullPlugin):
                return self.previous().getPlugin().__doc__

    def getPlugin(self) -> AbstractPlugin:
        """ Returns the currently selected plugin. Might return a NullPlugin when nothing is selected. """
        if hasattr(self, '_combo_box_frame'): # A bit dirty, but might be called before initialization (see Frame::isConfigurable)
            return self._combo_box_frame.selectedPlugin()
        else:
            return NullPlugin(self._context)

    def isConfigurable(self):
        """ Checks whether the plugin which computes the input is configurable. """
        if self.hasPrevious():
            plugin = self.previous().getPlugin()
            return plugin and plugin.isConfigurable()
        return False

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
            self.frameChanged.emit(self.id())

    def fromDict(self, frame_config):
        self.setInputText(frame_config["text"])
        self.flashStatus(frame_config["status"]["type"], frame_config["status"]["message"])
        plugin = PluginBuilder(self._context).build(frame_config["plugin"])
        if plugin:
            self.selectComboBoxEntryByPlugin(plugin, blockSignals=True)
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
