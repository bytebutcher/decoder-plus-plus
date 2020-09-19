from dpp.core.plugin import HasherPlugin

class Plugin(HasherPlugin):
    """
    Hashes a string using KECCAK 224.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            dbf87ddd2f01eb7f172b18d94baf83ace62cb71c6ec2b5c82bdf2bab
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('KECCAK 224', "Thomas Engel", ["_pysha3"], context)

    def run(self, text):
        import _pysha3
        return _pysha3.keccak_224(text.encode('utf-8', errors='surrogateescape')).hexdigest()
