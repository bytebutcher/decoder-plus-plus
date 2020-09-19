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
    """ A set of global signals to emit or connect to. """

    # Signals that a new tab should be created with the specified text
    newTabRequested = pyqtSignal(str)  # text

    # Signals that the selected frame changed (e.g. to update the hex view)
    selectedFrameChanged = pyqtSignal(str, str, str)  # tab_id, frame_id, text

    # Signals that the text inside the codec frame changed (e.g. to update the hex view)
    textChanged = pyqtSignal(str, str, str)  # tab_id, frame_id, text

    # Signals that the text selection inside the codec frame changed (e.g. to update the hex view)
    textSelectionChanged = pyqtSignal(str, str, str)  # tab_id, frame_id, text

    # Signals that text of a codec frame should be changed to the specified text (e.g. when hex view was edited by user)
    textSubmitted = pyqtSignal(str, str, str) # tab_id, frame_id, text

    def __init__(self, context: 'core.context.Context'):
        super(__class__, self).__init__()
        # Logs each event when being triggered
        self.newTabRequested.connect(lambda text:
            context.logger().debug("newTabRequested({})".format(text)))
        self.selectedFrameChanged.connect(lambda tab_id, frame_id, text:
            context.logger().debug("selectedFrameChanged({}, {}, {})".format(tab_id, frame_id, text)))
        self.textChanged.connect(lambda tab_id, frame_id, text:
            context.logger().debug("textChanged({}, {}, {})".format(tab_id, frame_id, text)))
        self.textSelectionChanged.connect(lambda tab_id, frame_id, text:
            context.logger().debug("textSelectionChanged({}, {}, {})".format(tab_id, frame_id, text)))
        self.textSubmitted.connect(lambda tab_id, frame_id, text:
            context.logger().debug("textSubmitted({}, {}, {})".format(tab_id, frame_id, text)))
