from dpp.core.plugin import EncoderPlugin

class Plugin(EncoderPlugin):
    """
    Encodes a string to a comma separated decimal string.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            97,98,99,100,101,102,103,104,\\
            105,106,107,108,109,110,111,112,\\
            ...
            10,48,49,50,51,52,53,54,\\
            55,56,57
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('DEC (str)', "Thomas Engel", [], context)

    def run(self, text):
        return ",".join(str(ord(c)) for c in text)
