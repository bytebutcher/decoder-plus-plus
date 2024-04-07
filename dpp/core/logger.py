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


level_trace = logging.DEBUG - 5


def logmethod(name=None, level=level_trace, prefix_callback=None):
    """ Decorator for logging method calls. """
    if not name:
        name = __name__
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            prefix = ''
            if prefix_callback:
                prefix = prefix_callback(self)
            logging.getLogger(name=name).log(
                level=level,
                msg=f'{prefix}{method.__name__}({args, kwargs})'
            )
            #print(f'{level}: {logger_message}')
            result = method(self, *args, **kwargs)
            if result is not None:
                logging.getLogger(name=name).log(
                    level=level,
                    msg=f'{prefix}{method.__name__}({args, kwargs}) returns {result}'
                )
            return result

        return wrapper

    return decorator


def _get_log_format(level: int) -> str:
    """ Returns the log format for the specified log level. """
    if level == logging.DEBUG or level == level_trace:
        return f'%(asctime)s: %(levelname)7s: %(filename)s:%(lineno)s:%(funcName)s: %(msg)s'
    else:
        return f'%(asctime)s: %(levelname)7s: %(msg)s'


def addLoggingLevel(levelName, levelNum, methodName=None):
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`. `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
    used.

    To avoid accidental clobberings of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present

    Example
    -------
    >>> addLoggingLevel('TRACE', logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).trace('that worked')
    >>> logging.trace('so did this')
    >>> logging.TRACE
    5

    """
    if not methodName:
        methodName = levelName.lower()

    if hasattr(logging, levelName):
        raise AttributeError('{} already defined in logging module'.format(levelName))
    if hasattr(logging, methodName):
        raise AttributeError('{} already defined in logging module'.format(methodName))
    if hasattr(logging.getLoggerClass(), methodName):
        raise AttributeError('{} already defined in logger class'.format(methodName))

    # This method was inspired by the answers to Stack Overflow post
    # http://stackoverflow.com/q/2183233/2988730, especially
    # http://stackoverflow.com/a/13638084/2988730
    def logForLevel(self, msg, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, msg, args, **kwargs)
    def logToRoot(msg, *args, **kwargs):
        logging.log(levelNum, msg, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)


def getLogger(name: str, level: int) -> logging.Logger:
    """ Initializes a logging.Logger with the specified level. """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    try:
        addLoggingLevel('TRACE', level_trace)
    except AttributeError as err:
        logger.debug(f'Failed to add TRACE logging level: {err}')
    console_logger = logging.StreamHandler(sys.stderr)
    console_logger.setFormatter(logging.Formatter(_get_log_format(level)))
    logger.addHandler(console_logger)
    return logger
