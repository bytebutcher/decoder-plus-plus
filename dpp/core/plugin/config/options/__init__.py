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
from dpp.core.plugin.config import Option


class String(Option):

    def __init__(self, label, value, description, is_required=True):
        """
        :param value: the string (e.g. "ab cd ef gh ij kl mn op qr st uv wx yz").
        """
        super(String, self).__init__(label, value, description, is_required)


class Text(String):

    def __init__(self, label, value, description, is_required=True, read_only=False, wrap_lines=False):
        """
        :param value: the text (e.g. "ab\ncd\nef\ngh\nij\nkl\nmn\nop\nqr\nst\nuv\nwx\nyz").
        """
        super(Text, self).__init__(label, value, description, is_required)
        self.read_only = read_only
        self.wrap_lines = wrap_lines


class Integer(Option):

    def __init__(self, label, value, description, is_required, range=None):
        """
        :param value: the integer (e.g. ..., -2, -1, 0, 1, 2, ...).
        :param range: a list containing the minimum and maximum (e.g. [-2, 2])
        """
        super(Integer, self).__init__(label, value, description, is_required)
        self.range = range


class Slider(Integer):

    def __init__(self, label, value, description, is_required, range):
        """
        :param value: the integer (e.g. ..., -2, -1, 0, 1, 2, ...).
        :param range: a list containing the minimum and maximum (e.g. [-2, 2])
        """
        super(Slider, self).__init__(label, value, description, is_required, range)


class Boolean(Option):

    def __init__(self, label, value, description, is_required):
        """
        :param value: the boolean value (e.g. True/False).
        """
        super(Boolean, self).__init__(label, value, description, is_required)

    @property
    def is_checked(self):
        return bool(self.value)


class Group(Boolean):
    """ An option with group name and checked status. """

    def __init__(self, label, value, description, is_required, group_name):
        """
        :param group_name: defines whether the option is associated with another group of options.
        """
        super(Group, self).__init__(label, value, description, is_required)
        self.group_name = group_name


class ComboBox(Option):

    def __init__(self, label, value, values, description, is_required):
        """
        :param value: the selected value.
        :param values: the available values to select.
        """
        super(ComboBox, self).__init__(label, value, description, is_required)
        self.values = values


class CodeEditor(Option):

    def __init__(self, label, value, description, is_required):
        """
        :param value: the source code (e.g. "def run(input_text):\n\treturn input_text").
        """
        super(CodeEditor, self).__init__(label, value, description, is_required)