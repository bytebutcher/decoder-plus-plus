from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QPlainTextEdit, QHBoxLayout


class PlainView(QFrame):

    textChanged = pyqtSignal()

    def __init__(self, text):
        super(PlainView, self).__init__()
        layout = QHBoxLayout()
        self._plain_text = QPlainTextEdit(text)
        self._plain_text.textChanged.connect(self.textChanged.emit)
        layout.addWidget(self._plain_text)
        self.setLayout(layout)

    def toPlainText(self):
        return self._plain_text.toPlainText()

    def setPlainText(self, text):
        return self._plain_text.setPlainText(text)

    def setFocus(self, Qt_FocusReason=None):
        self._plain_text.setFocus()