import qtawesome
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QRadioButton, QFrame, QFormLayout, QDialogButtonBox, QLineEdit, \
    QLabel, QGroupBox, QWidget, QCheckBox, QShortcut

from core.exception import AbortedException
from core.plugin.plugin import ScriptPlugin, PluginConfig


class Plugin(ScriptPlugin):
    """
    Splits and Rejoins a string.

    Example 1:

        Split by character ' ' and join with ''

        Input:
            ab cd ef gh ij kl mn op qr st uv wx yz

        Output:
            abcdefghijklmnopqrstuvwxyz

    Example 2:

        Split by length '2' and join with ' '

        Input:
            abcdefghijklmnopqrstuvwxyz

        Output:
            ab cd ef gh ij kl mn op qr st uv wx yz

    """

    class Option(object):
        SplitText = "split_text"
        SplitByLength = "split_by_length"
        SplitByChars = "split_by_chars"
        RejoinWithChars = "rejoin_with_chars"

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('Split & Rejoin', "Thomas Engel", [], context)
        self._init_config()
        self._dialog = None
        self._dialog_return_code = None

    def _init_config(self):
        def _validate_split_text(config: PluginConfig, value: str):
            if not value:
                return "Split by text should not be empty."

        def _validate_rejoin_with_chars(config: PluginConfig, value: str):
            if config.get(Plugin.Option.SplitByLength).value:
                try:
                    length = int(config.get(Plugin.Option.SplitText).value)
                    if length <= 0:
                        return "Split by text should be greater than 0."
                except:
                    return "Split by text should be an integer."

        self.config().add(PluginConfig.Option.String(
            name=Plugin.Option.SplitText,
            value="",
            description="the parameter used for splitting",
            is_required=True,
            validator=_validate_split_text
        ))
        self.config().add(PluginConfig.Option.Group(
            name=Plugin.Option.SplitByChars,
            value=True,
            description="specifies whether text should be split at chars",
            is_required=False,
            group_name="split_behaviour"
        ))
        self.config().add(PluginConfig.Option.Group(
            name=Plugin.Option.SplitByLength,
            value=False,
            description="specifies whether text should be split at interval",
            is_required=False,
            group_name="split_behaviour"
        ))
        self.config().add(PluginConfig.Option.String(
            name=Plugin.Option.RejoinWithChars,
            value="",
            description="the chars used to join the split text",
            is_required=True,
            validator=_validate_rejoin_with_chars
        ))

    def title(self):
        if self.config().get(Plugin.Option.SplitByLength).is_checked:
            return "Split by length {} and rejoin with '{}'".format(
                self.config().get(Plugin.Option.SplitText).value,
                self.config().get(Plugin.Option.RejoinWithChars).value
            )
        elif self.config().get(Plugin.Option.SplitByChars).is_checked:
            return "Split by characters '{}' and rejoin with '{}'".format(
                self.config().get(Plugin.Option.SplitText).value,
                self.config().get(Plugin.Option.RejoinWithChars).value
            )
        else:
            self.logger().debug("Invalid option.")
            return "Split and Rejoin"

    def select(self, text: str):
        if not self._dialog:
            try:
                self._dialog = PluginConfigDialog(
                    self._context, self.config().clone(), "Split & Rejoin", qtawesome.icon("fa.edit"))
            except BaseException as e:
                self._context.logger().exception(e, exc_info=self._context.isDebugModeEnabled())

        self._dialog_return_code = self._dialog.exec_()

        if self._dialog_return_code != QDialog.Accepted:
            # User clicked the Cancel-Button.
            raise AbortedException("Aborted")

        self.config().update(self._dialog.config())

        return self.run(text)

    def run(self, text: str):
        if text:
            input = ""
            if self.config().get(Plugin.Option.SplitByLength).is_checked:
                input = self._chunk_string(text, int(self.config().get(Plugin.Option.SplitText).value))
            elif self.config().get(Plugin.Option.SplitByChars).is_checked:
                input = text.split(self.config().get(Plugin.Option.SplitText).value)
            return self.config().get(Plugin.Option.RejoinWithChars).value.join(input)
        return ''

    def _chunk_string(self, string, length):
        return [string[0 + i:length + i] for i in range(0, len(string), length)]


