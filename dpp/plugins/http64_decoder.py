import re

from dpp.core.plugin import DecoderPlugin

class Plugin(DecoderPlugin):
    """
    Decodes a HTTP64 string.

    HTTP64 is a BASE64 derivation which remaps following characters:

     Location  Base64  Http64
     --------  ------  ------
       62        +       -
       63        /       _
      (pad)      =       $

    Example:

        Input:
            YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXoKXsKwISLCpyQlJi8oKT0_wrRgPD58ICwuLTs6XyMrJyp-CjAxMjM0NTY3ODk$

        Output:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('HTTP64', "Thomas Engel", ["base64"], context)

    def run(self, text):
        import base64
        encoded = self._add_missing_padding(text.encode('utf-8', errors="surrogateescape"))
        encoded = encoded.replace('-', '+')
        encoded = encoded.replace('_', '/')
        encoded = encoded.replace('$', '=')
        return base64.b64decode(encoded).decode('utf-8', errors="surrogateescape")

    def _add_missing_padding(self, text):
        missing_padding = len(text) % 4
        if missing_padding != 0:
            text += '$' * (4 - missing_padding)
        return text.decode('utf-8', errors="surrogateescape")

    def can_decode_input(self, input):
        if len(input) % 4 == 0:
            if input.startswith("0o") and input[2:].isdigit():
                # This looks more like an octal encoding.
                return False
            if re.search(r'^(?:[A-Za-z0-9\-_]{4})*(?:[A-Za-z0-9\-_]{2}\$\$|[A-Za-z0-9\-_]{3}\$)?$', input):
                return True
        return False
