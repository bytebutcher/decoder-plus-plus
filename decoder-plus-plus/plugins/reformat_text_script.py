import re

import qtawesome
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFrame, QLabel, QGroupBox, QFormLayout, QLineEdit, QCheckBox, \
    QDialogButtonBox, QPlainTextEdit, QLayout, QHBoxLayout, QPushButton

from core.exception import AbortedException
from core.plugin.plugin import ScriptPlugin, PluginConfig


class Plugin(ScriptPlugin):
    """
    Reformats the input.
    """

    class Option(object):

        Format = "format"
        SplitChars = "split_char"
        IsRegex = "is_regex"

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('Reformat Text', "Thomas Engel", [], context)
        self.config().add(PluginConfig.Option(
            Plugin.Option.Format, "", "the format string to be used"))
        self.config().add(PluginConfig.Option(
            Plugin.Option.SplitChars, " ", "the characters used to split the text in individual parts (default=' ')", False))
        self.config().add(PluginConfig.Option(
            Plugin.Option.IsRegex, False, "defines whether the split chars is a regular expression (default=False)", False))
        self._dialog = None
        self._codec = ReformatCodec()

    def select(self, text: str):
        if not self._dialog:
            self._dialog = ReformatDialog(self._context, text, self.config().clone(), self._codec)
        else:
            self._dialog.setInput(text)

        self._dialog_return_code = self._dialog.exec_()

        if self._dialog_return_code != QDialog.Accepted:
            # User clicked the Cancel-Button.
            raise AbortedException("Aborted")

        self.config().update(self._dialog.config())
        return self.run(text)


    def title(self):
        return "Reformat text with '{}' using '{}' as {}delimiter".format(
            self.config().get(Plugin.Option.Format).value,
            self.config().get(Plugin.Option.SplitChars).value,
            "regex-" if self.config().get(Plugin.Option.IsRegex).value else ""
        )

    def run(self, text):
        if text:
            format = self.config().get(Plugin.Option.Format).value
            delimiter = self.config().get(Plugin.Option.SplitChars).value
            is_regex = self.config().get(Plugin.Option.IsRegex).value
            return self._codec.reformat(text, format, delimiter, is_regex)
        return ''


class ReformatCodec:

    def reformat(self, input, format, split_by_chars, is_regex):
        if input:
            if format:
                try:
                    if is_regex:
                        split_input = re.split(split_by_chars, input)
                    else:
                        split_input = input.split(split_by_chars)
                    return format.format(*split_input)
                except BaseException:
                    raise Exception("Error during reformat operation! Check your format string!")
            else:
                return input
        return ''

class ReformatDialog(QDialog):

    def __init__(self, context, input, config, codec):
        super(ReformatDialog, self).__init__()
        self._context = context
        self._input = input
        self._config = config
        self._codec = codec
        self.setLayout(self._init_main_layout())
        self._update_view()
        self.setWindowIcon(qtawesome.icon("fa.edit"))
        self.setWindowTitle("Reformat Text")

    def _init_main_layout(self):
        frm_main_layout = QVBoxLayout()
        frm_main_layout.addWidget(self._init_form_frame())
        self._txt_preview = QPlainTextEdit(self)
        self._txt_preview.setReadOnly(True)
        self._txt_preview.setFixedHeight(126)
        frm_main_layout.addWidget(self._txt_preview)
        frm_main_layout.addWidget(self._init_error_frame())
        self._btn_box = self._init_button_box()
        frm_main_layout.addWidget(self._btn_box)
        return frm_main_layout

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
        # Define input fields and register change events
        self._txt_format = QLineEdit()
        self._txt_format.setText(self._config.get(Plugin.Option.Format).value)
        self._txt_format.textChanged.connect(self._on_change_event)

        self._btn_format_help = QPushButton("?")
        self._btn_format_help.clicked.connect(lambda evt: QDesktopServices.openUrl(QUrl("https://pyformat.info/")))

        self._txt_split_char = QLineEdit()
        self._txt_split_char.setText(self._config.get(Plugin.Option.SplitChars).value)
        self._txt_split_char.textChanged.connect(self._on_change_event)

        self._chk_regex = QCheckBox("Regex")
        self._chk_regex.setChecked(self._config.get(Plugin.Option.IsRegex).value)
        self._chk_regex.clicked.connect(self._on_change_event)

        # Build layout
        frm_frame = QFrame()
        frm_layout = QHBoxLayout()
        frm_layout.addWidget(QLabel("Format: "))
        frm_layout.addWidget(self._txt_format)
        frm_layout.addWidget(self._btn_format_help)
        frm_layout.addWidget(QLabel("Split by: "))
        frm_layout.addWidget(self._txt_split_char)
        frm_layout.addWidget(self._chk_regex)
        frm_frame.setLayout(frm_layout)
        return frm_frame

    def _init_button_box(self):
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        return btn_box

    def _validate_regex(self):
        try:
            if self._is_regex():
                re.compile(self._get_format_text())
            return True
        except:
            return False

    def config(self) -> PluginConfig:
        return self._config

    def _update_view(self):
        self._txt_format.setText(self._config.get(Plugin.Option.Format).value)
        self._txt_split_char.setText(self._config.get(Plugin.Option.SplitChars).value)
        self._chk_regex.setChecked(self._config.get(Plugin.Option.IsRegex).value)
        self._on_change_event(None)

    def _on_change_event(self, event):
        if not self._txt_split_char.text():
            self._show_error_message(self._txt_split_char, "Split by text should not be empty!")
            self._btn_box.button(QDialogButtonBox.Ok).setEnabled(False)
            return

        if self._chk_regex.isChecked() and self._validate_regex():
            self._show_error_message(self._txt_split_char, "Invalid regular expression!")
            self._btn_box.button(QDialogButtonBox.Ok).setEnabled(False)
            return

        if not self._do_preview():
            self._show_error_message(self._txt_format, "Invalid format string!")
            self._btn_box.button(QDialogButtonBox.Ok).setEnabled(False)
            return

        self._hide_error_message([self._txt_format, self._txt_split_char])
        self._btn_box.button(QDialogButtonBox.Ok).setEnabled(True)

        self.config().get(Plugin.Option.Format).value = self._txt_format.text()
        self.config().get(Plugin.Option.IsRegex).value = self._chk_regex.isChecked()
        self.config().get(Plugin.Option.SplitChars).value = self._txt_split_char.text()

    def _do_preview(self):
        try:
            result = self._codec.reformat(self._input, self._txt_format.text(), self._txt_split_char.text(), self._chk_regex.isChecked())
            self._txt_preview.setPlainText(result)
            return True
        except BaseException as e:
            return False

    def _show_error_message(self, widget, text: str):
        widget.setStyleSheet('QLineEdit { background-color: red }')
        self._error_frame.setHidden(False)
        self._error_text.setText(text)

    def _hide_error_message(self, widgets):
        self._error_frame.setHidden(False)
        self._error_text.setText("")
        for widget in widgets:
            widget.setStyleSheet('QLineEdit {  }')

    def setInput(self, input):
        self._input = input
