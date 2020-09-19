from dpp.core.plugin import DecoderPlugin

class Plugin(DecoderPlugin):
    """
    Decodes a Base16 string.

    Example:

        Input:
            6162636465666768696A6B6C6D6E6F70717273747576777 \\
            8797A0A5EC2B02122C2A72425262F28293D3FC2B4603C3E \\
            7C202C2E2D3B3A5F232B272A7E0A30313233343536373839

        Output:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('BASE16', "Thomas Engel", ["base64"], context)

    def run(self, text):
        import base64
        return base64.b16decode(text.encode('utf-8', errors='surrogateescape')).decode('utf-8', errors='surrogateescape')
