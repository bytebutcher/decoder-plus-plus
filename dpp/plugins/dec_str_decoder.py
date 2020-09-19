from dpp.core.plugin import DecoderPlugin

class Plugin(DecoderPlugin):
    """
    Decodes a string of comma separated decimals to its character representation.

    Example:

        Input:
            97,98,99,100,101,102,103,104,\\
            105,106,107,108,109,110,111,112,\\
            ...
            10,48,49,50,51,52,53,54,\\
            55,56,57

        Output:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('DEC (str)', "Thomas Engel", [], context)

    def run(self, text):
        return "".join(chr(int(c)) for c in text.split(","))
