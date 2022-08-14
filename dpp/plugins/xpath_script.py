import qtawesome

from PyQt6.QtWidgets import QDialog
from lxml.etree import XMLSyntaxError

from dpp.core.exception import AbortedException
from dpp.core.plugin import ScriptPlugin, PluginConfig
from dpp.ui.dialog.plugin_config_dialog import PluginConfigPreviewDialog


class Plugin(ScriptPlugin):
	"""
	Opens a dialog to filter xml text by certain xpath expression.

	Example:

		Input:
			<a><b>text</b></a>

		Expression:
			//b

		Output:
			<b>text</b>

	"""

	class Option(object):
		Expression = PluginConfig.Option.Label("xpath_expression", "XPath:")

	class Codec:

		def run(self, config: PluginConfig, text: str):
			try:
				from lxml import etree
				expression = config.get(Plugin.Option.Expression).value
				root = etree.fromstring(text)
				return "".join(etree.tostring(item).decode('utf-8', errors="surrogateescape")
					for item in root.xpath(expression)
				)
			except XMLSyntaxError as e:
				raise Exception("Error decoding XML!")
			except Exception as e:
				# Ignore exceptions - most likely an error in the xpath expression
				pass

	def __init__(self, context):
		# Name, Author, Dependencies
		super().__init__('XPath', "Thomas Engel", ["lxml"], context)
		self._context = context
		self._logger = context.logger
		self._codec = Plugin.Codec()
		self.config.add(PluginConfig.Option.String(
			label=Plugin.Option.Expression,
			value="",
			description="xpath expression to filter by",
			is_required=True
		))
		self._dialog = None
		self._dialog_return_code = QDialog.Accepted

	def select(self, text: str):
		if not self._dialog:
			self._dialog = PluginConfigPreviewDialog(self._context, self.config.clone(), "XPath",
													 self._codec.run, qtawesome.icon("fa.filter"))

		self._dialog.setInput(text)
		self._dialog_return_code = self._dialog.exec_()

		if self._dialog_return_code != QDialog.Accepted:
			# User clicked the Cancel-Button.
			raise AbortedException("Aborted")

		self.config.update(self._dialog.config)
		return self.run(text)

	def title(self):
		return "Filter by XPath expression '{}'".format(self.config.get(Plugin.Option.Expression).value)

	def run(self, text: str):
		return self._codec.run(self.config, text)
