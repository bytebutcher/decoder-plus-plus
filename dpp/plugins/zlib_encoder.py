from dpp.core.plugin import EncoderPlugin

class Plugin(EncoderPlugin):
    """
        Encodes a string using ZLib.

        Example:

            Input:
                abcdefghijklmnopqrstuvwxyz
                ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
                0123456789

            Output:
                [bytes]
        """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('Zlib', "Thomas Engel", ["zlib"], context)

    def run(self, text):
        import zlib
        return zlib.compress(text.encode('utf-8', errors='surrogateescape')).decode('utf-8', errors='surrogateescape')
