from dpp.core.plugin import HasherPlugin

class Plugin(HasherPlugin):
    """
    Hashes a string using SHA3 512.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            82ca87f576cadb05d4c911f36c98ed2735f45cad359d6ef5f6d544f5a3210e3e \
            cf080be15e539e23c15e2eb23054677d8a015ee56be2d9673c9f187d290906ed
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('SHA3 512', "Thomas Engel", ["_pysha3"], context)

    def run(self, text):
        import _pysha3
        return _pysha3.sha3_512(text.encode('utf-8', errors='surrogateescape')).hexdigest()
