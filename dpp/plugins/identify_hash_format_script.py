from dpp.core.plugin import ScriptPlugin


class Plugin(ScriptPlugin):
    """
    Identifies the hash format of the input text based on structure.
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('Identify Data Format', "Thomas Engel", ["hashid"], context)

    def _detect_hash_format(self, input):
        from hashid import HashID
        return "\n".join(map(str, HashID().identifyHash(input)))

    def run(self, input):
        return self._detect_hash_format(input)
