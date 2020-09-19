from dpp.core.plugin import ScriptPlugin


class Plugin(ScriptPlugin):
    """
    Removes all whitespaces from the input text.
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('Remove Whitespaces', "Thomas Engel", [], context)

    def run(self, text):
        return text.replace(' ', '').replace('\t', '').replace('\n', '').replace('\r', '')