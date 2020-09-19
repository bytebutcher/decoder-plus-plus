from dpp.core.plugin import DecoderPlugin

class Plugin(DecoderPlugin):
    """
    Decodes bytes using Gzip.

    Example:

        Input:
            [bytes]

        Output:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('Gzip', "Thomas Engel", ["gzip"], context)

    def run(self, text):
        import gzip
        return gzip.decompress(text.encode('utf-8', errors='surrogateescape')).decode('utf-8', errors='surrogateescape')

    def can_decode_input(self, input):
        if input:
            input_bytes = input.encode('utf-8', errors='surrogateescape')
            if len(input_bytes) > 2:
                return (input_bytes[0] == 0x1f) and (input_bytes[1] == 0x8b)
        return False
