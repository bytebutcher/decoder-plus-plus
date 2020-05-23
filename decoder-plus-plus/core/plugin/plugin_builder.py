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
from core import Context
from core.plugin.plugin import NullPlugin
from core.plugin.plugins import AbstractPlugin

class PluginBuilder:
    """ Builds a plugin from a configuration item. """

    def __init__(self, context: Context):
        self._context = context

    def build(self, config) -> AbstractPlugin:
        """ Returns a plugin as specified within configuration item. Returns a NullPlugin on error. """
        try:
            plugin = self._context.getPluginByName(config["name"], config["type"])
            plugin.setup(config["config"])
            return plugin
        except Exception as e:
            self._context.logger().debug("Error building plugin:")
            self._context.logger().debug("> {}".format(config))
            self._context.logger().exception(e)
            return NullPlugin(self._context)
