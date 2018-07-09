from core.plugin.abstract_plugin import AbstractPlugin
from core.command import Command

class Plugin(AbstractPlugin):

    def __init__(self, context):
        # Name, Type, Author, Dependencies
        super().__init__('URL+', Command.Type.DECODER, "Thomas Engel", ["urllib"])

    def run(self, text):
        import urllib.parse
        return urllib.parse.unquote_plus(text)
