from dpp.core.plugin import DecoderPlugin

class Plugin(DecoderPlugin):
    """
    Replaces a letter with the 13th letter after it.

    Example:

        Input:
            nopqrstuvwxyzabcdefghijklm
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('ROT13', "Robin Krumnow", ["codecs"], context)

    def run(self, text):
        import codecs
        return codecs.encode(text, 'rot_13')
