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
            0ECJPC% CC3DVED5QDO$D/3EHFE QEA%ET4F3GF:D1PROM84GROSP4A$4L35JX7TROL7CL+7134V$5.L7A1CMK5XG5/C1*96DL6WW66:6C1
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('BASE45', "Thomas Engel", ["base45"], context)

    def run(self, text):
        import base45
        return base45.b45encode(text.encode('utf-8', errors="surrogateescape")).decode('utf-8', errors="surrogateescape")
