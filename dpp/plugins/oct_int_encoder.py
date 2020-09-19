from dpp.core.plugin import EncoderPlugin

class Plugin(EncoderPlugin):
    """
    Encodes an integer to an octal string.

    Example:

        Input:
            123456789

        Output:
            726746425
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('OCT (int)', "Thomas Engel", [], context)

    def run(self, text):
        return self._run_lines(text, lambda text_part: format(int(text_part), "o"))
