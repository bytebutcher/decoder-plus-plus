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

import importlib
import os

from core.command.command import Command


class AbstractPlugin(object):

    def __init__(self, name, type, author, dependencies=None):
        assert(name is not None and len(name) > 0), "Name is required and should not be None or Empty"
        assert(type in [Command.Type.DECODER, Command.Type.ENCODER, Command.Type.HASHER, Command.Type.SCRIPT]), \
            "Type is required and should be either 'DECODER', 'ENCODER', 'HASHER' or 'SCRIPT'"
        assert(author is not None and len(author) > 0), "Author is required and should not be None or Empty"
        self._name = name
        self._type = type
        self._author = author
        self._dependencies = dependencies

    def name(self):
        return self._name

    def type(self):
        return self._type

    def title(self):
        return "{} {}".format(self._name, self._type.capitalize())

    def author(self):
        return self._author

    def check_dependencies(self):
        unresolved_dependencies = []
        if self._dependencies:
            for dependency in self._dependencies:
                try:
                    importlib.import_module(dependency)
                except Exception as e:
                    unresolved_dependencies.append(dependency)
        return unresolved_dependencies

    def run(self, *args, **kwargs):
        raise NotImplementedError("Method must be implemented from upper class")

    def _run_lines(self, text, callback):
        lines = []
        for text_line in text.splitlines():
            result = []
            for text_part in text_line.split(" "):
                if text_part:
                    result.append(callback(text_part))
            lines.append(' '.join(result))
        return os.linesep.join(lines)

    def select(self, *args, **kwargs):
        return self.run(*args)