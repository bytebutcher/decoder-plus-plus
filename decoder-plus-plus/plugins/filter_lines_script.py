import os
import re
import qtawesome

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QFrame, QPlainTextEdit, QShortcut, \
    QHBoxLayout, QCheckBox

from core.exception import AbortedException
from core.plugin.plugin import ScriptPlugin, PluginConfig
from ui import SearchField


class Plugin(ScriptPlugin):
    """
    Opens a dialog to filter text by certain conditions.
    """

    class Option(object):
        Filter_Term = "filter_term"
        Should_Match_Case = "should_match_case"
        Should_Invert_Match = "should_invert_match"
        Is_Regex = "is_regex"

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('Filter Lines', "Thomas Engel", [], context)
        self.config().add(PluginConfig.Option(
            Plugin.Option.Filter_Term, "", "term to filter by"))
        self.config().add(PluginConfig.Option(
            Plugin.Option.Should_Match_Case, True, "defines whether filter should match case", False))
        self.config().add(PluginConfig.Option(
            Plugin.Option.Should_Invert_Match, False, "defines whether filter should invert match", False))
        self.config().add(PluginConfig.Option(
            Plugin.Option.Is_Regex, False, "defines whether filter term is a regex", False))
        self._dialog = None
        self._dialog_return_code = QDialog.Accepted

    def select(self, text: str):
        if not self._dialog:
            self._dialog = FilterDialog(text, self.config().clone(), self._do_filter)
        else:
            self._dialog.setInput(text)

        self._dialog_return_code = self._dialog.exec_()

        if self._dialog_return_code != QDialog.Accepted:
            # User clicked the Cancel-Button.
            raise AbortedException("Aborted")

        self.config().update(self._dialog.config())
        return self.run(text)

    def title(self):
        return "Filter lines by '{}' using {}".format(
            self._get_filter_term(self.config()), self._getOptionAsHumanReadableString())

    def _getOptionAsHumanReadableString(self):
        options = []
        if self._should_match_case(self.config()):
            options.append('Match Case')
        else:
            options.append('Ignore Case')
        if self._is_regex(self.config()):
            options.append('Regular Expression')
        if self._should_invert_match(self.config()):
            options.append('Invert Match')

        return self._join_options_as_human_readable_string(options)

    def _get_filter_term(self, config: PluginConfig):
        return config.get(Plugin.Option.Filter_Term).value

    def _should_invert_match(self, config: PluginConfig):
        return config.get(Plugin.Option.Should_Invert_Match).value

    def _should_match_case(self, config: PluginConfig):
        return config.get(Plugin.Option.Should_Match_Case).value

    def _is_regex(self, config: PluginConfig):
        return config.get(Plugin.Option.Is_Regex).value

    def run(self, text: str):
        return self._do_filter(text, self.config())

    def _do_filter(self, text: str, config: PluginConfig):
        lines = []
        for text_line in text.splitlines():
            try:
                if self._should_filter(text_line, config):
                    if self._is_regex(config) and self._should_match_case(config):
                        match = re.match(self._get_filter_term(config), text_line)
                        lines.append(match.group(0))
                    elif self._is_regex(config):
                        match = re.match(self._get_filter_term(config), text_line, flags=re.IGNORECASE)
                        lines.append(match.group(0))
                    else:
                        lines.append(text_line)
            except Exception as e:
                # Ignore exceptions - most likely an error in the regex filter string
                self._logger.exception(e)
        return os.linesep.join(lines)

    def _should_filter(self, text_line: str, config: PluginConfig):
        if self._is_regex(config) and self._should_match_case(config):
            result = re.match(self._get_filter_term(config), text_line, flags=re.IGNORECASE) is not None
        elif self._is_regex(config):
            result = re.match(self._get_filter_term(config), text_line) is not None
        elif self._should_match_case(config):
            result = self._get_filter_term(config) in text_line
        else:
            result = self._get_filter_term(config).lower() in text_line.lower()
        if self._should_invert_match(config):
            return not result
        else:
            return result


