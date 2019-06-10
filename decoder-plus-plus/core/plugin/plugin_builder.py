from core import Context
from core.plugin.plugins import AbstractPlugin

class PluginBuilder:

    def __init__(self, context: Context):
        self._context = context

    def build(self, config) -> AbstractPlugin:
        try:
            plugin = self._context.getPluginByName(config["name"], config["type"])
            plugin.setup(config["config"])
            return plugin
        except:
            return None
