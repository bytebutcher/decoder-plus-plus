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
    """ Defines a shortcut with a unique identifier. """

    def __init__(self, id: str, name: str, shortcut_key: str, callback, widget):
        """
        Initializes a shortcut.
        :param id: the unique id of the shortcut (e.g. "next_frame_focus").
        :param name: the name of the shortcut which is displayed to the user (e.g. "Focus next frame").
        :param shortcut_key: the shortcut key which triggers an action (e.g. "Alt+Down").
        :param callback: the callback which should be triggered when the shortcut key is pressed.
        :param widget: the widget on which the shortcut is bound to.
        """
        self._id = id
        self._name = name
        self._shortcut = QShortcut(QKeySequence(shortcut_key), widget)
        self._shortcut.activated.connect(callback)
        self._callback = callback

    def id(self) -> str:
        """ Returns the unique id of the shortcut (e.g. "next_frame_focus"). """
        return self._id

    def name(self) -> str:
        """ Returns the name of the shortcut (e.g. "Focus next frame"). """
        return self._name

    def setName(self, name: str):
        """ Sets the name of the shortcut which is displayed to the user (e.g. "Focus next frame"). """
        self._name = name

    def shortcut(self) -> QShortcut:
        """ Returns the shortcut which triggers an action. """
        return self._shortcut

    def key(self) -> str:
        """ Returns the shortcut key (e.g. "Alt+Down") which triggers an action. """
        return self._shortcut.key().toString()

    def setKey(self, key: str):
        """ Sets the shortcut key (e.g. "Alt+Down") which triggers an action. """
        self._shortcut.setKey(QKeySequence(key))

    def setShortcut(self, shortcut: QShortcut):
        """ Sets the shortcut which triggers an action. """
        self._shortcut = shortcut

    def callback(self):
        """ Returns the callback which is triggered when the shortcut key is pressed. """
        return self._callback


class NullShortcut(Shortcut):
    """ Defines an empty shortcut which is used in case of an error (e.g. when no shortcut was defined). """

    def __init__(self):
        self._widget = QWidget()
        # id, name, shortcut_key, callback, widget
        super(NullShortcut, self).__init__("", "", "", lambda: None, self._widget)
