from dpp.core.plugin import HasherPlugin

class Plugin(HasherPlugin):
    """
    Hashes a string using MD5.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            4384c8873a173210f11c30d6ae54baec
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('MD5', "Thomas Engel", ["hashlib"], context)

    def run(self, text):
        import hashlib
        return hashlib.md5(text.encode('utf-8', errors='surrogateescape')).hexdigest()
