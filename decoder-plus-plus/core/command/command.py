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


"""
Represents a codec (e.g. Decoder, Encoder, Hasher or Script).
"""
from typing import Callable


class Command(object):

    class Type(object):

        DECODER = "Decoder"
        ENCODER = "Encoder"
        HASHER = "Hasher"
        SCRIPT = "Script"

    def __init__(self, name: str, type: str, author: str,
                 title_method: Callable, run_method: Callable, select_method: Callable):
        self._name = name
        self._type = type
        self._author = author
        self._title_method = title_method
        self._run_method = run_method
        self._select_method = select_method

    def name(self) -> str:
        """ Returns the static name of the command (e.g. 'Search and Replace'). """
        return self._name

    def type(self) -> str:
        """ Returns the type of the command (e.g. DECODER, ENCODER, HASHER, SCRIPT). """
        return self._type

    def title(self) -> str:
        """
        Returns the (dynamic) command title. This may be the same string as returned by the name-method.
        But it may also include hints of the current configuration of the command (e.g. 'Replace "A" with "B"' instead
        of 'Search and Replace').
        """
        return self._title_method()

    def author(self) -> str:
        """
        Returns the author of the command. This is usually set by plugins. Custom commands return an empty author.
        """
        return self._author

    def select(self, *args, **kwargs) -> str:
        """
        Executes the select method. In it's simplest form the select-method is only executing the run-method.
        However, there may be cases where a configuration of the newly selected command is required.
        :param args: A list of arguments. Usually a input-text which should be transformed.
        :return: The transformed input.
        """
        return self._select_method(*args)

    def run(self, *args, **kwargs) -> str:
        """
        Executes the commands main-function and returns a transformed input-text.
        :param args: A list of arguments. Usually a input-text which should be transformed.
        :return: The transformed input.
        """
        return self._run_method(*args)

    def __key(self):
        return (self._name, self._type)

    def __eq__(x, y):
        return x.__key() == y.__key()

    def __hash__(self):
        return hash(self.__key())


class NullCommand(Command):
    """ Implements a command which may be used as a Null-Object. """

    def __init__(self):
        super(NullCommand, self).__init__("", "", "", lambda: "", self.run, self.select)

    def select(self, *args, **kwargs):
        pass

    def run(self, *args, **kwargs):
        pass
