import json

import pyjq as pyjq
import qtawesome

from PyQt5.QtWidgets import QDialog

from dpp.core.exception import AbortedException
from dpp.core.plugin import ScriptPlugin, PluginConfig
from dpp.ui.dialog.plugin_config_dialog import PluginConfigPreviewDialog


class Plugin(ScriptPlugin):
	"""
	Opens a dialog to filter xml text by certain jq expression.
	"""

	class Option(object):
		JQ_Expression = PluginConfig.Option.Label("jq_expression", "Expression:")

	class XPathCodec:

		def run(self, config: PluginConfig, text: str):
			try:
				jq_expression = config.get(Plugin.Option.JQ_Expression).value
				# TODO: The filter area is not expanded correctly
				# TODO: The filter area does line wrapping. There should be an option for that for activating/deactivating.
				return json.dumps(pyjq.all(jq_expression, json.loads(text)))
			except Exception as e:
				# Ignore exceptions - most likely an error in the jq expression
				pass

	def __init__(self, context):
		# Name, Author, Dependencies
		super().__init__('JQ', "Thomas Engel", ["pyjq"], context)
		self._context = context
		self._logger = context.logger
		self._codec = Plugin.XPathCodec()
		self.config.add(PluginConfig.Option.String(
			label=Plugin.Option.JQ_Expression,
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
		return "Filter by jq expression '{}'".format(self.config.get(Plugin.Option.JQ_Expression).value)

	def run(self, text: str):
		return self._codec.run(self.config, text)
