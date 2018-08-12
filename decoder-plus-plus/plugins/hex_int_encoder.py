from core.plugin.plugin import EncoderPlugin

class Plugin(EncoderPlugin):

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('HEX (int)', "Thomas Engel", [])

    def run(self, text):
        return self._run_lines(text, lambda text_part: hex(int(text_part)))
