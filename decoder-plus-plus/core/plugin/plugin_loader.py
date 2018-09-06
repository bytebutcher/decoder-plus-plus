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
from typing import Dict

from core.plugin.plugin import AbstractPlugin


class PluginLoader():
    """ Loads python files of type Plugin from a specified folder. """

    def __init__(self, context):
        self._context = context
        self._logger = context.logger()
        self._unresolved_dependencies = {}
        self._errors = {}
        self._plugins_path = {}

    def load(self, path: str) -> Dict[str, AbstractPlugin]:
        """
        Loads plugins from the specified path and returns them in a list.
        :param path: the path were plugin files (.py) are found.
        :return: a list of plugins.
        """
        if path in self._plugins_path:
            return self._plugins_path[path]
        self._plugins_path[path] = {}
        sys.path.insert(0, path)
        for f in os.listdir(path):
                fname, ext = os.path.splitext(f)
                if ext == '.py':
                    try:
                        mod = __import__(fname)
                        plugin = mod.Plugin(self._context)
                        unresolved_dependencies = plugin.check_dependencies()
                        if unresolved_dependencies:
                            self._unresolved_dependencies[plugin.name()] = unresolved_dependencies
                            self._logger.error("{}: Unresolved dependencies {}".format(
                                plugin.name(), ", ".join(unresolved_dependencies)))
                        self._plugins_path[path][fname] = plugin
                    except Exception as e:
                        self._logger.error("{}: {}".format(fname, str(e)))
                        self._errors[fname] = str(e)
                        pass
        sys.path.pop(0)
        return self._plugins_path[path]

    def _get_plugins(self):
        plugins = {}
        for path in self._plugins_path:
            for fname in self._plugins_path[path]:
                plugins[fname] = self._plugins_path[path][fname]
        return plugins

    def get_unresolved_dependencies(self, filter_enabled_plugins: bool=True) -> Dict[str, str]:
        """ Returns unresolved dependencies of all plugins.
        :param filter_enabled_plugins: when True, returns only unresolved dependencies of enabled plugins.
        """
        unresolved_dependencies = {}
        plugins = self._get_plugins()
        for plugin_name in plugins:
            plugin = plugins[plugin_name]
            plugin_unresolved_dependencies = plugin.check_dependencies()
            if (not filter_enabled_plugins or (filter_enabled_plugins and plugin.is_enabled())) \
                    and plugin_unresolved_dependencies:
                unresolved_dependencies[plugin.name()] = plugin_unresolved_dependencies
        return unresolved_dependencies

    def get_errors(self) -> Dict[str, str]:
        """ Returns all errors which occured during loading plugins."""
        return self._errors
