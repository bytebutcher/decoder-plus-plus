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
import qtawesome
from qtpy.QtGui import QIcon


class Icon:
    EDIT = 'fa.edit'
    FILTER = 'fa.filter'
    SEARCH = 'fa.search'
    CLOSE = 'fa.times'
    DOCK_HEX = 'fa.code'
    DOCK_LOG = 'fa.align-left'
    LOG_CLEAR = 'fa.trash'
    LOG_FILTER_DEBUG = 'fa.bug'
    LOG_FILTER_INFO = 'fa.info-circle'
    LOG_FILTER_ERROR = 'fa.exclamation-triangle'
    MSG_INFO = 'fa.info-circle'
    MSG_ERROR = 'fa.exclamation-triangle'
    FRAME_UP = 'fa.chevron-up'
    FRAME_DOWN = 'fa.chevron-down'
    FRAME_CONFIG = 'fa.cog'
    IDENTIFY_CODEC = 'ei.indent-left'
    IDENTIFY_HASH = 'ei-align-justify'
    STATUS_ERROR = 'fa.exclamation'
    STATUS_INFO = 'fa.info'
    STATUS_READY = 'fa.check'
    SEPARATOR_H = 'fa.ellipsis-h'
    SEPARATOR_V = 'fa.ellipsis-v'
    TAB_NEW = 'fa.plus'


icons = {}


def icon(name: str) -> QIcon:
    if name not in icons:
        try:
            icons[name] = qtawesome.icon(name)
        except:
            return QIcon()
    return icons[name]
