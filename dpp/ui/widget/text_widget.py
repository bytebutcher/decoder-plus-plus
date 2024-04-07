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

from qtpy import QtCore
from qtpy.QtCore import QPoint, QEvent
from qtpy.QtGui import QCursor
from qtpy.QtWidgets import QFrame, QPlainTextEdit, QHBoxLayout, QAction

from dpp.core.listener import Signal


class TextWidget(QFrame):

    # Note: Currently the value changed event is not triggered to avoid event snow balling.
    textChanged = Signal(str)  # text

    def __init__(self, text, read_only=False, wrap_lines=False):
        super().__init__()
        self._logger = logging.getLogger(__name__)
        view_frame_layout = QHBoxLayout()
        view_frame_layout.setContentsMargins(0, 5, 0, 5)
        self._txt_field = QPlainTextEdit(self)
        self._txt_field.setPlainText(str(text))
        self._txt_field.setReadOnly(read_only)
        self._txt_field.setLineWrapMode(QPlainTextEdit.NoWrap if not wrap_lines else QPlainTextEdit.LineWrapMode)
        self._txt_field.customContextMenuRequested.connect(self._show_context_menu)
        self._txt_field.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        view_frame_layout.addWidget(self._txt_field)
        self.setLayout(view_frame_layout)

    def setText(self, text: str):
        self._txt_field.blockSignals(True)
        self._txt_field.setPlainText(str(text))
        self._txt_field.blockSignals(False)

    def text(self) -> str:
        return self._txt_field.toPlainText()

    def _show_context_menu(self, point: QPoint = None):
        """ Displays a customized context menu for the plain view. """

        def _on_plain_text_context_menu_wrap_lines(e: QEvent):
            """ Un-/wraps lines when user clicks the wrap-lines action within the plain views context-menu. """
            if self._txt_field.lineWrapMode() == QPlainTextEdit.NoWrap:
                self._txt_field.setLineWrapMode(QPlainTextEdit.WidgetWidth)
            else:
                self._txt_field.setLineWrapMode(QPlainTextEdit.NoWrap)

        if not point:
            point = QCursor.pos()
        context_menu = self._txt_field.createStandardContextMenu()
        context_menu.addSeparator()
        wrap_lines_action = QAction(self)
        wrap_lines_action.setText("Wrap Lines")
        wrap_lines_action.setCheckable(True)
        wrap_lines_action.setChecked(self._txt_field.lineWrapMode() == QPlainTextEdit.WidgetWidth)
        wrap_lines_action.triggered.connect(_on_plain_text_context_menu_wrap_lines)
        context_menu.addAction(wrap_lines_action)
        context_menu.exec(self._txt_field.mapToGlobal(point))
