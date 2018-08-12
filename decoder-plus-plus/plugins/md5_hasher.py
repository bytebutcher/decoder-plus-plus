from core.plugin.abstract_plugin import HasherPlugin

class Plugin(HasherPlugin):

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('MD5', "Thomas Engel", ["hashlib"])

    def run(self, text):
        import hashlib
        return hashlib.md5(text.encode('utf-8')).hexdigest()
