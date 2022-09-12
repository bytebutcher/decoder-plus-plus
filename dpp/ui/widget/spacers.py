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
from qtpy.QtWidgets import QWidget, QSizePolicy


class Spacer(QWidget):

    def __init__(self, parent=None, width_policy=QSizePolicy.Expanding, height_policy=QSizePolicy.Expanding):
        super(Spacer, self).__init__(parent)
        self.setSizePolicy(width_policy, height_policy)
        self.setVisible(True)


class VSpacer(QWidget):

    def __init__(self, parent=None):
        super(__class__, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.setVisible(True)


class HSpacer(QWidget):

    def __init__(self, parent=None):
        super(__class__, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setVisible(True)
