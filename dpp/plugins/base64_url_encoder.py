from dpp.core.plugin import EncoderPlugin

class Plugin(EncoderPlugin):
    """
    Encodes a text using Base64.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXoKXsKwISLCpyQlJi8oKT0_wrRgPD58ICwuLTs6XyMrJyp-CjAxMjM0NTY3ODk=
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('BASE64 (URL-safe)', "Thomas Engel", ["base64"], context)

    def run(self, text):
        import base64
        return base64.urlsafe_b64encode(text.encode('utf-8', errors="surrogateescape"))\
            .decode('utf-8', errors="surrogateescape")
