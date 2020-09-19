import os
import re
import qtawesome

from PyQt5.QtWidgets import QDialog

from dpp.core.exception import AbortedException
from dpp.core.plugin import ScriptPlugin, PluginConfig
from dpp.ui.dialog.plugin_config_dialog import PluginConfigPreviewDialog


class Plugin(ScriptPlugin):
    """
    Opens a dialog to filter text by certain conditions.
    """

    class Option(object):
        Filter_Term = PluginConfig.Option.Label("filter_term", "Filter:")
        Should_Match_Case = PluginConfig.Option.Label("should_match_case", "Match Case")
        Should_Invert_Match = PluginConfig.Option.Label("should_invert_match", "Invert Lines")
        Is_Regex = PluginConfig.Option.Label("is_regex", "Regex")

    class FilterCodec:

        def run(self, config: PluginConfig, text: str):
            lines = []
            filter_term = config.get(Plugin.Option.Filter_Term).value
            is_regex = config.get(Plugin.Option.Is_Regex).value
            should_match_case = config.get(Plugin.Option.Should_Match_Case).value
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
            filter_term = config.get(Plugin.Option.Filter_Term).value
            is_regex = config.get(Plugin.Option.Is_Regex).value
            should_match_case = config.get(Plugin.Option.Should_Match_Case).value
            should_invert_match = config.get(Plugin.Option.Should_Invert_Match).value
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


    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('Filter Lines', "Thomas Engel", [], context)
        self._context = context
        self._logger = context.logger
        self._codec = Plugin.FilterCodec()
        self.config.add(PluginConfig.Option.String(
            label=Plugin.Option.Filter_Term,
            value="",
            description="term to filter by",
            is_required=True
        ))
        self.config.add(PluginConfig.Option.Boolean(
            label=Plugin.Option.Should_Match_Case,
            value=True,
            description="defines whether filter should match case",
            is_required=False
        ))
        self.config.add(PluginConfig.Option.Boolean(
            label=Plugin.Option.Should_Invert_Match,
            value=False,
            description="defines whether filter should invert match",
            is_required=False
        ))
        self.config.add(PluginConfig.Option.Boolean(
            label=Plugin.Option.Is_Regex,
            value=False,
            description="defines whether filter term is a regex",
            is_required=False
        ))
        self._dialog = None
        self._dialog_return_code = QDialog.Accepted

    def select(self, text: str):
        if not self._dialog:
            self._dialog = PluginConfigPreviewDialog(self._context, self.config.clone(), "Filter Lines",
                                                     self._codec.run, qtawesome.icon("fa.filter"))

        self._dialog.setInput(text)
        self._dialog_return_code = self._dialog.exec_()

        if self._dialog_return_code != QDialog.Accepted:
            # User clicked the Cancel-Button.
            raise AbortedException("Aborted")

        self.config.update(self._dialog.config)
        return self.run(text)

    def title(self):
        return "Filter lines by '{}' using {}".format(
            self.config.get(Plugin.Option.Filter_Term).value, self._getOptionAsHumanReadableString())

    def _getOptionAsHumanReadableString(self):
        options = []
        if self.config.get(Plugin.Option.Should_Match_Case).value:
            options.append('Match Case')
        else:
            options.append('Ignore Case')
        if self.config.get(Plugin.Option.Is_Regex).value:
            options.append('Regular Expression')
        if self.config.get(Plugin.Option.Should_Invert_Match).value:
            options.append('Invert Match')

        return self._join_options_as_human_readable_string(options)

    def run(self, text: str):
        return self._codec.run(self.config, text)
