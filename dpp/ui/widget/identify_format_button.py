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

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QPushButton

from dpp.core.plugin import IdentifyPlugin, AbstractPlugin


class IdentifyFormatButton(QFrame):
    """ A button which provides a identify-format functionality. """

    clicked = pyqtSignal()

    def __init__(self, parent, plugins: List[IdentifyPlugin]):
        super(__class__, self).__init__(parent)
        self._plugins = plugins
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 6, 0, 0)
        self._button = self._init_button()
        layout.addWidget(self._button)
        self.setLayout(layout)

    def _init_button(self):
        button = QPushButton("Identify format")
        button.clicked.connect(self._button_click_event)
        return button

    def _button_click_event(self):
        """ Forwards the "Identify format" button click event. """
        self.clicked.emit()


    def _test_plugins(self, input, plugins) -> List[AbstractPlugin]:
        """ Returns a list of plugins which did not threw an error when executing them with the specified input. """
        plugins_without_error = []
        for plugin in plugins:
            try:
                plugin.select(input)
                plugins_without_error.append(plugin)
            except:
                pass
        return plugins_without_error

    def get_possible_identifiers(self, input) -> List[str]:
        """ Returns a list of possible identifiers for the specified input. """
        return self._test_plugins(input, self._plugins)
