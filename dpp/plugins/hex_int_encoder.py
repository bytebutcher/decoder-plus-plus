from dpp.core.plugin import EncoderPlugin

class Plugin(EncoderPlugin):
    """
    Encodes an integer to a hex string.

    Example:

        Input:
            123456789

        Output:
            0x75bcd15
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('HEX (int)', "Thomas Engel", [], context)

    def run(self, text):
        return self._run_lines(text, lambda text_part: hex(int(text_part)))
