from core.plugin.abstract_plugin import HasherPlugin

class Plugin(HasherPlugin):

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('KECCAK_256', "Tim Menapace", ["sha3"])

    def run(self, text):
        import sha3
        return sha3.keccak_256(text.encode('utf-8')).hexdigest()