import qtawesome
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QRadioButton, QFrame, QFormLayout, QDialogButtonBox, QLineEdit, \
    QLabel, QGroupBox

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
        Split_By_Length = "split_by_length"
        Split_By_Chars = "split_by_chars"
        Rejoin_With_Chars = "rejoin_with_chars"

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('Split & Rejoin', "Thomas Engel", [], context)
        self.config().add(PluginConfig.OptionGroup(
            Plugin.Option.Split_By_Chars, "", "", True, "SplitBehaviour", True))
        self.config().add(PluginConfig.OptionGroup(
            Plugin.Option.Split_By_Length, 0, "", True, "SplitBehaviour", False))
        self.config().add(PluginConfig.Option(
            Plugin.Option.Rejoin_With_Chars, "", "", True))
        self._dialog = None
        self._dialog_return_code = None

    def title(self):
        if self.config().get(Plugin.Option.Split_By_Length).is_checked:
            return "Split by length {} and rejoin with '{}'".format(
                self.config().get(Plugin.Option.Split_By_Length).value,
                self.config().get(Plugin.Option.Rejoin_With_Chars).value
            )
        elif self.config().get(Plugin.Option.Split_By_Chars).is_checked:
            return "Split by characters '{}' and rejoin with '{}'".format(
                self.config().get(Plugin.Option.Split_By_Chars).value,
                self.config().get(Plugin.Option.Rejoin_With_Chars).value
            )
        else:
            self.logger().debug("Invalid option.")
            return "Split and Rejoin"

    def select(self, text: str):
        if not self._dialog:
            self._dialog = SplitAndRejoinDialog(self.config().clone())

        self._dialog_return_code = self._dialog.exec_()

        if self._dialog_return_code != QDialog.Accepted:
            # User clicked the Cancel-Button.
            raise AbortedException("Aborted")

        self.config().update(self._dialog.config())

        return self.run(text)

    def run(self, text: str):
        if text:
            input = ""
            if self.config().get(Plugin.Option.Split_By_Length).is_checked:
                input = self._chunk_string(text, self.config().get(Plugin.Option.Split_By_Length).value)
            elif self.config().get(Plugin.Option.Split_By_Chars).is_checked:
                input = text.split(self.config().get(Plugin.Option.Split_By_Chars).value)
            return self.config().get(Plugin.Option.Rejoin_With_Chars).value.join(input)
        return ''

    def _chunk_string(self, string, length):
        return [string[0 + i:length + i] for i in range(0, len(string), length)]


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
        self._split_by_character_radio_button.setChecked(self._config.get(Plugin.Option.Split_By_Chars).is_checked)
        self._split_by_length_radio_button = QRadioButton("Length")
        self._split_by_length_radio_button.setChecked(self._config.get(Plugin.Option.Split_By_Length).is_checked)

        self._split_by_line_edit = QLineEdit()
        if self._config.get(Plugin.Option.Split_By_Chars).is_checked:
            self._split_by_line_edit.setText(self._config.get(Plugin.Option.Split_By_Chars).value)
        else:
            self._split_by_line_edit.setText(self._config.get(Plugin.Option.Split_By_Length).value)
        self._join_with_line_edit = QLineEdit()
        self._join_with_line_edit.setText(self._config.get(Plugin.Option.Rejoin_With_Chars).value)

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

        if self._get_split_by_text() and self._config.get(Plugin.Option.Split_By_Length).is_checked:
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
            self._set_option(Plugin.Option.Split_By_Length, self._get_split_by_length,
                             self._split_by_length_radio_button.isChecked())
            self._set_option(Plugin.Option.Split_By_Chars, self._get_split_by_text,
                             self._split_by_character_radio_button.isChecked())
            self.config().get(Plugin.Option.Rejoin_With_Chars).value = self._get_join_with_text()

    def _set_option(self, option_name, callback, is_checked):
        if is_checked:
            self.config().get(option_name).value = callback()
        else:
            self.config().get(option_name).value = None
        self.config().get(option_name).is_checked = is_checked

    def _get_split_by_text(self):
        return self._split_by_line_edit.text()

    def _get_split_by_length(self):
        return int(self._get_split_by_text() if self._get_split_by_text() else 0)

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
