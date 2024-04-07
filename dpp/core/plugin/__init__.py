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
import logging
import os
import sys
from typing import List

from dpp.core.assertions import assert_type
from dpp.core.listener import Signal
from dpp.core.plugin import config
from dpp.core.plugin.config import ui, PluginConfig
from dpp.core.plugin.config import options
from dpp.core.plugin.config.ui import Layout, Widget
from dpp.core.plugin.config.ui.layouts import FormLayout, VBoxLayout
from dpp.core.plugin.config.ui.widgets import Option, GroupBox, TextPreview


class PluginType(object):
    DECODER = "Decoder"
    ENCODER = "Encoder"
    HASHER = "Hasher"
    SCRIPT = "Script"
    IDENTIFY = "Identify"


class AbstractPlugin:
    """ Base-class to all plugins. Should not be used directly. Instead, use one of its abstract implementations. """

    # Signals used to communicate error or success to the plugin configuration dialog.
    onError = Signal('PyQt_PyObject')
    onSuccess = Signal('PyQt_PyObject')

    def __init__(self, name: str, type: str, author: str, dependencies: List[str],
                 context: 'dpp.core.context.Context', icon: tuple = None):
        """ Initializes a plugin.
        :param name: the name of the plugin.
        :param type: the type of the plugin (either DECODER, ENCODER, HASHER, SCRIPT, IDENTIFY).
        :param author: the author of the plugin.
        :param dependencies: the dependencies of the plugin (either None or a list of strings).
        :param context: the application context.
        :param icon: an optional tuple e.g. ('file', 'images/dpp.png') representing an icon.
        """
        self._name = name
        self._safe_name = None
        self._type = type
        self._author = author
        self._dependencies = dependencies
        self._config = PluginConfig(context)
        self._context = context
        self._icon = icon
        self._logger = logging.getLogger(__name__)

    def setup(self, config: dict, safe_mode: bool = False):
        """ Injects a given configuration into the plugin. """
        for name, value in config.items():
            self.config.add(value)

    def is_configurable(self) -> bool:
        """ :return: True, when plugin is configurable, otherwise False. """
        return self.config.count() > 0

    def is_unconfigured(self) -> List[str]:
        """ :returns all required options which are currently not configured. """
        configured_groups = []
        for key in self.config.keys():
            option = self.config.option(key)
            if isinstance(option, config.options.Group) and option.is_required and option.is_initialized:
                configured_groups.append(option.group_name)

        unconfigured_options = []
        for key in self.config.keys():
            option = self.config.option(key)
            if option.is_required and not option.is_initialized:
                if isinstance(option, config.options.Group):
                    if option.group_name in configured_groups:
                        continue
                unconfigured_options.append(key)
        return unconfigured_options

    @property
    def name(self) -> str:
        """ :returns the name of the plugin (e.g. "url_plus"). """
        return self._name

    @property
    def safe_name(self) -> str:
        """ :returns a human-readable name is returned (e.g. "URL+"). """
        if not self._safe_name:
            self._safe_name, _ = os.path.splitext(os.path.basename(sys.modules[self.__class__.__module__].__file__))
        return self._safe_name

    @property
    def full_name(self) -> str:
        """ :returns the full name of the plugin including name and type (e.g. "URL+" -> "URL+-Decoder"). """
        return f'{self._name}-{self._type}'

    @property
    def method_name(self) -> str:
        """ :returns the safe name of the plugin without type-information (e.g. url_plus). """
        return self.safe_name[:self.safe_name.rfind("_")]

    @property
    def type(self) -> str:
        """ :returns the type of the plugin (either DECODER, ENCODER, HASHER, SCRIPT, IDENTIFY). """
        return self._type

    @property
    def title(self) -> str:
        """ :returns the title of the plugin which is usually displayed to the user. """
        return f'{self._name} {self._type.capitalize()}'

    @property
    def author(self) -> str:
        """ :returns the author of the plugin. """
        return self._author

    @property
    def config(self) -> PluginConfig:
        return self._config

    @property
    def icon(self) -> tuple:
        return self._icon

    def check_properties(self):
        """ Makes sure that the defined properties still return the expected types.
        If this check fails the property has probably been overwritten by a subclass.
        """
        assert_type(self.name, str)
        assert_type(self.safe_name, str)
        assert_type(self.full_name, str)
        assert_type(self.method_name, str)
        assert_type(self.type, str)
        assert_type(self.title, str)
        assert_type(self.author, str)
        assert_type(self.config, PluginConfig)
        assert_type(self.icon, tuple, allow_none=True)

    def check_dependencies(self) -> List[str]:
        """ Checks whether all specified dependencies can be loaded.
        :returns a list of unresolved dependencies, or an empty list if all dependencies could be resolved.
        """
        self._logger.trace(f'Checking dependencies for {self.name} {self.type}')
        unresolved_dependencies = []
        if self._dependencies:
            for dependency in self._dependencies:
                if not self.check_dependency(dependency):
                    unresolved_dependencies.append(dependency)
        return unresolved_dependencies

    def check_dependency(self, dependency) -> bool:
        """ Checks whether the given dependency is met.
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

    def validate_options(self, input_text, option_keys=None):
        if option_keys:
            for option_key in option_keys:
                self.config.validate(self.config.option(option_key), input_text)

    def run(self, text: str) -> str:
        """ The main method of the plugin which must be implemented by the plugin. """
        raise NotImplementedError('Method must be implemented by the upper class')

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

    def _create_options_group_box(self, input_text) -> Widget:
        return GroupBox(label='Options', layout=self._create_options_layout(input_text))

    def _create_options_layout(self, input_text) -> Layout:
        return FormLayout(widgets=[Option(option) for option in self._config.values()])

    def _create_preview_group_box(self, input_text) -> Widget:
        return GroupBox(label='Preview', layout=self._create_preview_layout(input_text))

    def _create_preview_layout(self, input_text) -> Layout:
        return VBoxLayout(widgets=[TextPreview(self, input_text)])

    def layout(self, input_text: str) -> Layout:
        """ Returns a layout containing all configuration entries. """
        return VBoxLayout(
            widgets=[
                self._create_options_group_box(input_text),
                self._create_preview_group_box(input_text)
            ]
        )

    def _join_options_as_human_readable_string(self, options: List[str]):
        """ Returns the list of options as human-readable string.

        Examples:
            [] => ''
            ['a'] => 'a'
            ['a', 'b'] => 'a and b'
            ['a', 'b', 'c'] => 'a, b and c'

        :param options: a list of options.
        :returns the list of options as human-readable string.
        """
        if not options:
            return ''
        elif len(options) == 1:
            return options[0]
        else:
            return ' and '.join([','.join(options[:-1]), options[-1]])

    def is_enabled(self) -> bool:
        """ :returns whether the plugin is enabled/disabled. """
        return self._context.config.getPluginStatus(self.full_name)

    def is_runnable(self) -> bool:
        """ :returns whether the plugin can be run. Usually true, except for NullPlugin. """
        return True

    def set_enabled(self, status):
        """ Sets the status of the plugin to enabled/disabled. """
        self._context.config.setPluginStatus(self.full_name, status)

    def _set(self, name, config):
        """ Sets a fields value according to its configuration. """
        setattr(self, name, config[name])

    def __key(self):
        return (self._name, self._type)

    def __eq__(x, y):
        return x.__key() == y.__key()

    def __hash__(self):
        return hash(self.__key())

    def clone(self, config: PluginConfig = None) -> 'AbstractPlugin':
        plugin = self.__class__(context=self._context)
        if config:
            plugin._config = config
        else:
            plugin._config = self._config.clone()
        return plugin

    def toDict(self):
        return {
            "name": self.name,
            "type": self.type,
            "config": self.config.toDict(),
        }


class DecoderPlugin(AbstractPlugin):

    def __init__(self, name: str, author: str, dependencies: List[str], context: 'dpp.core.context.Context', icon=None):
        """ Initializes a plugin.
        :param name: the name of the plugin.
        :param author: the author of the plugin.
        :param dependencies: the dependencies of the plugin (either None or a list of strings).
        :param context: the application context.
        """
        super().__init__(name, PluginType.DECODER, author, dependencies, context, icon)

    def can_decode_input(self, input_text: str) -> bool:
        """ Returns whether it might be possible to decode the specified input with this plugin.

        Override this method to implement custom "Smart decode" behaviour. See DecoderPlugin implementations for more
        information regarding this matter.

        returns: True by default.
        """
        return True


class EncoderPlugin(AbstractPlugin):

    def __init__(self, name: str, author: str, dependencies: List[str], context: 'dpp.core.context.Context', icon=None):
        """ Initializes a plugin.
        :param name: the name of the plugin.
        :param author: the author of the plugin.
        :param dependencies: the dependencies of the plugin (either None or a list of strings).
        :param context: the application context.
        """
        super().__init__(name, PluginType.ENCODER, author, dependencies, context, icon)


class HasherPlugin(AbstractPlugin):

    def __init__(self, name: str, author: str, dependencies: List[str], context: 'dpp.core.context.Context', icon=None):
        """ Initializes a plugin.
        :param name: the name of the plugin.
        :param author: the author of the plugin.
        :param dependencies: the dependencies of the plugin (either None or a list of strings).
        :param context: the application context.
        """
        super().__init__(name, PluginType.HASHER, author, dependencies, context, icon)


class ScriptPlugin(AbstractPlugin):

    def __init__(self, name: str, author: str, dependencies: List[str], context: 'dpp.core.context.Context', icon=None):
        """
        Initializes a plugin.
        :param name: the name of the plugin.
        :param author: the author of the plugin.
        :param dependencies: the dependencies of the plugin (either None or a list of strings).
        :param context: the application context.
        """
        super().__init__(name, PluginType.SCRIPT, author, dependencies, context, icon)


class IdentifyPlugin(AbstractPlugin):

    def __init__(self, name: str, author: str, dependencies: List[str], context: 'dpp.core.context.Context', icon=None):
        """
        Initializes a plugin.
        :param name: the name of the plugin.
        :param author: the author of the plugin.
        :param dependencies: the dependencies of the plugin (either None or a list of strings).
        :param context: the application context.
        """
        super().__init__(name, PluginType.IDENTIFY, author, dependencies, context, icon)


class NullPlugin(AbstractPlugin):
    """ Implements a plugin which can be used as a Null-Object. """

    def __init__(self, context=None):
        super().__init__('', '', '', [], context)

    def run(self, text: str) -> str:
        return ''

    def is_runnable(self) -> bool:
        return False
