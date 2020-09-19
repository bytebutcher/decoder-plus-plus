from dpp.core.plugin import DecoderPlugin

class Plugin(DecoderPlugin):
    """
    Decodes a URL. Plus-signs are decoded to spaces.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz \\
            %0A%5E%C2%B0%21%22%C2%A7%24%25%26/%28%29%3D%3F%C2%B4%60%3C%3E%7C+%2C.-%3B%3A_%23%2B%27%2A%7E%0A \\
            0123456789

        Output:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('URL+', "Thomas Engel", ["urllib"], context)

    def run(self, text):
        import urllib.parse
        return urllib.parse.unquote_plus(text)

    def can_decode_input(self, input):
        """
        Checks whether input can be decoded. When the input contains no plus sign we return False.
        When decoded input does not match the initial input some decoding must have happened so we return True.
        """
        if input and "+" in input:
            try:
                return self.run(input) != input.replace('+', ' ')
            except:
                return False
        return False
