import json
from json import JSONDecodeError
import os

import qtawesome

from PyQt6.QtWidgets import QDialog

from dpp.core.exception import AbortedException
from dpp.core.plugin import ScriptPlugin, PluginConfig
from dpp.ui.dialog.plugin_config_dialog import PluginConfigPreviewDialog


class Plugin(ScriptPlugin):
	"""
	Opens a dialog to filter xml text by certain JSONPath expression.

	Example:

		Input:
			{"foo": [{"baz": 1}, {"baz": 2}]}

		Expression:
			foo[*].baz

		Output:
			1
			2

	"""

	class Option(object):
		Expression = PluginConfig.Option.Label("expression", "Expression:")

	class Codec:

		def run(self, config: PluginConfig, text: str):
			try:
				from jsonpath_ng import jsonpath, parse
				expression = config.get(Plugin.Option.Expression).value
				return os.linesep.join([
					json.dumps(item.value) for item in parse(expression).find(json.loads(text))
				])
			except JSONDecodeError as e:
				raise Exception("Error decoding json!")
			except Exception as e:
				# Ignore exceptions - most likely an error in the jq expression
				pass

	def __init__(self, context):
		# Name, Author, Dependencies
		super().__init__('JSONPath', "Thomas Engel", ["jsonpath_ng"], context)
		self._context = context
		self._logger = context.logger
		self._codec = Plugin.Codec()
		self.config.add(PluginConfig.Option.String(
			label=Plugin.Option.Expression,
			value="",
			description="JSONPath expression to filter by",
			is_required=True
		))
		self._dialog = None
		self._dialog_return_code = QDialog.Accepted

	def select(self, text: str):
		if not self._dialog:
			self._dialog = PluginConfigPreviewDialog(self._context, self.config.clone(), "JSONPath",
													 self._codec.run, qtawesome.icon("fa.filter"))

		self._dialog.setInput(text)
		self._dialog_return_code = self._dialog.exec_()

		if self._dialog_return_code != QDialog.Accepted:
			# User clicked the Cancel-Button.
			raise AbortedException("Aborted")

		self.config.update(self._dialog.config)
		return self.run(text)

	def title(self):
		return "Filter by JSONPath expression '{}'".format(self.config.get(Plugin.Option.Expression).value)

	def run(self, text: str):
		return self._codec.run(self.config, text)
