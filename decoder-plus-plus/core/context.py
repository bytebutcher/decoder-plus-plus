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
import sys
from pathlib import Path

from core.command import Commands, Command
from core.plugin.plugin_loader import PluginLoader
from core.shortcut import Shortcut


class Context(object):

    def __init__(self):
        self._logger = {}
        self._config = self._init_config()
        self._commands = None
        self._plugin_loader = PluginLoader(self)
        self._shortcuts = {}

    def _init_config(self):
        try:
            from core.config import Config
            return Config(self.logger())
        except:
            return None

    def _init_logger(self, log_format):
        logger = logging.getLogger('decoder_plusplus')
        logging.root.setLevel(logging.DEBUG)
        hdlr = logging.StreamHandler(sys.stderr)
        hdlr.setFormatter(logging.Formatter(log_format))
        logger.addHandler(hdlr)
        return logger

    def _init_plugins(self):
        plugins = self._load_default_plugins() + self._load_user_plugins()
        commands = []
        for plugin in plugins:
            commands.append(Command.Builder().name(plugin.name()).type(plugin.type()).author(plugin.author()).title(plugin.title).run(plugin.run).select(plugin.select).build())
        return Commands(self, commands)

    def _load_user_plugins(self):
        try:
            user_plugin_folder = os.path.join(str(Path.home()), ".config", "dpp", "plugins")
            if not os.path.exists(user_plugin_folder):
                os.makedirs(user_plugin_folder)
            return list(self._plugin_loader.load(user_plugin_folder).values())
        except Exception as e:
            self.logger().error("Error loading user defined plugins: {}".format(str(e)))
            return []

    def _load_default_plugins(self):
        try:
            return list(self._plugin_loader.load("plugins/").values())
        except Exception as e:
            self.logger().error("Error loading default plugins: {}".format(str(e)))
            return []

    def config(self):
        return self._config

    def logger(self, log_format="%(module)s: %(lineno)d: %(msg)s", log_fields=None):
        if log_format not in self._logger:
            self._logger[log_format] = self._init_logger(log_format)
        if log_fields:
            return logging.LoggerAdapter(self._logger[log_format], log_fields)
        return self._logger[log_format]

    def commands(self):
        if not self._commands:
            self._commands = self._init_plugins()
        return self._commands

    def registerShortcut(self, the_key, the_name, the_default_shortcut, the_callback, the_widget):
        from PyQt5.QtGui import QKeySequence
        from PyQt5.QtWidgets import QShortcut
        the_shortcut = self._config.getShortcut(the_key)
        if not the_shortcut:
            the_shortcut = the_default_shortcut
        self.logger().debug("Registering shortcut {} to {}".format(the_key, the_shortcut))
        shortcut = QShortcut(QKeySequence(the_shortcut), the_widget)
        shortcut.activated.connect(the_callback)
        self._shortcuts[the_key] = Shortcut(the_key, the_name, shortcut, the_callback)
        self._config.setShortcut(the_key, the_shortcut)

    def updateShortcut(self, the_key, the_shortcut):
        from PyQt5.QtGui import QKeySequence
        if not the_key in self._shortcuts:
            self.logger().error("Shortcut {} is not defined".format(the_key))
            return

        self.logger().debug("Updating shortcut {} to {}".format(the_key, the_shortcut))
        shortcut = self._shortcuts[the_key]
        shortcut.shortcut().setKey(QKeySequence(the_shortcut))
        self._config.setShortcut(the_key, the_shortcut)

    def getShortcuts(self):
        return self._shortcuts.values()

    def getUnresolvedDependencies(self):
        return self._plugin_loader.getUnresolvedDependencies()