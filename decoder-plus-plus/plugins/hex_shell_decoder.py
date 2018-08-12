from core.plugin.plugin import DecoderPlugin

class Plugin(DecoderPlugin):

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('HEX (shell)', "Thomas Engel", ["codecs"])

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
