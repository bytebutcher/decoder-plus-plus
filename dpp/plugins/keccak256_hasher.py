from dpp.core.plugin import HasherPlugin

class Plugin(HasherPlugin):
    """
    Hashes a string using KECCAK 256.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            53205b3c714c875f1d892d9ec3e7e9194f908d5b61a744d08c32f1f0a7c94c6e
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('KECCAK 256', "Tim Menapace", ["_pysha3"], context)

    def run(self, text):
        import _pysha3
        return _pysha3.keccak_256(text.encode('utf-8', errors='surrogateescape')).hexdigest()