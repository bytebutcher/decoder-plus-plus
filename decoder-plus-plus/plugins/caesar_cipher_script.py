import string

import qtawesome
from PyQt5 import QtCore
from PyQt5.QtGui import QKeySequence, QIntValidator
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLineEdit, QFrame, QPlainTextEdit, QShortcut, \
    QSlider, QHBoxLayout

from core.exception import AbortedException
from core.plugin.abstract_plugin import AbstractPlugin
from core.command import Command

class Plugin(AbstractPlugin):

    def __init__(self, context):
        # Name, Type, Author, Dependencies
        super().__init__('Caesar Cipher', Command.Type.SCRIPT, "Thomas Engel", )
        self._shift = None
        self._dialog = None

    def select(self, text):
        if not self._dialog:
            self._dialog = CaesarCipherDialog(text, self._do_caesar)
        if self._dialog.exec_() == QDialog.Accepted:
            self._shift = self._dialog.getShift()
            return self.run(text)
        else:
            # User clicked the Cancel-Button.
            self._shift = None
            raise AbortedException("Aborted")

    def title(self):
        return "{} shift {}".format("Caesar Cipher", self._shift)

    def run(self, text, shift=None):
        return self._do_caesar(text, self._shift)

    def _do_caesar(self, plaintext, shift):
        alphabet = string.ascii_lowercase
        shifted_alphabet = alphabet[shift:] + alphabet[:shift]
        table = str.maketrans(alphabet, shifted_alphabet)
        return plaintext.translate(table)


class CaesarCipherDialog(QDialog):

    def __init__(self, input, callback):
        super(CaesarCipherDialog, self).__init__()
        main_layout = QVBoxLayout()
        main_layout.addWidget(self._init_editor_frame())
        main_layout.addWidget(self._init_button_box())
        self.setLayout(main_layout)
        self.setWindowIcon(qtawesome.icon("fa.edit"))
        self.setWindowTitle("Caesar Cipher")
        self._setup_shortcuts()
        self._input = input
        self._text_area.setPlainText(self._input)
        self._callback = callback


    def _setup_shortcuts(self):
        ctrl_return_shortcut = QShortcut(QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_Return), self)
        ctrl_return_shortcut.activated.connect(self._accept)
        alt_return_shortcut = QShortcut(QKeySequence(QtCore.Qt.ALT + QtCore.Qt.Key_Return), self)
        alt_return_shortcut.activated.connect(self._accept)
        alt_o_shortcut = QShortcut(QKeySequence(QtCore.Qt.ALT + QtCore.Qt.Key_O), self)
        alt_o_shortcut.activated.connect(self._accept)

    def _init_button_box(self):
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._accept)
        button_box.rejected.connect(self.reject)
        return button_box

    def _init_editor_frame(self):
        main_frame = QFrame()
        main_frame_layout = QVBoxLayout()

        slider_frame = self._init_slider_frame()
        main_frame_layout.addWidget(slider_frame)

        self._text_area = QPlainTextEdit()
        self._text_area.setReadOnly(True)
        self._text_area.setFixedHeight(126)
        main_frame_layout.addWidget(self._text_area)

        main_frame.setLayout(main_frame_layout)
        return main_frame

    def _init_slider_frame(self):
        slider_frame = QFrame()
        slider_frame_layout = QHBoxLayout()
        self._shift_slider = QSlider(QtCore.Qt.Horizontal)
        self._shift_slider.setMinimum(0)
        self._shift_slider.setMaximum(26)
        self._shift_slider.setValue(0)
        self._shift_slider.valueChanged.connect(self._shift_slider_changed)
        slider_frame_layout.addWidget(self._shift_slider)
        self._shift_text = QLineEdit()
        self._shift_text.setText("0")
        self._shift_text.setFixedWidth(30)
        self._shift_text.setValidator(QIntValidator(0, 26))
        self._shift_text.textChanged.connect(self._shift_text_changed)
        slider_frame_layout.addWidget(self._shift_text)
        slider_frame.setLayout(slider_frame_layout)
        return slider_frame

    def _shift_slider_changed(self, shift):
        if not shift:
            shift = 0
        self._shift_changed(shift)

    def _shift_text_changed(self, shift):
        if not shift:
            shift = 0
        self._shift_changed(int(shift))

    def _shift_changed(self, shift):
        self._shift_text.blockSignals(True)
        self._shift_slider.blockSignals(True)
        self._shift_slider.setValue(shift)
        self._shift_text.setText(str(shift))
        self._text_area.setPlainText(self._callback(self._input, shift))
        self._shift_slider.blockSignals(False)
        self._shift_text.blockSignals(False)

    def _accept(self):
        self.accept()

    def getShift(self):
        return self._shift_slider.value()
