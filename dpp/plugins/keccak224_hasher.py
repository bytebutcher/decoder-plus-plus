from dpp.core.plugin import HasherPlugin

class Plugin(HasherPlugin):
    """
    Hashes a string using KECCAK 224.

    Example:

        Input:
            abcdefghijklmnopqrstuvwxyz
            ^°!"§$%&/()=?´`<>| ,.-;:_#+'*~
            0123456789

        Output:
            dbf87ddd2f01eb7f172b18d94baf83ace62cb71c6ec2b5c82bdf2bab
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('KECCAK 224', "Thomas Engel", ["cryptodome"], context)

    def run(self, text):
        from Crypto.Hash import keccak
        return keccak.new(digest_bits=224, data=text.encode('utf-8', errors='surrogateescape')).hexdigest()
