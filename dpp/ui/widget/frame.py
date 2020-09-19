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
from PyQt5.QtWidgets import QFrame

from dpp.core import Context


class Frame(QFrame):
    """
    Encapsulates the basic frame behaviour.
    """

    frameChanged = pyqtSignal(str)

    def __init__(self, parent, context: Context, frame_id: str):
        super(__class__, self).__init__(parent)
        self._frame_id = frame_id
        self._context = context
        self._listener = self._context.listener()
        self._logger = context.logger()

    def id(self) -> str:
        """ Returns the individual identifier of the frame. """
        return self._frame_id

    def isConfigurable(self) -> bool:
        """
        Returns whether the frame is configurable (always False).
        This method needs to be overridden if other behaviour is required.
        """
        return False
