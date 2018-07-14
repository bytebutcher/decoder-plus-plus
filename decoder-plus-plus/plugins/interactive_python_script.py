import qtawesome
from PyQt5.Qsci import QsciScintilla, QsciLexerPython
from PyQt5.QtGui import QFontMetrics, QColor, QFont
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout

from core.exception import AbortedException
from core.plugin.abstract_plugin import AbstractPlugin

from PyQt5.QtCore import pyqtSignal, QSize, Qt
from PyQt5.QtWidgets import QHBoxLayout, QFrame

from core.command import Command

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
            raise Exception("{}".format(e))



class InteractivePythonScriptDialog(QDialog):

    def __init__(self, code):
        super(__class__, self).__init__()
        layout = QVBoxLayout()
        self._code_view = CodeView()
        self._code_view.setCode(code)
        self._code_view.controlReturnKeyPressedEvent.connect(self.accept)
        self._code_view.escapeKeyPressedEvent.connect(self.reject)
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
    escapeKeyPressedEvent = pyqtSignal()

    def __init__(self, parent=None):
        super(CodeView, self).__init__(parent)
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
        self._editor.escapeKeyPressed.connect(self.escapeKeyPressedEvent.emit)
        editor_layout.addWidget(self._editor)
        editor_frame.setLayout(editor_layout)
        return editor_frame

    def setCode(self, text):
        self._editor.setText(text)

    def code(self):
        return self._editor.text()


class CodeEditor(QsciScintilla):
    ARROW_MARKER_NUM = 8

    controlReturnKeyPressed = pyqtSignal()
    escapeKeyPressed = pyqtSignal()

    def __init__(self, parent=None):
        super(CodeEditor, self).__init__(parent)

        # Set the default font
        font = QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.setFont(font)
        self.setMarginsFont(font)
        self.setTabWidth(4)

        # Margin 0 is used for line numbers
        fontmetrics = QFontMetrics(font)
        self.setMarginsFont(font)
        self.setMarginWidth(0, fontmetrics.width("00000") + 6)
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QColor("#90FF90"))

        # Clickable margin 1 for showing markers
        self.setMarginSensitivity(1, True)
        self.marginClicked.connect(self.on_margin_clicked)

        # Brace matching: enable for a brace immediately before or after the current position
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        # Set Python lexer
        # Set style for Python comments (style number 1) to a fixed-width courier.
        lexer = QsciLexerPython()
        lexer.setDefaultFont(font)
        self.setLexer(lexer)

        text = bytearray(str.encode("Arial"))
        # 32, "Courier New"
        self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, 1, text)

        # Don't want to see the horizontal scrollbar at all
        self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)

    def on_margin_clicked(self, nmargin, nline, modifiers):
        # Toggle marker for the line the margin was clicked on
        if self.markersAtLine(nline) != 0:
            self.markerDelete(nline, self.ARROW_MARKER_NUM)
        else:
            self.markerAdd(nline, self.ARROW_MARKER_NUM)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
            self.controlReturnKeyPressed.emit()
        if event.key() == Qt.Key_Escape:
            self.escapeKeyPressed.emit()
        super(CodeEditor, self).keyPressEvent(event)

