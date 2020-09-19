from dpp.core.plugin import EncoderPlugin

class Plugin(EncoderPlugin):
    """
    Encodes a string to HTML.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            abcdefghijklmnopqrstuvwxyz
            ^°!&quot;§$%&amp;/()=?´`&lt;&gt;| ,.-;:_#+&#x27;*~
            0123456789
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('HTML', "Thomas Engel", ["html"], context)

    def run(self, text):
        import html
        return html.escape(text)
