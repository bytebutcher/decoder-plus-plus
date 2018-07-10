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

    def __init__(self, logger):
        super().__init__('net.bytebutcher', 'decoder++')
        self._logger = logger

    def getName(self):
        return "Decoder++"

    def getVersion(self):
        return "0.90"

    def getSize(self):
        return self.value('size', QSize(640, 440))

    def getPosition(self):
        return self.value('position')

    def setSize(self, size):
        self.setValue('size', size)

    def setPosition(self, position):
        self.setValue('position', position)

    def setShortcut(self, key, shortcut):
        self.setValue('shortcut.{}'.format(key), shortcut)

    def getShortcut(self, key):
        return self.value('shortcut.{}'.format(key))



