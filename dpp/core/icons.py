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
import logging
import os

import qtawesome
from qtpy.QtGui import QIcon

from dpp import app_path

logger = logging.getLogger(__name__)


class Icon:
    EDIT = 'awesome', 'fa.edit'
    FILTER = 'awesome', 'fa.filter'
    SEARCH = 'awesome', 'fa.search'
    CLOSE = 'awesome', 'fa.times'
    DOCK_HEX = 'awesome', 'fa.code'
    DOCK_LOG = 'awesome', 'fa.align-left'
    LOG_CLEAR = 'awesome', 'fa.trash'
    LOG_FILTER_DEBUG = 'awesome', 'fa.bug'
    LOG_FILTER_INFO = 'awesome', 'fa.info-circle'
    LOG_FILTER_ERROR = 'awesome', 'fa.exclamation-triangle'
    MSG_INFO = 'awesome', 'fa.info-circle'
    MSG_ERROR = 'awesome', 'fa.exclamation-triangle'
    FRAME_REFRESH = 'awesome', 'fa.refresh'
    FRAME_UP = 'awesome', 'fa.chevron-up'
    FRAME_DOWN = 'awesome', 'fa.chevron-down'
    FRAME_RUN = 'awesome', 'fa.play'
    FRAME_PAUSE = 'awesome', 'fa.pause'
    FRAME_CONFIG = 'awesome', 'fa.cog'
    IDENTIFY_CODEC = 'awesome', 'ei.indent-left'
    IDENTIFY_HASH = 'awesome', 'fa.hashtag'
    IDENTIFY_FORMAT = 'awesome', 'ei.align-justify'
    STATUS_ERROR = 'awesome', 'fa.exclamation'
    STATUS_INFO = 'awesome', 'fa.info'
    STATUS_READY = 'awesome', 'fa.check'
    SEPARATOR_H = 'awesome', 'fa.ellipsis-h'
    SEPARATOR_V = 'awesome', 'fa.ellipsis-v'
    TAB_NEW = 'awesome', 'fa.plus'
    INDICATOR_DEFAULT = 'file', os.path.join('images', 'indicator_grey.png')
    INDICATOR_SUCCESS = 'file', os.path.join('images', 'indicator_green.png')
    INDICATOR_ERROR = 'file', os.path.join('images', 'indicator_red.png')


icons = {}


def icon(key, **kwargs) -> QIcon:
    source, name = key
    kwargs_id = str(hash(frozenset(kwargs.items())))
    if name not in icons:
        logger.trace(f'Initializing icon {source}://{name} ...')
        try:
            icons[name + kwargs_id] = {
                'awesome': lambda: qtawesome.icon(name, **kwargs),
                'file': lambda: QIcon(os.path.join(app_path, name))
            }.get(source)()
        except Exception as err:
            logger.debug(err, exc_info=True)
            return QIcon()
    logger.trace(f'Loading icon {source}://{name} ...')
    return icons[name + kwargs_id]
