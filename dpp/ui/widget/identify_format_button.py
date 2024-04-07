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
import logging
from typing import List

from qtpy.QtWidgets import QAction, QFrame, QHBoxLayout, QPushButton, QMenu

from dpp.core.exceptions import CodecException
from dpp.core.icons import Icon, icon
from dpp.core.plugin import DecoderPlugin, IdentifyPlugin, AbstractPlugin


class IdentifyFormatButton(QFrame):
    """ A button which provides a identify-format functionality. """

    def __init__(self, parent, plugins: List[AbstractPlugin], get_input_callback, select_plugin_callback):
        super(__class__, self).__init__(parent)
        self._logger = logging.getLogger(__name__)
        self._plugins = plugins
        self._get_input = get_input_callback
        self._select_plugin = select_plugin_callback
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

    def _populate_button_menu(self, input_text):
        """ Populates the button menu with a list of matching plugins for the specified input. """
        menu = self._button.menu()
        menu.clear()

        if input_text:
            for plugin in self._plugins:
                actions = self._identify_format(input_text, plugin)
                if actions:
                    # Add plugin name as title to menu
                    action = menu.addAction(plugin.name)
                    action.setDisabled(True)
                    # Add the formats the plugin was able to identify
                    menu.addActions(sorted(actions, key=lambda action: action.text()))

        if not menu.actions():
            action = menu.addAction("No matching format found ...")
            action.setEnabled(False)

    def _identify_format(self, input_text, plugin):
        actions = []
        if isinstance(plugin, IdentifyPlugin):
            self._logger.debug(f'Guessing input using {plugin.name} identify plugin ...')
            for identifier in plugin.run(input_text).splitlines():
                self._logger.debug(f'Adding possible {identifier} ...')
                if plugin.icon:
                    action = QAction(icon(plugin.icon), identifier, self)
                else:
                    action = QAction(identifier, self)
                actions.append(action)
        return actions
