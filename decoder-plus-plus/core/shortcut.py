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
from PyQt5.QtCore import QObject
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut, QWidget


class Shortcut(QObject):

    def __init__(self, id, name, shortcut_key, callback, widget):
        self._id = id
        self._name = name
        self._shortcut = QShortcut(QKeySequence(shortcut_key), widget)
        self._shortcut.activated.connect(callback)
        self._callback = callback

    def id(self):
        return self._id

    def name(self):
        return self._name

    def setName(self, name):
        self._name = name

    def shortcut(self):
        return self._shortcut

    def key(self):
        return self._shortcut.key().toString()

    def setKey(self, key):
        self._shortcut.setKey(QKeySequence(key))

    def setShortcut(self, shortcut):
        self._shortcut = shortcut

    def callback(self):
        return self._callback


class NullShortcut(Shortcut):

    def __init__(self):
        self._widget = QWidget()
        # id, name, shortcut_key, callback, widget
        super(NullShortcut, self).__init__("", "", "", lambda: None, self._widget)
