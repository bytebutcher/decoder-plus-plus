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

from qtpy.QtCore import Qt
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QMainWindow, QFrame, QDialogButtonBox, QShortcut, QVBoxLayout

from dpp.core import Context
from dpp.core.logger import logmethod
from dpp.core.shortcuts import KeySequence
from dpp.ui.dock.hex_dock import HexDock
from dpp.ui.dock.log_dock import LogDock
from dpp.ui.view.classic.classic_main_window_widget import ClassicMainWindowWidget
from dpp.ui.view.classic import CodecTab
from dpp.ui.view.modern.modern_main_window_widget import ModernMainWindowWidget
from dpp.ui.widget.dock_tabs_widget import DockTabsWidget


class DecoderPlusPlusGui(QMainWindow):

    def __init__(self, context: 'core.context.Context'):
        super().__init__()
        self._context = context
        self._init_window_size()
        self.setWindowTitle("Decoder++")
        self.setWindowIcon(QIcon(os.path.join(self._context.getAppPath(), 'images', 'dpp_128.png')))

    def _init_window_size(self):
        """ Initializes the window size. Looks and uses any previously saved sizing. """
        if self._context.config.getSize():
            self.resize(self._context.config.getSize())
        self.setMinimumWidth(520)
        self.setMinimumHeight(300)


class DecoderPlusPlusWindow(DecoderPlusPlusGui):
    """ The DecoderPlusPlus application. """

    def __init__(self, context: 'core.context.Context', input_text: str = None):
        """
        Initializes the DecoderPlusPlus application.
        :param context: the application context.
        :param input_text: the user input.
        """
        super().__init__(context)
        self.setCentralWidget(ClassicMainWindowWidget(self, self._context, input_text))
        self.show()

    def newTab(self, input_text: str) -> (int, CodecTab):
        """
        Opens a new tab with the specified input as content for the first codec frame.
        This function is used when user runs Decoder++ when it is already running and the --new-instance switch
        was not used.
        """
        self._context.logger.info("Opening input in new tab...")
        return self.centralWidget().newTab(input_text=input_text)


class DecoderPlusPlusDialog(DecoderPlusPlusGui):
    """
    The DecoderPlusPlusDialog with OK- and Cancel button.
    When the OK-button is triggered the transformed text is printed to stdout.
    When the Cancel-button is triggered or the user exist the application in any other way the initial input is
    printed to stdout.
    """

    def __init__(self, context: 'core.context.Context', input_text: str = None):
        """
        Initializes the DecoderPlusPlus dialog.
        :param context: the application context.
        :param input_text: the user input.
        """
        # Store the initial user input which is returned when the user cancels application.
        self._user_input = input_text

        # As long as the "OK"-button is not triggered we assume that the application was closed by the user.
        self._application_was_canceled = True

        super().__init__(context)

        # Build main window and codec tab
        self.setCentralWidget(QFrame())
        self.centralWidget().setLayout(QVBoxLayout())
        self._codec_tab_widget = CodecTab(self, self._context, context.plugins())
        self._codec_tab_widget.frames().getFocusedFrame().setInputText(input_text)
        self.centralWidget().layout().addWidget(self._codec_tab_widget)
        self.centralWidget().layout().addWidget(self._init_button_box())

        # Initialize docks
        self._log_dock_widget = LogDock(self.docksWidget(), context.logger)
        self.docksWidget().registerDockWidget(Context.DockWidget.LOG_DOCK_WIDGET, self._log_dock_widget)
        self.docksWidget().registerDockWidget(Context.DockWidget.HEX_DOCK_WIDGET, HexDock(context, self))

        # Setup additional shortcuts to allow user to quickly hit the accept button.
        self._setup_shortcuts()

        # Do not show statusbar in dialog mode.
        self.statusBar().hide()

        # Show dialog.
        self.show()

    @logmethod()
    def _setup_shortcuts(self):
        """ Setup shortcuts to allow user to quickly hit the accept button. """
        ctrl_return_shortcut = QShortcut(KeySequence(Qt.CTRL, Qt.Key_Return), self)
        ctrl_return_shortcut.activated.connect(self.onAccept)
        alt_return_shortcut = QShortcut(KeySequence(Qt.ALT, Qt.Key_Return), self)
        alt_return_shortcut.activated.connect(self.onAccept)
        alt_o_shortcut = QShortcut(KeySequence(Qt.ALT, Qt.Key_O), self)
        alt_o_shortcut.activated.connect(self.onAccept)

    @logmethod()
    def _init_button_box(self):
        """ Initialize the central dialog buttons.  """
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.onAccept)
        button_box.rejected.connect(self.onReject)
        button_box.setContentsMargins(0, 35, 0, 0)
        return button_box

    def docksWidget(self) -> DockTabsWidget:
        if not hasattr(self, '_docks_widget'):
            self._docks_widget = DockTabsWidget(self, self._context)
        return self._docks_widget

    @logmethod()
    def onAccept(self):
        # Return the transformed input when user triggered the OK-button.
        codec_frames = self._codec_tab_widget.frames().getFrames()
        print(codec_frames[-1].getInputText(), end='')
        self._application_was_canceled = False
        self.close()

    @logmethod()
    def onReject(self):
        # Return the initial user input (here: no change) when user cancelled application.
        print(self._user_input, end='')
        self.close()
