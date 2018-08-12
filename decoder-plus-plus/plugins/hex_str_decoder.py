from core.plugin.plugin import DecoderPlugin

class Plugin(DecoderPlugin):

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('HEX (str)', "Thomas Engel", [])

    def run(self, text):
        return bytes.fromhex(text).decode('ascii')
