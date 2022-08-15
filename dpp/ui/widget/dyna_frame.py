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
from qtpy.QtWidgets import QWidget, QFrame, QHBoxLayout, QStackedWidget


class DynaFrame(QFrame):
    """ The DynaFrame class wraps one custom widget which can be replaced with another during runtime. """

    def __init__(self, parent, widget: QWidget=None):
        super(__class__, self).__init__(parent)
        layout = QHBoxLayout()
        self._stk_widget = QStackedWidget()
        if widget is not None:
            self.setWidget(widget)
        layout.addWidget(self._stk_widget)
        self.setLayout(layout)

    def setWidget(self, widget: QWidget):
        """ Replaces the currently present widget (if any) with the specified one. """
        self._clear_stack_widget()
        self._stk_widget.addWidget(widget)

    def getWidget(self) -> QWidget:
        """ Returns the widget wrapped in the frame. """
        return self._stk_widget.widget(0)

    def _clear_stack_widget(self):
        """ Clears all widgets which were added to the stack. """
        count = self._stk_widget.count()
        assert 0 <= count <= 1
        for index in range(0, count):
            widget = self._stk_widget.widget(index)
            self._stk_widget.removeWidget(widget)
