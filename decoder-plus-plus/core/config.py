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


from PyQt5.QtCore import QSettings, QSize


class Config(QSettings):
    """ The main settings of the application. """

    def __init__(self, logger):
        super().__init__('net.bytebutcher', 'decoder++')
        self._logger = logger

    def getName(self) -> str:
        """ Returns the name of the application. """
        return "Decoder++"

    def getVersion(self) -> str:
        """ Returns the version of the application. """
        return "0.90"

    def getSize(self) -> QSize:
        """
        Returns the saved window size of the application.
        When no size was specified a default size will be returned.
        """
        return self.value('size', QSize(640, 440))

    def getPosition(self) -> int:
        """ Returns the saved position of the window."""
        return self.value('position')

    def setSize(self, size: QSize):
        """ Stores the size of the window. """
        self.setValue('size', size)

    def setPosition(self, position: int):
        """ Stores the position of the window. """
        self.setValue('position', position)

    def setShortcutKey(self, id: str, shortcut_key: str):
        """ Stores a shortcut key. """
        self.setValue('shortcut.{}'.format(id), shortcut_key)

    def getShortcutKey(self, id: str):
        """ Returns a saved shortcut key or None when no shortcut were defined for the specified id. """
        return self.value('shortcut.{}'.format(id))



