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

import collections
from typing import List

from core.plugin.plugin import Plugin


class Plugins(object):
    """ Defines a list of plugins and additional helper methods for working with them. """

    def __init__(self, context: 'core.context.Context', plugin_list: List[Plugin]):
        self._context = context
        self._logger = context.logger()
        self._plugin_list = plugin_list
        self._index = 0

    def names(self, type: str=None, author: str=None) -> List[str]:
        """
        Returns the plugin names in a list. Does match cases.
        :param type: Filter plugin names by type (e.g. Plugin.Type.DECODER, ...)
        :param author: Filter plugin names by author (e.g. Thomas Engel, ...)
        """
        if type and author:
            return [plugin.name() for plugin in self._plugin_list if plugin.type() == type and plugin.author() == author]
        elif type:
            return [plugin.name() for plugin in self._plugin_list if plugin.type() == type]
        elif author:
            return [plugin.name() for plugin in self._plugin_list if plugin.author() == author]
        else:
            return [plugin.name() for plugin in self._plugin_list]

    def types(self) -> List[str]:
        """ Returns all possible plugin types in a list. """
        return [Plugin.Type.DECODER, Plugin.Type.ENCODER, Plugin.Type.HASHER, Plugin.Type.SCRIPT]

    def plugin(self, name: str, type: str) -> Plugin:
        """
        Returns the plugin matching name and type. Does not match cases. There can only be one.
        :param name: The name of the plugin (e.g. SHA1/sha1).
        :param type: The type of the plugin (e.g. DECODER/decoder).
        """
        the_type = type.lower()
        the_plugin_name = name.lower()
        for plugin in self._plugin_list:
            if plugin.type().lower() == the_type and plugin.name().lower() == the_plugin_name:
                return plugin
        raise Exception("Undefined plugin '{}::{}'!".format(name, type))

    def authors(self) -> List[str]:
        """ Returns all authors in a list. """
        authors = [plugin.author() for plugin in self._plugin_list if plugin.author()]
        return [author for author, _ in collections.Counter(authors).most_common()]

    def filter(self, name: str=None, type:str =None) -> List[Plugin]:
        """
        Returns the plugins matching name and/or type. Does not match cases.
        :param name: The name of the plugin (e.g. SHA1/sha1).
        :param type: The type of the plugin (e.g. DECODER/decoder).
        :raise Exception when neither name nor type is specified.
        """
        if name and type:
            try:
                return [self.plugin(name, type)]
            except:
                return []
        if name:
            the_plugin_name = name.lower()
            return [plugin for plugin in self._plugin_list if plugin.name().lower() == the_plugin_name]
        if type:
            the_type_name = type.lower()
            return [plugin for plugin in self._plugin_list if plugin.type().lower() == the_type_name]
        raise Exception("Unknown Error '{}::{}'!".format(name, type))

    def __len__(self):
        return len(self._plugin_list)