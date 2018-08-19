from core.plugin.plugin import EncoderPlugin

class Plugin(EncoderPlugin):
    """
    Encodes a string to a hex string.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz%0A%21%22%C2%A7%24%25%26/%28%29%3D%3F%C2%B4%60%0A0123456789%0A
        Output:
            6162636465666768696a6b6c6d6e6f70717273747576777 \\
            8797a0a5ec2b02122c2a72425262f28293d3fc2b4603c3e \\
            7c202c2e2d3b3a5f232b272a7e0a30313233343536373839
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('HEX (str)', "Thomas Engel", ["codecs"])

    def safe_name(self):
        return "hex_str"

    def run(self, text):
        import codecs
        return codecs.encode(text.encode('utf-8', errors='surrogateescape'), 'hex').decode('utf-8')
