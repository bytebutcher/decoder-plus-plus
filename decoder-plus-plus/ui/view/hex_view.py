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

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QRegExp
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor, QRegExpValidator, QFont, QFontMetrics
from PyQt5.QtWidgets import QTableView, QLineEdit, QStyledItemDelegate


class HexValidatorDelegate(QStyledItemDelegate):
    def createEditor(self, widget, option, index):
        if not index.isValid():
            return 0
        editor = QLineEdit(widget)
        validator = QRegExpValidator(QRegExp("[0-9a-fA-F]?[0-9a-fA-F]"))
        editor.setValidator(validator)
        return editor

class QHexEdit(QTableView):

    textChanged = pyqtSignal('PyQt_PyObject')

    def __init__(self, parent, context, frame_id, input_text):
        super(QHexEdit, self).__init__(parent)
        self._context = context
        self._frame_id = frame_id
        self._logger = context.logger()
        self._init_item_font()
        self._input_text = input_text
        chunks = self._chunk_string(self._input_text, 16)
        self._init_model(chunks)
        self._init_headers(chunks)
        self._init_column_size()
        self.setItemDelegate(HexValidatorDelegate())

    def _init_item_font(self):
        self._item_font = QFont()
        self._item_font.setFamily('Courier')
        self._item_font.setFixedPitch(True)
        self._item_font.setPointSize(8)

    def _init_column_size(self):
        for i in range(0, 16):
            self.resizeColumnToContents(i)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setDefaultAlignment(QtCore.Qt.AlignCenter)
        self.verticalHeader().setFixedWidth(self._vertical_header_width())
        self.verticalHeader().setFont(self._item_font)

    def _vertical_header_width(self):
        # BUG: Synchronizing hex-views and code-views vertical header's width does not work (FixedWidth vs MarginWidth).
        # WORKAROUND: HexView requires additional 16 units.
        # NOTE: To set CodeEditor vertical header we use setMarginWidth which is just not the same as setFixedWidth().
        vertical_header_font = QFont()
        vertical_header_font.setFamily('Courier')
        vertical_header_font.setFixedPitch(True)
        vertical_header_font.setPointSize(10)
        vertical_header_width = QFontMetrics(vertical_header_font).width("00000") + 16 + 6
        return vertical_header_width

    def _init_headers(self, chunks):
        self._init_vertical_header(chunks, self.model())
        self.horizontalHeader().hide()

    def _init_model(self, chunks):
        model = QStandardItemModel(len(chunks), 1 + 16)
        self._populate_items(chunks, model)
        model.itemChanged.connect(self._hex_value_changed_event)
        self.setModel(model)

    def _populate_items(self, chunks, model):
        model.blockSignals(True)
        if not chunks:
            self._populate_row(0, "", model)
        else:
            for row_index, chunk in enumerate(chunks):
                self._populate_row(row_index, chunk, model)
        model.blockSignals(False)

    def _init_vertical_header(self, chunks, model):
        if len(chunks) > 0:
            model.setVerticalHeaderLabels(["0x{0:04x}".format(i) for i in range(len(chunks))])
        else:
            model.setVerticalHeaderLabels(["0x{0:04x}".format(0)])

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

    def _hex_value_changed_event(self, item):
        model = self.model()
        self._prefix_hex_value(item, model)
        self._set_hex_text(item, model)
        hex_string = self._get_hex_text(model)
        self.textChanged.emit(bytearray.fromhex(hex_string).decode(encoding="Latin1"))

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
        model_item.setText(str(self._get_text_view(hex_text)))
        model.blockSignals(False)

    def _prefix_hex_value(self, item, model):
        hex_char = model.data(model.index(item.row(), item.column()))
        if len(hex_char) == 1:
            model.blockSignals(True)
            model.item(item.row(), item.column()).setText("0" + hex_char)
            model.blockSignals(False)

    """
    Breaks the string into a list of chunks with a specified max length. 
    """
    def _chunk_string(self, string, length):
        return [string[0 + i:length + i] for i in range(0, len(string), length)]

    def _get_hex_view(self, string):
        hex_view = ["{0:02x}".format(ord(string[i])) for i in range(0, len(string))]
        return hex_view

    def _get_text_view(self, hex):
        text = ""
        hex_chunks = self._chunk_string(hex, 2)
        for hex_chunk in hex_chunks:
            if int(hex_chunk, 16) <= 32 or int(hex_chunk, 16) >= 127:
                text += "."
            else:
                text += bytearray.fromhex(hex_chunk).decode(encoding="Latin1")
        return text

    def setData(self, input_text):
        self._input_text = input_text
        self._refresh_model()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            self.edit(self.selectionModel().currentIndex())
        super(QHexEdit, self).keyPressEvent(event)