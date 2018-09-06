import qtawesome
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QRadioButton, QFrame, QFormLayout, QDialogButtonBox, QLineEdit, \
    QLabel, QGroupBox

from core.exception import AbortedException
from core.plugin.plugin import ScriptPlugin


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

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('Split & Rejoin', "Thomas Engel", [], context)
        self._dialog = None
        self._dialog_return_code = None

    def title(self):
        if self._dialog.getSplitByOption() == SplitAndRejoinDialog.SPLIT_BY_LENGTH:
            return "Split by length {} and Rejoin with '{}'".format(
                self._dialog.getSplitByText(), self._dialog.getJoinWithText()
            )
        elif self._dialog.getSplitByOption() == SplitAndRejoinDialog.SPLIT_BY_CHARACTER:
            return "Split by character '{}' and Rejoin with '{}'".format(
                self._dialog.getSplitByText(), self._dialog.getJoinWithText()
            )
        return "Split by '{}' and Rejoin with '{}'".format(self._dialog.getSplitByText(), self._dialog.getJoinWithText())

    def safe_name(self):
        return "split_and_rejoin"

    def select(self, text):
        if not self._dialog:
            self._dialog = SplitAndRejoinDialog()
        self._dialog_return_code = self._dialog.exec_()
        return self.run(text)

    def run(self, text):
        if text:
            if self._dialog_return_code == QDialog.Accepted:
                input = ""
                if self._dialog.getSplitByOption() == SplitAndRejoinDialog.SPLIT_BY_LENGTH:
                    input = self._chunk_string(text, self._dialog.getSplitByLength())
                elif self._dialog.getSplitByOption() == SplitAndRejoinDialog.SPLIT_BY_CHARACTER:
                    input = text.split(self._dialog.getSplitByText())
                return self._dialog.getJoinWithText().join(input)
            else:
                # User clicked the Cancel-Button.
                raise AbortedException("Aborted")
        return ''

    def _chunk_string(self, string, length):
        return [string[0 + i:length + i] for i in range(0, len(string), length)]


class SplitAndRejoinDialog(QDialog):

    SPLIT_BY_ERROR = -1
    SPLIT_BY_CHARACTER = 1
    SPLIT_BY_LENGTH = 2

    def __init__(self):
        super(SplitAndRejoinDialog, self).__init__()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self._init_form_frame())
        main_layout.addWidget(self._init_error_frame())
        main_layout.addWidget(self._init_button_box())
        self.setLayout(main_layout)
        self.setWindowIcon(qtawesome.icon("fa.edit"))
        self.setWindowTitle("Split & Rejoin")

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
        button_box.accepted.connect(self._accept)
        button_box.rejected.connect(self.reject)
        return button_box

    def _accept(self):
        if not self.getSplitByText():
            self._show_split_by_text_error("Split by text should not be empty.")
            return

        if self.getSplitByText() and self.getSplitByOption() == self.SPLIT_BY_LENGTH:
            try:
                length = int(self.getSplitByText())
                if length <= 0:
                    self._show_split_by_text_error("Split by text should be greater than 0.")
                    return
            except:
                self._show_split_by_text_error("Split by text should be an integer.")
                return

        self._error_text.setHidden(True)
        self.accept()

    def getSplitByOption(self):
        if self._split_by_character_radio_button.isChecked():
            return self.SPLIT_BY_CHARACTER
        if self._split_by_length_radio_button.isChecked():
            return self.SPLIT_BY_LENGTH
        return self.SPLIT_BY_ERROR

    def getSplitByText(self):
        return self._split_by_line_edit.text()

    def getSplitByLength(self):
        return int(self.getSplitByText())

    def getJoinWithText(self):
        return self._join_with_line_edit.text()

    def _init_form_frame(self):
        form_frame = QGroupBox()
        form_frame_layout = QFormLayout()
        self._split_by_character_radio_button = QRadioButton("Character")
        self._split_by_character_radio_button.setChecked(True)
        self._split_by_length_radio_button = QRadioButton("Length")
        self._split_by_length_radio_button.setChecked(False)
        self._split_by_line_edit = QLineEdit()
        self._join_with_line_edit = QLineEdit()
        split_by_layout = QVBoxLayout()
        split_by_layout.addWidget(self._split_by_line_edit)
        split_by_layout.addWidget(self._split_by_character_radio_button)
        split_by_layout.addWidget(self._split_by_length_radio_button)
        form_frame_layout.addRow(QLabel("Split by"), split_by_layout)
        form_frame_layout.addRow(QLabel("Rejoin with"), self._join_with_line_edit)
        form_frame.setLayout(form_frame_layout)
        return form_frame

    def _show_split_by_text_error(self, text: str):
        self._split_by_line_edit.setStyleSheet('QLineEdit { background-color: #f6989d }')
        self._error_frame.setHidden(False)
        self._error_text.setText(text)
