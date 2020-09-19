from dpp.core.plugin import DecoderPlugin

class Plugin(DecoderPlugin):
    """
    Decodes a HTML string.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!&quot;§$%&amp;/()=?´`&lt;&gt;| ,.-;:_#+&#x27;*~
            0123456789

        Output:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('HTML', "Thomas Engel", ["html"], context)

    def run(self, text):
        import html
        return html.unescape(text)

    def can_decode_input(self, input):
        """
        Checks whether input can be decoded. When decoded input does not match the initial input some decoding must
        have happened so we return True.
        """
        if input:
            try:
                return self.run(input) != input
            except:
                return False
        return False
