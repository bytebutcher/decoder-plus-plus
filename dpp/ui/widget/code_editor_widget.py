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
import logging
import re

from qtpy.QtCore import Qt, Signal
from qtpy.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor, QFontDatabase
from qtpy.QtWidgets import QFrame, QPlainTextEdit, QHBoxLayout


class CodeEditorWidget(QFrame):

    textChanged = Signal(str)  # source code

    def __init__(self, source_code):
        super().__init__()
        self._logger = logging.getLogger(__name__)
        view_frame_layout = QHBoxLayout()
        view_frame_layout.setContentsMargins(0, 5, 0, 5)
        self._highlighter = Highlighter()
        self._editor = self._setup_editor(source_code)
        self._old_text = self.text()
        self._editor.textChanged.connect(lambda: self._text_changed())
        view_frame_layout.addWidget(self._editor)
        self.setLayout(view_frame_layout)

    def _setup_editor(self, source_code):
        class_format = QTextCharFormat()
        class_format.setFontWeight(QFont.Bold)
        class_format.setForeground(Qt.blue)
        pattern = r'^\s*class\s+\w+\(.*$'
        self._highlighter.add_mapping(pattern, class_format)

        function_format = QTextCharFormat()
        function_format.setFontItalic(True)
        function_format.setForeground(Qt.blue)
        pattern = r'^\s*def\s+\w+\s*\(.*\)\s*:\s*$'
        self._highlighter.add_mapping(pattern, function_format)

        comment_format = QTextCharFormat()
        comment_format.setBackground(QColor("#77ff77"))
        self._highlighter.add_mapping(r'^\s*#.*$', comment_format)

        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        editor = QPlainTextEdit(source_code)
        editor.setFont(font)
        self._highlighter.setDocument(editor.document())
        return editor

    def _text_changed(self):
        # BUG: The text changed event is triggered even if there isn't an actual text change.
        # FIX: Check whether there is really a change and only then issue the textChanged event.
        if self._old_text != self.text():
            self._old_text = self.text()
            self.textChanged.emit(self._editor.toPlainText())


    def setText(self, text: str):
        self._editor.blockSignals(True)
        self._editor.setPlainText(text)
        self._editor.blockSignals(False)

    def text(self) -> str:
        return self._editor.toPlainText()


class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        QSyntaxHighlighter.__init__(self, parent)

        self._mappings = {}

    def add_mapping(self, pattern, format):
        self._mappings[pattern] = format

    def highlightBlock(self, text):
        for pattern, format in self._mappings.items():
            for match in re.finditer(pattern, text):
                start, end = match.span()
                self.setFormat(start, end - start, format)