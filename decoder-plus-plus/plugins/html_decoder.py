from core.plugin.plugin import DecoderPlugin

class Plugin(DecoderPlugin):
    """
    Decodes a html string.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            !&quot;§$%&amp;/()=?´`
            0123456789
        Output:
            abcdefghijklmnopqrstuvwxyz
            !"§$%&/()=?´`
            0123456789
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('HTML', "Thomas Engel", ["html"])

    def run(self, text):
        import html
        return html.unescape(text)
