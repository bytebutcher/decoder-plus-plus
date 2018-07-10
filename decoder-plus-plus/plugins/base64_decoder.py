from core.plugin.abstract_plugin import AbstractPlugin
from core.command import Command

class Plugin(AbstractPlugin):

    def __init__(self, context):
        # Name, Type, Author, Dependencies
        super().__init__('BASE64', Command.Type.DECODER, "Thomas Engel", ["base64"])

    def run(self, text):
        import base64
        return base64.b64decode(text.encode('utf-8')).decode('utf-8')
