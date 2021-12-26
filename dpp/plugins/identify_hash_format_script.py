from dpp.core.plugin import IdentifyPlugin


class Plugin(IdentifyPlugin):
    """
    Identifies the hash format of the input text based on structure.
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('Identify Hash Format', "Thomas Engel", ["hashid"], context)

    def _detect_hash_format(self, input):
        from hashid import HashID
        return "\n".join(sorted([item.name for item in HashID().identifyHash(input)]))

    def run(self, input):
        return self._detect_hash_format(input)
