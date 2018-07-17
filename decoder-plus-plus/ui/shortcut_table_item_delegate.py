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

from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QStyledItemDelegate, QLineEdit


class ShortcutTableItemDelegate(QStyledItemDelegate):

    def __init__(self, parent):
        super(__class__, self).__init__(parent)
        self._parent = parent

    class LineEdit(QLineEdit):

        def __init__(self, parent, widget):
            QLineEdit.__init__(self, parent)
            self._widget = widget
            self._text = None

        def keyPressEvent(self, event):
            try:
                key_sequence = QKeySequence(event.modifiers() | event.key())
                key_sequence_ascii_representation = key_sequence.toString().encode('ascii', errors='ignore').decode()
                self.setText(key_sequence_ascii_representation)
            except Exception as e:
                # Ignoring unknown errors since we can't do anything about it.
                pass

        def keyReleaseEvent(self, *args, **kwargs):
            # BUG: Using Enter-Key to go into Edit-Mode results in an immediate closing of the selected cell.
            # WORKAROUND: The ItemDelegate is responsible for this behaviour. To fix this issue a custom editing-started
            #             variable is used to inform the ItemDelegate when the Enter-Key was being pressed.
            if self._widget.hasEditingStarted():
                self._widget.setEditingEnded()
                return
            # Only allow complete key-sequences (e.g. 'A', 'Ctrl+A').
            if len(self.text()) == 0 or self.text().endswith("+"):
                # Remove incomplete key-sequences (e.g. 'Ctrl+') when releasing keys.
                self.setText("")
                return
            self.close()

    def createEditor(self, parent, option, proxyModelIndex):
        return ShortcutTableItemDelegate.LineEdit(parent, self._parent)
