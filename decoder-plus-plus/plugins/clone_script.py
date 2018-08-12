from core.plugin.plugin import ScriptPlugin


class Plugin(ScriptPlugin):

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('Clone', "Thomas Engel", [])

    def run(self, text):
        return text
