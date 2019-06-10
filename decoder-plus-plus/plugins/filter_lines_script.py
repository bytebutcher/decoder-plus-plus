import os
import re
import qtawesome

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QFrame, QPlainTextEdit, QShortcut, \
    QHBoxLayout, QCheckBox

from core.exception import AbortedException
from core.plugin.plugin import ScriptPlugin
from ui import SearchField


class Plugin(ScriptPlugin):
    """
    Opens a dialog to filter text by certain conditions.
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('Filter Lines', "Thomas Engel", [], context)
        self._dialog = None
        self._filter_term = ""
        self._should_match_case = True
        self._should_invert_match = False
        self._is_regex = False
        self._dialog_return_code = QDialog.Accepted

    def config(self):
        return {
            "_filter_term": self._filter_term,
            "_should_match_case": self._should_match_case,
            "_should_invert_match": self._should_invert_match,
            "_is_regex": self._is_regex,
            "_dialog_return_case": self._dialog_return_code
        }

    def select(self, text):
        if not self._dialog:
            self._dialog = FilterDialog(text, self._do_filter)
        else:
            self._dialog.setInput(text)

        self._dialog_return_code = self._dialog.exec_()
        self._filter_term = self._dialog.getFilterTerm()
        self._should_match_case = self._dialog.shouldMatchCase()
        self._should_invert_match = self._dialog.shouldInvertMatch()
        self._is_regex = self._dialog.isRegex()
        return self.run(text)

    def title(self):
        return "Filter lines by '{}' using {}".format(
            self._getFilterTerm(), self._getOptionAsHumanReadableString())

    def _getOptionAsHumanReadableString(self):
        options = []
        if self._shouldMatchCase():
            options.append('Match Case')
        else:
            options.append('Ignore Case')
        if self._isRegex():
            options.append('Regular Expression')
        if self._shouldInvertMatch():
            options.append('Invert Match')

        return self._join_options_as_human_readable_string(options)

    def _getFilterTerm(self):
        return self._filter_term

    def _shouldInvertMatch(self):
        return self._should_invert_match

    def _shouldMatchCase(self):
        return self._should_match_case

    def _isRegex(self):
        return self._is_regular_expression

    def run(self, text, shift=None):
        if self._dialog_return_code == QDialog.Accepted:
            return self._do_filter(text)
        else:
            # User clicked the Cancel-Button.
            raise AbortedException("Aborted")

    def _do_filter(self, text):
        lines = []
        for text_line in text.splitlines():
            if self._should_filter(text_line):
                lines.append(text_line)
        return os.linesep.join(lines)

    def _should_filter(self, text_line):
        if self._isRegex() and self._shouldMatchCase():
            result = len(re.match(self._getFilterTerm(), text_line, flags=re.IGNORECASE)) > 0
        elif self._isRegex():
            result = len(re.match(self._getFilterTerm(), text_line)) > 0
        elif self._shouldMatchCase():
            result = self._getFilterTerm() in text_line
        else:
            result = self._getFilterTerm().lower() in text_line.lower()
        if self._shouldInvertMatch():
            return not result
        else:
            return result


class FilterDialog(QDialog):

    def __init__(self, input, callback):
        super(__class__, self).__init__()
        main_layout = QVBoxLayout()
        main_layout.addWidget(self._init_editor_frame())
        main_layout.addWidget(self._init_button_box())
        self.setLayout(main_layout)
        self.setWindowIcon(qtawesome.icon("fa.filter"))
        self.setWindowTitle("Filter Lines")
        self._setup_shortcuts()
        self._input = input
        self._text_area.setPlainText(self._input)
        self._callback = callback

    def _setup_shortcuts(self):
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

        self._text_area = QPlainTextEdit()
        self._text_area.setReadOnly(True)
        self._text_area.setFixedHeight(126)
        main_frame_layout.addWidget(self._text_area)

        main_frame.setLayout(main_frame_layout)
        return main_frame

    def _init_filter_text_frame(self):
        filter_text_frame = QFrame()
        filter_text_frame_layout = QHBoxLayout()

        self._filter_term = SearchField()
        self._filter_term.setIcon(qtawesome.icon("fa.filter"))
        self._filter_term.setPlaceholderText("Filter")
        self._filter_term.textChanged.connect(lambda text: self._filter_changed())
        filter_text_frame_layout.addWidget(self._filter_term)

        self._match_case_checkbox = QCheckBox("Match Case")
        self._match_case_checkbox.setChecked(True)
        self._match_case_checkbox.stateChanged.connect(lambda state: self._filter_changed())
        filter_text_frame_layout.addWidget(self._match_case_checkbox)

        self._regex_checkbox = QCheckBox("Regex")
        self._regex_checkbox.setChecked(False)
        self._regex_checkbox.stateChanged.connect(lambda state: self._filter_changed())
        filter_text_frame_layout.addWidget(self._regex_checkbox)

        self._invert_match_checkbox = QCheckBox("Invert Match")
        self._invert_match_checkbox.setChecked(False)
        self._invert_match_checkbox.stateChanged.connect(lambda state: self._filter_changed())
        filter_text_frame_layout.addWidget(self._invert_match_checkbox)

        filter_text_frame_layout.setContentsMargins(0, 0, 0, 5)
        filter_text_frame.setLayout(filter_text_frame_layout)
        return filter_text_frame

    def _filter_changed(self):
        filter_text = self._callback(self._input)
        self._text_area.setPlainText(filter_text)

    def _accept(self):
        self.accept()

    def setInput(self, input):
        self._input = input
        self._filter_changed()

    def getFilterTerm(self):
        return self._filter_term.text()

    def shouldMatchCase(self):
        return self._match_case_checkbox.isChecked()

    def isRegex(self):
        return self._regex_checkbox.isChecked()

    def shouldInvertMatch(self):
        return self._invert_match_checkbox.isChecked()
