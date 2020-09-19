from dpp.core.plugin import HasherPlugin

class Plugin(HasherPlugin):
    """
    Hashes a string using SHA224.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            c4e1543ec474c3f9c4ef2871d598 \\
            8deac56bcc84cb02592d2ad8d784
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('SHA224', "Thomas Engel", ["hashlib"], context)

    def run(self, text):
        import hashlib
        return hashlib.sha224(text.encode('utf-8', errors='surrogateescape')).hexdigest()
