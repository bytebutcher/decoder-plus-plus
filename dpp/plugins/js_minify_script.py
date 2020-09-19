from dpp.core.plugin import ScriptPlugin


class Plugin(ScriptPlugin):
    """
    Minifies Java Script Code.
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('JS Minify', "Thomas Engel", ["css-html-js-minify"], context)

    def run(self, text):
        from css_html_js_minify import js_minify
        return js_minify(text)
