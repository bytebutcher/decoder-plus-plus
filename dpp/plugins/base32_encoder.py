from dpp.core.plugin import EncoderPlugin

class Plugin(EncoderPlugin):
    """
    Encodes a string using Base32.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            MFRGGZDFMZTWQ2LKNNWG23TPOBYXE43UOV3HO6DZPIFF5Q \\
            VQEERMFJZEEUTC6KBJHU74FNDAHQ7HYIBMFYWTWOS7EMVS \\
            OKT6BIYDCMRTGQ2TMNZYHE======
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('BASE32', "Thomas Engel", ["base64"], context)

    def run(self, text):
        import base64
        return base64.b32encode(text.encode('utf-8', errors='surrogateescape')).decode('utf-8', errors='surrogateescape')
