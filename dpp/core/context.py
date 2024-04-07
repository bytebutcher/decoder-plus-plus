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

import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import List

from qtpy.QtCore import Signal, QObject
from qtpy.QtWidgets import QAction

import dpp
from dpp.core import logger
from dpp.core.listener import Listener
from dpp.core.plugin import AbstractPlugin
from dpp.core.plugin.manager import PluginManager
from dpp.core.shortcuts import Shortcut, NullShortcut


class Context(QObject):
    """
    The context of the application.
    Contains access to often used functionalities like logging, configuration and plugins.
    Interaction with this class should be limited to minimize dependencies.
    """

    shortcutUpdated = Signal('PyQt_PyObject')

    class Mode:
        GUI_MODERN = "gui-modern"
        GUI_CLASSIC = "gui-classic"
        COMMAND_LINE = "cmd"

    class DockWidget:
        EMPTY_DOCK_WIDGET = "empty_dock_widget"
        LOG_DOCK_WIDGET = "log_dock_widget"
        HEX_DOCK_WIDGET = "hex_dock_widget"

    class Shortcut:
        FILE_EXIT = "file_exit"
        EDIT_CUT = "edit_cut"
        EDIT_COPY = "edit_copy"
        EDIT_PASTE = "edit_paste"
        OPEN_FILE = "open_file"
        SAVE_AS_FILE = "save_as_file"
        TAB_NEW = "tab_new"
        TAB_RENAME = "tab_rename"
        TAB_DUPLICATE = "tab_duplicate"
        TAB_NEXT = "tab_next"
        TAB_PREVIOUS = "tab_previous"
        TAB_CLOSE = "tab_close"
        TAB_SELECT_ = "tab_select_{}"
        TAB_SELECT_1 = "tab_select_1"
        TAB_SELECT_2 = "tab_select_2"
        TAB_SELECT_3 = "tab_select_3"
        TAB_SELECT_4 = "tab_select_4"
        TAB_SELECT_5 = "tab_select_5"
        TAB_SELECT_6 = "tab_select_6"
        TAB_SELECT_7 = "tab_select_7"
        TAB_SELECT_8 = "tab_select_8"
        TAB_SELECT_9 = "tab_select_9"
        FOCUS_CODEC_SEARCH = "focus_codec_search"
        FOCUS_ENCODER = "focus_encoder"
        FOCUS_DECODER = "focus_decoder"
        FOCUS_HASHER = "focus_hasher"
        FOCUS_SCRIPT = "focus_script"
        FOCUS_INPUT_TEXT = "focus_input_text"
        FOCUS_INPUT_TEXT_NEXT = "focus_input_text_next"
        FOCUS_INPUT_TEXT_PREVIOUS = "focus_input_text_previous"
        SELECT_MODERN_GUI = "select_modern_gui"
        SELECT_CLASSIC_GUI = "select_classic_gui"
        SELECT_HEX_DOCK = "select_hex_dock"
        SELECT_LOG_DOCK = "select_log_dock"
        TOGGLE_SEARCH_FIELD = "toggle_search_field"
        SHOW_PLUGINS = "show_plugins"
        SHOW_KEYBOARD_SHORTCUTS = "show_keyboard_shortcuts"
        SHOW_ABOUT = "show_about"

    def __init__(self, app_id, app_path):
        super(__class__, self).__init__()
        self._app_id = app_id
        self._app_path = app_path
        self._trace_mode = False
        self._debug_mode = self.config.isDebugModeEnabled()
        self._logger = logger.getLogger(name='dpp', level=self.getLogLevel())
        self._listener = Listener(self)
        self._plugins = None
        self._shortcuts = {}
        self._installed_packages = []
        self._mode = None

    @property
    def config(self):
        """ Returns the configuration. """
        if not hasattr(self, '_config') or not self._config:
            from dpp.core.config import Config
            self._config = Config()
        return self._config

    @property
    def logger(self) -> logging.Logger:
        """ Returns the standard logger for this application. """
        return self._logger

    def getAppName(self) -> str:
        """ Returns the name of the application. """
        return "Decoder++"

    def getAppVersion(self) -> str:
        """ Returns the version of the application. """
        return dpp.__version__

    def getAppPath(self):
        """ Returns the path where the main application is located. """
        return self._app_path

    def getAppID(self):
        """ Returns the ID of the application. """
        return self._app_id

    def setMode(self, mode: str):
        """ Sets the mode (see ``Context.Mode``) in which the application is currently running. """
        self._mode = mode

    def mode(self) -> str:
        """ :returns the mode (see ``Context.Mode``) the application is currently running in or None if unspecified. """
        return self._mode

    def getLogLevel(self):
        """ :returns the current log level. """
        if self._trace_mode:
            return logging.TRACE
        if self._debug_mode or self.isDebugModeEnabled():
            return logging.DEBUG
        return logging.INFO

    def setDebugMode(self, status: bool, temporary=False):
        """ Enables/Disables debug mode. """
        if not temporary:
            self.config.setDebugMode(status)
        self._debug_mode = status
        self._trace_mode = False
        self._logger.setLevel(logging.DEBUG if status else logging.INFO)
        status_string = "enabled" if status else "disabled"
        self._logger.info("Debug Mode: {} {}".format(status_string, " (temporary) " if temporary else ""))

    def setTraceMode(self, status: bool):
        """ Enables/Disables debug mode. """
        self._trace_mode = status
        self._debug_mode = False
        self._logger.setLevel(logging.TRACE if status else logging.INFO)
        status_string = 'enabled' if status else 'disabled'
        self._logger.info(f'Trace Mode: {status_string}')

    def toggleDebugMode(self):
        """ Toggles the debug-mode on/off. """
        self.setDebugMode(not self.config.isDebugModeEnabled())

    def isDebugModeEnabled(self):
        """ Returns whether the debug mode is currently configured or temporary enabled. """
        return self.config.isDebugModeEnabled() or self._debug_mode

    def namespace(self):
        """
        Returns the namespace of the application to allow instances like the console to access classes and functions.
        """
        return self._namespace

    def listener(self) -> Listener:
        """ Returns the listener instance which allows to subscribe to certain events. """
        return self._listener

    def plugins(self) -> PluginManager:
        """ Returns all plugins. """
        if not self._plugins:
            self._plugins = PluginManager([
                os.path.join(self._app_path, "plugins"),
                os.path.join(str(Path.home()), ".config", "dpp", "plugins")], self)
        return self._plugins

    def checkDependency(self, package):
        """
        Checks whether the desired package is already installed.
        :param package: the package to check.
        :return: True, when the package is already installed, otherwise False.
        """
        if not self._installed_packages:
            # lazy initialize installed packages.
            reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
            self._installed_packages = [r.decode().split('==')[0] for r in reqs.split()]
        return package in self._installed_packages

    def registerShortcut(self, id: str, name: str, default_shortcut_key: str, callback, widget) -> QAction:
        """
        Registers a shortcut with the specified parameters.
        :param id: the id of the shortcut.
        :param name: the name of the shortcut which is displayed to the user.
        :param default_shortcut_key: the default shortcut key which may be overwritten by the user.
        :param callback: the callback which should be triggered when the shortcut is used.
        :param widget: the widget to which the shortcut is bound to.
        """
        shortcut_key = self.config.getShortcutKey(id)
        if not shortcut_key:
            shortcut_key = default_shortcut_key

        self._logger.trace("Registering shortcut {} to {}".format(id, shortcut_key))
        if id in self._shortcuts:
            self._logger.debug("Retrieving previously registered shortcut {}".format(id, shortcut_key))
            return self._shortcuts[id].clone(name)

        shortcut = Shortcut(id, name, shortcut_key, callback, widget)
        self._shortcuts[id] = shortcut
        self.config.setShortcutKey(id, shortcut_key)
        self.shortcutUpdated.emit(shortcut)
        return shortcut

    def updateShortcutKey(self, id: str, shortcut_key: str):
        """
        Updates the shortcut with the specified id.
        :param id: the id of the shortcut.
        :param shortcut_key: the shortcut key which should be used onwards.
        """
        if id not in self._shortcuts:
            self._logger.error("Shortcut {} is not defined".format(id))
            return

        self._logger.debug("Updating shortcut {} to {}".format(id, shortcut_key))
        shortcut = self._shortcuts[id]
        shortcut.setKey(shortcut_key)
        self.config.setShortcutKey(id, shortcut_key)
        self.shortcutUpdated.emit(shortcut)

    def getShortcuts(self) -> List[Shortcut]:
        """ Returns a list of shortcuts. """
        return self._shortcuts.values()

    def getShortcutById(self, id: str):
        """ Returns the shortcut with the specified id. """
        if id not in self._shortcuts:
            self._logger.error("Shortcut {} is not defined".format(id))
            return NullShortcut()
        return self._shortcuts[id]

    def getPluginByName(self, name: str, type: str) -> AbstractPlugin:
        return self.plugins().plugin(name, type)

    def __deepcopy__(self, memo):
        """ There shall be only one. """
        return self
