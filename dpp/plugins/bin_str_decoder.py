from dpp.core.plugin import DecoderPlugin

class Plugin(DecoderPlugin):
    """
    Decodes a binary string.

    Example:

        Input:
            1100001 1100010 1100011 1100100 1100101 \\
            1100110 1100111 1101000 1101001 1101010 \\
            ...
            110100 110101 110110 110111 111000 111001

        Output:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('BIN (str)', "Thomas Engel", [], context)

    def run(self, text):
        n = int(text.replace(' ', ''), 2)
        return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode("utf-8", "surrogateescape") or '\0'
