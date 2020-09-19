from dpp.core.plugin import EncoderPlugin

class Plugin(EncoderPlugin):
    """
    Replaces a letter with the 13th letter after it.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            nopqrstuvwxyzabcdefghijklm
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('ROT13', "Robin Krumnow", ["codecs"], context)

    def run(self, text):
        import codecs
        return codecs.encode(text, 'rot_13')
