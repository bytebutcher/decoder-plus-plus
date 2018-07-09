from core.plugin.abstract_plugin import AbstractPlugin
from core.command import Command

class Plugin(AbstractPlugin):

    def __init__(self, context):
        # Name, Type, Author, Dependencies
        super().__init__('HEX (int)', Command.Type.DECODER, "Thomas Engel", [])

    def run(self, text):
        return self._run_lines(text, lambda text_part: str(int(text_part, 16)))

