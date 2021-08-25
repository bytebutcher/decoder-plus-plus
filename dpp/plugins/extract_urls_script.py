from dpp.core.plugin import ScriptPlugin
from os import linesep
from urlextract import URLExtract


class Plugin(ScriptPlugin):
    """
    Extracts URLs from the input string.
    """

    extractor = URLExtract()

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('Extract URLs', "Thomas Engel", ['urlextract'], context)

    def run(self, text):
        return linesep.join(self.extractor.find_urls(text))
