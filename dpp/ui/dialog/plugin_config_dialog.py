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
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QLabel, QRadioButton, QCheckBox, QLineEdit, QDialog, QDialogButtonBox, QFormLayout, \
    QGroupBox, QShortcut, QVBoxLayout, QFrame, QHBoxLayout, QPlainTextEdit

from dpp.core.plugin import PluginConfig


class PluginConfigDialog(QDialog):

    class WidgetWrapper:
        """ Wraps a widget (e.g. QLineEdit, QCheckbox, etc.) and enhances it with a validate and onChange method. """

        def __init__(self, option: PluginConfig.Option.Base, widget, get_value_callback, config, on_change_signal):
            self.name = option.name
            self.widget = widget
            self.config = config
            self._get_value_callback = get_value_callback
            self.validate = lambda codec, input: self.config.validate(option, codec, input)
            self.onChange = on_change_signal

        def _get_value(self):
            return self._get_value_callback()

        value = property(_get_value)

    def __init__(self, context, config, title, codec, icon=None):
        super(PluginConfigDialog, self).__init__()
        self._context = context
        self.config = config
        self._codec = codec
        self._input = None
        self._widgets = {}
        self.setLayout(self._init_main_layout())
        self._build()
        self._init_shortcuts()
        self._validate()
        self.setWindowTitle(title)
        if icon:
            self.setWindowIcon(icon)

    def _init_main_layout(self):
        main_layout = QVBoxLayout()
        main_layout.addWidget(self._init_input_frame())
        main_layout.addWidget(self._init_error_frame())
        self._btn_box = self._init_button_box()
        main_layout.addWidget(self._btn_box)
        return main_layout

    def _init_error_frame(self):
        self._error_frame = QFrame()
        layout = QVBoxLayout()
        self._error_text = QLabel("")
        self._error_text.setStyleSheet('QLabel { color: red }')
        layout.addWidget(self._error_text)
        self._error_frame.setLayout(layout)
        self._error_frame.setHidden(True)
        return self._error_frame

    def _init_button_box(self):
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        return button_box

    def _init_shortcuts(self):
        def _accept(self):
            if self._btn_box(QDialogButtonBox.Ok).isEnabled():
                self.accept()

        ctrl_return_shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Return), self)
        ctrl_return_shortcut.activated.connect(_accept)
        alt_return_shortcut = QShortcut(QKeySequence(Qt.ALT + Qt.Key_Return), self)
        alt_return_shortcut.activated.connect(_accept)
        alt_o_shortcut = QShortcut(QKeySequence(Qt.ALT + Qt.Key_O), self)
        alt_o_shortcut.activated.connect(_accept)

    def _init_input_frame(self):
        input_frame = QGroupBox()
        self._input_frame_layout = QFormLayout()
        input_frame.setLayout(self._input_frame_layout)
        return input_frame

    def _on_change(self):
        """ Update and validate options. """
        self.config.update({key: self._widgets[key].value for key in self.config.keys()})
        self._btn_box.button(QDialogButtonBox.Ok).setEnabled(self._validate())

    def _validate(self):
        """ Validate the current settings. """
        self._reset_errors()
        for key, widget_wrapper in self._widgets.items():
            message = widget_wrapper.validate(self._codec, self._input)
            if message is not True:
                self._show_error_indicator(widget_wrapper)
                self._show_error_message(message)
                return False

        message = self._try_codec()
        if message:
            self._show_error_message(message)
            return False

        return True

    def _try_codec(self):
        """ Tries to run the codec with the specified input. Either returns None or an error message."""
        try:
            self._codec(self.config, self._input)
        except BaseException as e:
            return str(e)

    def _reset_errors(self):
        """ Hides error message box and resets any error indicators. """
        self._error_frame.setHidden(True)
        self._error_text.setText("")
        for name in self.config.keys():
            self._reset_error(self._widgets[name])

    def _reset_error(self, widget_wrapper):
        """
        Resets any error indication on a specific widget.
        This method can be overwritten to allow customizing visualization of errors for specific widgets.
        """
        widget = widget_wrapper.widget
        if isinstance(widget, QLineEdit):
            widget.setStyleSheet('QLineEdit { }')

    def _show_error_indicator(self, widget_wrapper):
        """
        Indicates an error on a specific widget.
        This method can be overwritten to allow customizing visualization of errors for specific widgets.
        """
        widget = widget_wrapper.widget
        if isinstance(widget, QLineEdit):
            widget.setStyleSheet('QLineEdit { color: red }')

    def _show_error_message(self, message):
        """ Shows an error message within a error-box. """
        self._error_frame.setHidden(False)
        self._error_text.setText(message)

    def _build_option(self, option: PluginConfig.Option.Base) -> WidgetWrapper:
        """
        Automatically build the widget for this option.
        This method can be overwritten to allow building custom widgets.
        :return the widget for this option.
        """
        if isinstance(option, PluginConfig.Option.String):
            x = QLineEdit(option.value)
            w = PluginConfigDialog.WidgetWrapper(option, x, x.text, self.config, x.textChanged)
            w.onChange.connect(lambda evt: self._on_change())
        elif isinstance(option, PluginConfig.Option.Integer):
            x = QLineEdit(option.value)
            w = PluginConfigDialog.WidgetWrapper(option, x, x.text, self.config, x.textChanged)
            w.onChange.connect(lambda evt: self._on_change())
        elif isinstance(option, PluginConfig.Option.Group):
            x = QRadioButton(option.name)
            x.setChecked(option.value)
            w = PluginConfigDialog.WidgetWrapper(option, x, x.isChecked, self.config, x.clicked)
            w.onChange.connect(lambda evt: self._on_change())
        elif isinstance(option, PluginConfig.Option.Boolean):
            x = QCheckBox(option.name)
            x.setChecked(option.value)
            w = PluginConfigDialog.WidgetWrapper(option, x, x.isChecked, self.config, x.clicked)
            w.onChange.connect(lambda evt: self._on_change())
        else:
            raise Exception("Invalid option of type {} detected!".format(type(option)))
        return w

    def _add_option_widget(self, label: QLabel, widget):
        self._input_frame_layout.addRow(label, widget)

    def _build(self):
        """
        Automatically build the widgets for all options.
        This method can be overwritten to allow building custom widgets.
        """
        for key, option in self.config.items():
            label = QLabel()
            if not isinstance(option, PluginConfig.Option.Boolean):
                label.setText(option.name)
            self._widgets[key] = self._build_option(option)
            self._add_option_widget(label, self._widgets[key].widget)

    def setInput(self, text):
        self._input = text
        self._on_change()


