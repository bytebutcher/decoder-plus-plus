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
	Opens a dialog to filter xml text by certain jq expression.

	Example:

		Input:
			{"a": [{"b": "c"}, {"b": "d"}]}

		Expression:
			.a[].b

		Output:
			"c"
			"d"

	"""

	class Option(object):
		Expression = PluginConfig.Option.Label("expression", "Expression:")

	class Codec:

		def run(self, config: PluginConfig, text: str):
			try:
				import pyjq as pyjq
				expression = config.get(Plugin.Option.Expression).value
				return os.linesep.join([
					json.dumps(item) for item in pyjq.all(expression, json.loads(text))
				])
			except JSONDecodeError as e:
				raise Exception("Error decoding json!")
			except Exception as e:
				# Ignore exceptions - most likely an error in the jq expression
				pass

	def __init__(self, context):
		# Name, Author, Dependencies
		super().__init__('JQ', "Thomas Engel", ["pyjq"], context)
		self._context = context
		self._logger = context.logger
		self._codec = Plugin.Codec()
		self.config.add(PluginConfig.Option.String(
			label=Plugin.Option.Expression,
			value="",
			description="jq expression to filter by",
			is_required=True
		))
		self._dialog = None
		self._dialog_return_code = QDialog.Accepted

	def select(self, text: str):
		if not self._dialog:
			self._dialog = PluginConfigPreviewDialog(self._context, self.config.clone(), "jq",
													 self._codec.run, qtawesome.icon("fa.filter"))

		self._dialog.setInput(text)
		self._dialog_return_code = self._dialog.exec_()

		if self._dialog_return_code != QDialog.Accepted:
			# User clicked the Cancel-Button.
			raise AbortedException("Aborted")

		self.config.update(self._dialog.config)
		return self.run(text)

	def title(self):
		return "Filter by jq expression '{}'".format(self.config.get(Plugin.Option.Expression).value)

	def run(self, text: str):
		return self._codec.run(self.config, text)
