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

        class Label(object):

            def __init__(self, key, name):
                self.key = key
                self.name = name

            def __str__(self):
                return self.key

        class Base(object):

            def __init__(self, label, value, description, is_required=True):
                """
                :param label: the label of the option (e.g. OptionLabel("search", "Search:"), ...).
                :param value: the default value of the option  (e.g. "foo", 42, False, ...).
                :param description: the description of the option.
                :param is_required: defines whether the user needs to configure this option (default = True).
                """
                self.label = label
                self.value = value
                self.description = description
                self.is_required = is_required
                self.is_initialized = False

            def _name(self):
                return self.label.name

            def _key(self):
                return self.label.key

            def __str__(self):
                self._key()

            def __deepcopy__(self, memo):
                """ Makes a deep copy of the option while reusing callable's. """
                cls = self.__class__
                result = cls.__new__(cls)
                memo[id(self)] = result
                for k, v in self.__dict__.items():
                    setattr(result, k, v if callable(v) else copy.deepcopy(v, memo))
                return result

            name = property(fget=_name)
            key = property(fget=_key)

        class String(Base):

            def __init__(self, label, value, description, is_required):
                """
                :param value: the string (e.g. "ab cd ef gh ij kl mn op qr st uv wx yz").
                """
                super(PluginConfig.Option.String, self).__init__(label, value, description, is_required)

        class Integer(Base):

            def __init__(self, label, value, description, is_required, range=None):
                """
                :param value: the integer (e.g. ..., -2, -1, 0, 1, 2, ...).
                :param range: a list containing the minimum and maximum (e.g. [-2, 2])
                """
                super(PluginConfig.Option.Integer, self).__init__(label, value, description, is_required)
                self.range = range

        class Boolean(Base):

            def __init__(self, label, value, description, is_required):
                """
                :param value: the boolean value (e.g. True/False).
                """
                super(PluginConfig.Option.Boolean, self).__init__(label, value, description, is_required)

            def _is_checked(self):
                return bool(self.value)

            is_checked = property(_is_checked)

        class Group(Boolean):
            """ A option with group name and checked status. """

            def __init__(self, label, value, description, is_required, group_name):
                """
                :param group_name: defines whether the option is associated with another group of options.
                """
                super(PluginConfig.Option.Group, self).__init__(label, value, description, is_required)
                self.group_name = group_name

    def __init__(self):
        self._config = {}
        self._validators = {}

    def add(self, option: Option.Base, validator=None):
        """
        Adds an option to the plugin configuration.

        :param option: the option to store.
        :param validator: by default validator is None which indicates that no validation is performed.
                          otherwise a callback function is expected which should be able to take three arguments,
                          the config, the codec and the value. the callback is expected to return None when validation
                          succeeded or a string containing the error message when validation failed.
        """
        self._config[option.key] = option
        self._validators[option.key] = validator

    def get(self, label: Option.Label) -> Option:
        """ Returns the option with the specified name. """
        if isinstance(label, PluginConfig.Option.Label):
            return self._config[label.key]
        else:
            return self._config[label]

    def value(self, label: Option.Label) -> str:
        """ Returns the value of the option with the specified name. """
        if isinstance(label, PluginConfig.Option.Label):
            return self._config[label.key].value
        else:
            return self._config[label].value

    def keys(self):
        """ Returns the individual configuration option names. """
        return self._config.keys()

    def items(self):
        """ Returns the individual configuration options. """
        return self._config.items()

    def count(self) -> int:
        """ Returns the number of configuration options. """
        return len(self._config.keys())

    def update(self, options, ignore_invalid=False):
        """
        Updates the value for each specified option.
        :param options: either a name-value-dictionary or an instance of PluginConfig.
        :param ignore_invalid: when set to True an exception will be thrown when illegal options are
                                discovered (default = False).

        If options is a name-value dictionary the is_initialized attribute of the associated PluginConfigOption
        is set to True, to indicate that the option was manually configured.

        Example:
            update({"foo": "bar", "bar": "foo"})
            update(config.clone())
        """
        if isinstance(options, PluginConfig):
            self._config = options._config
        else:
            def uncheck_group(group_name):
                """ Unchecks every option within the specified group. """
                for option in self._config.items():
                    if type(option) == PluginConfig.Option.Group and option.group_name == group_name:
                        option.value = False

            for option_name in options.keys():
                if option_name not in self._config:
                    if not ignore_invalid:
                        raise KeyError("Unknown plugin configuration option '{}={}'!".format(
                            option_name, options[option_name]))
                    continue

                option = self._config[option_name]

                # When option is within a group, mark it as checked and uncheck all other options
                if type(option) == PluginConfig.Option.Group:
                    uncheck_group(option.group_name)

                option.value = options[option_name]

                # Mark option as initialized
                option.is_initialized = True

    def clone(self) -> 'PluginConfig':
        """ Returns a deep copy of the plugin configuration. """
        plugin_config = PluginConfig()
        plugin_config._config = copy.deepcopy(self._config)
        plugin_config._validators = self._validators
        return plugin_config

    def validate(self, option: Option.Base, codec, input) -> str:
        """ Returns True if validation succeeded, else error message. """
        if option.key in self._validators and self._validators[option.key] is not None:
            message = self._validators[option.key](self, codec, input)
            if message is not None:
                return message
        return True

    def __str__(self):
        return json.dumps(self._config, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def toDict(self):
        """ Returns the plugin configuration as dictionary. """
        return copy.deepcopy(self._config)

    def toJSON(self):
        """ Returns the json representation of the configuration. """
        return json.dumps(self._config, default=lambda o: o.__dict__, sort_keys=True, indent=4)


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
        self.config = PluginConfig()
        self._context = context
        self._aborted = False

    def setup(self, config: dict):
        """ Injects a given configuration into the plugin. """
        for name, value in config.items():
            self.config.add(value)

    def logger(self) -> Logger:
        """ Returns an logger instance which can be used within the plugin. """
        return self._context.logger()

    def is_configurable(self) -> bool:
        """
        Returns whether the plugin can be configured.
        :return: True, when configurable, otherwise False.
        """
        return self.config.count() > 0

    def is_unconfigured(self) -> List[str]:
        """
        :returns all required options which are currently not configured.
        """
        configured_groups = []
        for key in self.config.keys():
            option = self.config.get(key)
            if type(option) == PluginConfig.Option.Group and option.is_required and option.is_initialized:
                configured_groups.append(option.group_name)

        unconfigured_options = []
        for key in self.config.keys():
            option = self.config.get(key)
            if option.is_required and not option.is_initialized:
                if type(option) == PluginConfig.Option.Group and option.group_name not in configured_groups:
                    unconfigured_options.append(key)

        return unconfigured_options

    def name(self, safe_name=False) -> str:
        """
        :param safe_name: when False a human readable name is returned (e.g. "URL+"). Otherwise the name is parsed
        from the file name (e.g. url_plus) of the plugin. Defaults to False.
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
        self._context.logger().debug("Checking dependencies for {} {}".format(self.name(), self.type()))
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
        return self._context.config.getPluginStatus(self.full_name())

    def is_runnable(self) -> bool:
        """ :returns whether the plugin can be run. Usually true, except for NullPlugin. """
        return True

    def set_enabled(self, status):
        """ Sets the status of the plugin to enabled/disabled. """
        self._context.config.setPluginStatus(self.full_name(), status)

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

    def __deepcopy__(self, memo):
        """ Makes a deep copy of the option while reusing callable's. """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, v if callable(v) else copy.deepcopy(v, memo))
        return result

    def toDict(self):
        return {
            "name": self.name(),
            "type": self.type(),
            "config": self.config.toDict()
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


class PluginBuilder:
    """ Builds a plugin from a configuration item. """

    def __init__(self, context: 'core.context.Context'):
        self._context = context

    def build(self, config) -> AbstractPlugin:
        """ Returns a plugin as specified within configuration item. Returns a NullPlugin on error. """
        try:
            plugin = self._context.getPluginByName(config["name"], config["type"])
            plugin.setup(config["config"])
            return plugin
        except Exception as e:
            self._context.logger().debug("Error building plugin:")
            self._context.logger().debug("> {}".format(config))
            self._context.logger().exception(e)
            return NullPlugin(self._context)


class PluginLoader:
    """ Loads python files of type Plugin from a specified folder. """

    def __init__(self, context):
        self._context = context
        self._logger = context.logger()
        self._unresolved_dependencies = {}
        self._errors = {}
        self._plugins_path = {}

    def load(self, paths: List['str']) -> List[AbstractPlugin]:
        """
        Loads plugins from the specified paths and returns them in an ordered list.
        :param path: the paths were plugin files (.py) are found.
        :return: ordered list of plugins.
        """
        plugins = {}
        for path in paths:
            try:
                if not os.path.exists(path):
                    self._logger.debug("Creating plugin folder '{}' ...".format(path))
                    os.makedirs(path)
                for f in os.listdir(path):
                    if f.endswith(".py"):
                        plugin = self._load_plugin(path, f)
                        if not plugin:
                            self._logger.error("Loading plugin {} at {} failed!".format(path, f))
                            continue
                        plugins[plugin.name(safe_name=True)] = plugin
            except:
                self._logger.warning("Loading plugin folder '{}' failed!".format(path))

        return [plugins[key] for key in sorted(plugins.keys())]

    def _load_plugin(self, path, f):
        self._logger.debug("Loading plugin at {}/{}".format(path, f))
        sys.path.insert(0, path)
        plugin = None
        try:
            fname, ext = os.path.splitext(f)
            mod = __import__(fname)
            plugin = mod.Plugin(self._context)
        except Exception as e:
            self._logger.error("{}: {}".format(f, str(e)))
            self._errors[f] = str(e)
            pass
        sys.path.pop(0)
        return plugin

    def _get_plugins(self):
        plugins = {}
        for path in self._plugins_path:
            for fname in self._plugins_path[path]:
                plugins[fname] = self._plugins_path[path][fname]
        return plugins


class Plugins:
    """ Defines a list of plugins and additional helper methods for working with them. """

    def __init__(self, plugin_paths: List['str'], context: 'core.context.Context'):
        self._context = context
        self._logger = context.logger()
        self._plugin_loader = PluginLoader(context)
        self._plugin_list = self._plugin_loader.load(plugin_paths)
        self._index = 0

    def names(self, type: str=None, author: str=None, safe_names=False) -> List[str]:
        """
        Returns the plugin names in a list. Does match cases.
        :param type: Filter plugin names by type (e.g. PluginType.DECODER, ...)
        :param author: Filter plugin names by author (e.g. Thomas Engel, ...)
        :param safe_names: when False human readable names are returned (e.g. "URL+"). Otherwise names are parsed
        from the file name (e.g. url_plus_encoder) of the individual plugin. Defaults to False.
        """
        if type and author:
            return [plugin.name(safe_names) for plugin in self._plugin_list if plugin.type() == type and plugin.author() == author]
        elif type:
            return [plugin.name(safe_names) for plugin in self._plugin_list if plugin.type() == type]
        elif author:
            return [plugin.name(safe_names) for plugin in self._plugin_list if plugin.author() == author]
        else:
            return [plugin.name(safe_names) for plugin in self._plugin_list]

    def types(self) -> List[str]:
        """ Returns all possible plugin types in a list. """
        return [PluginType.DECODER, PluginType.ENCODER, PluginType.HASHER, PluginType.SCRIPT]

    def plugins(self) -> List[AbstractPlugin]:
        return self._plugin_list

    def plugin(self, name: str, type: str) -> AbstractPlugin:
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

    def filter(self, name: str=None, type: str=None) -> List[AbstractPlugin]:
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

    def __getitem__(self, item):
        """ Returns the specified plugin. """
        return self._plugin_list[item]

    def __len__(self):
        """ Returns the number of plugins. """
        return len(self._plugin_list)

