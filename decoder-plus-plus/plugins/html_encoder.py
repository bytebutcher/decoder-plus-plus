from core.plugin.plugin import EncoderPlugin

class Plugin(EncoderPlugin):
    """
    Encodes a string to it's html representation.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            !"§$%&/()=?´`
            0123456789
        Output:
            abcdefghijklmnopqrstuvwxyz
            !&quot;§$%&amp;/()=?´`
            0123456789
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('HTML', "Thomas Engel", ["html"])

    def run(self, text):
        import html
        return html.escape(text)