class FilterDialog(QDialog):

    def __init__(self, input: str, config: PluginConfig, filter_callback):
        super(__class__, self).__init__()
        self._config = config
        self._do_filter = filter_callback
        main_layout = QVBoxLayout()
        main_layout.addWidget(self._init_editor_frame())
        self._btn_box = self._init_button_box()
        main_layout.addWidget(self._btn_box)
        self.setLayout(main_layout)
        self.setWindowIcon(qtawesome.icon("fa.filter"))
        self.setWindowTitle("Filter Lines")
        self._setup_shortcuts()
        self._input = input
        self._text_area.setPlainText(self._input)

    #############################################
    #   Initialize
    #############################################

    def _setup_shortcuts(self):
        return_shortcut = QShortcut(QKeySequence(Qt.Key_Return), self)
        return_shortcut.activated.connect(self._accept)
        ctrl_return_shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Return), self)
        ctrl_return_shortcut.activated.connect(self._accept)
        alt_return_shortcut = QShortcut(QKeySequence(Qt.ALT + Qt.Key_Return), self)
        alt_return_shortcut.activated.connect(self._accept)
        alt_o_shortcut = QShortcut(QKeySequence(Qt.ALT + Qt.Key_O), self)
        alt_o_shortcut.activated.connect(self._accept)

    def _init_button_box(self):
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._accept)
        button_box.rejected.connect(self.reject)
        return button_box

    def _init_editor_frame(self):
        main_frame = QFrame()
        main_frame_layout = QVBoxLayout()

        filter_frame = self._init_filter_text_frame()
        main_frame_layout.addWidget(filter_frame)

        self._text_area = QPlainTextEdit(self)
        self._text_area.setReadOnly(True)
        self._text_area.setFixedHeight(126)
        main_frame_layout.addWidget(self._text_area)

        main_frame.setLayout(main_frame_layout)
        return main_frame

    def _init_filter_text_frame(self):
        filter_text_frame = QFrame()
        filter_text_frame_layout = QHBoxLayout()

        self._filter_term = SearchField(self)
        self._filter_term.setIcon(qtawesome.icon("fa.filter"))
        self._filter_term.setPlaceholderText("Filter")
        self._filter_term.setText(self._config.get(Plugin.Option.Filter_Term).value)
        self._filter_term.textChanged.connect(lambda text: self._filter_changed())
        filter_text_frame_layout.addWidget(self._filter_term)

        self._match_case_checkbox = QCheckBox("Match Case")
        self._match_case_checkbox.setChecked(self._config.get(Plugin.Option.Should_Match_Case).value)
        self._match_case_checkbox.stateChanged.connect(lambda state: self._filter_changed())
        filter_text_frame_layout.addWidget(self._match_case_checkbox)

        self._regex_checkbox = QCheckBox("Regex")
        self._regex_checkbox.setChecked(self._config.get(Plugin.Option.Is_Regex).value)
        self._regex_checkbox.stateChanged.connect(lambda state: self._filter_changed())
        filter_text_frame_layout.addWidget(self._regex_checkbox)

        self._invert_match_checkbox = QCheckBox("Invert Match")
        self._invert_match_checkbox.setChecked(self._config.get(Plugin.Option.Should_Invert_Match).value)
        self._invert_match_checkbox.stateChanged.connect(lambda state: self._filter_changed())
        filter_text_frame_layout.addWidget(self._invert_match_checkbox)

        filter_text_frame_layout.setContentsMargins(0, 0, 0, 5)
        filter_text_frame.setLayout(filter_text_frame_layout)
        return filter_text_frame

    #############################################
    #   Events
    #############################################

    def _filter_changed(self):
        if self._validate_filter_term():
            self._filter_term.setStyleSheet("QLineEdit { }")
            self._btn_box.button(QDialogButtonBox.Ok).setEnabled(True)
            self._config.update({
                Plugin.Option.Filter_Term: self._get_filter_term(),
                Plugin.Option.Is_Regex: self._is_regex(),
                Plugin.Option.Should_Invert_Match: self._should_invert_match(),
                Plugin.Option.Should_Match_Case: self._should_match_case()
            })
            filter_text = self._do_filter(self._input, self.config())
            self._text_area.setPlainText(filter_text)
        else:
            self._filter_term.setStyleSheet("QLineEdit { background-color: #f6989d }")
            self._btn_box.button(QDialogButtonBox.Ok).setEnabled(False)

    #############################################
    #   Private interface
    #############################################

    def _get_filter_term(self):
        return self._filter_term.text()

    def _validate_filter_term(self):
        try:
            if self._is_regex():
                re.compile(self._get_filter_term())
            return True
        except:
            return False

    def _should_match_case(self):
        return self._match_case_checkbox.isChecked()

    def _is_regex(self):
        return self._regex_checkbox.isChecked()

    def _should_invert_match(self):
        return self._invert_match_checkbox.isChecked()

    def _accept(self):
        self.accept()

    #############################################
    #   Public interface
    #############################################

    def config(self):
        return self._config

    def setInput(self, input: str):
        self._input = input
        self._filter_changed()
