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
import importlib.util
import os
from typing import List


class PluginType(object):

        DECODER = "Decoder"
        ENCODER = "Encoder"
        HASHER = "Hasher"
        SCRIPT = "Script"


class AbstractPlugin(object):
    """ Base-class to all plugins. Should not be used directly. Instead use one of its abstract implementations. """

    def __init__(self, name: str, type: str, author: str, dependencies: List[str], context: 'core.context.Context'):
        """
        Initializes a plugin.
        :param name: the name of the plugin.
        :param type: the type of the plugin (either DECODER, ENCODER, HASHER or SCRIPT).
        :param author: the author of the plugin.
        :param dependencies: the dependencies of the plugin (either None or a list of strings).
        :param context: the application context.
        """
        self._name = name
        self._type = type
        self._author = author
        self._dependencies = dependencies
        self._context = context
        self._aborted = False

    def setup(self, config: dict):
        """ Injects a given configuration into the plugin. """
        for name, value in config.items():
            setattr(self, name, value)

    def config(self) -> dict:
        """
        Returns the current configuration of the plugin.
        :returns empty dictionary since most plugins do not possess any special configuration.
        """
        return {}

    def isConfigurable(self) -> bool:
        """
        Returns whether the plugin can be configured.
        :return: True, when configurable, otherwise False.
        """
        return bool(self.config())

    def name(self) -> str:
        """ :returns the name of the plugin (e.g. "URL+"). """
        return self._name

    def full_name(self) -> str:
        """ :returns the full name of the plugin including name and type (e.g. "URL+" -> "URL+-Decoder"). """
        return "{}-{}".format(self.name(), self.type())

    def safe_name(self) -> str:
        """
        Name for usage in the Decoder++ command-line (lower-case, none-alphanumeric chars to underscores)

        NOTE:
            It is recommended to override this method to prevent naming-collisions and use better names.

            "URL+" -> "url_"        (not so good)
            "URL+" -> "url_plus"    (good)

        :returns the safe name of the plugin (e.g. "URL+" -> "url_").
        """
        safe_name = ""
        for char in self._name.lower():
            if char.isalnum():
                safe_name += char
            else:
                safe_name += "_"
        return safe_name

    def full_safe_name(self) -> str:
        """ :returns the full name of the plugin including name and type (e.g. "URL+" -> "url_-decoder"). """
        return "{}-{}".format(self.safe_name(), self.type()).lower()

    def type(self) -> str:
        """ :returns the type of the plugin (either DECODER, ENCODER, HASHER or SCRIPT). """
        return self._type

    def title(self) -> str:
        """ :returns the title of the plugin which is usually displayed to the user. """
        return "{} {}".format(self._name, self._type.capitalize())

    def author(self) -> str:
        """ :returns the author of the plugin. """
        return self._author

    def check_dependencies(self) -> List[str]:
        """
        Checks whether all specified dependencies can be loaded.
        :returns a list of unresolved dependencies, or an empty list if all dependencies could be resolved.
        """
        unresolved_dependencies = []
        if self._dependencies:
            for dependency in self._dependencies:
                if not self.check_dependency(dependency):
                    unresolved_dependencies.append(dependency)
        return unresolved_dependencies

    def check_dependency(self, dependency) -> bool:
        """
        Checks whether the given dependency is met.
        :returns True when given dependency is met, otherwise False.
        """
        try:
            if self._context.checkDependency(dependency):
                return True
            if importlib.util.find_spec(dependency) is not None:
                return True
            importlib.import_module(dependency)
            return True
        except Exception as e:
            return False

    def dependencies(self) -> List[str]:
        """ :returns all dependencies in a list. """
        return self._dependencies

    def run(self, *args, **kwargs) -> str:
        """ The main method of the plugin which must be implemented by the plugin. """
        raise NotImplementedError("Method must be implemented from upper class")

    def _run_lines(self, text: str, callback):
        """ Helper method which executes a callback for each line of text. """
        lines = []
        for text_line in text.splitlines():
            result = []
            for text_part in text_line.split(" "):
                if text_part:
                    result.append(callback(text_part))
            lines.append(' '.join(result))
        return os.linesep.join(lines)

    def select(self, *args, **kwargs) -> str:
        """
        This method is usually called when the plugin gets selected for execution.
        In its simplest form it may just call the run method. But it can also be used to ask the user for additional
        parameters (e.g. by displaying dialogs).
        """
        return self.run(*args)

    def _join_options_as_human_readable_string(self, options: List[str]):
        """
        Returns the list of options as human readable string.

        Examples:
            [] => ''
            ['a'] => 'a'
            ['a', 'b'] => 'a and b'
            ['a', 'b', 'c'] => 'a, b and c'

        :param options: a list of options.
        :returns the list of options as human readable string.
        """
        if not options:
            return ''
        elif len(options) == 1:
            return options[0]
        else:
            return ' and '.join([','.join(options[:-1]), options[-1]])

    def is_enabled(self) -> bool:
        """ :returns whether the plugin is enabled/disabled. """
        return self._context.config().getPluginStatus(self.full_safe_name())

    def is_runnable(self) -> bool:
        """ :returns whether the plugin can be run. Usually true, except for NullPlugin. """
        return True

    def set_enabled(self, status):
        """ Sets the status of the plugin to enabled/disabled. """
        self._context.config().setPluginStatus(self.full_safe_name(), status)

    def set_aborted(self, status):
        """ Sets whether the execution of the plugin was aborted by the user. """
        self._aborted = status

    def was_aborted(self) -> bool:
        """ :returns whether the execution of the plugin was aborted by the user. """
        return self._aborted

    def _set(self, name, config):
        """ Sets a fields value according to its configuration. """
        setattr(self, name, config[name])

    def __key(self):
        return (self._name, self._type)

    def __eq__(x, y):
        return x.__key() == y.__key()

    def __hash__(self):
        return hash(self.__key())

    def toDict(self):
        return {
            "name": self.name(),
            "type": self.type(),
            "config": self.config()
        }

