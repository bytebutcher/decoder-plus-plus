from dpp.core.plugin import HasherPlugin

class Plugin(HasherPlugin):
    """
    Hashes a string using SHA3 224.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            0049b8b6c811930a8873b7b14bd5191e56931661626e89248ee476e9
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('SHA3 224', "Thomas Engel", ["_pysha3"], context)

    def run(self, text):
        import _pysha3
        return _pysha3.sha3_224(text.encode('utf-8', errors='surrogateescape')).hexdigest()
