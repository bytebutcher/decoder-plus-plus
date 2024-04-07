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
from dpp.core import plugin
from dpp.core.plugin.config.ui import Widget


class Frame(Widget):

    def __init__(self, label=None, layout=None):
        super().__init__(label=label, layout=layout)


class Label(Widget):

    def __init__(self, value):
        super().__init__()
        if isinstance(value, plugin.config.Label):
            self.value = value.name
        elif isinstance(value, plugin.config.Option):
            self.value = value.label
        else:
            self.value = value


class Option(Widget):

    def __init__(self, label: plugin.config.Label, show_label: bool = None):
        super().__init__(label=label.name, show_label=show_label)
        self.key = label.key


class GroupBox(Widget):

    def __init__(self, label=None, layout=None, show_label=False):
        super().__init__(label=label, layout=layout, show_label=show_label)


class Button(Widget):

    def __init__(self, label, on_click, description="", show_label=False, icon=None):
        super().__init__(label=label, show_label=show_label)
        self.on_click = on_click
        self.description = description
        self.icon = icon


class ToolButton(Button):
    ...


class HSpace(Widget):
    ...

class VSpace(Widget):
    ...


class TextPreview(Widget):

    def __init__(self, plugin, input_text):
        super().__init__()
        self.plugin = plugin
        self.input_text = input_text
