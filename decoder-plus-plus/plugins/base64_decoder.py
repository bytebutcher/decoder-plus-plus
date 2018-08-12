from core.plugin.plugin import DecoderPlugin

class Plugin(DecoderPlugin):

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('BASE64', "Thomas Engel", ["base64"])

    def run(self, text):
        import base64
        return base64.b64decode(text.encode('utf-8')).decode('utf-8')
