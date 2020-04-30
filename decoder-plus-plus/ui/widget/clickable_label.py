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
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLabel


class ClickableLabel(QLabel):
    """ A label which is clickable. """

    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super(ClickableLabel, self).__init__(parent)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super(ClickableLabel, self).mousePressEvent(event)