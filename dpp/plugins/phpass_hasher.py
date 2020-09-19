from dpp.core.plugin import HasherPlugin

class Plugin(HasherPlugin):
    """
    Hashes a string using PHPass.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            $P$HaRrI8HUeMkKf2xmFE6mUg/NUtBEzp/
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('PHPass', "Thomas Engel", ["passlib"], context)

    def run(self, text):
        from passlib.hash import phpass
        return phpass.encrypt(text.encode('utf-8', errors='surrogateescape'))
