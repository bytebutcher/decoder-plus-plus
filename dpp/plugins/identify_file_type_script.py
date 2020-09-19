from dpp.core.plugin import ScriptPlugin


class Plugin(ScriptPlugin):
    """
    Detects the file type of the input text based on magic bytes.
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('Identify File Type', "Thomas Engel", ["filemagic"], context)

    def _detect_magic_bytes(self, input):
        import magic
        with magic.Magic() as m:
            return m.id_buffer(input)

    def run(self, input):
        return self._detect_magic_bytes(input)