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
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QVBoxLayout, QFrame, QShortcut, QDialogButtonBox

from ui import MainWindow, MainWindowWidget, CodecTab


class DecoderPlusPlusDialog(MainWindow):

    def __init__(self, context: 'core.context.Context', input: str=None):
        super().__init__(context, input)
        self._user_input = input
        self._application_was_canceled = True
        layout = QVBoxLayout()
        self._codec_tab_widget = CodecTab(self, self._context, context.plugins())
        self._codec_tab_widget.getFocusedFrame().setInputText(input)
        layout.addWidget(self._codec_tab_widget)
        layout.addWidget(self._init_button_box())
        self._main_window_widget = QFrame()
        self._main_window_widget.setLayout(layout)
        self.setCentralWidget(self._main_window_widget)
        self._setup_shortcuts()
        self.show()

    def _setup_shortcuts(self):
        ctrl_return_shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Return), self)
        ctrl_return_shortcut.activated.connect(self._accept)
        alt_return_shortcut = QShortcut(QKeySequence(Qt.ALT + Qt.Key_Return), self)
        alt_return_shortcut.activated.connect(self._accept)
        alt_o_shortcut = QShortcut(QKeySequence(Qt.ALT + Qt.Key_O), self)
        alt_o_shortcut.activated.connect(self._accept)

    def _init_button_box(self):
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._accept)
        button_box.rejected.connect(self._reject)
        return button_box

    def _accept(self):
        self._application_was_canceled = False
        self.close()

    def _reject(self):
        self.close()

    def closeEvent(self, event):
        if self._application_was_canceled:
            print(self._user_input, end='')
        else:
            codec_frames = self._codec_tab_widget.getFrames()
            print(codec_frames[-1].getInputText(), end = '')
        event.accept()

class DecoderPlusPlusWindow(MainWindow):

    def __init__(self, context: 'core.context.Context', input: str=None):
        super().__init__(context, input)
        self._main_window_widget = MainWindowWidget(self, self._context, input)
        self.setCentralWidget(self._main_window_widget)
        self.show()

    def newTab(self, input: str):
        """ Opens a new tab. """
        self._main_window_widget.newTab(input)