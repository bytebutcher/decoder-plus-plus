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
import string

from qtpy.QtCore import QUrl
from qtpy.QtGui import QDesktopServices

from dpp.core.exceptions import ValidationError
from dpp.core.icons import Icon
from dpp.core.plugin import ScriptPlugin
from dpp.core.plugin.config import Label
from dpp.core.plugin.config.options import String, Boolean
from dpp.core.plugin.config.ui import Layout
from dpp.core.plugin.config.ui.layouts import FormLayout, HBoxLayout
from dpp.core.plugin.config.ui.widgets import ToolButton, Frame, Option


class Plugin(ScriptPlugin):
    """
    Reformats the input.

    Example:

        Input:
            123 456

        Parameters:

                    Format = "{1} {0}"
                  Split by = " "
                     Regex = False
            Handle Newline = True

        Output:
            456 123
    """

    class Option(object):

        Format = Label("format_string", "Format:")
        SplitChars = Label("split_chars", "Split by:")
        IsRegex = Label("is_regex", "Regex")
        HandleNewlines = Label("handle_newlines", "Handle Newlines")

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies, Icon
        super().__init__('Reformat Text', "Thomas Engel", [], context, Icon.EDIT)

        def _validate_split_chars(input_text: str):

            def _validate_regex():
                try:
                    re.compile(self.config.value(Plugin.Option.SplitChars))
                    return True
                except:
                    return False

            if not self.config.value(Plugin.Option.SplitChars):
                raise ValidationError("Split by should not be empty!")

            if self.config.value(Plugin.Option.IsRegex) and not _validate_regex():
                raise ValidationError("Invalid regular expression!")

        def _validate_format(input_text: str):
            try:
                self.run(input_text)
            except:
                raise ValidationError("Invalid format string!")

        self.config.add(String(
            label=Plugin.Option.Format,
            value="",
            description="the format string to be used",
            is_required=True
        ), validator=_validate_format)
        self.config.add(String(
            label=Plugin.Option.SplitChars,
            value=" ",
            description="the characters used to split the text in individual parts (default=' ')",
            is_required=False
        ), validator=_validate_split_chars)
        self.config.add(Boolean(
            label=Plugin.Option.IsRegex,
            value=False,
            description="defines whether the split chars is a regular expression (default=False)",
            is_required=False
        ))
        self.config.add(Boolean(
            label=Plugin.Option.HandleNewlines,
            value=True,
            description="defines whether the operation should be applied for each individual line (default=True)",
            is_required=False
        ))
        self._codec = ReformatCodec()

    def _create_options_layout(self, input_text: str) -> Layout:
        return FormLayout(
            widgets=[
                Frame(
                    label=Plugin.Option.Format.name,
                    layout=HBoxLayout(
                        widgets=[
                            Option(self._config.option(Plugin.Option.Format), show_label=False),
                            ToolButton(
                                label='?',
                                on_click=lambda evt: QDesktopServices.openUrl(QUrl("https://pyformat.info/"))
                            )
                        ]
                    )
                ),
                Option(Plugin.Option.SplitChars),
                Option(Plugin.Option.IsRegex),
                Option(Plugin.Option.HandleNewlines)
            ]
        )

    @property
    def title(self) -> str:
        return "Reformat text with '{}' using '{}' as {}delimiter{}".format(
            self.config.value(Plugin.Option.Format),
            self.config.value(Plugin.Option.SplitChars),
            "regex-" if self.config.value(Plugin.Option.IsRegex) else "",
            " (newline sensitive)" if self.config.value(Plugin.Option.HandleNewlines) else ""
        )

    def run(self, input_text: str) -> str:
        if input_text:
            return self._codec.reformat(self._config, input_text)
        return ''


class ReformatCodec:

    def reformat(self, config, input_text):

        format = config.value(Plugin.Option.Format)
        split_by_chars = config.value(Plugin.Option.SplitChars)
        is_regex = config.value(Plugin.Option.IsRegex)
        handle_newlines = config.value(Plugin.Option.HandleNewlines)

        def _fill_blanks(format, values):
            """ Ensure that there are always at least as many values as there are placeholders. """
            format_len = len([i for i in string.Formatter().parse(format)])
            if len(values) < format_len:
                for i in range(1, format_len - len(values)):
                    values.append("")
            return values

        def _reformat(text):
            if is_regex:
                split_input = re.split(split_by_chars, text)
            else:
                split_input = text.split(split_by_chars)
            return format.format(*_fill_blanks(format, split_input))

        if input_text:
            if format:
                try:
                    if handle_newlines:
                        return os.linesep.join([_reformat(line) for line in input_text.split(os.linesep)])
                    else:
                        return _reformat(input_text)
                except BaseException:
                    raise Exception("Error during reformat operation! Check your format string!")
            else:
                return input_text
        return ''
