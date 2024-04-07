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
from dpp.core.exceptions import ValidationError
from dpp.core.icons import Icon
from dpp.core.plugin import ScriptPlugin
from dpp.core.plugin.config import Label
from dpp.core.plugin.config.options import String, Group


class Plugin(ScriptPlugin):
    """
    Splits and Rejoins a string.

    Example 1:

        Split by character ' ' and join with ''

        Input:
            ab cd ef gh ij kl mn op qr st uv wx yz

        Output:
            abcdefghijklmnopqrstuvwxyz

    Example 2:

        Split by length '2' and join with ' '

        Input:
            abcdefghijklmnopqrstuvwxyz

        Output:
            ab cd ef gh ij kl mn op qr st uv wx yz

    """

    class Option(object):
        SplitText = Label("split_term", "Split by:")
        SplitByLength = Label("split_by_length", "Length")
        SplitByChars = Label("split_by_chars", "Character")
        RejoinWithChars = Label("rejoin_with_chars", "Rejoin with:")

    class SplitAndRejoinCodec:

        def _chunk_string(self, string, length):
            return [string[0 + i:length + i] for i in range(0, len(string), length)]

        def run(self, config, input_text):
            if config.option(Plugin.Option.SplitByLength).is_checked:
                input_text = self._chunk_string(input_text, int(config.value(Plugin.Option.SplitText)))
            elif config.option(Plugin.Option.SplitByChars).is_checked:
                input_text = input_text.split(config.value(Plugin.Option.SplitText))
            return config.value(Plugin.Option.RejoinWithChars).join(input_text)

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies, Icon
        super().__init__('Split & Rejoin', "Thomas Engel", [], context, Icon.EDIT)
        self._init_config()
        self._codec = Plugin.SplitAndRejoinCodec()

    def _init_config(self):
        def _validate_split_text(input_text: str):
            if not self.config.value(Plugin.Option.SplitText):
                raise ValidationError("Split by should not be empty.")
            if self.config.value(Plugin.Option.SplitByLength):
                try:
                    length = int(self.config.value(Plugin.Option.SplitText))
                    if length <= 0:
                        raise ValidationError("Split by should be greater than 0.")
                except:
                    raise ValidationError("Split by should be an integer.")

        self.config.add(String(
            label=Plugin.Option.SplitText,
            value=",",  # default, since non-empty is not allowed (see validator)
            description="the parameter used for splitting",
            is_required=True
        ), validator=_validate_split_text)
        self.config.add(Group(
            label=Plugin.Option.SplitByChars,
            value=True,
            description="specifies whether text should be split at chars",
            is_required=False,
            group_name="split_behaviour"
        ))
        self.config.add(Group(
            label=Plugin.Option.SplitByLength,
            value=False,
            description="specifies whether text should be split at interval",
            is_required=False,
            group_name="split_behaviour"
        ))
        self.config.add(String(
            label=Plugin.Option.RejoinWithChars,
            value="",
            description="the chars used to join the split text",
            is_required=True
        ))

    @property
    def title(self):
        if self.config.option(Plugin.Option.SplitByLength).is_checked:
            return "Split by length {} and rejoin with '{}'".format(
                self.config.value(Plugin.Option.SplitText),
                self.config.value(Plugin.Option.RejoinWithChars)
            )
        elif self.config.option(Plugin.Option.SplitByChars).is_checked:
            return "Split by characters '{}' and rejoin with '{}'".format(
                self.config.value(Plugin.Option.SplitText),
                self.config.value(Plugin.Option.RejoinWithChars)
            )
        else:
            self._logger.debug("Invalid option.")
            return "Split and Rejoin"

    def run(self, input_text: str) -> str:
        if input_text:
            return self._codec.run(self.config, input_text)
        return ''
