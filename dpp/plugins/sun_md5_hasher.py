from dpp.core.plugin import HasherPlugin

class Plugin(HasherPlugin):
    """
    Hashes a string using Sun MD5.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            $md5,rounds=34000$l3zQgEcw$$WilWKupRZIxRHlKHC1azb1
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('Sun-MD5', "Thomas Engel", ["passlib"], context)

    def run(self, text):
        from passlib.hash import sun_md5_crypt
        return sun_md5_crypt.encrypt(text.encode('utf-8', errors='surrogateescape'))
