from core.plugin.abstract_plugin import AbstractPlugin
from core.command import Command

class Plugin(AbstractPlugin):

    def __init__(self, context):
        # Name, Type, Author, Dependencies
        super().__init__('HEX (str)', Command.Type.ENCODER, "Thomas Engel", ["codecs"])

    def run(self, text):
        import codecs
        return codecs.encode(text.encode('utf-8'), 'hex').decode('utf-8')
