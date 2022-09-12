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
import inspect

from qtpy import QtCore
from qtpy.QtWidgets import QVBoxLayout, QGroupBox, QLabel, QFrame

from dpp.core.plugin import AbstractPlugin


class PluginFrame(QFrame):

    def __init__(self, context, plugin: AbstractPlugin, parent=None):
        super(PluginFrame, self).__init__(parent)

        self._context = context
        self._plugin = plugin

        layout = QVBoxLayout()
        layout.addWidget(self._make_group_text_field("Name", plugin.name))
        layout.addWidget(self._make_group_text_field("Description", self._clean_description(plugin.__doc__)))
        if plugin.dependencies():
            layout.addWidget(self._make_group_text_field("Dependencies", self._clean_dependencies(plugin.dependencies())))
        layout.addWidget(self._make_group_text_field("Author", plugin.author))
        layout.addStretch(1)
        self.setLayout(layout)

    def _make_group_text_field(self, title, text):
        grp_field = QGroupBox(title)
        grp_field_layout = QVBoxLayout()
        txt_field = QLabel()
        txt_field.setTextFormat(QtCore.Qt.RichText)
        txt_field.setWordWrap(True)
        txt_field.setText(text)
        grp_field_layout.addWidget(txt_field)
        grp_field.setLayout(grp_field_layout)
        return grp_field

    def _clean_description(self, description_text):
        return "<br/>".join(inspect.cleandoc(description_text).split("\n"))

    def _clean_dependencies(self, dependencies):
        dependencies_text = ""
        for dependency in dependencies:
            is_unresolved_dependency = not self._plugin.check_dependency(dependency)
            if is_unresolved_dependency:
                dependencies_text += "<div style='color:red;'>{} (unresolved)</div>".format(dependency)
            else:
                dependencies_text += "<div>{}</div>".format(dependency)
            dependencies_text += "</br>"
        return dependencies_text
