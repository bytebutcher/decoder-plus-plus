from core.plugin.abstract_plugin import EncoderPlugin

class Plugin(EncoderPlugin):

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('HEX (shell)', "Thomas Engel", ["codecs"])

    def run(self, text):
        if text:
            import codecs
            output = codecs.encode(text.encode('utf-8'), 'hex').decode('utf-8')
            return "\\x" + "\\x".join([i+j for i, j in zip(output[::2], output[1::2])])
        else:
            return ""
