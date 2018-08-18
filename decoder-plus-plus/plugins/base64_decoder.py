import re

from core.plugin.plugin import DecoderPlugin

class Plugin(DecoderPlugin):
    """
    Decodes a base64 string.

    Example:

        Input:
            YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXoKMDEyMzQ1Njc4OQ===
        Output:
            abcdefghijklmnopqrstuvwxyz
            0123456789
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('BASE64', "Thomas Engel", ["base64"])

    def run(self, text):
        import base64
        text = self._add_missing_padding(text.encode('utf-8', errors="surrogateescape"))
        return base64.b64decode(text).decode('utf-8', errors="surrogateescape")

    def _add_missing_padding(self, text):
        missing_padding = len(text) % 4
        if missing_padding != 0:
            text += b'=' * (4 - missing_padding)
        return text

    def can_decode_input(self, input):
        if len(input) % 4 == 0:
            if re.search(r'^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$', input):
                return True
        return False
