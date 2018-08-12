from core.plugin.abstract_plugin import HasherPlugin

class Plugin(HasherPlugin):

    def __init__(self, context):
        # Name, Type, Author, Dependencies
        super().__init__('RIPEMD160', "Tim Menapace", ["hashlib"])

    def run(self, text):
        import hashlib
        return hashlib.new('ripemd160',text.encode('utf-8')).hexdigest()