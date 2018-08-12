from core.plugin.abstract_plugin import DecoderPlugin

class Plugin(DecoderPlugin):

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('BASE32', "Thomas Engel", ["base64"])

    def run(self, text):
        import base64
        return base64.b32decode(text.encode('utf-8')).decode('utf-8')
