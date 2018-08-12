from core.plugin.plugin import HasherPlugin

class Plugin(HasherPlugin):

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('SHA224', "Thomas Engel", ["hashlib"])

    def run(self, text):
        import hashlib
        return hashlib.sha224(text.encode('utf-8')).hexdigest()
