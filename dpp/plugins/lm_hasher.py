from dpp.core.plugin import HasherPlugin

class Plugin(HasherPlugin):
    """
    Hashes a string using LanManager.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            e0c510199cc66abd8c51ec214bebdea1
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('LM', "Thomas Engel", ["passlib"], context)

    def run(self, text):
        from passlib.hash import lmhash
        return lmhash.encrypt(text.encode('utf-8', errors='surrogateescape'))
