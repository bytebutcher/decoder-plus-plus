from dpp.core.plugin import HasherPlugin

class Plugin(HasherPlugin):
    """
    Hashes a string using MD2.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            f5299f20b7bf89a89bc575f1dcea358a
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('MD2', "Thomas Engel", ["Crypto"], context)

    def run(self, text):
        from Crypto.Hash import MD2
        return MD2.new(text.encode('utf-8', errors='surrogateescape')).hexdigest()
