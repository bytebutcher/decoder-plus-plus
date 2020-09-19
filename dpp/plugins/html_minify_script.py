from dpp.core.plugin import ScriptPlugin


class Plugin(ScriptPlugin):
    """
    Minifies HTML Code.
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('HTML Minify', "Thomas Engel", ["css-html-js-minify"], context)

    def run(self, text):
        from css_html_js_minify import html_minify
        return html_minify(text)