class PluginConfigDialog(QDialog):

    class WidgetWrapper:

        def __init__(self, name, widget, get_value_callback, validate_callback, on_change_signal):
            self.name = name
            self.widget = widget
            self._get_value_callback = get_value_callback
            self.validate = validate_callback
            self.onChange = on_change_signal

        def get_value(self):
            return self._get_value_callback()

        value = property(get_value)

    def __init__(self, context, config, title, icon=None):
        super(PluginConfigDialog, self).__init__()
        self._context = context
        self._config = config
        self._widgets = {}
        self.setLayout(self._init_main_layout())
        self._build()
        self._init_shortcuts()
        self.setWindowTitle(title)
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

    def _update_and_validate(self):
        """ Update and validate options. """
        self._config.update({name: self._widgets[name].value for name in self._config.keys()})
        self._btn_box.button(QDialogButtonBox.Ok).setEnabled(self._validate())

    def _validate(self):
        """ Validate the current settings. """
        self._reset_errors()
        for key, widget_wrapper in self._widgets.items():
            message = widget_wrapper.validate(self._config, widget_wrapper.value)
            if message:
                self._show_error_indicator(widget_wrapper)
                self._show_error_message(widget_wrapper, message)
                return False
        return True

    def _reset_errors(self):
        """ Hides error message box and resets any error indicators. """
        self._error_frame.setHidden(True)
        self._error_text.setText("")
        for name in self._config.keys():
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

    def _show_error_message(self, widget_wrapper, message):
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
            w = PluginConfigDialog.WidgetWrapper(option.name, x, x.text, option.validate, x.textChanged)
            w.onChange.connect(lambda evt: self._update_and_validate())
        elif isinstance(option, PluginConfig.Option.Integer):
            x = QLineEdit(option.value)
            w = PluginConfigDialog.WidgetWrapper(option.name, x, x.text, option.validate, x.textChanged)
            w.onChange.connect(lambda evt: self._update_and_validate())
        elif isinstance(option, PluginConfig.Option.Boolean):
            x = QCheckBox(option.name)
            x.setChecked(option.value)
            w = PluginConfigDialog.WidgetWrapper(option.name, x, x.isChecked, option.validate, x.clicked)
            w.onChange.connect(lambda evt: self._update_and_validate())
        elif isinstance(option, PluginConfig.Option.Group):
            x = QRadioButton(option.name)
            x.setChecked(option.value)
            w = PluginConfigDialog.WidgetWrapper(option.name, x, x.isChecked, option.validate, x.clicked)
            w.onChange.connect(lambda evt: self._update_and_validate())
        else:
            raise Exception("Invalid option of type {} detected!".format(type(option)))
        return w

    def _build(self):
        """
        Automatically build the widgets for all options.
        This method can be overwritten to allow building custom widgets.
        """
        for name, option in self._config.items():
            label = QLabel()
            if not isinstance(option, PluginConfig.Option.Group):
                label.setText(name)
            self._widgets[name] = self._build_option(option)
            self._input_frame_layout.addRow(label, self._widgets[name].widget)

    def config(self):
        return self._config


