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
import os
import unittest

plugins_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'plugins'))
test_path = os.path.dirname(os.path.realpath(__file__))


def load_tests_from_path(suite, loader, filter, path):
    for r, d, f in os.walk(path):
        module_path = os.path.relpath(r, os.path.dirname(test_path)).replace(os.path.sep, ".")
        for file in f:
            filename, ext = os.path.splitext(file)
            if ext == ".py" and not file.startswith("_"):
                if not filter or module_path + "." + filename in filter:
                    print("[ADD ] " + module_path + "." + filename)
                    test = loader.loadTestsFromName(module_path + "." + filename)
                    suite.addTest(test)
                else:
                    print("[SKIP] " + module_path + "." + filename)


def load_tests(loader, filter):
    """ Load all test cases and return a unittest.TestSuite object. """
    suite = unittest.TestSuite()
    for path in [test_path, plugins_path]:
        load_tests_from_path(suite, loader, filter, path)
    return suite
