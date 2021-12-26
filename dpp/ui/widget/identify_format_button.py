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
import qtawesome
from typing import List

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QPushButton, QMenu, QAction

from dpp.core.plugin import DecoderPlugin, IdentifyPlugin, AbstractPlugin


class IdentifyFormatButton(QFrame):
    """ A button which provides a identify-format functionality. """

    def __init__(self, parent, plugins: List[AbstractPlugin], get_input_callback, select_plugin_callback, logger):
        super(__class__, self).__init__(parent)
        self._plugins = plugins
        self._get_input = get_input_callback
        self._select_plugin = select_plugin_callback
        self._logger = logger
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 6, 0, 0)
        self._button = self._init_button()
        layout.addWidget(self._button)
        self.setLayout(layout)

    def _init_button(self):
        button = QPushButton("Identify format")
        menu = QMenu(self)
        menu.aboutToShow.connect(lambda: self._populate_button_menu(self._get_input()))
        button.setMenu(menu)
        return button

    def _can_plugin_identify_input(self, plugin: AbstractPlugin, input: str) -> bool:
        """ Returns whether the plugin can identify the specified input. """
        try:
            # Check whether it is a decoder plugin and it thinks it can decode the input
            if isinstance(plugin, DecoderPlugin) and not plugin.can_decode_input(input):
                return False
            # Check whether decoder/identifier actually can process the input without any error
            plugin.select(input)
            return True
        except:
            return False

    def _get_matching_plugins(self, input) -> List[AbstractPlugin]:
        """ Returns a list of matching plugins for the specified input. """
        if not input:
            return []

        return [plugin for plugin in self._plugins if self._can_plugin_identify_input(plugin, input)]

    def _populate_button_menu(self, input):
        """ Populates the button menu with a list of matching plugins for the specified input. """
        menu = self._button.menu()
        menu.clear()
        plugins = self._get_matching_plugins(input)
        if not plugins:
            action = menu.addAction("No matching format found ...")
            action.setEnabled(False)
            return

        actions = []
        for plugin in plugins:
            if isinstance(plugin, DecoderPlugin):
                action = QAction(qtawesome.icon("ei.indent-left"), plugin.name(), self)
                action.triggered.connect(lambda chk, item=plugin: self._select_plugin(item))
                actions.append(action)
            elif isinstance(plugin, IdentifyPlugin):
                for identifier in plugin.run(input).splitlines():
                    action = QAction(qtawesome.icon("ei.align-justify"), identifier, self)
                    actions.append(action)

        menu.addActions(sorted(actions, key=lambda action: action.text()))
