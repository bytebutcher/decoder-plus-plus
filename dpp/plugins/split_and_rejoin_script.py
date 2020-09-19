import qtawesome
from PyQt5.QtWidgets import QDialog

from dpp.core.exception import AbortedException
from dpp.core.plugin import ScriptPlugin, PluginConfig
from dpp.ui.dialog.plugin_config_dialog import PluginConfigDialog


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
        SplitText = PluginConfig.Option.Label("split_term", "Split by:")
        SplitByLength = PluginConfig.Option.Label("split_by_length", "Length")
        SplitByChars = PluginConfig.Option.Label("split_by_chars", "Character")
        RejoinWithChars = PluginConfig.Option.Label("rejoin_with_chars", "Rejoin with:")

    class SplitAndRejoinCodec:

        def _chunk_string(self, string, length):
            return [string[0 + i:length + i] for i in range(0, len(string), length)]

        def run(self, config, input):
            if config.get(Plugin.Option.SplitByLength).is_checked:
                input = self._chunk_string(input, int(config.get(Plugin.Option.SplitText).value))
            elif config.get(Plugin.Option.SplitByChars).is_checked:
                input = input.split(config.get(Plugin.Option.SplitText).value)
            return config.get(Plugin.Option.RejoinWithChars).value.join(input)

    def __init__(self, context):
        # Name, Author, Dependencies
        super().__init__('Split & Rejoin', "Thomas Engel", [], context)
        self._init_config()
        self._codec = Plugin.SplitAndRejoinCodec()
        self._dialog = None
        self._dialog_return_code = None

    def _init_config(self):
        def _validate_split_text(config: PluginConfig, codec, input):
            print("WHAT")
            if not config.get(Plugin.Option.SplitText).value:
                return "Split by should not be empty."
            if config.get(Plugin.Option.SplitByLength).value:
                try:
                    length = int(config.get(Plugin.Option.SplitText).value)
                    if length <= 0:
                        return "Split by should be greater than 0."
                except:
                    return "Split by should be an integer."

        self.config.add(PluginConfig.Option.String(
            label=Plugin.Option.SplitText,
            value=",", # default, since non-empty is not allowed (see validator)
            description="the parameter used for splitting",
            is_required=True
        ), validator=_validate_split_text)
        self.config.add(PluginConfig.Option.Group(
            label=Plugin.Option.SplitByChars,
            value=True,
            description="specifies whether text should be split at chars",
            is_required=False,
            group_name="split_behaviour"
        ))
        self.config.add(PluginConfig.Option.Group(
            label=Plugin.Option.SplitByLength,
            value=False,
            description="specifies whether text should be split at interval",
            is_required=False,
            group_name="split_behaviour"
        ))
        self.config.add(PluginConfig.Option.String(
            label=Plugin.Option.RejoinWithChars,
            value="",
            description="the chars used to join the split text",
            is_required=True
        ))

    def title(self):
        if self.config.get(Plugin.Option.SplitByLength).is_checked:
            return "Split by length {} and rejoin with '{}'".format(
                self.config.get(Plugin.Option.SplitText).value,
                self.config.get(Plugin.Option.RejoinWithChars).value
            )
        elif self.config.get(Plugin.Option.SplitByChars).is_checked:
            return "Split by characters '{}' and rejoin with '{}'".format(
                self.config.get(Plugin.Option.SplitText).value,
                self.config.get(Plugin.Option.RejoinWithChars).value
            )
        else:
            self.logger().debug("Invalid option.")
            return "Split and Rejoin"

    def select(self, text: str):
        if not self._dialog:
            try:
                self._dialog = PluginConfigDialog(
                    self._context, self.config.clone(), "Split & Rejoin", self._codec.run, qtawesome.icon("fa.edit"))
            except BaseException as e:
                self._context.logger().exception(e, exc_info=self._context.isDebugModeEnabled())

        self._dialog.setInput(text)
        self._dialog_return_code = self._dialog.exec_()

        if self._dialog_return_code != QDialog.Accepted:
            # User clicked the Cancel-Button.
            raise AbortedException("Aborted")

        self.config.update(self._dialog.config)

        return self.run(text)

    def run(self, text: str):
        if text:
            return self._codec.run(self.config, text)
        return ''
