import re

import qtawesome
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QFrame, QCheckBox

from core.exception import AbortedException
from core.plugin.plugin import ScriptPlugin, PluginConfig


class Plugin(ScriptPlugin):
    """
    Opens a search-and-replace dialog which supports Match-Case and Regular Expressions.
    """

    class Option(object):
        SearchTerm = "search_term"
        ReplaceTerm = "replace_term"
        ShouldMatchCase = "should_match_case"
        IsRegex = "is_regex"

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('Search & Replace', "Thomas Engel", [], context)
        self.config().add(PluginConfig.Option.String(
            name=Plugin.Option.SearchTerm,
            value="",
            description="the word or phrase to replace",
            is_required=True
        ))
        self.config().add(PluginConfig.Option.String(
            name=Plugin.Option.ReplaceTerm,
            value="",
            description="the word or phrase used as replacement",
            is_required=True
        ))
        self.config().add(PluginConfig.Option.Boolean(
            name=Plugin.Option.ShouldMatchCase,
            value=True,
            description="defines whether the search term should match case",
            is_required=False
        ))
        self.config().add(PluginConfig.Option.Boolean(
            name=Plugin.Option.IsRegex,
            value=False,
            description="defines whether the search term is a regular expression",
            is_required=False
        ))
        self._dialog = None
        self._dialog_return_code = QDialog.Accepted

    def select(self, text: str):
        if not self._dialog:
            self._dialog = SearchAndReplaceDialog(self.config().clone())

        self._dialog_return_code = self._dialog.exec_()

        if self._dialog_return_code != QDialog.Accepted:
            # User clicked the Cancel-Button.
            raise AbortedException("Aborted")

        self._config.update(self._dialog.config())
        return self.run(text)

    def title(self):
        return "Search and Replace '{}' with '{}' using {}".format(
            self._get_search_term(), self._get_replace_term(), self._get_option_as_human_readable_string())

    def _get_option_as_human_readable_string(self):
        if self._should_match_case():
            return 'Match Case'
        elif self._is_regex():
            return 'Regular Expression'
        else:
            return 'Ignore Case'

    def _get_search_term(self):
        return self.config().get(Plugin.Option.SearchTerm).value

    def _get_replace_term(self):
        return self.config().get(Plugin.Option.ReplaceTerm).value

    def _should_match_case(self):
        return self.config().get(Plugin.Option.ShouldMatchCase).value

    def _is_regex(self):
        return self.config().get(Plugin.Option.IsRegex).value

    def run(self, text: str):
        if self._is_regex() and self._should_match_case():
            return re.sub(self._get_search_term(), self._get_replace_term(), text, flags=re.IGNORECASE)
        elif self._is_regex():
            return re.sub(self._get_search_term(), self._get_replace_term(), text)
        elif self._should_match_case():
            return text.replace(self._get_search_term(), self._get_replace_term())
        else:
            return self._replace_ignore_case(text)

    def _replace_ignore_case(self, text):
        regexp = re.compile(re.escape(self._get_search_term()), re.IGNORECASE)
        return regexp.sub(self._get_replace_term(), text)


class SearchAndReplaceDialog(QDialog):

    def __init__(self, config: PluginConfig):
        super(SearchAndReplaceDialog, self).__init__()

        self._config = config

        main_layout = QVBoxLayout()
        main_layout.addWidget(self._init_form_frame())
        main_layout.addWidget(self._init_error_frame())
        main_layout.addWidget(self._init_button_box())
        self.setLayout(main_layout)
        self.setWindowIcon(qtawesome.icon("fa.search"))
        self.setWindowTitle("Search & Replace")

    #############################################
    #   Init
    #############################################

    def _init_button_box(self):
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._accept)
        button_box.rejected.connect(self.reject)
        return button_box

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
        form_frame = QFrame()
        form_frame_layout = QFormLayout()
        self._search_term_edit = QLineEdit(self._config.get(Plugin.Option.SearchTerm).value)
        self._search_term_edit.textChanged.connect(self._on_config_change)
        form_frame_layout.addRow(QLabel("Search:"), self._search_term_edit)
        self._replace_term_edit = QLineEdit(self._config.get(Plugin.Option.ReplaceTerm).value)
        self._replace_term_edit.textChanged.connect(self._on_config_change)
        form_frame_layout.addRow(QLabel("Replace:"), self._replace_term_edit)
        self._match_case_checkbox = QCheckBox("Match Case")
        self._match_case_checkbox.setChecked(self._config.get(Plugin.Option.ShouldMatchCase).value)
        self._match_case_checkbox.clicked.connect(self._on_config_change)
        form_frame_layout.addWidget(self._match_case_checkbox)
        self._regex_checkbox = QCheckBox("Regex")
        self._regex_checkbox.setChecked(self._config.get(Plugin.Option.IsRegex).value)
        self._regex_checkbox.clicked.connect(self._on_config_change)
        form_frame_layout.addWidget(self._regex_checkbox)

        form_frame.setLayout(form_frame_layout)
        return form_frame

    #############################################
    #   Events
    #############################################

    def _on_config_change(self, event):
        self._config.update({
            Plugin.Option.SearchTerm: self._get_search_term(),
            Plugin.Option.ReplaceTerm: self._get_replace_term(),
            Plugin.Option.ShouldMatchCase: self._should_match_case(),
            Plugin.Option.IsRegex: self._is_regex()
        })

    #############################################
    #   Private interface
    #############################################

    def _get_search_term(self):
        return self._search_term_edit.text()

    def _get_replace_term(self):
        return self._replace_term_edit.text()

    def _should_match_case(self):
        return self._match_case_checkbox.isChecked()

    def _is_regex(self):
        return self._regex_checkbox.isChecked()

    def _accept(self):
        if not self._get_search_term():
            self._search_term_edit.setStyleSheet('QLineEdit { background-color: #f6989d }')
            self._error_frame.setHidden(False)
            self._error_text.setText("Search term should not be empty.")
            return
        self._error_text.setHidden(True)
        self.accept()

    #############################################
    #   Private interface
    #############################################

    def config(self):
        return self._config