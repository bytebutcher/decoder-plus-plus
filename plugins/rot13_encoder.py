from core.plugin.abstract_plugin import AbstractPlugin
from core.command import Command

class Plugin(AbstractPlugin):

    def __init__(self, context):
        # Name, Type, Author, Dependencies
        super().__init__('ROT13', Command.Type.ENCODER, "Robin Krumnow", ["codecs"])

    def run(self, text):
        import codecs
        return codecs.encode(text, 'rot_13')
