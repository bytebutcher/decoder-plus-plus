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

from core.command.command import Command


class Commands(object):

    def __init__(self, context, command_list):
        self._context = context
        self._logger = context.logger()
        self._command_list = command_list
        self._index = 0

    def add(self, command):
        self._command_list.append(command)

    def names(self, type=None, author=None):
        if type and author:
            return [command.name() for command in self._command_list if command.type() == type and command.author() == author]
        elif type:
            return [command.name() for command in self._command_list if command.type() == type]
        elif author:
            return [command.name() for command in self._command_list if command.author() == author]
        else:
            return [command.name() for command in self._command_list]

    def types(self):
        return [Command.Type.DECODER, Command.Type.ENCODER, Command.Type.HASHER, Command.Type.SCRIPT]

    def command(self, name, type):
        the_type = type.lower()
        the_command_name = name.lower()
        for command in self._command_list:
            if command.type().lower() == the_type and command.name().lower() == the_command_name:
                return command
        raise Exception("Undefined command '{}::{}'!".format(name, type))

    def authors(self):
        authors = [command.author() for command in self._command_list if command.author()]
        return [author for author, _ in collections.Counter(authors).most_common()]

    def filter(self, name=None, type=None):
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