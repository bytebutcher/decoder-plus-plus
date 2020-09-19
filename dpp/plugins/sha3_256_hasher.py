from dpp.core.plugin import HasherPlugin

class Plugin(HasherPlugin):
    """
    Hashes a string using SHA3 256.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            15fd91bcfe6b705f56b436766dcd01e2d3bda8156154c80a6e030f2515956ff8
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('SHA3 256', "Thomas Engel", ["_pysha3"], context)

    def run(self, text):
        import _pysha3
        return _pysha3.sha3_256(text.encode('utf-8', errors='surrogateescape')).hexdigest()
