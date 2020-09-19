import os
import re
import string

import qtawesome
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFrame, QLabel, QLineEdit, QCheckBox, \
    QDialogButtonBox, QPlainTextEdit, QHBoxLayout, QToolButton

from dpp.core.exception import AbortedException
from dpp.core.plugin import ScriptPlugin, PluginConfig
from dpp.ui.dialog.plugin_config_dialog import PluginConfigPreviewDialog


class Plugin(ScriptPlugin):
    """
    Reformats the input.

    Example:

        Input:
            123 456

        Parameters:

                    Format = "{1} {0}"
                  Split by = " "
                     Regex = False
            Handle Newline = True

        Output:
            456 123
    """

    class Option(object):

        Format = PluginConfig.Option.Label("format_string", "Format:")
        SplitChars = PluginConfig.Option.Label("split_chars", "Split by:")
        IsRegex = PluginConfig.Option.Label("is_regex", "Regex")
        HandleNewlines = PluginConfig.Option.Label("handle_newlines", "Handle Newlines")

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('Reformat Text', "Thomas Engel", [], context)

        def _validate_split_chars(config, codec, input):

            def _validate_regex():
                try:
                    re.compile(config.get(Plugin.Option.SplitChars).value)
                    return True
                except:
                    return False

            if not config.get(Plugin.Option.SplitChars).value:
                return "Split by should not be empty!"

            if config.get(Plugin.Option.IsRegex).value and not _validate_regex():
                return "Invalid regular expression!"

        def _validate_format(config, codec, input):
            try:
                codec(config, input)
            except:
                return "Invalid format string!"

        self.config.add(PluginConfig.Option.String(
            label=Plugin.Option.Format,
            value="",
            description="the format string to be used",
            is_required=True
        ), validator=_validate_format)
        self.config.add(PluginConfig.Option.String(
            label=Plugin.Option.SplitChars,
            value=" ",
            description="the characters used to split the text in individual parts (default=' ')",
            is_required=False
        ), validator=_validate_split_chars)
        self.config.add(PluginConfig.Option.Boolean(
            label=Plugin.Option.IsRegex,
            value=False,
            description="defines whether the split chars is a regular expression (default=False)",
            is_required=False
        ))
        self.config.add(PluginConfig.Option.Boolean(
            label=Plugin.Option.HandleNewlines,
            value=True,
            description="defines whether the operation should be applied for each individual line (default=True)",
            is_required=False
        ))
        self._dialog = None
        self._codec = ReformatCodec()

    def select(self, text: str):
        if not self._dialog:
            self._dialog = PluginConfigPreviewDialog(self._context, self.config.clone(),
                                              "Reformat Text", self._codec.reformat, qtawesome.icon("fa.edit"))

        self._dialog.setInput(text)
        self._dialog_return_code = self._dialog.exec_()

        if self._dialog_return_code != QDialog.Accepted:
            # User clicked the Cancel-Button.
            raise AbortedException("Aborted")

        self.config.update(self._dialog.config)
        return self.run(text)


    def title(self):
        return "Reformat text with '{}' using '{}' as {}delimiter{}".format(
            self.config.get(Plugin.Option.Format).value,
            self.config.get(Plugin.Option.SplitChars).value,
            "regex-" if self.config.get(Plugin.Option.IsRegex).value else "",
            " (newline sensitive)" if self.config.get(Plugin.Option.HandleNewlines).value else ""
        )

    def run(self, text):
        if text:
            return self._codec.reformat(self.config, text)
        return ''


class ReformatCodec:

    class SafeDict(dict):
        def __missing__(self, key):
            return '{' + key + '}'

    def reformat(self, config, input):

        format = config.get(Plugin.Option.Format).value
        split_by_chars = config.get(Plugin.Option.SplitChars).value
        is_regex = config.get(Plugin.Option.IsRegex).value
        handle_newlines = config.get(Plugin.Option.HandleNewlines).value

        def _fill_blanks(format, values):
            """ Ensure that there are always at least as many values as there are placeholders. """
            format_len = len([i for i in string.Formatter().parse(format)])
            if len(values) < format_len:
                for i in range(1, format_len - len(values)):
                    values.append("")
            return values

        def _reformat(text):
            if is_regex:
                split_input = re.split(split_by_chars, text)
            else:
                split_input = text.split(split_by_chars)
            return format.format(*_fill_blanks(format, split_input))

        if input:
            if format:
                try:
                    if handle_newlines:
                        return os.linesep.join([_reformat(line) for line in input.split(os.linesep)])
                    else:
                        return _reformat(input)
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
        self.config = config
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
        self._txt_format.setText(self.config.get(Plugin.Option.Format).value)
        self._txt_format.textChanged.connect(self._on_change_event)

        self._btn_format_help = QToolButton()
        self._btn_format_help.setText("?")
        self._btn_format_help.clicked.connect(lambda evt: QDesktopServices.openUrl(QUrl("https://pyformat.info/")))

        self._txt_split_char = QLineEdit()
        self._txt_split_char.setText(self.config.get(Plugin.Option.SplitChars).value)
        self._txt_split_char.textChanged.connect(self._on_change_event)

        self._chk_regex = QCheckBox("Regex")
        self._chk_regex.setChecked(self.config.get(Plugin.Option.IsRegex).value)
        self._chk_regex.clicked.connect(self._on_change_event)

        self._chk_new_lines = QCheckBox("Handle Newline")
        self._chk_new_lines.setChecked(self.config.get(Plugin.Option.HandleNewlines).value)
        self._chk_new_lines.clicked.connect(self._on_change_event)

        # Build layout
        frm_frame = QFrame()
        frm_layout = QHBoxLayout()
        frm_layout.addWidget(QLabel("Format: "))
        frm_layout.addWidget(self._txt_format)
        frm_layout.addWidget(self._btn_format_help)
        frm_layout.addWidget(QLabel("Split by: "))
        frm_layout.addWidget(self._txt_split_char)
        frm_layout.addWidget(self._chk_regex)
        frm_layout.addWidget(self._chk_new_lines)
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

    def _update_view(self):
        self._txt_format.setText(self.config.get(Plugin.Option.Format).value)
        self._txt_split_char.setText(self.config.get(Plugin.Option.SplitChars).value)
        self._chk_regex.setChecked(self.config.get(Plugin.Option.IsRegex).value)
        self._chk_new_lines.setChecked(self.config.get(Plugin.Option.HandleNewlines).value)
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

        self.config.get(Plugin.Option.Format).value = self._txt_format.text()
        self.config.get(Plugin.Option.IsRegex).value = self._chk_regex.isChecked()
        self.config.get(Plugin.Option.SplitChars).value = self._txt_split_char.text()

    def _do_preview(self):
        try:
            result = self._codec.reformat(self._input, self._txt_format.text(), self._txt_split_char.text(),
                                          self._chk_regex.isChecked(), self._chk_new_lines.isChecked())
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
