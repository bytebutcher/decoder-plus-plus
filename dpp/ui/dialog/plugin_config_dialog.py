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
from qtpy.QtWidgets import QFrame, QDialog, QDialogButtonBox, QVBoxLayout, QShortcut

from dpp.core.icons import icon, Icon
from dpp.core.plugin import AbstractPlugin
from dpp.core.shortcuts import KeySequence
from dpp.ui.builder.plugin_config_widget_builder import PluginConfigWidgetBuilder
from dpp.ui.widget.message_box_widget import MessageBox


class PluginConfigDialog(QDialog):

    def __init__(self, context, plugin: AbstractPlugin, input_text: str):
        super(PluginConfigDialog, self).__init__()
        self._context = context
        self._input_text = input_text

        # Dialog operates on a copy of the plugin and its configuration. This allows that configuration changes made
        # in the dialog do not have an immediate effect to the real configuration. Synchronization with original
        # configuration occurs when the accept button is pressed.
        self._plugin_clone = plugin.clone()

        self._widget = PluginConfigWidgetBuilder(self, self._plugin_clone, input_text).build()

        self._main_layout = self._init_main_layout(self._widget)
        self._init_shortcuts()
        self._validate_options(input_text)
        self.setLayout(self._main_layout)
        self.setWindowTitle(plugin.name)
        if plugin.icon:
            self.setWindowIcon(icon(plugin.icon))

        # Synchronize cloned configuration with the original one.
        self.accepted.connect(lambda: plugin.config.update(self._plugin_clone.config))

        # Handle success and error on plugin run.
        # Remember: onSuccess/onError is usually being run by the preview window.
        self._plugin_clone.onSuccess.connect(self._show_success_message)
        self._plugin_clone.onError.connect(self._show_error_message)

    def _init_main_layout(self, widget):
        main_layout = QVBoxLayout()
        main_layout.addWidget(self._init_input_frame(widget))
        main_layout.addWidget(self._init_message_box(widget))
        main_layout.addWidget(self._init_button_box())
        return main_layout

    def _init_input_frame(self, widget) -> QFrame:
        input_frame = QFrame()
        input_frame_layout = QVBoxLayout()
        input_frame_layout.addWidget(widget)
        input_frame.setLayout(input_frame_layout)
        return input_frame

    def _init_button_box(self):
        frm = QFrame()
        frm_layout = QVBoxLayout()
        self._btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self._btn_box.accepted.connect(self.accept)
        self._btn_box.rejected.connect(self.reject)
        frm_layout.addWidget(self._btn_box)
        frm.setLayout(frm_layout)
        return frm

    def _init_message_box(self, parent):
        self._message_box = MessageBox(self)
        self._message_box.hide()
        return self._message_box

    def _init_shortcuts(self):
        def _accept():
            if self._btn_box.button(QDialogButtonBox.Ok).isEnabled():
                self.accept()

        ctrl_return_shortcut = QShortcut(KeySequence(Qt.CTRL, Qt.Key_Return), self)
        ctrl_return_shortcut.activated.connect(_accept)
        alt_return_shortcut = QShortcut(KeySequence(Qt.ALT, Qt.Key_Return), self)
        alt_return_shortcut.activated.connect(_accept)
        alt_o_shortcut = QShortcut(KeySequence(Qt.ALT, Qt.Key_O), self)
        alt_o_shortcut.activated.connect(_accept)

    def _validate_options(self, input_text, option_keys=None):
        """ Update and validate options. """
        # TODO: Indicate error on the individual widgets instead.
        #       This method has the disadvantage that we can only show one error message at a time.
        #       In addition the error message might not indicate directly which widget/field is responsible.
        try:
            self._plugin_clone.validate_options(input_text, option_keys)
        except BaseException as err:
            self._show_error_message(str(err))

    def _hide_message_box(self):
        """ Hide message box and enable OK button. """
        self._btn_box.button(QDialogButtonBox.Ok).setEnabled(True)
        self._message_box.setHidden(True)

    def _show_error_message(self, message):
        """ Shows an error message within a message-box. """
        if not message:
            self._hide_message_box()
            return
        self._btn_box.button(QDialogButtonBox.Ok).setEnabled(False)
        self._message_box.setFrameStyle("background-color: black;")
        self._message_box.setTextStyle("QLabel { color: white }")
        self._message_box.setIcon(Icon.MSG_ERROR, color='red')
        self._message_box.setText(message)
        self._message_box.setHidden(False)
        self._context.logger.debug(message)

    def _show_success_message(self, message):
        """ Shows a success message within a message box. """
        if not message:
            self._hide_message_box()
            return
        self._btn_box.button(QDialogButtonBox.Ok).setEnabled(True)
        self._message_box.setFrameStyle("background-color: white;")
        self._message_box.setTextStyle("QLabel { color: black }")
        self._message_box.setIcon(Icon.MSG_INFO, color='blue')
        self._message_box.setText(message)
        self._message_box.setHidden(False)
        self._context.logger.debug(message)
