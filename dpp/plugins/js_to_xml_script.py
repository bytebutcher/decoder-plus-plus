from dpp.core.plugin import ScriptPlugin


class Plugin(ScriptPlugin):
    """
    Transforms valid JSON- into XML-structure.
    """

    def __init__(self, context: 'core.context.Context'):
        # Name, Author, Dependencies
        super().__init__('JS to XML', "Thomas Engel", ["json2xml"], context)

    def run(self, text):
        from json2xml import json2xml, readfromstring
        return json2xml.Json2xml(readfromstring(text)).to_xml()
