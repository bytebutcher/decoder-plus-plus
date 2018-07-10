from core.plugin.abstract_plugin import AbstractPlugin
from core.command import Command

class Plugin(AbstractPlugin):

    def __init__(self, context):
        # Name, Type, Author, Dependencies
        super().__init__('HEX (shell)', Command.Type.DECODER, "Thomas Engel", ["codecs"])

    def run(self, text):
        if text:
            import codecs
            import re
            output = text
            for hex_code in set(sorted(re.findall(r'\\[Xx][0-9a-fA-F][0-9a-fA-F]', text))):
                try:
                    output = output.replace(hex_code, codecs.decode(hex_code[-2:], 'hex').decode('utf-8'))
                except:
                    pass
            return output
        else:
            return ""
