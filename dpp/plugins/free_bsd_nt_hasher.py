from dpp.core.plugin import HasherPlugin

class Plugin(HasherPlugin):
    """
    Hashes a string using FreeBSD NT.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            $3$$d6a56df12312ac8f5e208d75164cdcb2
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('FreeBSD NT', "Thomas Engel", ["passlib"], context)

    def run(self, text):
        from passlib.hash import bsd_nthash
        return bsd_nthash.encrypt(text.encode('utf-8', errors='surrogateescape'))
