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
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QLabel


class ClickableLabel(QLabel):
    """ A label which emits click signals. """

    clicked = pyqtSignal('PyQt_PyObject') # event
    doubleClicked =  pyqtSignal('PyQt_PyObject') # event

    def __init__(self, parent=None):
        super(ClickableLabel, self).__init__(parent)

    def mouseReleaseEvent(self, event):
        if self.isEnabled(): self.clicked.emit(event)
        super(ClickableLabel, self).mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self.isEnabled(): self.doubleClicked.emit(event)
        super(ClickableLabel, self).mouseDoubleClickEvent(event)
