from core.plugin.plugin import DecoderPlugin

class Plugin(DecoderPlugin):
    """
     Decodes a base16 string.

     Example:

         Input:
             6162636465666768696A6B6C6D6E6F707172737475767778797A0A30313233343536373839
         Output:
             abcdefghijklmnopqrstuvwxyz
             0123456789
     """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('BASE16', "Thomas Engel", ["base64"])

    def run(self, text):
        import base64
        return base64.b16decode(text.encode('utf-8', errors='surrogateescape')).decode('utf-8', errors='surrogateescape')
