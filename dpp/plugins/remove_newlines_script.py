from dpp.core.plugin import ScriptPlugin


class Plugin(ScriptPlugin):
    """
    Removes all newlines from the input text.
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('Remove Newlines', "Thomas Engel", [], context)

    def run(self, text):
        return text.replace('\n', '').replace('\r', '')