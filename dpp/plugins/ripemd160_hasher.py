from dpp.core.plugin import HasherPlugin

class Plugin(HasherPlugin):
    """
    Hashes a string using RIPEMD160.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            1b63bae30eb8be665459c3f2021293811ac2d63b
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('RIPEMD160', "Tim Menapace", ["hashlib"], context)

    def run(self, text):
        import hashlib
        return hashlib.new('ripemd160',text.encode('utf-8', errors='surrogateescape')).hexdigest()