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
import os

from qtpy.QtCore import QSize, Qt
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QDialog, QLabel, QVBoxLayout

from dpp.core.shortcuts import KeySequence
from dpp.ui.widget.icon_label import IconLabel


class KeyboardShortcutDialog(QDialog):
    """ A dialog to let users change a keyboard shortcut. """

    __INFO_MESSAGE_DEFAULT_TEXT = "Press Esc to cancel or Backspace to reset the shortcut."
    __INFO_MESSAGE_HINT_STYLE = "QLabel { color: gray }"
    __INFO_MESSAGE_ERROR_STYLE = "QLabel { color: red }"

    def __init__(self, parent, context: 'core.context.Context', keyboard_shortcut_name):
        """
        Initializes the shortcut dialog.
        :param parent: the widget which is calling the dialog.
        :param context: the context of the application
        :param keyboard_shortcut_name: the name of the keyboard shortcut to be changed (e.g. "New Tab").
        """
        super().__init__(parent)
        self._context = context
        self._keyboard_shortcut_name = keyboard_shortcut_name
        self._should_be_reset = False

        layout = QVBoxLayout()
        lbl_title = QLabel("Enter the new keyboard shortcut to change <b>{}</b>".format(keyboard_shortcut_name))
        layout.addWidget(lbl_title)
        layout.setAlignment(lbl_title, Qt.AlignHCenter)

        keyboard_image_path = os.path.join(self._context.getAppPath(), 'images', 'keyboard.png')
        lbl_keyboard_image = IconLabel(self, QIcon(keyboard_image_path))
        lbl_keyboard_image.setFixedSize(QSize(128, 128))
        layout.addWidget(lbl_keyboard_image)
        layout.setAlignment(lbl_keyboard_image, Qt.AlignHCenter)

        self._lbl_keyboard_shortcut = QLabel()
        layout.addWidget(self._lbl_keyboard_shortcut)
        layout.setAlignment(self._lbl_keyboard_shortcut, Qt.AlignHCenter)

        self._lbl_hint = QLabel(self.__INFO_MESSAGE_DEFAULT_TEXT)
        self._lbl_hint.setStyleSheet(self.__INFO_MESSAGE_HINT_STYLE)
        layout.setAlignment(Qt.AlignCenter)
        layout.setAlignment(self._lbl_hint, Qt.AlignHCenter)
        layout.addWidget(self._lbl_hint)

        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)
        self.setMinimumWidth(150)
        self.setWindowTitle("Set Keyboard Shortcut")

    def _show_error_message(self, text):
        self._lbl_hint.setStyleSheet(self.__INFO_MESSAGE_ERROR_STYLE)
        self._lbl_hint.setText(text)

    def _show_info_message(self, text=""):
        if not text:
            text = self.__INFO_MESSAGE_DEFAULT_TEXT
        self._lbl_hint.setStyleSheet(self.__INFO_MESSAGE_HINT_STYLE)
        self._lbl_hint.setText(text)

    def setKeyboardShortcut(self, shortcut: str):
        self._lbl_keyboard_shortcut.setText(shortcut)

    def keyboardShortcut(self) -> str:
        return self._lbl_keyboard_shortcut.text()

    def shouldBeReset(self):
        return self._should_be_reset

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.setKeyboardShortcut("")
            self.close()
            return

        if event.key() == Qt.Key_Backspace:
            self.setKeyboardShortcut("")
            self._should_be_reset = True
            self.close()
            return

        try:
            key_sequence = KeySequence(event.modifiers(), event.key())
            key_sequence_ascii_representation = key_sequence.toString().encode('ascii',
                                                                               errors='ignore').decode()
            self.setKeyboardShortcut(key_sequence_ascii_representation)
        except Exception as e:
            # Ignoring unknown errors since we can't do anything about it.
            pass

    def keyReleaseEvent(self, event):
        # Only allow complete key-sequences (e.g. 'A', 'Ctrl+A').
        if len(self.keyboardShortcut()) == 0 or self.keyboardShortcut().endswith("+"):
            # Remove incomplete key-sequences (e.g. 'Ctrl+') when releasing keys.
            self.setKeyboardShortcut("")
            self._show_info_message()
            return

        # Check for duplicates
        for keyboard_shortcut in self._context.getShortcuts():
            if keyboard_shortcut.key() == self.keyboardShortcut() and \
                    keyboard_shortcut.name() != self._keyboard_shortcut_name:
                self._show_error_message("<b>{}</b> is already being used for <b>{}</b>.".format(
                    keyboard_shortcut.key(), keyboard_shortcut.name(remove_anchors=True)))
                return

        self.close()
