import re

from dpp.core.plugin import DecoderPlugin

class Plugin(DecoderPlugin):
    """
    Decodes a Base54 string.

    Example:

        Input:
            0ECJPC% CC3DVED5QDO$D/3EHFE QEA%ET4F3GF:D1PROM84GROSP4A$4L35JX7TROL7CL+7134V$5.L7A1CMK5XG5/C1*96DL6WW66:6C1

        Output:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('BASE45', "Thomas Engel", ["base45"], context)

    def run(self, text):
        import base45
        return base45.b45decode(str.encode(text)).decode('utf-8', errors="surrogateescape")

    def can_decode_input(self, input):
        if input.startswith("0o") and input[2:].isdigit():
            # This looks more like an octal encoding.
            return False
        if re.search(r'^[A-Z0-9 $%*+-./:]*$', input):
            return True
        return False

