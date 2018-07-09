from core.plugin.abstract_plugin import AbstractPlugin
from core.command import Command

class Plugin(AbstractPlugin):

    def __init__(self, context):
        # Name, Type, Author, Dependencies
        super().__init__('HTML', Command.Type.DECODER, "Thomas Engel", ["html"])

    def run(self, text):
        import html
        return html.unescape(text)
