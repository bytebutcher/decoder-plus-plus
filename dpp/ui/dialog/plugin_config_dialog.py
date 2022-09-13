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
from qtpy.QtWidgets import QHBoxLayout, QSizePolicy, QFrame, QLabel, QDialog, QDialogButtonBox, QVBoxLayout, QShortcut

from dpp.core.icons import icon, Icon
from dpp.core.plugin import AbstractPlugin
from dpp.core.plugin.config.ui.layouts import VBoxLayout
from dpp.core.plugin.config.ui.widgets import TextPreview, GroupBox
from dpp.core.shortcuts import KeySequence
from dpp.ui import IconLabel
from dpp.ui.builder.plugin_config_widget_builder import PluginConfigWidgetBuilder


class PluginConfigDialog(QDialog):

    def __init__(self, context, plugin: AbstractPlugin, input_text: str):
        super(PluginConfigDialog, self).__init__()
        self._context = context
        self._input_text = input_text

        # Dialog operates on a copy of the plugin and its configuration. This allows that configuration changes made
        # in the dialog do not have an immediate effect to the real configuration. Synchronization with original
        # configuration occurs when the accept button is pressed.
        self._plugin_clone = plugin.clone()
        self._plugin_clone.config.onChange.connect(lambda keys: self._on_config_change())

        self._widget = PluginConfigWidgetBuilder(self, self._plugin_clone, input_text).layout(
            lambda layout_spec: VBoxLayout(
                widgets=[
                    GroupBox(label='Options', layout=layout_spec),
                    GroupBox(label='Preview', layout=VBoxLayout(
                        widgets=[TextPreview(self._plugin_clone, self._input_text)]
                    ))
                ]
            )
        ).build()

        self._main_layout = self._init_main_layout(self._widget)
        self._init_shortcuts()
        self._validate_options()
        self.setLayout(self._main_layout)
        self.setWindowTitle(plugin.name)
        if plugin.icon:
            self.setWindowIcon(icon(plugin.icon))

        # Synchronize cloned configuration with the original one.
        self.accepted.connect(lambda: plugin.config.update(self._plugin_clone.config))

    def _init_main_layout(self, widget):
        main_layout = QVBoxLayout()
        main_layout.addWidget(self._init_input_frame(widget))
        main_layout.addWidget(self._init_error_frame())
        main_layout.addWidget(self._init_button_box())
        return main_layout

    def _init_input_frame(self, widget) -> QFrame:
        input_frame = QFrame()
        input_frame_layout = QVBoxLayout()
        input_frame_layout.addWidget(widget)
        input_frame.setLayout(input_frame_layout)
        return input_frame

    def _init_error_frame(self):
        frm = QFrame()
        frm_layout = QVBoxLayout()
        self._error_frame = QFrame()
        self._error_frame.setStyleSheet("background-color: black;")
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        lbl_error = IconLabel(self, icon(Icon.MSG_ERROR, color='red'))
        layout.addWidget(lbl_error)
        self._error_text = QLabel("")
        self._error_text.setStyleSheet('QLabel { color: white }')
        self._error_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self._error_text)
        self._error_frame.setLayout(layout)
        self._error_frame.setHidden(True)
        frm_layout.addWidget(self._error_frame)
        frm_layout.setContentsMargins(10, 0, 10, 10)
        frm.setLayout(frm_layout)
        return frm

    def _init_button_box(self):
        frm = QFrame()
        frm_layout = QVBoxLayout()
        self._btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self._btn_box.accepted.connect(self.accept)
        self._btn_box.rejected.connect(self.reject)
        frm_layout.addWidget(self._btn_box)
        frm.setLayout(frm_layout)
        return frm

    def _init_shortcuts(self):
        def _accept(self):
            if self._btn_box(QDialogButtonBox.Ok).isEnabled():
                self.accept()

        ctrl_return_shortcut = QShortcut(KeySequence(Qt.CTRL, Qt.Key_Return), self)
        ctrl_return_shortcut.activated.connect(_accept)
        alt_return_shortcut = QShortcut(KeySequence(Qt.ALT, Qt.Key_Return), self)
        alt_return_shortcut.activated.connect(_accept)
        alt_o_shortcut = QShortcut(KeySequence(Qt.ALT, Qt.Key_O), self)
        alt_o_shortcut.activated.connect(_accept)

    def _on_config_change(self):
        """ Update and validate options when change occurred. """
        self._validate_options()

    def _validate_options(self):
        """ Update and validate options. """
        try:
            self._plugin_clone.run(self._input_text)
            self._reset_errors()
        except BaseException as err:
            self._show_error_message(str(err))

    def _reset_errors(self):
        """ Hides error message box and resets any error indicators. """
        self._btn_box.button(QDialogButtonBox.Ok).setEnabled(True)
        self._error_frame.setHidden(True)
        self._error_text.setText("")

    def _show_error_message(self, message):
        """ Shows an error message within a error-box. """
        self._btn_box.button(QDialogButtonBox.Ok).setEnabled(False)
        self._context.logger.debug(message)
        self._error_frame.setHidden(False)
        self._error_text.setText(message)
