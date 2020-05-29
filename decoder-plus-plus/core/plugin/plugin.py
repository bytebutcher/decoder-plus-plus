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
import copy
import importlib
import importlib.util
import json
import os
import sys
from logging import Logger
from typing import List


class PluginType(object):
    DECODER = "Decoder"
    ENCODER = "Encoder"
    HASHER = "Hasher"
    SCRIPT = "Script"


class PluginConfig(object):
    """ A customizable list of configuration options for a plugin. """

    class Option(object):

        def __init__(self, name, value, description, is_config_required=True):
            """
            :param name: the name of the option (e.g. "search", "replace", "is_case_insensitive", ...).
            :param value: the default value of the option  (e.g. "foo", 42, False, ...).
            :param description: the description of the option.
            :param is_config_required: defines whether the user needs to configure this option (default = True).
            """
            self.name = name
            self.value = value
            self.description = description
            self.is_config_required = is_config_required

    class OptionGroup(Option):
        """ A option with group name and checked status. """

        def __init__(self, name, value, description, is_config_required, group_name, is_checked):
            """
            :param name: the name of the option (e.g. "search", "replace", "is_case_insensitive", ...).
            :param value: the default value of the option  (e.g. "foo", 42, False, ...).
            :param description: the description of the option.
            :param is_config_required: defines whether the user needs to configure this option (default = True).
            :param group_name: defines whether the option is associated with another group of options (default = None).
            :param is_checked: defines whether the option is checked. Within a option group there should only be one
            checked option.
            """
            super(PluginConfig.OptionGroup, self).__init__(name, value, description, is_config_required)
            self.group_name = group_name
            self.is_checked = is_checked

    def __init__(self, context: "core.context.Context"):
        self._context = context
        self._config = {}

    def add(self, option: Option):
        """
        Adds an option to the plugin configuration.
        """
        self._config[option.name] = option

    def get(self, name) -> Option:
        """ Returns the option with the specified name. """
        return self._config[name]

    def value(self, name) -> str:
        """ Returns the value of the option with the specified name. """
        return self._config[name].value

    def keys(self):
        """ Returns the individual configuration options. """
        return self._config.keys()

    def count(self) -> int:
        """ Returns the number of configuration options. """
        return len(self._config.keys())

    def update(self, options):
        """
        Updates the value for each specified option.
        :param options: either a name-value-dictionary or an instance of PluginConfig.

        If options is a name-value dictionary the is_config_required attribute of the associated PluginConfigOption
        is set to False, to indicate that the option is configured now.

        Example:
            update({"foo": "bar", "bar": "foo"})
            update(config.clone())
        """
        if isinstance(options, PluginConfig):
            self._config = options._config
        else:
            for option_name in options.keys():
                self._config[option_name].value = options[option_name]
                self._config[option_name].is_config_required = False

    def clone(self) -> 'PluginConfig':
        """ Returns a deep copy of the plugin configuration. """
        plugin_config = PluginConfig(self._context)
        plugin_config._config = copy.deepcopy(self._config)
        return plugin_config

    def __str__(self):
        return json.dumps(self._config, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def toDict(self):
        """ Returns the plugin configuration as dictionary. """
        return copy.deepcopy(self._config)


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
        self._safe_name, _ = os.path.splitext(os.path.basename(sys.modules[self.__class__.__module__].__file__))
        self._method_name = self._safe_name[:self._safe_name.rfind("_")]
        self._type = type
        self._author = author
        self._dependencies = dependencies
        self._config = PluginConfig(context)
        self._context = context
        self._logger = context.logger()
        self._aborted = False

    def setup(self, config: dict):
        """ Injects a given configuration into the plugin. """
        for name, value in config.items():
            setattr(self, name, value)

    def logger(self) -> Logger:
        """ Returns an logger instance which can be used within the plugin. """
        return self._context.logger()

    def config(self) -> PluginConfig:
        """ Returns the current configuration of the plugin if any, else None. """
        return self._config

    def is_configurable(self) -> bool:
        """
        Returns whether the plugin can be configured.
        :return: True, when configurable, otherwise False.
        """
        return self._config.count() > 0

    def is_configured(self) -> List[str]:
        """
        Returns whether all required options are configured.
        :return: List of required options are, empty if everything is configured correctly False.
        """
        return [key for key in self._config.keys() if self._config.get(key).is_config_required]

    def name(self, safe_name=False) -> str:
        """
        :param safe_name: when False a human readable name is returned (e.g. "URL+"). Otherwise the name is parsed
        from the file name (e.g. url_plus_encoder) of the plugin. Defaults to False.
        :returns the name of the plugin.
        """
        if not safe_name:
            return self._name
        else:
            return self._safe_name

    def full_name(self) -> str:
        """ :returns the full name of the plugin including name and type (e.g. "URL+" -> "URL+-Decoder"). """
        return "{}-{}".format(self.name(), self.type())

    def method_name(self) -> str:
        """ :returns the safe name of the plugin without type-information (e.g. url_plus). """
        return self._method_name

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
        self._logger.debug("Checking dependencies for {} {}".format(self.name(), self.type()))
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

    def run(self, text: str) -> str:
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

    def select(self, text: str) -> str:
        """
        This method is usually called when the plugin gets selected for execution.
        In its simplest form it may just call the run method. But it can also be used to ask the user for additional
        parameters (e.g. by displaying dialogs).
        """
        return self.run(text)

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
        return self._context.config().getPluginStatus(self.full_name())

    def is_runnable(self) -> bool:
        """ :returns whether the plugin can be run. Usually true, except for NullPlugin. """
        return True

    def set_enabled(self, status):
        """ Sets the status of the plugin to enabled/disabled. """
        self._context.config().setPluginStatus(self.full_name(), status)

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
            "config": self.config().toDict()
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

    def select(self, text: str):
        pass

    def run(self, text: str):
        pass

    def is_runnable(self) -> bool:
        return False
