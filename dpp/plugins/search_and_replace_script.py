# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of Decoder++
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import re

from dpp.core.exceptions import ValidationError
from dpp.core.icons import Icon
from dpp.core.plugin import ScriptPlugin, PluginConfig
from dpp.core.plugin.config import Label
from dpp.core.plugin.config.options import String, Boolean


class Plugin(ScriptPlugin):
    """
    Opens a search-and-replace dialog which supports Match-Case and Regular Expressions.
    """

    class Option(object):
        SearchTerm = Label("search_term", "Search:")
        ReplaceTerm = Label("replace_term", "Replace:")
        ShouldMatchCase = Label("should_match_case", "Match Case")
        IsRegex = Label("is_regex", "Regex")

    class SearchAndReplaceCodec:

        def run(self, config, input_text):
            is_regex = config.value(Plugin.Option.IsRegex)
            should_match_case = config.value(Plugin.Option.ShouldMatchCase)
            search_term = config.value(Plugin.Option.SearchTerm)
            replace_term = config.value(Plugin.Option.ReplaceTerm)
            if is_regex and should_match_case:
                return re.sub(search_term, replace_term, input_text, flags=re.IGNORECASE)
            elif is_regex:
                return re.sub(search_term, replace_term, input_text)
            elif should_match_case:
                return input_text.replace(search_term, replace_term)
            else:
                regexp = re.compile(re.escape(search_term), re.IGNORECASE)
                return regexp.sub(search_term, input_text)

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies, Icon
        super().__init__('Search & Replace', "Thomas Engel", [], context, Icon.SEARCH)
        self._codec = Plugin.SearchAndReplaceCodec()
        self._init_config()

    def _init_config(self):
        def _validate_search_term(input_text: str):
            if not self.config.value(Plugin.Option.SearchTerm):
                raise ValidationError("Search term should not be empty.")

        self.config.add(String(
            label=Plugin.Option.SearchTerm,
            value="",
            description="the word or phrase to replace",
            is_required=True
        ), validator=_validate_search_term)
        self.config.add(String(
            label=Plugin.Option.ReplaceTerm,
            value="",
            description="the word or phrase used as replacement",
            is_required=True
        ))
        self.config.add(Boolean(
            label=Plugin.Option.ShouldMatchCase,
            value=True,
            description="defines whether the search term should match case",
            is_required=False
        ))
        self.config.add(Boolean(
            label=Plugin.Option.IsRegex,
            value=False,
            description="defines whether the search term is a regular expression",
            is_required=False
        ))

    @property
    def title(self) -> str:
        return "Search and Replace '{}' with '{}' using {}".format(
            self._get_search_term(), self._get_replace_term(), self._get_option_as_human_readable_string())

    def _get_option_as_human_readable_string(self) -> str:
        if self._should_match_case():
            return 'Match Case'
        elif self._is_regex():
            return 'Regular Expression'
        else:
            return 'Ignore Case'

    def _get_search_term(self) -> str:
        return self.config.value(Plugin.Option.SearchTerm)

    def _get_replace_term(self) -> str:
        return self.config.value(Plugin.Option.ReplaceTerm)

    def _should_match_case(self) -> bool:
        return self.config.value(Plugin.Option.ShouldMatchCase)

    def _is_regex(self) -> bool:
        return self.config.value(Plugin.Option.IsRegex)

    def run(self, input_text: str) -> str:
        return self._codec.run(self.config, input_text)
