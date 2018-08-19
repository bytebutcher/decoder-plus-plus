from core.plugin.plugin import DecoderPlugin

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
        super().__init__('HTML', "Thomas Engel", ["html"])

    def run(self, text):
        import html
        return html.unescape(text)
