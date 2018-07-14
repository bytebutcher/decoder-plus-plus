import string

import qtawesome
from PyQt5 import QtCore
from PyQt5.QtGui import QKeySequence, QIntValidator
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLineEdit, QFrame, QPlainTextEdit, QShortcut, \
    QSlider, QHBoxLayout

from core.exception import AbortedException
from core.plugin.abstract_plugin import AbstractPlugin
from core.command import Command

from PyQt5.QtCore import pyqtSignal, QSize
from PyQt5.QtWidgets import QHBoxLayout, QFrame

from core.command import Command
from ui.code_editor import CodeEditor

# Import DecoderPlusPlus required for Interactive Mode.
# from core.decoder_plus_plus import DecoderPlusPlus
from core.decoder_plus_plus import DecoderPlusPlus


class Plugin(AbstractPlugin):

    def __init__(self, context):
        # Name, Type, Author, Dependencies
        super().__init__('Interactive Python', Command.Type.SCRIPT, "Thomas Engel", )
        self._code = None
        self._dialog = None

    def select(self, text):
        if not self._dialog:
            self._dialog = InteractivePythonScriptDialog("def run(input):\n\treturn input")
            self._dialog.resize(QSize(500, 200))
            self._dialog.setMinimumWidth(500)
            self._dialog.setMinimumHeight(200)
        if self._dialog.exec_() == QDialog.Accepted:
            self._code = self._dialog.getCode()
            return self.run(text)
        else:
            # User clicked the Cancel-Button.
            self._code = None
            raise AbortedException("Aborted")

    def run(self, text, code=None):
        try:
            exec(self._dialog.getCode(), globals(), locals())
            return eval("run")(text)
        except Exception as e:
            raise Exception("Interactive Mode: {}".format(e))



class InteractivePythonScriptDialog(QDialog):

    def __init__(self, code):
        super(__class__, self).__init__()
        layout = QVBoxLayout()
        self._code_view = CodeView()
        self._code_view.setCode(code)
        layout.addWidget(self._code_view)
        layout.addWidget(self._init_button_box())
        self.setLayout(layout)
        self.setWindowIcon(qtawesome.icon("fa.edit"))
        self.setWindowTitle("Interactive Python Script")

    def _init_button_box(self):
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        return button_box

    def setCode(self, code):
        self._code_view.setCode(code)

    def getCode(self):
        return self._code_view.code()


class CodeView(QFrame):

    controlReturnKeyPressedEvent = pyqtSignal()

    def __init__(self, parent=None):
        super(CodeView, self).__init__(parent)
        self._type_to_method = {
            Command.Type.DECODER: "decode",
            Command.Type.ENCODER: "encode",
            Command.Type.HASHER: "hash",
            Command.Type.SCRIPT: "script"
        }
        self._text_changed = False

        # BUG: Blocking text-change-events within code-editor will have nasty side-effects.
        # WORKAROUND: Implement custom text-change-event-blocker.
        self._block_text_changed_event = False
        python_view_layout = QHBoxLayout()
        python_view_layout.setContentsMargins(0, 0, 0, 0)
        python_view_layout.addWidget(self._init_editor_frame())
        self.setLayout(python_view_layout)

    def _init_editor_frame(self):
        editor_frame = QFrame()
        editor_frame.setContentsMargins(0, 0, 0, 0)
        editor_layout = QHBoxLayout()
        editor_layout.setContentsMargins(0, 0, 0, 0)
        self._editor = CodeEditor()
        self._editor.controlReturnKeyPressed.connect(self.controlReturnKeyPressedEvent.emit)
        editor_layout.addWidget(self._editor)
        editor_frame.setLayout(editor_layout)
        return editor_frame

    def setTextByCommand(self, command):
        self._block_text_changed_event = True
        self.setCode("def run(input):\n\treturn DecoderPlusPlus(input).{type}().{name}().run()".format(
            type=self._type_to_method[command.type()], name=command.name(safe_name=True)))
        self._block_text_changed_event = False

    def setCode(self, text):
        self._text_changed = False
        self._block_text_changed_event = True
        self._editor.setText(text)
        self._block_text_changed_event = False

    def code(self):
        return self._editor.text()
