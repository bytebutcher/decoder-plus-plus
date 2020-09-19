from dpp.core.plugin import HasherPlugin

class Plugin(HasherPlugin):
    """
    Hashes a string using SHA256.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            0a4035197aa3b94d8ee2ff7d5b286636 \\
            f6264f6c96ffccf3c4b777a8fb9be674
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('SHA256', "Thomas Engel", ["hashlib"], context)

    def run(self, text):
        import hashlib
        return hashlib.sha256(text.encode('utf-8', errors='surrogateescape')).hexdigest()
