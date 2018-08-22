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
import qtawesome
from PyQt5.QtCore import pyqtSignal, QRegExp, Qt
from PyQt5.QtGui import QColor, QBrush, QTextCharFormat, QTextCursor
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QPlainTextEdit

from ui import SearchField


class PlainView(QFrame):
    """
    Represents the plain-view of the Decoder++ application.
    """

    textChanged = pyqtSignal()

    def __init__(self, text):
        """
        Initializes the plain view.
        :param text: the text to be shown in the plain-text-edit.
        """
        super(PlainView, self).__init__()
        self._logger = logging.getLogger('decoder_plusplus')

        self._plain_text = QPlainTextEdit(text)
        self._plain_text.dragEnterEvent = self._on_plain_text_drag_enter_event
        self._plain_text.dropEvent = self._on_plain_text_drop_event
        self._plain_text.textChanged.connect(self._on_plain_text_changed_event)

        self._search_field = SearchField()
        self._search_field.setClosable(True)
        self._search_field.setIcon(qtawesome.icon("fa.search"))
        self._search_field.setPlaceholderText("Search text")
        self._search_field.escapePressed.connect(self._on_search_field_escape_pressed_event)
        self._search_field.textChanged.connect(self._do_highlight_text)
        self._search_field.closeEvent.connect(self._do_close_search_field)
        self._search_field.setVisible(False)

        layout = QVBoxLayout()
        layout.addWidget(self._plain_text)
        layout.addWidget(self._search_field)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

    def _on_plain_text_drag_enter_event(self, e):
        """ Catches the drag-enter-event which is triggered when media is dragged into the plain text area. """
        data = e.mimeData()
        if data.hasUrls():
            if len(data.urls()) == 1:
                url = data.urls()[0].toString()
                if (url.startswith("file://")):
                    # Accept single file to be dragged into the plain text area.
                    return e.accept()
        elif data.hasText():
            # Accept text to be dragged into the plain text area.
            return e.accept()
        # Ignore everything else.
        return e.ignore()

    def _on_plain_text_drop_event(self, e):
        """ Catches the drop-event which is triggered when media is dropped into the plain text area. """
        data = e.mimeData()
        if data.hasUrls():
            file_path = data.urls()[0].toLocalFile()
            try:
                with open(file_path, mode='rb') as f:
                    # Drops text within (binary) file into plain text area.
                    self._plain_text.setPlainText(f.read().decode('utf-8', errors='surrogateescape'))
            except Exception as e:
                self._logger.error("Error reading file: " + str(e))
        elif data.hasText():
            # Drops text into text field.
            self._plain_text.setPlainText(data.text())

    def _on_plain_text_changed_event(self):
        """ Signals that text has changed and highlights text when search field is active. """
        self.textChanged.emit()
        if self._search_field.isVisible():
            self._do_highlight_text()

    def _on_search_field_escape_pressed_event(self):
        """ Closes the search field when search field is focused. """
        if self._search_field.hasFocus() and self._search_field.isVisible():
            self._do_close_search_field()

    def _do_highlight_clear(self):
        """ Clears any highlighting found within the plain text area. """
        self._plain_text.blockSignals(True)
        format = QTextCharFormat()
        format.setForeground(QBrush(QColor("black")))
        cursor = self._plain_text.textCursor()
        cursor.setPosition(0)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor, 1)
        cursor.mergeCharFormat(format)
        self._plain_text.blockSignals(False)

    def _do_highlight_text(self):
        """ Highlights text in the plain-view matching the current search-term."""

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
        self._plain_text.blockSignals(True)
        searchString = self._search_field.text()
        if searchString:
            format = QTextCharFormat()
            format.setForeground(QBrush(QColor("red")))
            highlight_text(searchString, format)
        self._plain_text.blockSignals(False)

    def _do_open_search_field(self):
        """ Opens the search field. """
        self._search_field.setVisible(True)
        self._do_highlight_text()
        self._search_field.setFocus()

    def _do_close_search_field(self):
        """ Closes the search field. """
        self._do_highlight_clear()
        self._plain_text.setFocus()
        self._search_field.setVisible(False)

    def toggleSearchField(self):
        """ Toggles the search field. """
        if self._search_field.hasFocus() and self._search_field.isVisible():
            self._do_close_search_field()
        else:
            self._do_open_search_field()

    def toPlainText(self):
        """ Returns the plain text of the plain text area. """
        return self._plain_text.toPlainText()

    def setPlainText(self, text):
        """ Sets the text of the text area. """
        return self._plain_text.setPlainText(text)

    def setFocus(self, Qt_FocusReason=None):
        """ Sets the focus to the plain text area. """
        self._plain_text.setFocus()
