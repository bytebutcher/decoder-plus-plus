from dpp.core.plugin import EncoderPlugin

class Plugin(EncoderPlugin):
    """
    Encodes a text using HTTP64.

    HTTP64 is a BASE64 derivation which remaps following characters:

     Location  Base64  Http64
     --------  ------  ------
       62        +       -
       63        /       _
      (pad)      =       $

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXoKXsKwISLCpyQlJi8oKT0_wrRgPD58ICwuLTs6XyMrJyp-CjAxMjM0NTY3ODk$
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('HTTP64', "Thomas Engel", ["base64"], context)

    def run(self, text):
        import base64
        encoded = base64.b64encode(text.encode('utf-8', errors="surrogateescape")).decode('utf-8', errors="surrogateescape")
        encoded = encoded.replace('+', '-')
        encoded = encoded.replace('/', '_')
        encoded = encoded.replace('=', '$')
        return encoded

