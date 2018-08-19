from core.plugin.plugin import DecoderPlugin

class Plugin(DecoderPlugin):
    """
    Decodes a URL.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz%0A%21%22%C2%A7%24%25%26/%28%29%3D%3F%C2%B4%60%0A0123456789%0A
        Output:
            abcdefghijklmnopqrstuvwxyz
            !&quot;§$%&amp;/()=?´`
            0123456789
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('URL+', "Thomas Engel", ["urllib"])

    def run(self, text):
        import urllib.parse
        return urllib.parse.unquote_plus(text)
