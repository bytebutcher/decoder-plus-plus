from dpp.core.plugin import EncoderPlugin

class Plugin(EncoderPlugin):
    """
    Encodes a string to a hex string.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            6162636465666768696a6b6c6d6e6f70717273747576777 \\
            8797a0a5ec2b02122c2a72425262f28293d3fc2b4603c3e \\
            7c202c2e2d3b3a5f232b272a7e0a30313233343536373839
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('HEX (str)', "Thomas Engel", ["codecs"], context)

    def run(self, text):
        import codecs
        return codecs.encode(text.encode('utf-8', errors='surrogateescape'), 'hex').decode('utf-8', errors='surrogateescape')
