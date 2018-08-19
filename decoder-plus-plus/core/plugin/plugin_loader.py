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

    def load(self, path: str) -> List[AbstractPlugin]:
        """
        Loads plugins from the specified path and returns them in a list.
        :param path: the path were plugin files (.py) are found.
        :return: a list of plugins.
        """
        self._plugins = {}
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
                            continue
                        self._plugins[fname] = plugin
                    except Exception as e:
                        self._logger.error("{}: {}".format(fname, str(e)))
                        self._logger.debug("Unknown error: {}", e)
                        pass
        sys.path.pop(0)
        return self._plugins

    def getUnresolvedDependencies(self):
        return self._unresolved_dependencies

