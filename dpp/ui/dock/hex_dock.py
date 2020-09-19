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

from typing import List

import qtawesome
from PyQt5.QtWidgets import QWidget

from dpp.core import Context
from dpp.ui.view.hex_view import HexView
from dpp.ui.widget.dock_widget import DockWidget


class HexDock(DockWidget):
    """ A widget to show a hex view of a string representation. """

    def __init__(self, context: Context, parent: QWidget):
        super(HexDock, self).__init__("Hex", qtawesome.icon("fa.code"), parent)
        self.addWidget(HexView(context, self))
