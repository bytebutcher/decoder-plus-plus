from dpp.core.plugin import ScriptPlugin


class Plugin(ScriptPlugin):
    """
    Minifies Cascading Style Sheets (CSS) Code.
    """

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('CSS Minify', "Thomas Engel", ["css-html-js-minify"], context)

    def run(self, text):
        from css_html_js_minify import css_minify
        return css_minify(text)
