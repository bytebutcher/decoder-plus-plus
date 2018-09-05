import re

from core.plugin.plugin import DecoderPlugin

class Plugin(DecoderPlugin):
    """
    Decodes a hex string to an integer.

    Example:

        Input:
            0x75bcd15

        Output:
            123456789
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('HEX (int)', "Thomas Engel", [])

    def safe_name(self):
        return "hex_int"

    def run(self, text):
        return self._run_lines(text, lambda text_part: str(int(text_part, 16)))

    def can_decode_input(self, input):
        if len(input) % 2 == 0:
            hex = re.search(r'^(0x|0X)[a-fA-F0-9]+$', input)
            if hex:
                return True
        return False