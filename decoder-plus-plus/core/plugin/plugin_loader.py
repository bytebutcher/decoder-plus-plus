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

from core.plugin.plugin import AbstractPlugin


class PluginLoader():
    """ Loads python files of type Plugin from a specified folder. """

    def __init__(self, context):
        self._context = context
        self._logger = context.logger()
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
            for f in os.listdir(path):
                if f.endswith(".py"):
                    plugin = self._load_plugin(path, f)
                    plugins[plugin.safe_name()] = plugin
        return [plugins[key] for key in sorted(plugins.keys())]

    def _load_plugin(self, path, f):
        self._logger.debug("Loading plugin at {}/{}".format(path, f))
        sys.path.insert(0, path)
        plugin = None
        try:
            fname, ext = os.path.splitext(f)
            mod = __import__(fname)
            plugin = mod.Plugin(self._context)
        except Exception as e:
            self._logger.error("{}: {}".format(f, str(e)))
            self._errors[f] = str(e)
            pass
        sys.path.pop(0)
        return plugin

    def _get_plugins(self):
        plugins = {}
        for path in self._plugins_path:
            for fname in self._plugins_path[path]:
                plugins[fname] = self._plugins_path[path][fname]
        return plugins
