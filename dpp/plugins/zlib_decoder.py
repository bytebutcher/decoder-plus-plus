from dpp.core.plugin import DecoderPlugin

class Plugin(DecoderPlugin):
    """
    Decodes bytes using ZLib.

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
        super().__init__('Zlib', "Thomas Engel", ["zlib"], context)

    def run(self, text):
        import zlib
        return zlib.decompress(text.encode('utf-8', errors='surrogateescape')).decode('utf-8', errors='surrogateescape')

    def can_decode_input(self, input):
        if input:
            input_bytes = input.encode('utf-8', errors='surrogateescape')
            if len(input_bytes) > 2:
                return (input_bytes[0] == 0x78) and (input_bytes[1] in (
                    0x01, # No Compression/Low
                    0x9c, # Default Compression
                    0xda  # Best Compression
                ))
        return False
