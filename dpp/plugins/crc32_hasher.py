from dpp.core.plugin import HasherPlugin

class Plugin(HasherPlugin):
    """
    Hashes a string using CRC32.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            0x4d9dcc47
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('CRC32', "Thomas Engel", ["zlib"], context)

    def run(self, text):
        import zlib
        return hex(zlib.crc32(text.encode('utf-8', errors='surrogateescape')))
