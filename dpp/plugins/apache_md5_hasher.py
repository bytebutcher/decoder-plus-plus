from dpp.core.plugin import HasherPlugin

class Plugin(HasherPlugin):
    """
    Hashes a string using Apache MD5.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            $apr1$l97celjJ$SaLNyFiJgatX5pHuQ5cNI0
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('Apache-MD5', "Thomas Engel", ["passlib"], context)

    def run(self, text):
        from passlib.hash import apr_md5_crypt
        return apr_md5_crypt.encrypt(text.encode('utf-8', errors='surrogateescape'))
