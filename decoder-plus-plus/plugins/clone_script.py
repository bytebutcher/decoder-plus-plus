from core.plugin.abstract_plugin import ScriptPlugin
from core.command import Command

class Plugin(ScriptPlugin):

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('Clone', "Thomas Engel", [])

    def run(self, text):
        return text
