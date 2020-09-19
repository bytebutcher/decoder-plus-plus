from dpp.core.plugin import DecoderPlugin

class Plugin(DecoderPlugin):
    """
    Decodes a binary string to an integer.

    Example:

        Input:
            111010110111100110100010101

        Output:
            123456789
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('BIN (int)', "Thomas Engel", [], context)

    def run(self, text):
        return self._run_lines(text, lambda text_part: str(int(text_part, 2)))
