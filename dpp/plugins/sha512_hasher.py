from dpp.core.plugin import HasherPlugin

class Plugin(HasherPlugin):
    """
    Hashes a string using SHA512.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            58cd501bee1ece7411a23b2e86bfb795b136f2aae5d8f94a59c551622d9a0d7e \\
            293a04a8584244eadf1f9bedd34cbcb7e99f7bdedaac56591f88bb282c5146cd

    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('SHA512', "Thomas Engel", ["hashlib"], context)

    def run(self, text):
        import hashlib
        return hashlib.sha512(text.encode('utf-8', errors='surrogateescape')).hexdigest()
