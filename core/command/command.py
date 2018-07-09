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
class Command(object):

    class Type(object):

        DECODER = "Decoder"
        ENCODER = "Encoder"
        HASHER = "Hasher"
        SCRIPT = "Script"

    def __init__(self, name, type, author, title_method, run_method, select_method):
        self._name = name
        self._type = type
        self._author = author
        self._title_method = title_method
        self._run_method = run_method
        self._select_method = select_method

    def _get_safe_name(self):
        keepcharacters = ('_')
        name = self._name.lower().replace(" ", "_").replace("+", "plus")
        return "".join(c for c in name if c.isalnum() or c in keepcharacters).rstrip()

    """
    Returns the static name of the command (e.g. 'Search and Replace'). When safe_name is set to True this method
    eliminates special characters (e.g. +, <space>, etc.).
    """
    def name(self, safe_name=False):
        if safe_name:
            return self._get_safe_name()
        return self._name

    """
    Returns the type of the command (e.g. DECODER, ENCODER, HASHER, SCRIPT).
    """
    def type(self):
        return self._type

    """
    Returns the (dynamic) command title. This may be the same string as returned by the name-method.
    But it may also include hints of the current configuration of the command (e.g. 'Replace "A" with "B"' instead
    of 'Search and Replace').
    """
    def title(self):
        return self._title_method()

    """
    Returns the author of the command. This is usually set by plugins. Custom commands return an empty author.
    """
    def author(self):
        return self._author

    """
    Executes the commands main-function and returns a transformed input-text.
    """
    def run(self, *args, **kwargs):
        return self._run_method(*args)

    """
    Executes the select method. In it's simplest form the select-method is only executing the run-method. 
    However, there may be cases where a configuration of the newly selected command is required.
    """
    def select(self, *args, **kwargs):
        return self._select_method(*args)

    class Builder(object):

        def __init__(self):
            self._name = None
            self._type = None
            self._author = None
            self._run_source = None
            self._run_method = None
            self._select_method = None
            self._title_method = None

        def name(self, name):
            self._name = name
            return self

        def type(self, type):
            self._type = type
            return self

        def author(self, author):
            self._author = author
            return self

        def title(self, title_method):
            self._title_method = title_method
            return self

        def run_source(self, run_source):
            self._run_source = run_source
            return self

        def run(self, run_method):
            self._run_method = run_method
            return self

        def select(self, select_method):
            self._select_method = select_method
            return self

        def build(self):
            assert self._name is not None and len(self._name) > 0, "Name is required and should not be None or Empty."
            assert self._type is not None, "Type is required and should not be None."
            assert self._run_method is not None or self._run_source is not None, "Run method or run source is required and should not be None."
            assert not (self._run_method is None and self._run_source is None), "Run method or run source is required. Not both."
            def _select_method(*args, **kwargs):
                self._run_method(*args)
            if self._run_source is not None:
                def _run_method(input):
                    exec(self._run_source, globals(), locals())
                    return eval("run")(input)
                self._run_method = _run_method
            if self._select_method is None:
                self._select_method = _select_method
            if self._title_method is None:
                self._title_method = lambda: "{} {}".format(self._name, self._type.capitalize())
            return Command(self._name, self._type, self._author, self._title_method, self._run_method, self._select_method)


""" Implements a command which may be used as a Null-Object. """
class NullCommand(Command):

    def __init__(self):
        super(NullCommand, self).__init__("", "", "", lambda: "", self.run, self.select)

    def select(self, *args, **kwargs):
        pass

    def run(self, *args, **kwargs):
        pass
