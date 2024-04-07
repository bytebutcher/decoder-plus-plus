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
import copy

import dpp
from dpp.core import plugin
from dpp.core.plugin import AbstractPlugin, NullPlugin


class PluginBuilder:
    """ Builds a plugin from a configuration item. """

    def __init__(self, context: 'dpp.core.context.Context'):
        self._context = context

    def _build_config(self, config):
        result = {}
        for name, value in config.items():
            if isinstance(value, plugin.config.Option):
                result[name] = copy.deepcopy(value)
                continue
            try:
                clazz = value.pop("clazz")
                value["label"] = plugin.config.Label(value["label"]["key"], value["label"]["name"])
                value.pop("is_initialized")
                mod = __import__('dpp.core.plugin.config.options', fromlist=[clazz])
                result[name] = getattr(mod, clazz)(**value)
            except:
                raise Exception("Error while loading plugin configuration!")

        return result

    def build(self, config, safe_mode: bool = False) -> AbstractPlugin:
        """ Returns a plugin as specified within configuration item. Returns a NullPlugin on error. """
        try:
            plugin = self._context.getPluginByName(config["name"], config["type"])
            plugin.setup(self._build_config(config['config']), safe_mode)
            return plugin
        except Exception as err:
            self._context.logger.debug("Error building plugin:")
            self._context.logger.debug("> {}".format(config))
            self._context.logger.debug(err, exc_info=True)
            return NullPlugin(self._context)
