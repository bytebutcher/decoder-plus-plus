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
import sys
from functools import partial
from typing import Callable

logging.TRACE = logging.DEBUG - 5

console_logger = None


def _get_log_format(level: int) -> str:
    """ Returns the log format for the specified log level. """
    if level == logging.DEBUG or level == logging.TRACE:
        return f'%(asctime)s: %(levelname)7s: %(filename)s:%(lineno)s:%(funcName)s: %(msg)s'
    else:
        return f'%(asctime)s: %(levelname)7s: %(msg)s'


def _init_log_trace(logger: logging.Logger) -> Callable:
    """ Add custom log level TRACE. Do not define if it already exists. """
    if logging.getLevelName(logging.TRACE) == f'Level {logging.TRACE}':
        logging.addLevelName(logging.TRACE, 'TRACE')
    return lambda msg, *args, **kwargs: logger.log(logging.TRACE, msg, *args, **kwargs)


def init_logger(level: int) -> logging.Logger:
    """ Initializes a logging.Logger with the specified level. """
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.trace = _init_log_trace(logger)

    global console_logger
    console_logger = logging.StreamHandler(sys.stderr)
    console_logger.setFormatter(logging.Formatter(_get_log_format(level)))
    logger.addHandler(console_logger)
    return logger


def set_level(level: int):
    """ Sets the specified level for the standard logger. """
    logger = logging.getLogger()
    logger.setLevel(level)
    global console_logger
    console_logger.setFormatter(logging.Formatter(_get_log_format(level)))
