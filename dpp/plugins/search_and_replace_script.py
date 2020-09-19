import re

import qtawesome
from PyQt5.QtWidgets import QDialog

from dpp.core.exception import AbortedException
from dpp.core.plugin import ScriptPlugin, PluginConfig
from dpp.ui.dialog.plugin_config_dialog import PluginConfigDialog


class Plugin(ScriptPlugin):
    """
    Opens a search-and-replace dialog which supports Match-Case and Regular Expressions.
    """

    class Option(object):
        SearchTerm = PluginConfig.Option.Label("search_term", "Search:")
        ReplaceTerm = PluginConfig.Option.Label("replace_term", "Replace:")
        ShouldMatchCase = PluginConfig.Option.Label("should_match_case", "Match Case")
        IsRegex = PluginConfig.Option.Label("is_regex", "Regex")

    class SearchAndReplaceCodec:

        def run(self, config, input):
            is_regex = config.get(Plugin.Option.IsRegex).value
            should_match_case = config.get(Plugin.Option.ShouldMatchCase).value
            search_term = config.get(Plugin.Option.SearchTerm).value
            replace_term = config.get(Plugin.Option.ReplaceTerm).value
            if is_regex and should_match_case:
                return re.sub(search_term, replace_term, input, flags=re.IGNORECASE)
            elif is_regex:
                return re.sub(search_term, replace_term, input)
            elif should_match_case:
                return input.replace(search_term, replace_term)
            else:
                regexp = re.compile(re.escape(search_term), re.IGNORECASE)
                return regexp.sub(search_term, input)

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('Search & Replace', "Thomas Engel", [], context)
        self._codec = Plugin.SearchAndReplaceCodec()
        self._init_config()

    def _init_config(self):
        def _validate_search_term(config: PluginConfig, codec, input):
            if not config.get(Plugin.Option.SearchTerm).value:
                return "Search term should not be empty."

        self.config.add(PluginConfig.Option.String(
            label=Plugin.Option.SearchTerm,
            value="",
            description="the word or phrase to replace",
            is_required=True
        ), validator=_validate_search_term)
        self.config.add(PluginConfig.Option.String(
            label=Plugin.Option.ReplaceTerm,
            value="",
            description="the word or phrase used as replacement",
            is_required=True
        ))
        self.config.add(PluginConfig.Option.Boolean(
            label=Plugin.Option.ShouldMatchCase,
            value=True,
            description="defines whether the search term should match case",
            is_required=False
        ))
        self.config.add(PluginConfig.Option.Boolean(
            label=Plugin.Option.IsRegex,
            value=False,
            description="defines whether the search term is a regular expression",
            is_required=False
        ))
        self._dialog = None
        self._dialog_return_code = QDialog.Accepted

    def select(self, text: str):
        if not self._dialog:
            self._dialog = PluginConfigDialog(self._context, self.config.clone(), "Search & Replace", self._codec.run,
                                              qtawesome.icon("fa.search"))

        self._dialog.setInput(text)
        self._dialog_return_code = self._dialog.exec_()

        if self._dialog_return_code != QDialog.Accepted:
            # User clicked the Cancel-Button.
            raise AbortedException("Aborted")

        self.config.update(self._dialog.config)
        return self.run(text)

    def title(self):
        return "Search and Replace '{}' with '{}' using {}".format(
            self._get_search_term(), self._get_replace_term(), self._get_option_as_human_readable_string())

    def _get_option_as_human_readable_string(self):
        if self._should_match_case():
            return 'Match Case'
        elif self._is_regex():
            return 'Regular Expression'
        else:
            return 'Ignore Case'

    def _get_search_term(self):
        return self.config.get(Plugin.Option.SearchTerm).value

    def _get_replace_term(self):
        return self.config.get(Plugin.Option.ReplaceTerm).value

    def _should_match_case(self):
        return self.config.get(Plugin.Option.ShouldMatchCase).value

    def _is_regex(self):
        return self.config.get(Plugin.Option.IsRegex).value

    def run(self, text: str):
        return self._codec.run(self.config, text)
