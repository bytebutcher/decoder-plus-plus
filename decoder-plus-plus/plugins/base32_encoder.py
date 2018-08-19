from core.plugin.plugin import EncoderPlugin

class Plugin(EncoderPlugin):
    """
     Encodes a string to base32.

     Example:

         Input:
             abcdefghijklmnopqrstuvwxyz
             0123456789
         Output:
             MFRGGZDFMZTWQ2LKNNWG23TPOBYXE43UOV3HO6DZPIFDAMJSGM2DKNRXHA4Q====
     """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('BASE32', "Thomas Engel", ["base64"])

    def run(self, text):
        import base64
        return base64.b32encode(text.encode('utf-8', errors='surrogateescape')).decode('utf-8', errors='surrogateescape')
