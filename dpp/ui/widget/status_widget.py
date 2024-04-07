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

from qtpy.QtWidgets import QWidget, QHBoxLayout


class StatusWidget(QWidget):

    # Indicates that the input text was manually edited by the user.
    DEFAULT = "DEFAULT"

    # Indicates that the plugin has been successfully executed.
    SUCCESS = "SUCCESS"

    # Indicates that the plugin has been executed but an error occurred.
    ERROR = "ERROR"

    def __init__(self, parent=None, status="DEFAULT", width=15, height=None):
        super(__class__, self).__init__(parent)
        layout = QHBoxLayout()
        self._widget = QWidget(self)
        if width is not None: self._widget.setFixedWidth(width)
        if height is not None: self._widget.setFixedHeight(height)
        self._status = {
            "DEFAULT": "background-color: rgba( 200, 200, 200, 50% );",
            "SUCCESS": "background-color: rgba( 0, 255, 0, 50% );",
            "ERROR": "background-color: rgba( 255, 0, 0, 50% );"
        }
        self.setStatus(status)
        layout.setContentsMargins(6, 6, 0, 6)

        layout.addWidget(self._widget)
        self.setLayout(layout)

    def setStatus(self, status_name, message=None):
        if status_name not in self._status:
            raise Exception("Unknown status name {}!".format(status_name))
        self._current_status_name = status_name
        self._current_status_message = message
        self._widget.setStyleSheet(self._status[self._current_status_name])
        if message:
            self.setToolTip(message)
        else:
            self.setToolTip("")

    def hasStatus(self, status_name):
        return self._current_status_name == status_name

    def status(self) -> (str, str):
        return self._current_status_name, self._current_status_message
