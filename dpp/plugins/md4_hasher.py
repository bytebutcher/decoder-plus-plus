from dpp.core.plugin import HasherPlugin

class Plugin(HasherPlugin):
    """
    Hashes a string using MD4.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            872e3f347295c197822d6dc7a6bbb94e
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('MD4', "Thomas Engel", ["Crypto"], context)

    def run(self, text):
        from Crypto.Hash import MD4
        return MD4.new(text.encode('utf-8', errors='surrogateescape')).hexdigest()
