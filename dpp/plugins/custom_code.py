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
import time

from qtpy.QtWidgets import QFileDialog

from dpp.core.plugin import ScriptPlugin, PluginConfig
from dpp.core.plugin.config import Label
from dpp.core.plugin.config.ui import Layout
from dpp.core.plugin.config.ui.layouts import HBoxLayout, VBoxLayout
from dpp.core.plugin.config.ui.widgets import Button, Option, GroupBox, Frame, HSpace
from dpp.core.plugin.config.options import CodeEditor, Text, Boolean


class Plugin(ScriptPlugin):
    """
    Allows users to use custom Python scripts for mangling input.
    """

    class Option(object):
        Source_Code = Label("source_code", "Source Code:")
        Preview = Label("preview", "Preview")
        Enabled = Label("enabled", "Enabled")

    class Eval:

        @staticmethod
        def eval(source_code, text):
            local_env = {}
            exec(source_code, globals(), local_env)
            result = local_env['run'](text)
            return result

    class CustomCodeCodec:

        def run(self, config: PluginConfig, text: str):
            source_code = config.value(Plugin.Option.Source_Code)
            return Plugin.Eval.eval(source_code, text)

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies
        super().__init__('Custom Code', "Thomas Engel", [], context)
        self._codec = Plugin.CustomCodeCodec()
        self.config.add(CodeEditor(
            label=Plugin.Option.Source_Code,
            value="""def run(input_text):
    return input_text""",
            description="source code used to process input.",
            is_required=True
        ))
        self.config.add(Boolean(
            label=Plugin.Option.Enabled,
            value=True,
            description="manages whether the code-execution is enabled/disabled",
            is_required=True
        ))
        self.config.add(Text(
            label=Plugin.Option.Preview,
            value="",
            description="internal value for storing the preview",
            is_required=False,
            read_only=True
        ))

    def setup(self, config: dict, safe_mode: bool = False):
        super().setup(config)
        if safe_mode:
            self._context.logger.error("Disabling execution of potentially dangerous custom code...")
            self.config.update({Plugin.Option.Enabled.key: False})

    def layout(self, input_text: str) -> Layout:
        """ Returns a layout containing all configuration entries. """
        return VBoxLayout(
            widgets=[
                Frame(layout=HBoxLayout(
                    widgets=[
                        Button(label="Open", description="Load code from file", on_click=lambda event: self._open_file_dialog(), icon=('awesome', 'fa.folder-open')),
                        Button(label="Save As...", description="Save code to file", on_click=lambda event: self._save_file_dialog(), icon=('awesome', 'fa.save')),
                        HSpace(),
                        Option(Plugin.Option.Enabled),
                        Button(
                            label="Test Code",
                            description="Test the execution of the code",
                            on_click=lambda event: self._test_button_clicked(event, input_text),
                            icon=('awesome', 'fa.rocket')
                        ),
                    ]
                )),
                Frame(layout=HBoxLayout(
                    widgets=[
                        GroupBox(label='Code Editor', layout=HBoxLayout(widgets=[Option(Plugin.Option.Source_Code)])),
                        GroupBox(label='Preview', layout=HBoxLayout(widgets=[Option(Plugin.Option.Preview)]))
                    ]
                ))
            ]
        )

    def _open_file_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(None, "Open File", "", "Python Files (*.py);;All Files (*)")
        if file_name:
            with open(file_name, 'r') as file:
                file_content = file.read()
                self.config.update({Plugin.Option.Source_Code.key: file_content})

    def _save_file_dialog(self):
        file_name, _ = QFileDialog.getSaveFileName(None, "Save File", "", "Python Files (*.py);;All Files (*)")
        if file_name:
            with open(file_name, 'w') as file:
                file_content = self.config.value(Plugin.Option.Source_Code)
                file.write(file_content)

    def _test_button_clicked(self, event, input_text):
        try:
            start_time = time.time()
            result = self.run(input_text)
            end_time = time.time()
            duration = (end_time - start_time) * 1000
            success_message = f"Code was successfully executed in {duration:.2f} milliseconds!"
            self.onSuccess.emit(success_message)
            self.config.update({Plugin.Option.Preview.key: result})
        except Exception as e:
            self.onError.emit(str(e))

    def run(self, input_text: str) -> str:
        enabled = self.config.value(Plugin.Option.Enabled)
        if not enabled:
            raise Exception(f"Execution of script currently disabled!")
        return self._codec.run(self.config, input_text)
