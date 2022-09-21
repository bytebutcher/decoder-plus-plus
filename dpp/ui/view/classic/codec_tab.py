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
import uuid
from typing import List

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QScrollArea, QFrame, QVBoxLayout

from dpp.core import Context
from dpp.core.logger import logmethod
from dpp.core.plugin.manager import PluginManager
from dpp.ui.view.classic.codec_frames import CodecFrames
from dpp.ui.widget.spacers import VSpacer
from dpp.ui.widget.status_widget import StatusWidget


class CodecTab(QScrollArea):

    @logmethod()
    def __init__(self, parent, context: Context, plugins: PluginManager):
        super(__class__, self).__init__(parent)
        self._context = context
        self._tab_id = uuid.uuid4().hex
        self._plugins = plugins
        self._frames = CodecFrames(self, context, self._tab_id, plugins)
        self._main_frame = QFrame(self)
        self._main_frame_layout = QVBoxLayout()
        self._main_frame_layout.setAlignment(Qt.AlignTop)
        self._main_frame_layout.addWidget(self._frames)
        self._main_frame_layout.addWidget(VSpacer(self))
        self._main_frame.setLayout(self._main_frame_layout)
        self._frames.newFrame("", "", 0, StatusWidget.DEFAULT)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setWidgetResizable(True)
        self.setWidget(self._main_frame)

    # ------------------------------------------------------------------------------------------------------------------

    def id(self):
        return self._tab_id

    def frames(self) -> CodecFrames:
        return self._frames

    # ------------------------------------------------------------------------------------------------------------------

    def toDict(self) -> List[dict]:
        return self._frames.toDict()
