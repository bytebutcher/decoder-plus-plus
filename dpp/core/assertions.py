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


def _assert(value, expected_type, is_list: bool = False):
    """ Assert, that the value has the expected type.
    :param value: the value being tested.
    :param expected_type: the type of the value which is expected.
    :param is_list: if set to True, the value is a list. All items within this list need to be of the expected type.
                    By default, is_list is set to False.
    """
    if is_list:
        assert isinstance(value, list), f'Expected {expected_type}, got {type(value)}'
        items = value
    else:
        items = [value]

    for item in items:
        yield item


def assert_instance(value, expected_type, is_list: bool = False, allow_none: bool = False):
    """ Assert, that the value is an instance of the expected type.
    :param value: the value being tested.
    :param expected_type: the type of the value which is expected.
    :param is_list: if set to True, the value is a list. All items within this list need to be of the expected type.
                    By default, is_list is set to False.
    :param allow_none: if set to True, the value is allowed to be None.
                       By default, allow_none is set to False.
    """
    if allow_none and value is None:
        return

    for item in _assert(value, expected_type, is_list):
        assert isinstance(item, expected_type), f'Expected {expected_type}, got {type(item)}'


def assert_type(value, expected_type, is_list: bool = False, allow_none: bool = False):
    """ Assert, that the value has the expected type.
    :param value: the value being tested.
    :param expected_type: the type of the value which is expected.
    :param is_list: if set to True, the value is a list. All items within this list need to be of the expected type.
                    By default, is_list is set to False.
    :param allow_none: if set to True, the value is allowed to be None.
                       By default, allow_none is set to False.
    """
    if allow_none and value is None:
        return

    for item in _assert(value, expected_type, is_list):
        assert type(item) == expected_type, f'Expected {expected_type}, got {type(item)}'