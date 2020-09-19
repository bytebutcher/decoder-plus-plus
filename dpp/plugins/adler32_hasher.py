from dpp.core.plugin import HasherPlugin

class Plugin(HasherPlugin):
    """
    Hashes a string using Adler-32.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            0xc713178c
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('Adler-32', "Thomas Engel", ["zlib"], context)

    def run(self, text):
        import zlib
        return hex(zlib.adler32(text.encode('utf-8', errors='surrogateescape')))
