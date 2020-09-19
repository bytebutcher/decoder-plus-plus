from dpp.core.plugin import HasherPlugin

class Plugin(HasherPlugin):
    """
    Hashes a string using KECCAK 512.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            e7eb5bc85e3d05ccab9863189ce1a34ef2a3feda8ce633b690dd133242a43e90 \
            44bd36c27cb30d66a5eef8b4cb917c609f6983e2c2b8625c0aedb3f87f364172
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('KECCAK 512', "Thomas Engel", ["_pysha3"], context)

    def run(self, text):
        import _pysha3
        return _pysha3.keccak_512(text.encode('utf-8', errors='surrogateescape')).hexdigest()
