from core.plugin.abstract_plugin import AbstractPlugin
from core.command import Command

class Plugin(AbstractPlugin):

    def __init__(self, context):
        # Name, Type, Author, Dependencies
        super().__init__('HEX (str)', Command.Type.DECODER, "Thomas Engel", [])

    def run(self, text):
        return bytes.fromhex(text).decode('ascii')
