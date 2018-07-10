from core.plugin.abstract_plugin import AbstractPlugin
from core.command import Command

class Plugin(AbstractPlugin):

    def __init__(self, context):
        # Name, Type, Author, Dependencies
        super().__init__('Clone', Command.Type.SCRIPT, "Thomas Engel", [])

    def run(self, text):
        return text
