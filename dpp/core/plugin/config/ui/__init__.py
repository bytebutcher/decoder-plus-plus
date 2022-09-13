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
import uuid
from typing import List

from dpp.core.assertions import assert_type, assert_instance


class Layout:

    def __init__(self, widgets=None):
        self.widgets = widgets if not None else []
        self.key = str(uuid.uuid4())

    def __str__(self):
        return self.key


class Widget:

    def __init__(self, key: str = None, label: str = None, show_label: bool = True, layout: Layout = None,
                 widgets: List['Widget'] = None):
        assert_type(key, str, allow_none=True)
        assert_type(label, str, allow_none=True)
        assert_type(show_label, bool, allow_none=True)
        assert_instance(layout, Layout, allow_none=True)
        assert_instance(widgets, Widget, allow_none=True, is_list=True)
        self.label = label
        self.show_label = show_label
        self.layout = layout
        self.widgets = widgets
