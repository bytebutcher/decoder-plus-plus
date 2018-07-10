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

    class LineEdit(QLineEdit):

        def __init__(self, parent=None):
            QLineEdit.__init__(self, parent)
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
            # Only allow complete key-sequences (e.g. 'A', 'Ctrl+A').
            if len(self.text()) == 0 or self.text().endswith("+"):
                # Remove incomplete key-sequences (e.g. 'Ctrl+') when releasing keys.
                self.setText("")
                return
            self.close()

    def createEditor(self, parent, option, proxyModelIndex):
        return ShortcutTableItemDelegate.LineEdit(parent)
