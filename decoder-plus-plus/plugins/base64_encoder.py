from core.plugin.plugin import EncoderPlugin

class Plugin(EncoderPlugin):
    """
    Encodes a string to base64.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            0123456789
        Output:
            YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXoKMDEyMzQ1Njc4OQ===
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('BASE64', "Thomas Engel", ["base64"])

    def run(self, text):
        import base64
        return base64.b64encode(text.encode('utf-8', errors="surrogateescape")).decode('utf-8', errors="surrogateescape")
