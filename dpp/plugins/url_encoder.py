from dpp.core.plugin import EncoderPlugin

class Plugin(EncoderPlugin):
    """
    Encodes a string to an URL.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            abcdefghijklmnopqrstuvwxyz \\
            %0A%5E%C2%B0%21%22%C2%A7%24%25%26/%28%29%3D%3F%C2%B4%60%3C%3E%7C%20%2C.-%3B%3A_%23%2B%27%2A%7E%0A \\
            0123456789
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('URL', "Thomas Engel", ["urllib"], context)

    def run(self, text):
        import urllib.parse
        return urllib.parse.quote(text.encode('utf-8', errors='surrogateescape'))
