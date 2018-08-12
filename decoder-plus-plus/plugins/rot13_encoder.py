from core.plugin.plugin import EncoderPlugin

class Plugin(EncoderPlugin):

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('ROT13', "Robin Krumnow", ["codecs"])

    def run(self, text):
        import codecs
        return codecs.encode(text, 'rot_13')
