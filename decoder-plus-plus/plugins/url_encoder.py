from core.plugin.plugin import EncoderPlugin

class Plugin(EncoderPlugin):

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('URL', "Thomas Engel", ["urllib"])

    def run(self, text):
        import urllib.parse
        return urllib.parse.quote(text.encode('utf-8', errors='surrogateescape'))
