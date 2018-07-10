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

from PyQt5.QtCore import QObject, pyqtSignal


class LogFilter(logging.Filter, QObject):
    logInfoEvent = pyqtSignal('PyQt_PyObject')
    logWarnEvent = pyqtSignal('PyQt_PyObject')
    logErrorEvent = pyqtSignal('PyQt_PyObject')
    logDebugEvent = pyqtSignal('PyQt_PyObject')

    def __init__(self, parent):
        super(logging.Filter, self).__init__()
        super(QObject, self).__init__(parent)

    def filter(self, record):
        if not record.args:
            if record.levelno == logging.INFO:
                self.logInfoEvent.emit(record.msg)
            elif record.levelno == logging.ERROR:
                self.logErrorEvent.emit(record.msg)
            elif record.levelno == logging.WARN:
                self.logWarnEvent.emit(record.msg)
            elif record.levelno == logging.DEBUG:
                self.logDebugEvent.emit(record.msg)
        return True
