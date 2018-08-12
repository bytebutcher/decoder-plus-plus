from core.plugin.plugin import EncoderPlugin

class Plugin(EncoderPlugin):

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('HTML', "Thomas Engel", ["html"])

    def run(self, text):
        import html
        return html.escape(text)
