from dpp.core.plugin import EncoderPlugin

class Plugin(EncoderPlugin):
    """
    Encodes a string to a binary string.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            1100001 1100010 1100011 1100100 1100101 \\
            1100110 1100111 1101000 1101001 1101010 \\
            ...
            110100 110101 110110 110111 111000 111001
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('BIN (str)', "Thomas Engel", ["codecs"], context)

    def run(self, text):
        bits = bin(int.from_bytes(text.encode('utf-8', 'surrogateescape'), 'big'))[2:]
        return ' '.join(self._chunk_string(bits.zfill(8 * ((len(bits) + 7) // 8)), 8))

    def _chunk_string(self, string, length):
        return [string[0 + i:length + i] for i in range(0, len(string), length)]
