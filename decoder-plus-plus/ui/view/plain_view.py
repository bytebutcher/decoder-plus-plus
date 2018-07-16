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

import qtawesome
from PyQt5.QtCore import pyqtSignal, QRegExp, Qt
from PyQt5.QtGui import QColor, QBrush, QTextCharFormat, QTextCursor
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QPlainTextEdit

from ui import SearchField


class PlainView(QFrame):

    textChanged = pyqtSignal()

    def __init__(self, text):
        super(PlainView, self).__init__()
        layout = QVBoxLayout()
        self._plain_text = QPlainTextEdit(text)
        self._plain_text.textChanged.connect(self._onPlainTextChangedEvent)
        self._search_field = SearchField()
        self._search_field.setClosable(True)
        self._search_field.setIcon(qtawesome.icon("fa.search"))
        self._search_field.setPlaceholderText("Search text")
        self._search_field.escapePressed.connect(self._onEscapePressedEvent)
        self._search_field.textChanged.connect(self._onSearchFieldChangedEvent)
        self._search_field.setVisible(False)
        layout.addWidget(self._plain_text)
        layout.addWidget(self._search_field)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def _onPlainTextChangedEvent(self):
        self.textChanged.emit()
        if self._search_field.isVisible():
            self._onSearchFieldChangedEvent()

    def _onEscapePressedEvent(self):
        if self._search_field.hasFocus() and self._search_field.isVisible():
            self._doCloseSearchField()

    def _onSearchFieldChangedEvent(self):
        self._plain_text.blockSignals(True)
        self._do_highlight_text()
        self._plain_text.blockSignals(False)
        return False

    def _do_highlight_clear(self):
        format = QTextCharFormat()
        format.setForeground(QBrush(QColor("black")))
        cursor = self._plain_text.textCursor()
        cursor.setPosition(0)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor, 1)
        cursor.mergeCharFormat(format)

    def _do_highlight_text(self):

        def highlight_text(text, format):
            cursor = self._plain_text.textCursor()
            regex = QRegExp(QRegExp.escape(text))

            # Process the displayed document
            pos = 0
            index = regex.indexIn(self._plain_text.toPlainText(), pos)
            while index != -1:
                # Select the matched text and apply the desired format
                cursor.setPosition(index)
                cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor, len(text))
                cursor.mergeCharFormat(format)
                # Move to the next match
                pos = index + regex.matchedLength()
                index = regex.indexIn(self.toPlainText(), pos)

        self._do_highlight_clear()
        searchString = self._search_field.text()
        if searchString:
            format = QTextCharFormat()
            format.setForeground(QBrush(QColor("red")))
            highlight_text(searchString, format)

    def toggleSearchField(self):
        if self._search_field.hasFocus() and self._search_field.isVisible():
            self._doCloseSearchField()
        else:
            self._doOpenSearchField()

    def _doOpenSearchField(self):
        self._search_field.setVisible(True)
        self._do_highlight_text()
        self._search_field.setFocus()

    def _doCloseSearchField(self):
        self._do_highlight_clear()
        self._plain_text.setFocus()
        self._search_field.setVisible(False)

    def toPlainText(self):
        return self._plain_text.toPlainText()

    def setPlainText(self, text):
        return self._plain_text.setPlainText(text)

    def setFocus(self, Qt_FocusReason=None):
        self._plain_text.setFocus()
