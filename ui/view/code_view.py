# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of Decoder++
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout, QFrame

from core.command import Command
from ui.code_editor import CodeEditor
# Import DecoderPlusPlus required for Interactive Mode.
# from core.decoder_plus_plus import DecoderPlusPlus
from core.decoder_plus_plus import DecoderPlusPlus


class CodeView(QFrame):

    textChanged = pyqtSignal()
    runEvent = pyqtSignal()
    savePressed = pyqtSignal()

    def __init__(self, parent, context):
        super(CodeView, self).__init__(parent)
        self._type_to_method = {
            Command.Type.DECODER: "decode",
            Command.Type.ENCODER: "encode",
            Command.Type.HASHER: "hash",
            Command.Type.SCRIPT: "script"
        }
        self._context = context
        self._logger = context.logger()
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
        self._editor.textChanged.connect(self._text_changed_event)
        self._editor.controlReturnKeyPressed.connect(self.runEvent.emit)
        editor_layout.addWidget(self._editor)
        editor_frame.setLayout(editor_layout)
        return editor_frame

    def _text_changed_event(self):
        if not self._block_text_changed_event:
            self._text_changed = True
            self.textChanged.emit()

    def hasTextChanged(self):
        return self._text_changed

    def setTextByCommand(self, command):
        self._block_text_changed_event = True
        self.setText("def run(input):\n\treturn DecoderPlusPlus(input).{type}().{name}().run()".format(
            type=self._type_to_method[command.type()], name=command.name(safe_name=True)))
        self._block_text_changed_event = False

    def setText(self, text):
        self._text_changed = False
        self._block_text_changed_event = True
        self._editor.setText(text)
        self._block_text_changed_event = False

    def text(self):
        return self._editor.text()

    def run(self, input):
        try:
            exec(self.text(), globals(), locals())
            return eval("run")(input)
        except Exception as e:
            raise Exception("Interactive Mode: {}".format(e))
