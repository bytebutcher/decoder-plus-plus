from dpp.core.plugin import EncoderPlugin

class Plugin(EncoderPlugin):
    """
    Encodes an integer to a binary string.

    Example:

        Input:
            123456789

        Output:
            111010110111100110100010101
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('BIN (int)', "Thomas Engel", [], context)

    def run(self, text):
        return self._run_lines(text, lambda text_part: "{0:b}".format(int(text_part)))
