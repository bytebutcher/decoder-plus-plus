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
from qtpy import QtCore
from qtpy.QtCore import QRegularExpression, QPoint, QEvent
from qtpy.QtGui import QColor, QBrush, QTextCharFormat, QTextCursor, QCursor
from qtpy.QtWidgets import QAction, QFrame, QVBoxLayout, QPlainTextEdit

from dpp.core import Context
from dpp.core.icons import icon, Icon
from dpp.ui import SearchField


class PlainView(QFrame):
    """
    Represents the plain-view of the Decoder++ application.
    """

    class EventFilter(QtCore.QObject):

        def __init__(self, parent, context: 'core.context.Context', callback):
            QtCore.QObject.__init__(self, parent)
            self._context = context
            self._callback = callback

        def eventFilter(self, obj, event):
            self._callback(obj, event)
            return QtCore.QObject.eventFilter(self, obj, event)

    def __init__(self, tab_id: str, frame_id: str, text: str, context: Context, parent):
        """
        Initializes the plain view.
        :param text: the text to be shown in the plain-text-edit.
        """
        super(__class__, self).__init__(parent)
        self._context = context
        self._listener = context.listener()
        self._tab_id = tab_id
        self._frame_id = frame_id

        self._plain_text = QPlainTextEdit()
        self.setPlainText(text)
        self._plain_text.setLineWrapMode(QPlainTextEdit.NoWrap)
        self._plain_text.dragEnterEvent = self._on_plain_text_drag_enter_event
        self._plain_text.dropEvent = self._on_plain_text_drop_event
        self._plain_text.textChanged.connect(self._on_plain_text_changed_event)
        self._plain_text.selectionChanged.connect(self._on_plain_text_selection_changed_event)
        self._plain_text.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._plain_text.customContextMenuRequested.connect(self.showContextMenu)
        self._plain_text.installEventFilter(
            PlainView.EventFilter(self, self._context, self._on_plain_text_focus_changed_event))

        self._listener.textSubmitted.connect(self._on_plain_text_submitted_event)

        self._last_plain_text = self.toPlainText()
        self._last_selected_plain_text = self.toPlainText()

        self._search_field = SearchField(self)
        self._search_field.setClosable(True)
        self._search_field.setIcon(icon(Icon.SEARCH))
        self._search_field.setPlaceholderText("Search text")
        self._search_field.escapePressed.connect(self._on_search_field_escape_pressed_event)
        self._search_field.textChanged.connect(self._do_highlight_text)
        self._search_field.closeEvent.connect(self._do_close_search_field)
        self._search_field.setVisible(False)

        # Propagate that a new frame was loaded
        self._context.listener().selectedFrameChanged.emit(self._tab_id, self._frame_id, self.toPlainText())

        layout = QVBoxLayout()
        layout.addWidget(self._plain_text)
        layout.addWidget(self._search_field)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

    def id(self) -> str:
        return self._frame_id

    def showContextMenu(self, point: QPoint=None):
        """ Displays a customized context menu for the plain view. """
        if not point:
            point = QCursor.pos()
        context_menu = self._plain_text.createStandardContextMenu()

        textSelected = len(self._plain_text.textCursor().selectedText()) > 0

        open_selection_in_new_tab_action = QAction(self)
        open_selection_in_new_tab_action.setText("Open Selection In New Tab")
        open_selection_in_new_tab_action.setEnabled(textSelected)
        open_selection_in_new_tab_action.triggered.connect(self._on_plain_text_context_menu_open_selection_in_new_tab)
        context_menu.insertAction(context_menu.actions()[0], open_selection_in_new_tab_action)

        separator_action = QAction(self)
        separator_action.setSeparator(True)
        context_menu.insertAction(context_menu.actions()[1], separator_action)

        context_menu.addSeparator()
        wrap_lines_action = QAction(self)
        wrap_lines_action.setText("Wrap Lines")
        wrap_lines_action.setCheckable(True)
        wrap_lines_action.setChecked(self._plain_text.lineWrapMode() == QPlainTextEdit.WidgetWidth)
        wrap_lines_action.triggered.connect(self._on_plain_text_context_menu_wrap_lines)
        context_menu.addAction(wrap_lines_action)
        context_menu.exec(self._plain_text.mapToGlobal(point))

    def _on_plain_text_context_menu_wrap_lines(self, e: QEvent):
        """ Un-/wraps lines when user clicks the wrap-lines action within the plain views context-menu. """
        if self._plain_text.lineWrapMode() == QPlainTextEdit.NoWrap:
            self._plain_text.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        else:
            self._plain_text.setLineWrapMode(QPlainTextEdit.NoWrap)

    def _on_plain_text_context_menu_open_selection_in_new_tab(self, e: QEvent):
        """ Fires a signal that context-menu entry to open selection in new tab was triggered. """
        selectedText = self._plain_text.textCursor().selectedText()
        self._listener.newTabRequested.emit(None, selectedText)

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
                self._context.logger.error("Error reading file: " + str(e))
        elif data.hasText():
            # Drops text into text field.
            self._plain_text.setPlainText(data.text())

    def _on_plain_text_changed_event(self):
        """ Signals that text has changed and highlights text when search field is active. """
        if self._last_plain_text != self.toPlainText():
            self._last_plain_text = self.toPlainText()
            if self._search_field.isVisible():
                self._do_highlight_text()
        self._context.listener().textChanged.emit(self._tab_id, self._frame_id, self.toPlainText(), True)

    def _on_plain_text_selection_changed_event(self):
        cursor = self._plain_text.textCursor()
        selected_text = cursor.selectedText()
        if selected_text and selected_text != self._last_selected_plain_text:
            self._last_selected_plain_text = selected_text
            self._context.listener().textSelectionChanged.emit(self._tab_id, self._frame_id, selected_text)

    def _on_plain_text_focus_changed_event(self, obj, event):
        if event.type() == QtCore.QEvent.FocusIn and event.reason() == QtCore.Qt.MouseFocusReason:
            if self._plain_text.hasFocus():
                self._context.listener().selectedFrameChanged.emit(self._tab_id, self._frame_id, self.toPlainText())

    def _on_plain_text_submitted_event(self, tab_id: str, frame_id: str, text: str):
        if tab_id == self._tab_id and frame_id == self._frame_id:
            self._plain_text.setPlainText(text)

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
            regex = QRegularExpression(QRegularExpression.escape(text))

            # Process the displayed document
            iterator = regex.globalMatch(self._plain_text.toPlainText())
            while iterator.hasNext():
                match = iterator.next()
                # Select the matched text and apply the desired format
                cursor.setPosition(match.capturedStart())
                cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor, match.capturedLength())
                cursor.mergeCharFormat(format)

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

    def cutSelectedInputText(self):
        self._plain_text.cut()

    def copySelectedInputText(self):
        self._plain_text.copy()

    def pasteSelectedInputText(self):
        self._plain_text.paste()

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
        # Avoid triggering textChanged-event when setting text manually
        self._plain_text.blockSignals(True)
        self._plain_text.setPlainText(text)
        # Bug: When setting text the cursor position is set to beginning of plain text field.
        # Fix: Manually set cursor position to end of plain text field when setting text.
        self.setCursorPosition(QTextCursor.End)
        self._plain_text.blockSignals(False)

    def setCursorPosition(self, cursor_position: 'QTextCursor.MoveOperation'):
        """ Sets the cursor to the defined position. """
        plain_text_cursor = self._plain_text.textCursor()
        plain_text_cursor.movePosition(cursor_position)
        self._plain_text.setTextCursor(plain_text_cursor)

    def setFocus(self, Qt_FocusReason=None):
        """ Sets the focus to the plain text area. """
        self._plain_text.setFocus()
