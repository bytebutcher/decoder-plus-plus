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
from qtpy.QtWidgets import QHBoxLayout, QSizePolicy, QFrame, QLabel, QVBoxLayout

from dpp.core.icons import icon, Icon
from dpp.ui import IconLabel, HSpacer


class MessageBox(QFrame):

    def __init__(self, parent):
        super(__class__, self).__init__(parent)
        frm_layout = QVBoxLayout()
        self._msg_frame = QFrame()
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        self._msg_icon = IconLabel(self)
        layout.addWidget(self._msg_icon)
        self._msg_text = QLabel("")
        self._msg_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self._msg_text)
        close_icon = IconLabel(self, icon(Icon.CLOSE))
        close_icon.setHoverEffect(True)
        close_icon.setToolTip('Close')
        close_icon.clicked.connect(lambda: self.hide())
        layout.addWidget(HSpacer())
        layout.addWidget(close_icon)
        self._msg_frame.setLayout(layout)
        frm_layout.addWidget(self._msg_frame)
        frm_layout.setContentsMargins(10, 0, 10, 10)
        self.setLayout(frm_layout)

    def setText(self, text):
        self._msg_text.setText(text)

    def setIcon(self, icon_name, color=None):
        self._msg_icon.setIcon(icon(icon_name, color=color))

    def setFrameStyle(self, style):
        self._msg_frame.setStyleSheet(style)

    def setTextStyle(self, style):
        self._msg_text.setStyleSheet(style)