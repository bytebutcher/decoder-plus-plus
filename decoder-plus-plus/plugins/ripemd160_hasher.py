from core.plugin.abstract_plugin import AbstractPlugin
from core.command import Command

class Plugin(AbstractPlugin):

    def __init__(self, context):
        # Name, Type, Author, Dependencies
        super().__init__('RIPEMD160', Command.Type.HASHER, "Tim Menapace", ["hashlib"])

    def run(self, text):
        import hashlib
        return hashlib.new('ripemd160',text.encode('utf-8')).hexdigest()