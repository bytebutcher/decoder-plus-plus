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
from dpp.core.icons import Icon
from dpp.core.plugin import IdentifyPlugin, DecoderPlugin


class Plugin(IdentifyPlugin):
    """
    Detects the file type of the input text based on magic bytes.
    """

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies
        super().__init__('Identify Decoder', "Thomas Engel", [], context, icon=Icon.IDENTIFY_CODEC)

    def _can_plugin_decode_input(self, plugin, input_text: str) -> bool:
        """ Returns whether the plugin can identify the specified input. """
        try:
            # Check whether it is a decoder plugin and it thinks it can decode the input
            self._logger.debug(f'Trying to identify input using {plugin.name} ...')
            if not plugin.can_decode_input(input_text):
                self._logger.debug(f'Invalid input for {plugin.name}!')
                return False
            # Check whether decoder actually can process the input without any error
            plugin.run(input_text)
            return True
        except Exception as err:
            self._logger.debug(err)
            return False

    def _detect_decoders(self, input_text: str) -> list[str]:
        plugins = self._context.plugins()
        items = []
        for plugin in plugins:
            if isinstance(plugin, DecoderPlugin) and self._can_plugin_decode_input(plugin, input_text):
                items.append(plugin.name)
        return items

    def run(self, input_text: str) -> str:
        return "\n".join(self._detect_decoders(input_text))