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
#
from qtpy.QtWidgets import QAction


class ActionBuilder:
    """ Builder for QAction. """

    def __init__(self, parent=None):
        self._parent = parent
        self._name = None
        self._enabled = True
        self._callback = None

    def name(self, name: str):
        """ The name of the action (e.g. 'Copy'). """
        self._name = name
        return self

    def enabled(self, status: bool):
        """ The status of the action. When False this action can not be clicked. Default = True. """
        self._enabled = status
        return self

    def callback(self, callback):
        """ The callback which should be triggered when the action is clicked. """
        self._callback = callback # void QAction::triggered(bool checked = false)
        return self

    def build(self) -> QAction:
        """ Builds and returns the QAction with the specified parameters. """
        assert(self._name is not None), "Name is required and should not be None"
        assert(self._callback is not None), "Callback is required and should not be None"
        action = QAction(self._parent)
        action.setText(self._name)
        action.setEnabled(self._enabled)
        action.triggered.connect(self._callback)
        return action
