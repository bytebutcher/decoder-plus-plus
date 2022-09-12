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
from dpp.core.icons import Icon, icon
from dpp.ui import IconLabel


class VSep(IconLabel):
    """ Widget which draws a vertical separator. """

    def __init__(self, parent=None):
        super(VSep, self).__init__(parent, icon(Icon.SEPARATOR_V))
        self.setDisabled(True) # just for the effect


class HSep(IconLabel):
    """ Widget which draws a horizontal separator. """

    def __init__(self, parent=None):
        super(VSep, self).__init__(parent, icon(Icon.SEPARATOR_H))
        self.setDisabled(True) # just for the effect
