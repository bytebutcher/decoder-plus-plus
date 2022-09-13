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
import sys
from typing import List

from dpp.core.plugin import AbstractPlugin


class PluginLoader:
    """ Loads python files of type Plugin from a specified folder. """

    def __init__(self, context: 'dpp.core.context.Context'):
        self._context = context
        self._unresolved_dependencies = {}
        self._errors = {}
        self._plugins_path = {}

    def load(self, paths: List['str']) -> List[AbstractPlugin]:
        """
        Loads plugins from the specified paths and returns them in an ordered list.
        :param path: the paths were plugin files (.py) are found.
        :return: ordered list of plugins.
        """
        plugins = {}
        for path in paths:
            try:
                if not os.path.exists(path):
                    self._context.logger.debug("Creating plugin folder '{}' ...".format(path))
                    os.makedirs(path)
                for f in os.listdir(path):
                    if f.endswith(".py"):
                        plugin = self._load_plugin(path, f)
                        if not plugin:
                            self._context.logger.error("Loading plugin {} at {} failed!".format(path, f))
                            continue
                        plugins[plugin.safe_name] = plugin
            except Exception as err:
                self._context.logger.warning(f'Loading plugin folder {path} failed!')
                self._context.logger.debug(err, exc_info=True)

        return [plugins[key] for key in sorted(plugins.keys())]

    def _load_plugin(self, path, f):
        self._context.logger.debug(f'Loading plugin at {path}/{f}')
        sys.path.insert(0, path)
        plugin = None
        try:
            fname, ext = os.path.splitext(f)
            mod = __import__(fname)
            plugin = mod.Plugin(self._context)
            plugin.check_properties()
        except Exception as err:
            self._context.logger.debug(err, exc_info=True)
            self._context.logger.error(f'{f}: {str(err)}')
            self._errors[f] = str(err)
        sys.path.pop(0)
        return plugin

    def _get_plugins(self):
        plugins = {}
        for path in self._plugins_path:
            for fname in self._plugins_path[path]:
                plugins[fname] = self._plugins_path[path][fname]
        return plugins
