from dpp.core.plugin import ScriptPlugin


class Plugin(ScriptPlugin):
    """
    Escapes the input string.
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('Escape String', "Thomas Engel", [], context)

    def run(self, text):
        return repr(text)
