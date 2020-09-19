from dpp.core.plugin import ScriptPlugin


class Plugin(ScriptPlugin):
    """
    This little beautifier will reformat and re-indent bookmarklets, ugly JavaScript, unpack scripts packed by
    Dean Edward’s popular packer, as well as partly deobfuscate scripts processed by the npm package
    javascript-obfuscator.
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('JS Beautify', "Thomas Engel", ["jsbeautifier"], context)

    def run(self, text):
        import jsbeautifier
        return jsbeautifier.beautify(text)
