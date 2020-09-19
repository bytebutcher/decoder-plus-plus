from dpp.core.plugin import ScriptPlugin


class Plugin(ScriptPlugin):
    """
    This plugin will reformat HTML.
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('HTML Beautify', "Thomas Engel", ["lxml"], context)

    def run(self, text):
        from lxml import etree, html
        document_root = html.fromstring(text)
        return etree.tostring(document_root, encoding='unicode', pretty_print=True)
