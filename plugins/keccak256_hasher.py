from core.plugin.abstract_plugin import AbstractPlugin
from core.command import Command

class Plugin(AbstractPlugin):

    def __init__(self, context):
        # Name, Type, Author, Dependencies
        super().__init__('KECCAK_256', Command.Type.HASHER, "Tim Menapace", ["sha3"])

    def run(self, text):
        import sha3
        return sha3.keccak_256(text.encode('utf-8')).hexdigest()