class SplitAndRejoinDialog(QDialog):

    def __init__(self, config):
        super(SplitAndRejoinDialog, self).__init__()
        self._config = config
        self.setLayout(self._init_main_layout())
        self._on_change_event(None) # Update view
        self.setWindowIcon(qtawesome.icon("fa.edit"))
        self.setWindowTitle("Split & Rejoin")

    def _init_main_layout(self):
        main_layout = QVBoxLayout()
        main_layout.addWidget(self._init_form_frame())
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

    def _init_form_frame(self):
        form_frame = QGroupBox()
        form_frame_layout = QFormLayout()
        self._split_by_character_radio_button = QRadioButton("Character")
        self._split_by_character_radio_button.setChecked(self._config.get(Plugin.Option.SplitByChars).is_checked)
        self._split_by_length_radio_button = QRadioButton("Length")
        self._split_by_length_radio_button.setChecked(self._config.get(Plugin.Option.SplitByLength).is_checked)

        self._split_by_line_edit = QLineEdit()
        if self._config.get(Plugin.Option.SplitByChars).is_checked:
            self._split_by_line_edit.setText(self._config.get(Plugin.Option.SplitByChars).value)
        else:
            self._split_by_line_edit.setText(self._config.get(Plugin.Option.SplitByLength).value)
        self._join_with_line_edit = QLineEdit()
        self._join_with_line_edit.setText(self._config.get(Plugin.Option.RejoinWithChars).value)

        # Register change events
        self._split_by_character_radio_button.clicked.connect(self._on_change_event)
        self._split_by_length_radio_button.clicked.connect(self._on_change_event)
        self._split_by_line_edit.textChanged.connect(self._on_change_event)
        self._join_with_line_edit.textChanged.connect(self._on_change_event)

        split_by_layout = QVBoxLayout()
        split_by_layout.addWidget(self._split_by_line_edit)
        split_by_layout.addWidget(self._split_by_character_radio_button)
        split_by_layout.addWidget(self._split_by_length_radio_button)
        form_frame_layout.addRow(QLabel("Split by"), split_by_layout)
        form_frame_layout.addRow(QLabel("Rejoin with"), self._join_with_line_edit)
        form_frame.setLayout(form_frame_layout)
        return form_frame

    def _init_button_box(self):
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._accept)
        button_box.rejected.connect(self.reject)
        return button_box

    def _validate_split_by_text(self):
        if not self._get_split_by_text():
            return "Split by text should not be empty."

        if self._get_split_by_text() and self._split_by_length_radio_button.isChecked():
            try:
                length = int(self._get_split_by_text())
                if length <= 0:
                    return "Split by text should be greater than 0."
            except:
                return "Split by text should be an integer."

    def _accept(self):
        self.accept()

    def config(self) -> PluginConfig:
        return self._config

    def _on_change_event(self, event):
        split_by_text_error = self._validate_split_by_text()
        self._show_split_by_text_error(split_by_text_error)
        self._btn_box.button(QDialogButtonBox.Ok).setEnabled(True if not split_by_text_error else False)
        if split_by_text_error:
            self._set_option(Plugin.Option.SplitByLength, self._get_split_by_length,
                             self._split_by_length_radio_button.isChecked())
            self._set_option(Plugin.Option.SplitByChars, self._get_split_by_text,
                             self._split_by_character_radio_button.isChecked())
            self.config().get(Plugin.Option.RejoinWithChars).value = self._get_join_with_text()

    def _set_option(self, option_name, callback, is_checked):
        if is_checked:
            self.config().get(option_name).value = callback()
        else:
            self.config().get(option_name).value = None
        self.config().get(option_name).is_checked = is_checked

    def _get_split_by_text(self):
        return self._split_by_line_edit.text()

    def _get_split_by_length(self):
        return self._get_split_by_text() if self._get_split_by_text() else "0"

    def _get_join_with_text(self):
        return self._join_with_line_edit.text()

    def _show_split_by_text_error(self, text: str):
        if text:
            self._split_by_line_edit.setStyleSheet('QLineEdit { background-color: #f6989d }')
            self._error_frame.setHidden(False)
            self._error_text.setText(text)
        else:
            self._error_frame.setHidden(False)
            self._error_text.setText(text)
            self._split_by_line_edit.setStyleSheet('QLineEdit {  }')
