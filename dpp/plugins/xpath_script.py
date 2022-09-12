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
from lxml.etree import XMLSyntaxError

from dpp.core.icons import Icon
from dpp.core.plugin import ScriptPlugin, PluginConfig
from dpp.core.plugin.config import Label
from dpp.core.plugin.config.options import String


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
		Expression = Label("xpath_expression", "XPath:")

	class Codec:

		def run(self, config: PluginConfig, text: str):
			try:
				from lxml import etree
				expression = config.value(Plugin.Option.Expression)
				root = etree.fromstring(text)
				return "".join(etree.tostring(item).decode('utf-8', errors="surrogateescape")
					for item in root.xpath(expression)
				)
			except XMLSyntaxError as e:
				raise Exception("Error decoding XML!")
			except Exception as e:
				# Ignore exceptions - most likely an error in the xpath expression
				pass

	def __init__(self, context: 'dpp.core.context.Context'):
		# Name, Author, Dependencies, Icon
		super().__init__('XPath', "Thomas Engel", ["lxml"], context, Icon.FILTER)
		self._context = context
		self._codec = Plugin.Codec()
		self.config.add(String(
			label=Plugin.Option.Expression,
			value="",
			description="xpath expression to filter by",
			is_required=True
		))

	@property
	def title(self) -> str:
		return "Filter by XPath expression '{}'".format(self.config.value(Plugin.Option.Expression))

	def run(self, input_text: str) -> str:
		return self._codec.run(self.config, input_text)
