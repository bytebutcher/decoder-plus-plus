from core.plugin.plugin import EncoderPlugin

class Plugin(EncoderPlugin):
    """
    Encodes to hex shell code.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            0123456789
        Output:
            \\x61\\x62\\x63\\x64\\x65\\x66\\x67\\x68\\x69\\x6a\\x6b\\x6c\\x6d\\x6e\\x6f\\x70 \\
            \\x71\\x72\\x73\\x74\\x75\\x76\\x77\\x78\\x79\\x7a\\x0a\\x30\\x31\\x32\\x33\\x34 \\
            \\x35\\x36\\x37\\x38\\x39
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('HEX (shell)', "Thomas Engel", ["codecs"])

    def run(self, text):
        if text:
            import codecs
            output = codecs.encode(text.encode('utf-8', errors='surrogateescape'), 'hex').decode('utf-8', errors='surrogateescape')
            return "\\x" + "\\x".join([i+j for i, j in zip(output[::2], output[1::2])])
        else:
            return ""
