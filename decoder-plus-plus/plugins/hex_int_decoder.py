from core.plugin.plugin import DecoderPlugin

class Plugin(DecoderPlugin):

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('HEX (int)', "Thomas Engel", [])

    def run(self, text):
        return self._run_lines(text, lambda text_part: str(int(text_part, 16)))

