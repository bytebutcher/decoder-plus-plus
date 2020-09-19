from dpp.core.plugin import HasherPlugin

class Plugin(HasherPlugin):
    """
    Hashes a string using SHA3 384.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            4fa54dbfbdde8c191a64879a1bed6a062da45f53c82e7eb0fc59362e32f506cded9d17e69f881231b16395a259595c6b
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('SHA3 384', "Thomas Engel", ["_pysha3"], context)

    def run(self, text):
        import _pysha3
        return _pysha3.sha3_384(text.encode('utf-8', errors='surrogateescape')).hexdigest()
