from dpp.core.plugin import ScriptPlugin


class Plugin(ScriptPlugin):
    """
    Clones the input into another frame.
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('Clone', "Thomas Engel", [], context)

    def run(self, text):
        return text
