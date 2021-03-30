import re

from dpp.core.plugin import DecoderPlugin

class Plugin(DecoderPlugin):
    """
    Decodes a URL-safe BASE64 string.

    URL-safe BASE64 is a BASE64 derivation which remaps following characters:

     Location  Base64  Http64
     --------  ------  ------
       62        +       -
       63        /       _

    Example:

        Input:
            YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXoKXsKwISLCpyQlJi8oKT0_wrRgPD58ICwuLTs6XyMrJyp-CjAxMjM0NTY3ODk=

        Output:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('BASE64 (URL-safe)', "Thomas Engel", ["base64"], context)

    def run(self, text):
        import base64
        text = self._add_missing_padding(text.encode('utf-8', errors="surrogateescape"))
        return base64.urlsafe_b64decode(text).decode('utf-8', errors="surrogateescape")

    def _add_missing_padding(self, text):
        missing_padding = len(text) % 4
        if missing_padding != 0:
            text += b'=' * (4 - missing_padding)
        return text

    def can_decode_input(self, input):
        if len(input) % 4 == 0:
            if input.startswith("0o") and input[2:].isdigit():
                # This looks more like an octal encoding.
                return False
            if not ("-" in input or "_" in input):
                # The urlsafe b64 encoder substitutes - instead of + and _ instead of /.
                # If these characters are not found in the input string it might be b64, but it is not the urlsafe b64.
                return False
            if re.search(r'^(?:[A-Za-z0-9\-_]{4})*(?:[A-Za-z0-9\-_]{2}==|[A-Za-z0-9\-_]{3}=)?$', input):
                return True
        return False
