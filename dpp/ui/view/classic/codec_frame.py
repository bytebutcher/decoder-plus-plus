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
import uuid
from typing import Tuple

from qtpy import QtCore
from qtpy.QtCore import Signal
from qtpy.QtWidgets import QFrame, QVBoxLayout

from dpp.core import Context
from dpp.core.logger import logmethod
from dpp.core.plugin import PluginType, AbstractPlugin, NullPlugin
from dpp.core.plugin.manager import PluginManager
from dpp.core.plugin.builder import PluginBuilder
from dpp.ui import VSpacer
from dpp.ui.view.classic.codec_frame_header import CodecFrameHeader
from dpp.ui.view.classic.combo_box_frame import ComboBoxFrame
from dpp.ui.widget.plain_view import PlainView
from dpp.ui.widget.collapsible_frame import CollapsibleFrame
from dpp.ui.widget.identify_format_button import IdentifyFormatButton
from dpp.ui.widget.smart_decode_button import SmartDecodeButton
from dpp.ui.widget.status_widget import StatusWidget


class CodecFrame(CollapsibleFrame):

    # Signals that the frame was focused
    selectedFrameChanged = Signal(str, str, str)  # tab_id, frame_id, input_text

    # Signals that the text inside the codec frame changed
    textChanged = Signal(str, str, str)  # tab_id, frame_id, input_text

    # Signals that the text selection inside the codec frame changed
    textSelectionChanged = Signal(str, str, str)  # tab_id, frame_id, input_text

    # Signals that the text inside the codec frame should be updated
    refreshButtonClicked = Signal(str)  # frame_id

    # Signals that the frame should be repositioned
    upButtonClicked = Signal(str)  # frame_id
    downButtonClicked = Signal(str)  # frame_id
    configButtonClicked = Signal(str)  # frame_id
    closeButtonClicked = Signal(str)  # frame_id

    # Signals that the selected plugin changed
    pluginSelected = Signal(str, 'PyQt_PyObject')  # frame_id, plugin

    @logmethod()
    def __init__(self, parent, context: Context, tab_id: str, codec_frames, plugins: PluginManager, text):
        super().__init__(parent, context, uuid.uuid4().hex)

        self._tab_id = tab_id
        self._codec_frames = codec_frames
        self._context.shortcutUpdated.connect(self._shortcut_updated_event)
        self._plugins = plugins
        self._flash_event = None

        self._status_widget = StatusWidget(self)
        self.addWidget(self._status_widget)
        self.addWidget(self._init_input_frame(text))
        self.addWidget(self._init_button_frame())

        self._init_header()

        self.show()

    # ------------------------------------------------------------------------------------------------------------------

    @logmethod(prefix_callback=lambda self: f'{self.getFrameId()}::')
    def _init_header(self):

        self._header_frame.addWidget(CodecFrameHeader.IndicatorHeaderItem(self))
        self._header_frame.addWidget(CodecFrameHeader.ContentPreviewHeaderItem(self))

        self._header_frame.addWidget(CollapsibleFrame.HeaderFrame.VSepItem(self))
        self._header_frame.addWidget(CodecFrameHeader.TitleHeaderItem(self))

        self._header_frame.addWidget(CollapsibleFrame.HeaderFrame.VSepItem(self))
        self._header_frame.addWidget(CodecFrameHeader.LineCountInfoHeaderItem(self))
        self._header_frame.addWidget(CollapsibleFrame.HeaderFrame.VSepItem(self))
        self._header_frame.addWidget(CodecFrameHeader.ContentLengthInfoHeaderItem(self))
        self._header_frame.addWidget(CollapsibleFrame.HeaderFrame.VSepItem(self))
        self._header_frame.addWidget(CodecFrameHeader.EntropyInfoHeaderItem(self))
        self._header_frame.addWidget(CollapsibleFrame.HeaderFrame.VSepItem(self))

        def button_clicked_event(event, signal):
            if event.button() == QtCore.Qt.LeftButton:
                signal.emit(self.id())

        def init_button(button, signal):
            button.clicked.connect(lambda evt: button_clicked_event(evt, signal))
            self._header_frame.addWidget(button)
            return button

        self._move_up_button = init_button(CodecFrameHeader.UpButtonHeaderItem(self), self.upButtonClicked)
        self._move_down_button = init_button(CodecFrameHeader.DownButtonHeaderItem(self), self.downButtonClicked)
        self._refresh_button = init_button(CodecFrameHeader.RefreshButtonHeaderItem(self), self.refreshButtonClicked)
        self._config_button = init_button(CodecFrameHeader.ConfigButtonHeaderItem(self), self.configButtonClicked)
        self._close_button = init_button(CodecFrameHeader.CloseButtonHeaderItem(self), self.closeButtonClicked)

    def getMoveUpButton(self) -> CodecFrameHeader.ClickableCodecFrameHeaderItem:
        return self._move_up_button

    def getMoveDownButton(self) -> CodecFrameHeader.ClickableCodecFrameHeaderItem:
        return self._move_down_button

    def getRefreshButton(self) -> CodecFrameHeader.ClickableCodecFrameHeaderItem:
        return self._refresh_button

    def getConfigButton(self) -> CodecFrameHeader.ClickableCodecFrameHeaderItem:
        return self._config_button

    def getCloseButton(self) -> CodecFrameHeader.ClickableCodecFrameHeaderItem:
        return self._close_button

    # ------------------------------------------------------------------------------------------------------------------

    @logmethod(prefix_callback=lambda self: f'{self.getFrameId()}::')
    def _init_input_frame(self, text):
        input_frame = QFrame(self)
        frame_layout = QVBoxLayout()
        self._plain_view_widget = PlainView(self._tab_id, self._frame_id, text, self._context, self)
        self._plain_view_widget.selectedFrameChanged.connect(self.selectedFrameChanged.emit)
        self._plain_view_widget.textSelectionChanged.connect(self.textSelectionChanged.emit)
        self._plain_view_widget.textChanged.connect(self.textChanged.emit)

        frame_layout.addWidget(self._plain_view_widget)
        frame_layout.setContentsMargins(0, 6, 6, 6)
        input_frame.setLayout(frame_layout)
        return input_frame

    @logmethod(prefix_callback=lambda self: f'{self.getFrameId()}::')
    def _init_button_frame(self):
        button_frame = QFrame(self)
        button_frame_layout = QVBoxLayout()
        self._combo_box_frame = ComboBoxFrame(self, self._context)
        self._combo_box_frame.pluginSelected.connect(lambda plugin:
                                                     self.pluginSelected.emit(
                                                         self.id(),
                                                         plugin
                                                     ))
        button_frame_layout.addWidget(self._combo_box_frame)
        self._smart_decode_button = SmartDecodeButton(self,
                                                      self._plugins.filter(type=PluginType.DECODER),
                                                      self._plain_view_widget.toPlainText,
                                                      self.selectComboBoxEntryByPlugin)
        button_frame_layout.addWidget(self._smart_decode_button)
        self._identify_format_button = IdentifyFormatButton(self,
                                                            self._plugins.filter(type=PluginType.DECODER) +
                                                            self._plugins.filter(type=PluginType.IDENTIFY),
                                                            self._plain_view_widget.toPlainText,
                                                            self.selectComboBoxEntryByPlugin)
        button_frame_layout.addWidget(self._identify_format_button)
        button_frame_layout.addWidget(VSpacer(self))
        button_frame.setLayout(button_frame_layout)
        return button_frame

    @logmethod(prefix_callback=lambda self: f'{self.getFrameId()}::')
    def _shortcut_updated_event(self, shortcut):
        tooltip = self._get_tooltip_by_shortcut(shortcut)
        combo_box_type = self._get_combo_box_type_by_shortcut(shortcut)
        self._combo_box_frame.setToolTip(tooltip, combo_box_type)

    def _get_combo_box_type_by_shortcut(self, shortcut) -> str:
        combo_box_shortcut_map = {
            Context.Shortcut.FOCUS_DECODER: PluginType.DECODER,
            Context.Shortcut.FOCUS_ENCODER: PluginType.ENCODER,
            Context.Shortcut.FOCUS_HASHER: PluginType.HASHER,
            Context.Shortcut.FOCUS_SCRIPT: PluginType.SCRIPT
        }
        return combo_box_shortcut_map[shortcut.id()]

    def _get_tooltip_by_shortcut(self, shortcut):
        return "{description} ({shortcut_key})".format(description=shortcut.name(), shortcut_key=shortcut.key())

    def id(self) -> str:
        return self._frame_id

    def getPlugin(self) -> AbstractPlugin:
        """ Returns the currently selected plugin. Might return a NullPlugin when nothing is selected. """
        # A bit dirty, but might be called before initialization (see Frame::isConfigurable)
        if hasattr(self, '_combo_box_frame'):
            return self._combo_box_frame.selectedPlugin()
        else:
            return NullPlugin(self._context)

    def hasStatus(self, status_name: str) -> bool:
        return self._status_widget.hasStatus(status_name)

    def status(self) -> (str, str):
        return self._status_widget.status()

    @logmethod(prefix_callback=lambda self: f'{self.getFrameId()}::')
    def setStatus(self, type, message):
        self._header_frame.setStatus(type, message)
        self._status_widget.setStatus(type, message)

    # ------------------------------------------------------------------------------------------------------------------

    def hasTextSelected(self) -> bool:
        return self._plain_view_widget.hasTextSelected()

    def getSelectedText(self) -> Tuple[str, str, str]:
        return self._plain_view_widget.getSelectedText()

    # ------------------------------------------------------------------------------------------------------------------

    @logmethod(prefix_callback=lambda self: f'{self.getFrameId()}::')
    def selectComboBoxEntryByPlugin(self, plugin, block_signals=False):
        self._combo_box_frame.selectItem(plugin.type, plugin.name, block_signals=block_signals)

    @logmethod(prefix_callback=lambda self: f'{self.getFrameId()}::')
    def toggleSearchField(self):
        self._plain_view_widget.toggleSearchField()

    @logmethod(prefix_callback=lambda self: f'{self.getFrameId()}::')
    def setInputText(self, text):
        self._plain_view_widget.setPlainText(text)
        self.header().refresh()

    def getInputText(self) -> str:
        return self._plain_view_widget.toPlainText()

    def getOutputText(self) -> str:
        return self.getPlugin().run(self.getInputText())

    def getComboBoxes(self):
        return self._combo_box_frame

    @logmethod(prefix_callback=lambda self: f'{self.getFrameId()}::')
    def cutSelectedInputText(self):
        self._plain_view_widget.cutSelectedInputText()

    @logmethod(prefix_callback=lambda self: f'{self.getFrameId()}::')
    def copySelectedInputText(self):
        self._plain_view_widget.copySelectedInputText()

    @logmethod(prefix_callback=lambda self: f'{self.getFrameId()}::')
    def pasteSelectedInputText(self):
        self._plain_view_widget.pasteSelectedInputText()

    @logmethod(prefix_callback=lambda self: f'{self.getFrameId()}::')
    def focusInputText(self):
        self._plain_view_widget.setFocus()

    def hasFocus(self):
        return self._plain_view_widget.hasFocus()

    @logmethod(prefix_callback=lambda self: f'{self.getFrameId()}::')
    def focusComboBox(self, type):
        self._combo_box_frame.focusType(type)

    @logmethod(prefix_callback=lambda self: f'{self.getFrameId()}::')
    def setPlugin(self, plugin: AbstractPlugin, block_signals=True):
        if plugin:
            assert isinstance(plugin, AbstractPlugin), "Plugin must be of type AbstractPlugin"
            self.selectComboBoxEntryByPlugin(plugin, block_signals=block_signals)
            self.getPlugin().setup(plugin.config.toDict())
            self.selectedFrameChanged.emit(self._tab_id, self.id(), self.getInputText())

    def title(self) -> str:
        """ Returns the title of the current frame which is either the title of the previous plugin or None. """
        if self.hasPreviousFrame():
            return self.getPreviousFrame().getPlugin().title

    def name(self) -> str:
        """ Returns the name of the current frame which is either the title of the previous plugin or None. """
        if self.hasPreviousFrame():
            return self.getPreviousFrame().getPlugin().name

    def type(self) -> str:
        """ Returns the type of the current frame which is either the type of the previous plugin or "None". """
        if self.hasPreviousFrame():
            return self.getPreviousFrame().getPlugin().type or "None"
        return "None"

    def description(self) -> str:
        """
        Returns the description of the current frame which is either the description of the previous plugin or None.
        """
        if self.hasPreviousFrame():
            if not isinstance(self.getPreviousFrame().getPlugin(), NullPlugin):
                return self.getPreviousFrame().getPlugin().__doc__

    def isConfigurable(self):
        """ Checks whether the plugin which computes the input is configurable. """
        if self.hasPreviousFrame():
            plugin = self.getPreviousFrame().getPlugin()
            return plugin and plugin.is_configurable()
        return False

    def getFrameIndex(self) -> int:
        """ Returns the index of the codec frame. """
        return self._codec_frames.getFrameIndex(self._frame_id)

    def getFrameId(self) -> str:
        """ Returns the id of the codec frame. """
        return self._frame_id

    def hasPreviousFrame(self) -> bool:
        """ Checks whether there is a previous frame. Returns either True or False. """
        return self._codec_frames.hasPreviousFrame(self.getFrameIndex())

    def getPreviousFrame(self) -> 'dpp.ui.codec_frame.CodecFrame':
        """ Returns the previous frame if any, otherwise an exception is thrown. """
        return self._codec_frames.getFrameByIndex(self.getFrameIndex() - 1)

    def hasNextFrame(self) -> bool:
        """ Checks whether there is a next frame. Returns either True or False. """
        return self._codec_frames.hasNextFrame(self.getFrameIndex())

    def getNextFrame(self) -> 'dpp.ui.codec_frame.CodecFrame':
        """ Returns the next frame if any, otherwise an exception is thrown. """
        return self._codec_frames.getFrameByIndex(self.getFrameIndex() + 1)

    # ------------------------------------------------------------------------------------------------------------------

    @logmethod(prefix_callback=lambda self: f'{self.getFrameId()}::')
    def fromDict(self, frame_config, safe_mode: bool = False):
        """ Setups a tab from a given configuration.
        @param frame_config: configuration of a frame. See toDict method for more information.
        @param safe_mode: dictates how potentially dangerous plugins are handled.
        """
        self.setInputText(frame_config["text"])
        self.setStatus(frame_config["status"]["type"], frame_config["status"]["message"])
        plugin = frame_config["plugin"]
        if plugin["name"] and plugin["type"]:
            # Configure plugin if any. Last frame does not have a plugin configured, yet.
            self.selectComboBoxEntryByPlugin(PluginBuilder(self._context).build(plugin, safe_mode),
                                             block_signals=True)
        self.header().refresh()
        self.setCollapsed(frame_config["is_collapsed"])

    @logmethod(prefix_callback=lambda self: f'{self.getFrameId()}::')
    def toDict(self):
        status_type, status_message = self._status_widget.status()
        return {
            "title": self.title,
            "text": self.getInputText(),
            "is_collapsed": self.isCollapsed(),
            "status": {
                "type": status_type,
                "message": status_message
            },
            "plugin": self._combo_box_frame.selectedPlugin().toDict()
        }
