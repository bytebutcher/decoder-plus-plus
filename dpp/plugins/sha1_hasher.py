from dpp.core.plugin import HasherPlugin

class Plugin(HasherPlugin):
    """
    Hashes a string using SHA1.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            518d5653e6c74547aa62b376c953be024ea3c1d3
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('SHA1', "Thomas Engel", ["hashlib"], context)

    def run(self, text):
        import hashlib
        return hashlib.sha1(text.encode('utf-8', errors='surrogateescape')).hexdigest()
