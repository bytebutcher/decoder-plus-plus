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
import os
import re

from dpp.core.icons import Icon
from dpp.core.plugin import ScriptPlugin, PluginConfig
from dpp.core.plugin.config import Label
from dpp.core.plugin.config.options import String, Boolean


class Plugin(ScriptPlugin):
    """
    Opens a dialog to filter text by certain conditions.
    """

    class Option(object):
        Filter_Term = Label("filter_term", "Filter:")
        Should_Match_Case = Label("should_match_case", "Match Case")
        Should_Invert_Match = Label("should_invert_match", "Invert Lines")
        Is_Regex = Label("is_regex", "Regex")

    class FilterCodec:

        def run(self, config: PluginConfig, text: str):
            lines = []
            filter_term = config.value(Plugin.Option.Filter_Term)
            is_regex = config.value(Plugin.Option.Is_Regex)
            should_match_case = config.value(Plugin.Option.Should_Match_Case)
            for text_line in text.splitlines():
                try:
                    if self._should_filter(text_line, config):
                        if is_regex and should_match_case:
                            match = re.match(filter_term, text_line)
                            lines.append(match.group(0))
                        elif is_regex:
                            match = re.match(filter_term, text_line, flags=re.IGNORECASE)
                            lines.append(match.group(0))
                        else:
                            lines.append(text_line)
                except Exception as e:
                    # Ignore exceptions - most likely an error in the regex filter string
                    pass
            return os.linesep.join(lines)

        def _should_filter(self, text_line: str, config: PluginConfig):
            filter_term = config.value(Plugin.Option.Filter_Term)
            is_regex = config.value(Plugin.Option.Is_Regex)
            should_match_case = config.value(Plugin.Option.Should_Match_Case)
            should_invert_match = config.value(Plugin.Option.Should_Invert_Match)
            if is_regex and should_match_case:
                result = re.match(filter_term, text_line, flags=re.IGNORECASE) is not None
            elif is_regex:
                result = re.match(filter_term, text_line) is not None
            elif should_match_case:
                result = filter_term in text_line
            else:
                result = filter_term.lower() in text_line.lower()
            if should_invert_match:
                return not result
            else:
                return result

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies
        super().__init__('Filter Lines', "Thomas Engel", [], context, Icon.FILTER)
        self._context = context
        self._codec = Plugin.FilterCodec()
        self.config.add(String(
            label=Plugin.Option.Filter_Term,
            value="",
            description="term to filter by",
            is_required=True
        ))
        self.config.add(Boolean(
            label=Plugin.Option.Should_Match_Case,
            value=True,
            description="defines whether filter should match case",
            is_required=False
        ))
        self.config.add(Boolean(
            label=Plugin.Option.Should_Invert_Match,
            value=False,
            description="defines whether filter should invert match",
            is_required=False
        ))
        self.config.add(Boolean(
            label=Plugin.Option.Is_Regex,
            value=False,
            description="defines whether filter term is a regex",
            is_required=False
        ))

    @property
    def title(self):
        return "Filter lines by '{}' using {}".format(
            self.config.value(Plugin.Option.Filter_Term), self._getOptionAsHumanReadableString())

    def _getOptionAsHumanReadableString(self):
        options = []
        if self.config.value(Plugin.Option.Should_Match_Case):
            options.append('Match Case')
        else:
            options.append('Ignore Case')
        if self.config.value(Plugin.Option.Is_Regex):
            options.append('Regular Expression')
        if self.config.value(Plugin.Option.Should_Invert_Match):
            options.append('Invert Match')

        return self._join_options_as_human_readable_string(options)

    def run(self, input_text: str) -> str:
        return self._codec.run(self.config, input_text)
