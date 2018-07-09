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

class Shortcut(object):

    def __init__(self, id, name, shortcut, callback):
        self._id = id
        self._name = name
        self._shortcut = shortcut
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
        if self._shortcut:
            return self._shortcut.key().toString()

    def setShortcut(self, shortcut):
        self._shortcut = shortcut

    def callback(self):
        return self._callback
