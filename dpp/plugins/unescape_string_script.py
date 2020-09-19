from dpp.core.plugin import ScriptPlugin


class Plugin(ScriptPlugin):
    """
    Unescapes the input string.
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('Unescape String', "Thomas Engel", [], context)

    def run(self, text):
        return text.encode('utf-8').decode('unicode_escape')
