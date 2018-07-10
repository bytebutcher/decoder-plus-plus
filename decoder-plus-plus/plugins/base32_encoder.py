from core.plugin.abstract_plugin import AbstractPlugin
from core.command import Command

class Plugin(AbstractPlugin):

    def __init__(self, context):
        # Name, Type, Author, Dependencies
        super().__init__('BASE32', Command.Type.ENCODER, "Thomas Engel", ["base64"])

    def run(self, text):
        import base64
        return base64.b32encode(text.encode('utf-8')).decode('utf-8')
