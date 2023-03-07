import os
from typing import List

from dpp import app_path
from dpp.core import Context
from dpp.core.plugin import AbstractPlugin
from dpp.core.plugin.manager import PluginManager


context = Context('net.bytebutcher.decoder_plus_plus', app_path)
plugin_manager = PluginManager([os.path.join(app_path, "plugins")], context)


def load_plugins() -> List[AbstractPlugin]:
    return plugin_manager.plugins()


def load_plugin(name: str, type: str) -> AbstractPlugin:
    return plugin_manager.plugin(name, type)
