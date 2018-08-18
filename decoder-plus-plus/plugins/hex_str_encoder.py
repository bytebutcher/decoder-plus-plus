from core.plugin.plugin import EncoderPlugin

class Plugin(EncoderPlugin):

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('HEX (str)', "Thomas Engel", ["codecs"])

    def run(self, text):
        import codecs
        return codecs.encode(text.encode('utf-8', errors='surrogateescape'), 'hex').decode('utf-8')
