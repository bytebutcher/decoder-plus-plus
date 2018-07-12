import re

import qtawesome
from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QFrame, \
    QCheckBox, QToolTip

from core.exception import AbortedException
from core.plugin.abstract_plugin import AbstractPlugin
from core.command import Command

class Plugin(AbstractPlugin):

    def __init__(self, context):
        # Name, Type, Author, Dependencies
        super().__init__('Search & Replace', Command.Type.SCRIPT, "Thomas Engel", )
        self._dialog = None
        self._dialog_return_code = None

    def select(self, text):
        if not self._dialog:
            self._dialog = SearchAndReplaceDialog()
        self._dialog_return_code = self._dialog.exec_()
        return self.run(text)

    def title(self):
        return "Search and Replace '{}' with '{}' using {}".format(
            self._getSearchTerm(), self._getReplaceTerm(), self._getOptionAsHumanReadableString())

    def _getOptionAsHumanReadableString(self):
        if self._shouldMatchCase():
            return 'Match Case'
        elif self._isRegex():
            return 'Regular Expression'
        else:
            return 'Ignore Case'

    def _getSearchTerm(self):
        return self._dialog.getSearchTerm()

    def _getReplaceTerm(self):
        return self._dialog.getReplaceTerm()

    def _shouldMatchCase(self):
        return self._dialog.shouldMatchCase()

    def _isRegex(self):
        return self._dialog.isRegex()

    def run(self, text):
        if self._dialog_return_code == QDialog.Accepted:
            if self._isRegex() and self._shouldMatchCase():
                return re.sub(self._getSearchTerm(), self._getReplaceTerm(), text, flags=re.IGNORECASE)
            elif self._isRegex():
                return re.sub(self._getSearchTerm(), self._getReplaceTerm(), text)
            elif self._shouldMatchCase():
                return text.replace(self._getSearchTerm(), self._getReplaceTerm())
            else:
                return self._replace_ignore_case(text)
        else:
            # User clicked the Cancel-Button.
            raise AbortedException("Aborted")

    def _replace_ignore_case(self, text):
        regexp = re.compile(re.escape(self._getSearchTerm()), re.IGNORECASE)
        return regexp.sub(self._getReplaceTerm(), text)


class SearchAndReplaceDialog(QDialog):

    def __init__(self):
        super(SearchAndReplaceDialog, self).__init__()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self._init_form_frame())
        main_layout.addWidget(self._init_button_box())
        self.setLayout(main_layout)
        self.setWindowIcon(qtawesome.icon("fa.search"))
        self.setWindowTitle("Search & Replace")

    def _init_button_box(self):
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._accept)
        button_box.rejected.connect(self.reject)
        return button_box

    def _accept(self):
        if not self.getSearchTerm():
            self._search_term_edit.setStyleSheet('QLineEdit { background-color: #f6989d }')
            QToolTip.showText(self._search_term_edit.mapToGlobal(QPoint()), "Search term should not be empty.")
            return
        self.accept()

    def _init_form_frame(self):
        form_frame = QFrame()
        form_frame_layout = QFormLayout()
        self._search_term_edit = QLineEdit()
        form_frame_layout.addRow(QLabel("Search:"), self._search_term_edit)
        self._replace_term_edit = QLineEdit()
        form_frame_layout.addRow(QLabel("Replace:"), self._replace_term_edit)
        self._match_case_checkbox = QCheckBox("Match Case")
        self._match_case_checkbox.setChecked(True)
        form_frame_layout.addWidget(self._match_case_checkbox)
        self._regex_checkbox = QCheckBox("Regex")
        self._regex_checkbox.setChecked(False)
        form_frame_layout.addWidget(self._regex_checkbox)

        form_frame.setLayout(form_frame_layout)
        return form_frame

    def shouldMatchCase(self):
        return self._match_case_checkbox.isChecked()

    def isRegex(self):
        return self._regex_checkbox.isChecked()

    def getSearchTerm(self):
        return self._search_term_edit.text()

    def getReplaceTerm(self):
        return self._replace_term_edit.text()
