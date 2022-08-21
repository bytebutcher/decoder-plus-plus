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
from qtpy.QtWidgets import QMenu, QMenuBar


class MenuBar:

    def __init__(self, menu_bar: QMenuBar):
        self._menu_bar = menu_bar
        self._menus = {}

    def addMenu(self, title) -> QMenu:
        self._menus[title] = self._menu_bar.addMenu(title)
        return self._menus[title]

    def hasMenu(self, title) -> bool:
        return title in self._menus

    def getMenu(self, title) -> QMenu:
        return self._menus[title]
