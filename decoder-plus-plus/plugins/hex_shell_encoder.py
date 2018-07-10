from core.plugin.abstract_plugin import AbstractPlugin
from core.command import Command

class Plugin(AbstractPlugin):

    def __init__(self, context):
        # Name, Type, Author, Dependencies
        super().__init__('HEX (shell)', Command.Type.ENCODER, "Thomas Engel", ["codecs"])

    def run(self, text):
        if text:
            import codecs
            output = codecs.encode(text.encode('utf-8'), 'hex').decode('utf-8')
            return "\\x" + "\\x".join([i+j for i, j in zip(output[::2], output[1::2])])
        else:
            return ""
