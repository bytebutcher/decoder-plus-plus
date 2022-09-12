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
import argparse


class SingleArgs(argparse.Action):
    """ Defines an Argparse-Action which allows specifying an argument only once.

    Example:

        parser = argparse.ArgumentParser()
        parser.add_argument('--test1', action=SingleArgs)
        parser.add_argument('--test2', action=SingleArgs)

        parser.parse_args(['--test2', '2', '--test1', '1', '--test2', '3'])
        argparse.ArgumentTypeError: Argument "test2" can only be used once!

    """

    def __call__(self, parser, args, values, option_string=None):
        if getattr(args, self.dest) is not None:
            raise argparse.ArgumentTypeError('Argument "{f}" can only be used once!'.format(f=self.dest))
        setattr(args, self.dest, values)


class OrderedMultiArgs(argparse.Action):
    """ Defines an Argparse-Action which allows to specify an argument multiple times while order is preserved.

    Example:

        parser = argparse.ArgumentParser()
        parser.add_argument('--test1', action=CustomAction)
        parser.add_argument('--test2', action=CustomAction)

        parser.parse_args(['--test2', '2', '--test1', '1', '--test2', '3'])
        Namespace(ordered_args=[('test2', ['2']), ('test1', ['1']), ('test2', ['3'])], test1=True, test2=True)

    """

    def __call__(self, parser, args, values, option_string=None):
        if not 'ordered_args' in args:
            setattr(args, 'ordered_args', [])
        previous = args.ordered_args
        if type(values) != list:
            values = [values]
        previous.append((self.dest, values))
        setattr(args, 'ordered_args', previous)
        setattr(args, self.dest, True)
