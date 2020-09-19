import re

from dpp.core.plugin import DecoderPlugin

class Plugin(DecoderPlugin):
    """
    Decodes a hex shell code.

    Example:

        Input:
            \\x61\\x62\\x63\\x64\\x65\\x66\\x67\\x68\\x69\\x6a\\x6b\\x6c\\x6d\\x6e \\
            \\x6f\\x70\\x71\\x72\\x73\\x74\\x75\\x76\\x77\\x78\\x79\\x7a\\x0a\\x5e \\
            \\xc2\\xb0\\x21\\x22\\xc2\\xa7\\x24\\x25\\x26\\x2f\\x28\\x29\\x3d\\x3f \\
            \\xc2\\xb4\\x60\\x3c\\x3e\\x7c\\x20\\x2c\\x2e\\x2d\\x3b\\x3a\\x5f\\x23 \\
            \\x2b\\x27\\x2a\\x7e\\x0a\\x30\\x31\\x32\\x33\\x34\\x35\\x36\\x37\\x38 \\
            \\x39

        Output:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('HEX (shell)', "Thomas Engel", ["codecs"], context)

    def run(self, text):
        if text:
            import codecs
            import re
            output = text
            for hex_code in set(sorted(re.findall(r'\\[Xx][0-9a-fA-F][0-9a-fA-F]', text))):
                try:
                    output = output.replace(hex_code, codecs.decode(hex_code[-2:], 'hex').decode('utf-8', errors='surrogateescape'))
                except:
                    pass
            return output
        else:
            return ""

    def can_decode_input(self, input):
        contains_hex = re.findall(r'\\[Xx][0-9a-fA-F][0-9a-fA-F]', input)
        if contains_hex:
            return True
        return False
