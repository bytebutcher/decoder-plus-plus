import re

from dpp.core.plugin import DecoderPlugin

class Plugin(DecoderPlugin):
    """
    Decodes a Base32 string.

    Example:

        Input:
            MFRGGZDFMZTWQ2LKNNWG23TPOBYXE43UOV3HO6DZPIFF5Q \\
            VQEERMFJZEEUTC6KBJHU74FNDAHQ7HYIBMFYWTWOS7EMVS \\
            OKT6BIYDCMRTGQ2TMNZYHE======

        Output:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('BASE32', "Thomas Engel", ["base64"], context)

    def run(self, text):
        import base64
        return base64.b32decode(text.encode('utf-8', errors='surrogateescape')).decode('utf-8', errors='surrogateescape')

    def can_decode_input(self, input):
        if len(input) % 4 == 0:
            if re.search(r'^(?:[A-Z2-7]{8})*(?:[A-Z2-7]{2}={6}|[A-Z2-7]{4}={4}|[A-Z2-7]{5}={3}|[A-Z2-7]{7}=)?$', input):
                return True
        return False