class DecoderPlugin(AbstractPlugin):

    def __init__(self, name: str, author: str, dependencies: List[str], context: 'core.context.Context'):
        """
        Initializes a plugin.
        :param name: the name of the plugin.
        :param author: the author of the plugin.
        :param dependencies: the dependencies of the plugin (either None or a list of strings).
        :param context: the application context.
        """
        super(__class__, self).__init__(name, PluginType.DECODER, author, dependencies, context)

    def can_decode_input(self, input) -> bool:
        """
        Returns whether it might be possible to decode the specified input with this plugin.

        Override this method to implement custom "Smart decode" behaviour. See DecoderPlugin implementations for more
        information regarding this matter.

        :returns False by default.
        """
        return False

class EncoderPlugin(AbstractPlugin):

    def __init__(self, name: str, author: str, dependencies: List[str], context: 'core.context.Context'):
        """
        Initializes a plugin.
        :param name: the name of the plugin.
        :param author: the author of the plugin.
        :param dependencies: the dependencies of the plugin (either None or a list of strings).
        :param context: the application context.
        """
        super(__class__, self).__init__(name, PluginType.ENCODER, author, dependencies, context)


class HasherPlugin(AbstractPlugin):

    def __init__(self, name: str, author: str, dependencies: List[str], context: 'core.context.Context'):
        """
        Initializes a plugin.
        :param name: the name of the plugin.
        :param author: the author of the plugin.
        :param dependencies: the dependencies of the plugin (either None or a list of strings).
        :param context: the application context.
        """
        super(__class__, self).__init__(name, PluginType.HASHER, author, dependencies, context)


class ScriptPlugin(AbstractPlugin):

    def __init__(self, name: str, author: str, dependencies: List[str], context: 'core.context.Context'):
        """
        Initializes a plugin.
        :param name: the name of the plugin.
        :param author: the author of the plugin.
        :param dependencies: the dependencies of the plugin (either None or a list of strings).
        :param context: the application context.
        """
        super(__class__, self).__init__(name, PluginType.SCRIPT, author, dependencies, context)


class NullPlugin(AbstractPlugin):
    """ Implements a plugin which can be used as a Null-Object. """

    def __init__(self, context=None):
        super(NullPlugin, self).__init__("", "", "", [], context)

    def select(self, *args, **kwargs):
        pass

    def run(self, *args, **kwargs):
        pass

    def is_runnable(self) -> bool:
        return False