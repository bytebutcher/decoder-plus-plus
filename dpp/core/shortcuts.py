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
from qtpy.QtWidgets import QAction, QWidget
from qtpy.QtGui import QKeySequence


class KeySequence(QKeySequence):

    def __init__(self, modifiers=None, key=None):
        try:
            from PyQt6.QtCore import QKeyCombination
            super(__class__, self).__init__(QKeyCombination(modifiers, key))
        except:
            super(__class__, self).__init__(modifiers | key)


class MenuRegistry:

    def __init__(self):
        self.registry = dict()

    def register_menu_item(self, id, text, shortcut_key=None):
        def func_wrapper(f):
            self.registry[id] = (text, shortcut_key, f)
            return f

        return func_wrapper


class Shortcut(QAction):
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
        super(__class__, self).__init__(name, widget)
        self._id = id
        self._name = name
        self._callback = callback
        self._widget = widget
        if shortcut_key:
            self.setShortcut(shortcut_key)
        self.triggered.connect(lambda e: callback())

    def id(self) -> str:
        """ Returns the unique id of the shortcut (e.g. "next_frame_focus"). """
        return self._id

    def name(self, remove_anchors=False) -> str:
        """ Returns the name of the shortcut (e.g. "Focus next frame").
        :param remove_anchors: if True removes every occurences of the ampersand-symbol (&) within the name.
        """
        if remove_anchors:
            return self._name.replace("&", "")
        return self._name

    def setName(self, name: str):
        """ Sets the name of the shortcut which is displayed to the user (e.g. "Focus next frame"). """
        self._name = name

    def key(self) -> str:
        """ Returns the shortcut key (e.g. "Alt+Down") which triggers an action. """
        return self.shortcut().toString()

    def setKey(self, key: str):
        """ Sets the shortcut key (e.g. "Alt+Down") which triggers an action. """
        self.setShortcut(key)

    def clone(self, name):
        """
        Returns this Shortcut with a different name. Note, that the shortcut key is not set in the clone in order
        to avoid ambiguous shortcut overload errors.
        """
        return Shortcut(self.id(), name, None, self._callback, self._widget)


class NullShortcut(Shortcut):
    """ Defines an empty shortcut which is used in case of an error (e.g. when no shortcut was defined). """

    def __init__(self):
        self._widget = QWidget()
        # id, name, shortcut_key, callback, widget
        super(__class__, self).__init__("", "", "", lambda: None, self._widget)
