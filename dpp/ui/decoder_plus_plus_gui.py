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

from dpp.ui import MainWindow, MainWindowWidget, CodecTab


class DecoderPlusPlusWindow(MainWindow):
    """ The DecoderPlusPlus application. """

    def __init__(self, context: 'core.context.Context', input: str=None):
        """
        Initializes the DecoderPlusPlus application.
        :param context: the application context.
        :param input: the user input.
        """
        super().__init__(context, input)
        self._main_window_widget = MainWindowWidget(self, self._context, input)
        self.setCentralWidget(self._main_window_widget)
        self.show()

    def newTab(self, input: str):
        """ Opens a new tab with the specified input as content for the first codec frame. """
        self._main_window_widget.newTab(input)


class DecoderPlusPlusDialog(MainWindow):
    """
    The DecoderPlusPlusDialog with OK- and Cancel button.
    When the OK-button is triggered the transformed text is printed to stdout.
    When the Cancel-button is triggered or the user exist the application in any other way the initial input is
    printed to stdout.
    """

    def __init__(self, context: 'core.context.Context', input: str=None):
        """
        Initializes the DecoderPlusPlus dialog.
        :param context: the application context.
        :param input: the user input.
        """
        super().__init__(context, input)

        # Store the initial user input which is returned when the user cancels application.
        self._user_input = input

        # As long as the "OK"-button is not triggered we assume that the application was closed by the user.
        self._application_was_canceled = True

        # Build main window
        self._main_window_widget = QFrame()
        self._main_window_widget.setLayout(QVBoxLayout())
        self._codec_tab_widget = CodecTab(self, self._context, context.plugins())
        self._codec_tab_widget.frames().getFocusedFrame().setInputText(input)
        self._main_window_widget.layout().addWidget(self._codec_tab_widget)
        self._main_window_widget.layout().addWidget(self._init_button_box())
        self.setCentralWidget(self._main_window_widget)

        # Setup additional shortcuts to allow user to quickly hit the accept button.
        self._setup_shortcuts()

        # Do not show statusbar in dialog mode.
        self.statusBar().hide()

        # Show dialog.
        self.show()

    def _setup_shortcuts(self):
        """ Setup shortcuts to allow user to quickly hit the accept button. """
        ctrl_return_shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Return), self)
        ctrl_return_shortcut.activated.connect(self.onAccept)
        alt_return_shortcut = QShortcut(QKeySequence(Qt.ALT + Qt.Key_Return), self)
        alt_return_shortcut.activated.connect(self.onAccept)
        alt_o_shortcut = QShortcut(QKeySequence(Qt.ALT + Qt.Key_O), self)
        alt_o_shortcut.activated.connect(self.onAccept)

    def _init_button_box(self):
        """ Initialize the central dialog buttons.  """
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.onAccept)
        button_box.rejected.connect(self.onReject)
        button_box.setContentsMargins(0, 35, 0, 0)
        return button_box

    def onAccept(self):
        """ """
        self._application_was_canceled = False
        self.close()

    def onReject(self):
        self.close()

    def closeEvent(self, event):
        """ Handles the closeEvent which is triggered when the user exits the application. """
        if self._application_was_canceled:
            # Return the initial user input (here: no change) when user cancelled application.
            print(self._user_input, end='')
        else:
            # Return the transformed input when user triggered the OK-button.
            codec_frames = self._codec_tab_widget.getFrames()
            print(codec_frames[-1].getInputText(), end = '')
        super().closeEvent(event)
