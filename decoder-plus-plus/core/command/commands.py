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

from core.command import Command


class Commands(object):
    """ Defines a list of commands and additional helper methods for working with them. """

    def __init__(self, context: 'core.context.Context', command_list: List[Command]):
        self._context = context
        self._logger = context.logger()
        self._command_list = command_list
        self._index = 0

    def names(self, type: str=None, author: str=None) -> List[str]:
        """
        Returns the command names in a list. Does match cases.
        :param type: Filter command names by type (e.g. Command.Type.DECODER, ...)
        :param author: Filter command names by author (e.g. Thomas Engel, ...)
        """
        if type and author:
            return [command.name() for command in self._command_list if command.type() == type and command.author() == author]
        elif type:
            return [command.name() for command in self._command_list if command.type() == type]
        elif author:
            return [command.name() for command in self._command_list if command.author() == author]
        else:
            return [command.name() for command in self._command_list]

    def types(self) -> List[str]:
        """ Returns all possible command types in a list. """
        return [Command.Type.DECODER, Command.Type.ENCODER, Command.Type.HASHER, Command.Type.SCRIPT]

    def command(self, name: str, type: str) -> Command:
        """
        Returns the command matching name and type. Does not match cases. There can only be one.
        :param name: The name of the command (e.g. SHA1/sha1).
        :param type: The type of the command (e.g. DECODER/decoder).
        """
        the_type = type.lower()
        the_command_name = name.lower()
        for command in self._command_list:
            if command.type().lower() == the_type and command.name().lower() == the_command_name:
                return command
        raise Exception("Undefined command '{}::{}'!".format(name, type))

    def authors(self) -> List[str]:
        """ Returns all authors in a list. """
        authors = [command.author() for command in self._command_list if command.author()]
        return [author for author, _ in collections.Counter(authors).most_common()]

    def filter(self, name: str=None, type:str =None) -> List[Command]:
        """
        Returns the commands matching name and/or type. Does not match cases.
        :param name: The name of the command (e.g. SHA1/sha1).
        :param type: The type of the command (e.g. DECODER/decoder).
        :raise Exception when neither name nor type is specified.
        """
        if name and type:
            try:
                return [self.command(name, type)]
            except:
                return []
        if name:
            the_command_name = name.lower()
            return [command for command in self._command_list if command.name().lower() == the_command_name]
        if type:
            the_type_name = type.lower()
            return [command for command in self._command_list if command.type().lower() == the_type_name]
        raise Exception("Unknown Error '{}::{}'!".format(name, type))

    def __len__(self):
        return len(self._command_list)