class PluginConfigPreviewDialog(PluginConfigDialog):

    def __init__(self, context, config, title, codec, icon=None):
        super(PluginConfigPreviewDialog, self).__init__(context, config, title, codec, icon)

    def _init_main_layout(self):
        main_layout = QVBoxLayout()
        main_layout.addWidget(self._init_input_frame())
        main_layout.addWidget(self._init_preview_frame())
        main_layout.addWidget(self._init_error_frame())
        self._btn_box = self._init_button_box()
        main_layout.addWidget(self._btn_box)
        return main_layout

    def _init_preview_frame(self):
        view_frame = QFrame(self)
        view_frame_layout = QHBoxLayout()
        self._txt_preview = QPlainTextEdit(self)
        self._txt_preview.setReadOnly(True)
        self._txt_preview.setFixedHeight(126)
        view_frame_layout.addWidget(self._txt_preview)
        view_frame.setLayout(view_frame_layout)
        return view_frame

    def _init_input_frame(self):
        input_frame = QGroupBox()
        self._input_frame_layout = QHBoxLayout()
        input_frame.setLayout(self._input_frame_layout)
        return input_frame

    def _add_option_widget(self, label: QLabel, widget):
        self._input_frame_layout.addWidget(label)
        self._input_frame_layout.addWidget(widget)

    def _on_change(self):
        super(PluginConfigPreviewDialog, self)._on_change()
        if self._validate():
            self._do_preview()

    def _do_preview(self):
        try:
            result = self._codec(self.config, self._input)
            self._txt_preview.setPlainText(result)
            return True
        except BaseException as e:
            return False
