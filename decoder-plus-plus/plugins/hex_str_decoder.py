import re

from core.plugin.plugin import DecoderPlugin

class Plugin(DecoderPlugin):
    """
    Decodes a hex string.

    Example:

        Input:
            6162636465666768696a6b6c6d6e6f707172737475767778797a0a30313233343536373839
        Output:
            abcdefghijklmnopqrstuvwxyz
            0123456789
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('HEX (str)', "Thomas Engel", [])

    def run(self, text):
        return bytes.fromhex(text).decode('ascii')

    def can_decode_input(self, input):
        if len(input) % 2 == 0:
            hex = re.search(r'^[a-fA-F0-9]+$', input)
            if hex:
                return True
        return False