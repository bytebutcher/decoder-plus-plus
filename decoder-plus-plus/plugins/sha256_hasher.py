from core.plugin.abstract_plugin import HasherPlugin

class Plugin(HasherPlugin):

    def __init__(self, context):
        # Name, Type, Author, Dependencies
        super().__init__('SHA256', "Thomas Engel", ["hashlib"])

    def run(self, text):
        import hashlib
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
