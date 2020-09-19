from dpp.core.plugin import DecoderPlugin

class Plugin(DecoderPlugin):
    """
    Decodes JSON Web Tokens.

    Example:

        Input:
            eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzb21lIjoicGF5bG9hZCJ9.4twFt5NiznN84AWoo1d7KO1T_yoc0Z6XOpOVswacPZg

        Output:
            {'some': 'payload'}
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('JWT', "Thomas Engel", ["jwt"], context)

    def run(self, text):
        import jwt
        return str(jwt.decode(text.encode('utf-8', errors='surrogateescape'), verify=False))

    def can_decode_input(self, input):
        if input and input.startswith("ey"):
            try:
                self.run(input)
                return True
            except:
                pass
        return False
