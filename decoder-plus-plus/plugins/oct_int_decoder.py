from core.plugin.plugin import DecoderPlugin

class Plugin(DecoderPlugin):
    """
    Decodes an octal string to an integer.

    Example:

        Input:
            0o726746425
        Output:
            123456789
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('OCT (int)', "Thomas Engel", [])

    def safe_name(self):
        return "oct_int"

    def run(self, text):
        return self._run_lines(text, lambda text_part: str(int(text_part, 8)))
