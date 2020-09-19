from dpp.core.plugin import ScriptPlugin


class Plugin(ScriptPlugin):
    """
    Transforms a hex string from little to big endian vice versa.

    Example:

        Input:
            0002000A

        Output:
            0A000200
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('Little/Big Endian', "Thomas Engel", [], context)

    def title(self):
        return "Little/Big Endian Transform"

    def run(self, text):
        return ''.join(list(reversed(self._chunk_string(text, 2))))

    def _chunk_string(self, string, length):
        return [string[0 + i:length + i] for i in range(0, len(string), length)]