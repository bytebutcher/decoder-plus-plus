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

from typing import List

from qtpy import QtCore
from qtpy.QtCore import QRegularExpression
from qtpy.QtGui import QStandardItemModel, QStandardItem, QColor, QRegularExpressionValidator, QFont, QFontMetrics
from qtpy.QtWidgets import QTableView, QLineEdit, QStyledItemDelegate, QWidget

from dpp.core import Context
from dpp.core.icons import Icon, icon
from dpp.ui.widget.dock_widget import DockWidget


class HexDock(DockWidget):
    """ A widget to show a hex view of a string representation. """

    def __init__(self, context: Context, parent: QWidget):
        super(HexDock, self).__init__("Hex", icon(Icon.DOCK_HEX), parent)
        self.addWidget(HexView(context, self))


class HexValidatorDelegate(QStyledItemDelegate):
    def createEditor(self, widget, option, index):
        if not index.isValid():
            return 0
        editor = QLineEdit(widget)
        validator = QRegularExpressionValidator(QRegularExpression("[0-9a-fA-F]?[0-9a-fA-F]"))
        editor.setValidator(validator)
        return editor


class HexView(QTableView):

    def __init__(self, context: 'core.context.Context', parent):
        super(__class__, self).__init__(parent)
        self._context = context

        self._tab_id = 0
        self._frame_id = 0
        self._input_text = ""

        chunks = self._chunk_string(self._input_text, 16)

        self._init_item_font()
        self._init_model(chunks)
        self._init_headers(chunks)
        self._init_column_size()
        self._init_listener()

        self.setItemDelegate(HexValidatorDelegate())

    #############################################
    #   Init
    #############################################

    def _init_listener(self):
        """ Initialize change events. """
        self._context.listener().textChanged.connect(self._on_text_change)
        self._context.listener().textSelectionChanged.connect(self._on_selection_change)
        self._context.listener().selectedFrameChanged.connect(self._on_selected_frame_change)

    def _init_item_font(self):
        self._item_font = QFont()
        self._item_font.setFamily('Courier')
        self._item_font.setFixedPitch(True)
        self._item_font.setPointSize(8)

    def _init_column_size(self):
        # BUG: Columns should only have minimal padding.
        # FIX: Columns are resized to content.
        # NOTE:
        #   This is still not optimal but I couldn't figure out how to make columns even smaller.
        #
        #   Here's a list of things I've tried:
        #       * removing QLineEdit from HexValidatorDelegate
        #       * setting font size
        #       * setting section resize and using a bunch of stylesheets
        #       self.setStyleSheet("""
        #           QTableView::item { border: 0px; padding: 0px; margin: 0px; }
        #           QTableWidget::item { border: 0px; padding: 0px; margin: 0px; }
        #           QTableView { border: 0px; padding: 0px; margin: 0px; }
        #       """)
        #       self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        #
        for i in range(0, 16):
            self.resizeColumnToContents(i)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setDefaultAlignment(QtCore.Qt.AlignCenter)
        self.verticalHeader().setFixedWidth(self._init_vertical_header_width())
        self.verticalHeader().setFont(self._item_font)

    def _init_vertical_header_width(self):
        vertical_header_font = QFont()
        vertical_header_font.setFamily('Courier')
        vertical_header_font.setFixedPitch(True)
        vertical_header_font.setPointSize(8)
        vertical_header_width = QFontMetrics(vertical_header_font).width("00000") + 22
        return vertical_header_width

    def _init_headers(self, chunks):
        self._init_vertical_header(chunks, self.model())
        self.horizontalHeader().hide()

    def _init_model(self, chunks):
        model = QStandardItemModel(len(chunks), 1 + 16)
        self._populate_items(chunks, model)
        model.itemChanged.connect(self._on_hex_value_change)
        self.setModel(model)

    def _init_vertical_header(self, chunks, model):
        if len(chunks) > 0:
            model.setVerticalHeaderLabels(["0x{0:04x}".format(i) for i in range(len(chunks))])
        else:
            model.setVerticalHeaderLabels(["0x{0:04x}".format(0)])

    #############################################
    #   Private Interface
    #############################################

    def _populate_items(self, chunks, model):
        model.blockSignals(True)
        if not chunks:
            self._populate_row(0, "", model)
        else:
            for row_index, chunk in enumerate(chunks):
                self._populate_row(row_index, chunk, model)
        model.blockSignals(False)

    def _populate_row(self, row_index, chunk, model):
        hex_chars = self._set_cells(chunk, model, row_index)
        self._lock_empty_cells(hex_chars, model, row_index)
        self._set_text_cell(chunk, model, row_index)

    def _set_text_cell(self, chunk, model, row_index):
        text_item = QStandardItem(chunk)
        text_item.setFont(self._item_font)
        text_item.setFlags(text_item.flags() ^ QtCore.Qt.ItemIsEditable)
        model.setItem(row_index, 16, text_item)

    def _set_cells(self, chunk, model, row_index):
        hex_chars = self._get_hex_view(chunk)
        for col_index, hex_char in enumerate(hex_chars):
            hex_item = QStandardItem(hex_char)
            hex_item.setBackground(QColor("#90FF90"))
            hex_item.setFont(self._item_font)
            hex_item.setTextAlignment(QtCore.Qt.AlignCenter)
            model.setItem(row_index, col_index, hex_item)
        return hex_chars

    def _lock_empty_cells(self, hex_chars, model, row_index):
        for col_index in range(len(hex_chars), 16):
            hex_item = QStandardItem("")
            hex_item.setText("")
            hex_item.setFont(self._item_font)
            hex_item.setFlags(hex_item.flags() ^ QtCore.Qt.ItemIsEditable)
            model.setItem(row_index, col_index, hex_item)

    def _refresh_model(self):
        chunks = self._chunk_string(self._input_text, 16)
        model = self.model()
        model.clear()
        self._populate_items(chunks, model)
        self._init_headers(chunks)
        self._init_column_size()

    def _get_hex_text(self, model):
        hex_string = ""
        for row_index in range(0, model.rowCount()):
            for col_index in range(0, 16):
                item = model.data(model.index(row_index, col_index))
                if item:
                    hex_string += item
        return hex_string

    def _set_hex_text(self, item, model):
        hex_text = ""
        for col_index in range(0, 16):
            hex_char = model.data(model.index(item.row(), col_index))
            if hex_char:
                hex_text += hex_char
        model.blockSignals(True)
        model_item = model.item(item.row(), 16)
        model_item.setText(bytes.fromhex(hex_text).decode('utf-8', errors='surrogateescape'))
        model.blockSignals(False)

    def _prefix_hex_value(self, item, model):
        hex_char = model.data(model.index(item.row(), item.column()))
        if len(hex_char) == 1:
            model.blockSignals(True)
            model.item(item.row(), item.column()).setText("0" + hex_char)
            model.blockSignals(False)

    def _chunk_string(self, string: str, length: int) -> List[str]:
        """ Breaks the string into a list of chunks with a specified max length. """
        return [string[0 + i:length + i] for i in range(0, len(string), length)]

    def _get_hex_view(self, string: str) -> List[str]:
        def get_hex_char(str_char):
            """ Returns the hex representation of an utf-character while ignoring surrogate special characters. """
            return "{0:02x}".format(ord(str_char))[:2]

        return [get_hex_char(string[i]) for i in range(0, len(string))]

    def _update_view(self, tab_id: str, frame_id: str, input_text: str):
        if self._frame_id == frame_id and self._input_text != input_text:
            self._tab_id = tab_id
            self._frame_id = frame_id
            self._input_text = input_text
            self.setData(input_text)

    #############################################
    #   Events
    #############################################

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            self.edit(self.selectionModel().currentIndex())
        super(__class__, self).keyPressEvent(event)

    def _on_hex_value_change(self, item):
        model = self.model()
        self._prefix_hex_value(item, model)
        self._set_hex_text(item, model)
        hex_string = self._get_hex_text(model)
        self.blockSignals(True)
        self._context.listener().textSubmitted.emit(self._tab_id, self._frame_id,
                                                    bytearray.fromhex(hex_string).decode('utf-8',
                                                                                         errors='surrogateescape'))
        self.blockSignals(False)

    def _on_selection_change(self, tab_id: str, frame_id: str, input_text: str):
        self._update_view(tab_id, frame_id, input_text)

    def _on_text_change(self, tab_id: str, frame_id: str, input_text: str):
        self._update_view(tab_id, frame_id, input_text)

    def _on_selected_frame_change(self, tab_id: str, frame_id: str, input_text: str):
        self._frame_id = frame_id
        self._update_view(tab_id, frame_id, input_text)

    #############################################
    #   Public Interface
    #############################################

    def setData(self, input_text: str):
        self._input_text = input_text
        self._refresh_model()
