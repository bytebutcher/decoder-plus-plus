from core.plugin.plugin import EncoderPlugin

class Plugin(EncoderPlugin):
    """
    Encodes a string to a hex string.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            0123456789
        Output:
            6162636465666768696a6b6c6d6e6f707172737475767778797a0a30313233343536373839
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('HEX (str)', "Thomas Engel", ["codecs"])

    def run(self, text):
        import codecs
        return codecs.encode(text.encode('utf-8', errors='surrogateescape'), 'hex').decode('utf-8')
