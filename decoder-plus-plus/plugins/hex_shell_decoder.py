import re

from core.plugin.plugin import DecoderPlugin

class Plugin(DecoderPlugin):
    """
    Decodes an hex shell code.

    Example:

        Input:
            \x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c \
            \x6d\x6e\x6f\x70\x71\x72\x73\x74\x75\x76\x77\x78 \
            \x79\x7a\x0a\x30\x31\x32\x33\x34\x35\x36\x37\x38 \
            \x39
        Output:
            abcdefghijklmnopqrstuvwxyz
            0123456789
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('HEX (shell)', "Thomas Engel", ["codecs"])

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
        if len(input) % 4 == 0:
            hex = re.search(r'^(\\x|\\X)[a-fA-F0-9]+$', input)
            if hex:
                return True
        return False