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
from PyQt5.QtCore import QObject, pyqtSignal


class Listener(QObject):
    newTabRequested = pyqtSignal(str)  # text
    selectedFrameChanged = pyqtSignal(str, str, str)  # tab_id, frame_id, text
    textChanged = pyqtSignal(str, str, str)  # tab_id, frame_id, text
    textSelectionChanged = pyqtSignal(str, str, str)  # tab_id, frame_id, text

    def __init__(self, context: 'core.context.Context'):
        super(__class__, self).__init__()
        self.newTabRequested.connect(lambda text:
            context.logger().debug("newTabRequested({})".format(text)))
        self.selectedFrameChanged.connect(lambda tab_id, frame_id, text:
            context.logger().debug("selectedFrameChanged({}, {}, {})".format(tab_id, frame_id, text)))
        self.textChanged.connect(lambda tab_id, frame_id, text:
            context.logger().debug("textChanged({}, {}, {})".format(tab_id, frame_id, text)))
        self.textSelectionChanged.connect(lambda tab_id, frame_id, text:
            context.logger().debug("textSelectionChanged({}, {}, {})".format(tab_id, frame_id, text)))
