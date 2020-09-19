from dpp.core.plugin import HasherPlugin

class Plugin(HasherPlugin):
    """
    Hashes a string using KECCAK 384.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            2f1b4db7016471554160335867949a2d8a8bd68a002b0e0289f119ee25ab719e40ed2e8fc2f5604d8c4272ca3487cfe7
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('KECCAK 384', "Thomas Engel", ["_pysha3"], context)

    def run(self, text):
        import _pysha3
        return _pysha3.keccak_384(text.encode('utf-8', errors='surrogateescape')).hexdigest()
