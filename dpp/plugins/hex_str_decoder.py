import re

from dpp.core.plugin import DecoderPlugin

class Plugin(DecoderPlugin):
    """
    Decodes a hex string.

    Example:

        Input:
            6162636465666768696a6b6c6d6e6f70717273747576777 \\
            8797a0a5ec2b02122c2a72425262f28293d3fc2b4603c3e \\
            7c202c2e2d3b3a5f232b272a7e0a30313233343536373839

        Output:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('HEX (str)', "Thomas Engel", [], context)

    def run(self, text):
        return self._run_lines(text, lambda text_part: bytes.fromhex(text_part).decode('ascii'))

    def can_decode_input(self, input):
        if len(input) % 2 == 0:
            hex = re.search(r'^[a-fA-F0-9]+$', input)
            if hex:
                return True
        return False