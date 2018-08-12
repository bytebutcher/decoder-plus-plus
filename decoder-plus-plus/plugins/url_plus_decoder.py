from core.plugin.abstract_plugin import DecoderPlugin

class Plugin(DecoderPlugin):

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('URL+', "Thomas Engel", ["urllib"])

    def run(self, text):
        import urllib.parse
        return urllib.parse.unquote_plus(text)
