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
import json
from json import JSONDecodeError
import os


from dpp.core.icons import Icon
from dpp.core.plugin import ScriptPlugin, PluginConfig
from dpp.core.plugin.config import Label
from dpp.core.plugin.config.options import String


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
		Expression = Label("expression", "Expression:")

	class Codec:

		def run(self, config: PluginConfig, text: str):
			try:
				import pyjq as pyjq
				expression = config.value(Plugin.Option.Expression)
				return os.linesep.join([
					json.dumps(item) for item in pyjq.all(expression, json.loads(text))
				])
			except JSONDecodeError as e:
				raise Exception("Error decoding json!")
			except Exception as e:
				# Ignore exceptions - most likely an error in the jq expression
				pass

	def __init__(self, context: 'dpp.core.context.Context'):
		# Name, Author, Dependencies, Icon
		super().__init__('JQ', "Thomas Engel", ["pyjq"], context, Icon.FILTER)
		self._context = context
		self._codec = Plugin.Codec()
		self.config.add(String(
			label=Plugin.Option.Expression,
			value="",
			description="jq expression to filter by",
			is_required=True
		))

	@property
	def title(self) -> str:
		return "Filter by jq expression '{}'".format(self.config.value(Plugin.Option.Expression))

	def run(self, input_text: str) -> str:
		return self._codec.run(self.config, input_text)
