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
import json
from typing import List

import dpp
from dpp.core.exceptions import ValidationError
from dpp.core.listener import Signal
from dpp.core import plugin
from dpp.core.logger import logmethod


class Label:

    def __init__(self, key, name):
        self.key = key
        self.name = name

    def __str__(self):
        return self.key


class Option:

    def __init__(self, label: str, value: str, description: str, is_required: bool = True):
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
        self.clazz = str(self.__class__.__name__)

    def _name(self):
        return self.label.name

    def _key(self):
        return self.label.key

    def __str__(self):
        return self._key()

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


class PluginConfig:
    """ A customizable list of configuration options for a plugin. """

    onChange = Signal(List[str])  # List of config keys.

    def __init__(self, context: 'dpp.core.context.Context'):
        super().__init__()
        self._context = context
        self._config = {}
        self._validators = {}

    def add(self, option: Option, validator=None):
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
        self.onChange.emit([option.key])

    def option(self, label: Label) -> Option:
        """ Returns the option with the specified name. """
        if isinstance(label, Label):
            return self._config[label.key]
        else:
            return self._config[label]

    def value(self, label: Label) -> str:
        """ Returns the value of the option with the specified name. """
        if isinstance(label, Label):
            return self._config[label.key].value
        else:
            return self._config[label].value

    def keys(self):
        """ Returns the individual configuration option names. """
        return self._config.keys()

    def items(self):
        """ Returns the individual configuration options in a list of tuples (key, option). """
        return self._config.items()

    def values(self) -> List[Option]:
        """ Returns the individual configuration options in a list. """
        return self._config.values()

    def count(self) -> int:
        """ Returns the number of configuration options. """
        return len(self._config.keys())

    @logmethod()
    def update(self, options):
        """
        Updates the value for each specified option.
        :param options: either a name-value-dictionary or an instance of PluginConfig.

        If options is a name-value dictionary the is_initialized attribute of the associated PluginConfigOption
        is set to True, to indicate that the option was manually configured.

        Example:
            update({"foo": "bar", "bar": "foo"})
            update(config.clone())
        """
        from dpp.core.plugin.config.options import Group
        if isinstance(options, PluginConfig):
            # Adding/Removing config entries should not be possible during runtime.
            assert options.keys() == self._config.keys(), 'Invalid plugin config! Expected identical keys!'
            updated_keys = []
            for key in options.keys():
                if options.value(key) != self.value(key):
                    # Only update when there is an actual change of value.
                    self._config[key] = options._config[key]
                    updated_keys.append(key)
            if updated_keys:
                # Only emit the updated keys.
                self.onChange.emit(updated_keys)
        else:
            # Supplied options provide a subset of the plugin config. It should not define new entries.
            invalid_keys = '", "'.join([key for key in options.keys() if key not in self._config.keys()])
            if invalid_keys:
                raise Exception(f'Invalid plugin config option(s) "{invalid_keys}"!')

            def uncheck_group(group_name):
                """ Unchecks every option within the specified group. """
                for option in self._config.items():
                    if isinstance(option, Group) and option.group_name == group_name:
                        option.value = False

            updated_keys = []
            for key in options.keys():
                if options[key] == self._config[key].value:
                    # Option did not change. Continue with next entry.
                    continue

                original_option = self._config[key]

                # When option is within a group, uncheck all.
                if isinstance(key, plugin.config.options.Group):
                    uncheck_group(original_option.group_name)

                original_option.value = options[key]
                updated_keys.append(key)

                # Mark option as initialized
                original_option.is_initialized = True

            if updated_keys:
                self.onChange.emit(updated_keys)

    def clone(self) -> 'dpp.core.plugin.config.PluginConfig':
        """ Returns a deep copy of the plugin configuration. """
        plugin_config = PluginConfig(self._context)
        plugin_config._config = copy.deepcopy(self._config)
        plugin_config._validators = self._validators
        return plugin_config

    def validate(self, option: Option, input_text: str) -> str:
        """ Returns None if validation succeeded, else error message. """
        if option.key in self._validators and self._validators[option.key] is not None:
            try:
                return self._validators[option.key](input_text)
            except ValidationError as err:
                return str(err)
            except Exception as err:
                self._context.logger.critical(f'Programming Error: Expected ValidationError, got {type(err)}!')
                return str(err)

    def __str__(self):
        return json.dumps(self._config, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def toDict(self):
        """ Returns the plugin configuration as dictionary. """
        return copy.deepcopy(self._config)

    def toJSON(self):
        """ Returns the json representation of the configuration. """
        return json.dumps(self._config, default=lambda o: o.__dict__, sort_keys=True, indent=4)
