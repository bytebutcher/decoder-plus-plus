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
from collections import namedtuple
from pathlib import Path
from typing import List, Dict

from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QAction

from core.config import Config
from core.listener import Listener
from core.plugin.plugins import AbstractPlugin, Plugins
from core.plugin.plugin_loader import PluginLoader
from core.shortcut import Shortcut, NullShortcut


class Context(QObject):
    """
    The context of the application.
    This includes often used functionality like logging, configuration and plugins.
    Interaction with this class should be limited to minimize dependencies.
    """

    shortcutUpdated = pyqtSignal('PyQt_PyObject')

    class Shortcut:
        """ A set of all shortcut ids which can be used within the application. """

        FILE_EXIT = "file_exit"
        EDIT_CUT = "edit_cut"
        EDIT_COPY = "edit_copy"
        EDIT_PASTE = "edit_paste"
        OPEN_FILE = "open_file"
        SAVE_AS_FILE = "save_as_file"
        TAB_NEW = "tab_new"
        TAB_RENAME = "tab_rename"
        TAB_NEXT = "tab_next"
        TAB_PREVIOUS = "tab_previous"
        TAB_CLOSE = "tab_close"
        TAB_SELECT_ = "tab_select_{}"
        TAB_SELECT_1 = "tab_select_1"
        TAB_SELECT_2= "tab_select_2"
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
        SELECT_PLAIN_VIEW = "select_plain_view"
        SELECT_HEX_DOCK = "select_hex_dock"
        SELECT_LOG_DOCK = "select_log_dock"
        TOGGLE_SEARCH_FIELD = "toggle_search_field"

    def __init__(self, app_id):
        super(__class__, self).__init__()
        self._app_id = app_id
        self._logger = {}
        self._config = self._init_config()
        self._init_excepthook()
        self._listener = Listener(self)
        self._plugins = None
        self._plugin_loader = PluginLoader(self)
        self._shortcuts = {}
        self._installed_packages = []

    def _init_config(self):
        """ Returns the configuration. Might return None when initialization fails. """
        try:
            from core.config import Config
            return Config()
        except:
            return None

    def _init_logger(self, log_format):
        """ Returns the logger. """
        logger = logging.getLogger(self._app_id)
        log_level = logging.DEBUG if self._config.isDebugModeEnabled() else logging.WARN

        logging.root.setLevel(log_level)
        console_logger = logging.StreamHandler(sys.stderr)
        console_logger.setFormatter(logging.Formatter(log_format))
        logger.addHandler(console_logger)

        file_logger = logging.FileHandler(os.path.join(self.getAppPath(), "dpp.log"))
        file_logger.setLevel(log_level)
        file_logger_formatter = logging.Formatter(
            '%(asctime)s - %(module)s: %(lineno)d: %(msg)s',
            datefmt='%m/%d/%Y %I:%M:%S %p')
        file_logger.setFormatter(file_logger_formatter)
        logger.addHandler(file_logger)

        return logger

    def _init_excepthook(self):
        """
        Initializes an excepthook which handles uncaught exceptions.
        @see https://fman.io/blog/pyqt-excepthook/
        """

        def excepthook(exc_type, exc_value, exc_tb):
            enriched_tb = _add_missing_frames(exc_tb) if exc_tb else exc_tb
            # Note: sys.__excepthook__(...) would not work here.
            # We need to use print_exception(...):
            self.logger().error("Uncaught exception", exc_info=(exc_type, exc_value, enriched_tb))

        def _add_missing_frames(tb):
            result = fake_tb(tb.tb_frame, tb.tb_lasti, tb.tb_lineno, tb.tb_next)
            frame = tb.tb_frame.f_back
            while frame:
                result = fake_tb(frame, frame.f_lasti, frame.f_lineno, result)
                frame = frame.f_back
            return result

        fake_tb = namedtuple(
            'fake_tb', ('tb_frame', 'tb_lasti', 'tb_lineno', 'tb_next')
        )

        sys.excepthook = excepthook

    def _init_plugins(self) -> Plugins:
        """ Returns standard and user plugins which could be loaded successfully. """
        return Plugins(self, self._load_default_plugins() + self._load_user_plugins())

    def _load_default_plugins(self):
        """ Returns all standard plugins located at ${APPPATH}/plugins which could be loaded successfully. """
        try:
            self.logger().info("Loading default plugins ...")
            return list(self._plugin_loader.load(os.path.join(self.getAppPath(), "plugins")).values())
        except Exception as e:
            self.logger().error("Error loading default plugins: {}".format(str(e)))
            return []

    def _load_user_plugins(self):
        """ Returns all user plugins located at ${HOME}/.config/dpp/plugins which could be loaded successfully. """
        try:
            user_plugin_folder = os.path.join(str(Path.home()), ".config", "dpp", "plugins")
            if not os.path.exists(user_plugin_folder):
                os.makedirs(user_plugin_folder)
            self.logger().info("Loading user plugins ...")
            return list(self._plugin_loader.load(user_plugin_folder).values())
        except Exception as e:
            self.logger().error("Error loading user defined plugins: {}".format(str(e)))
            return []

    def getAppPath(self):
        """ Returns the path where the main application is located. """
        pathname = os.path.realpath(sys.argv[0])
        return os.path.dirname(pathname)

    def getAppID(self):
        """ Returns the ID of the application. """
        return self._app_id

    def toggleDebugMode(self):
        """ Toggles the debug-mode on/off. """
        self._config.setDebugMode(not self._config.isDebugModeEnabled())
        logging.root.setLevel(logging.DEBUG if self._config.isDebugModeEnabled() else logging.INFO)
        self.logger().info("Debug Mode: {}".format("enabled" if self._config.isDebugModeEnabled() else "disabled"))

    def config(self) -> Config:
        """ Returns the main configuration of the application. """
        return self._config

    def listener(self) -> Listener:
        return self._listener

    def logger(self, log_format="%(module)s: %(lineno)d: %(msg)s", log_fields=None):
        """ Returns the logger of the application. """
        if log_format not in self._logger:
            self._logger[log_format] = self._init_logger(log_format)
        if log_fields:
            return logging.LoggerAdapter(self._logger[log_format], log_fields)
        return self._logger[log_format]

    def plugins(self) -> Plugins:
        """ Returns all plugins which could be loaded successfully. """
        if not self._plugins:
            self._plugins = self._init_plugins()
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

    def registerShortcut(self, the_id: str, the_name: str, the_default_shortcut_key: str, the_callback, the_widget) -> QAction:
        """
        Registers a shortcut with the specified parameters.
        :param the_id: the id of the shortcut.
        :param the_name: the name of the shortcut which is displayed to the user.
        :param the_default_shortcut_key: the default shortcut key which may be overwritten by the user.
        :param the_callback: the callback which should be triggered when the shortcut is used.
        :param the_widget: the widget to which the shortcut is bound to.
        """
        the_shortcut_key = self._config.getShortcutKey(the_id)
        if not the_shortcut_key:
            the_shortcut_key = the_default_shortcut_key
        self.logger().debug("Registering shortcut {} to {}".format(the_id, the_shortcut_key))
        shortcut = Shortcut(the_id, the_name, the_shortcut_key, the_callback, the_widget)
        self._shortcuts[the_id] = shortcut
        self._config.setShortcutKey(the_id, the_shortcut_key)
        self.shortcutUpdated.emit(shortcut)
        return shortcut

    def updateShortcutKey(self, the_id: str, the_shortcut_key: str):
        """
        Updates the shortcut with the specified id.
        :param the_id: the id of the shortcut.
        :param the_shortcut_key: the shortcut key which should be used onwards.
        """
        if the_id not in self._shortcuts:
            self.logger().error("Shortcut {} is not defined".format(the_id))
            return

        self.logger().debug("Updating shortcut {} to {}".format(the_id, the_shortcut_key))
        shortcut = self._shortcuts[the_id]
        shortcut.setKey(the_shortcut_key)
        self._config.setShortcutKey(the_id, the_shortcut_key)
        self.shortcutUpdated.emit(shortcut)

    def getShortcuts(self) -> List[Shortcut]:
        """ Returns a list of shortcuts. """
        return self._shortcuts.values()

    def getShortcutById(self, the_id: str):
        """ Returns the shortcut with the specified id. """
        if the_id not in self._shortcuts:
            self.logger().error("Shortcut {} is not defined".format(the_id))
            return NullShortcut()
        return self._shortcuts[the_id]

    def getPluginByName(self, name: str, type: str) -> AbstractPlugin:
        return self.plugins().plugin(name, type)

    def getPluginsUnresolvedDependencies(self, filter_enabled_plugins: bool=True) -> Dict[str, str]:
        """ Returns all unresolved dependencies in a dict.
        :param filter_enabled_plugins: when True, returns only unresolved dependencies of enabled plugins.
        """
        return self._plugin_loader.get_unresolved_dependencies(filter_enabled_plugins)

    def getPluginsErrors(self) -> Dict[str, str]:
        """ Returns all errors which happened while loading plugins. """
        return self._plugin_loader.get_errors()

    def saveAsFile(self, filename: str, content: str):
        with open(filename, "w") as f:
            f.write(content)
