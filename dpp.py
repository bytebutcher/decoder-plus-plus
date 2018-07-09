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

import sys
import argparse

from PyQt5.QtWidgets import QApplication

from core.argparse.ordered_multi_args import OrderedMultiArgs
from core.argparse.single_args import SingleArgs
from core.command import Command
from core.context import Context
from core.decoder_plus_plus import Decoder, Encoder, Hasher, Script, DecoderPlusPlus
from ui import MainWindow


def get_safe_name(name):
    keepcharacters = ('_')
    name = name.lower().replace(" ", "_").replace("+", "plus").replace("-", "_")
    name = "".join(c for c in name if c.isalnum() or c in keepcharacters).rstrip()
    return name


def init_builder(commands, clazz, type):
    for command in commands.filter(type=type):
        if not command.name():
            continue
        def runner(command):
            def _runner(self):
                self._input = command.run(self._input)
                return self
            return _runner
        setattr(clazz, get_safe_name(command.name()), runner(command))


def setup_syntax_completion():
    try:
        import readline
    except ImportError:
        pass
    else:
        import rlcompleter
        readline.parse_and_bind("tab: complete")


def required_length(nmin,nmax):
    class RequiredLength(OrderedMultiArgs):
        def __call__(self, parser, args, values, option_string=None):
            super(RequiredLength, self).__call__(parser, args, values, option_string)
            if not nmin<=len(values)<=nmax:
                msg='Argument "{f}" requires between {nmin} and {nmax} arguments, {num} given!'.format(
                    f=self.dest,nmin=nmin,nmax=nmax, num=len(values))
                raise argparse.ArgumentTypeError(msg)
            setattr(args, self.dest, values)
    return RequiredLength


def get_input(context, args):
    assert bool(args.file) != bool(args.text), "Either file or text should be used."
    if args.file:
        try:
            with open(args.file, "r") as f:
                return f.read()
        except:
            context.logger().error("Error loading {file}. Aborting ...".format(file=args.file))
            sys.exit(1)
    if args.text:
        return args.text


def get_action_type(context, builder, name):
    return getattr(builder, name)


def get_action_command(context, action_type_name, action_type_method, method_name):
    try:
        return getattr(action_type_method(), method_name)
    except Exception as e:
        context.logger().error('No {type}-method named "{name}". Aborting ...'.format(type=action_type_name, name=method_name))
        sys.exit(1)


if __name__ == '__main__':
    try:
        # Loads logger, config and plugins.
        context = Context()

        # Builders can be used in interactive shell or within the ui's code-view.
        commands = context.commands()
        init_builder(commands, Decoder, Command.Type.DECODER)
        init_builder(commands, Encoder, Command.Type.ENCODER)
        init_builder(commands, Hasher, Command.Type.HASHER)
        init_builder(commands, Script, Command.Type.SCRIPT)

        parser = argparse.ArgumentParser()
        parser.add_argument('-t', '--text', action=SingleArgs,
                            help="Specifies the input-text")
        parser.add_argument('-f', '--file', action=SingleArgs,
                            help="Specifies the input-file")
        parser.add_argument('-i', '--interactive', action='store_true',
                            help="Drops into an interactive python shell")
        parser.add_argument('-e', '--encode', dest="encode", action=OrderedMultiArgs,
                            help="Encodes the input using the specified codec(s).")
        parser.add_argument('-d', '--decode', action=OrderedMultiArgs,
                            help="Decodes the input using the specified codec(s)")
        parser.add_argument('-a', '--hash', action=OrderedMultiArgs,
                            help="Transforms the input using the specified hash-functions")
        parser.add_argument('-s', '--script', nargs='+', action=required_length(1, 2),
                            help="Transforms the input using the specified script (optional arguments)")

        args = parser.parse_args()
        if not args.encode and not args.decode and not args.script and not args.hash and not args.interactive:
            # Start GUI when no other parameters were used.
            try:
                app = QApplication(sys.argv)
                ex = MainWindow(context)
                sys.exit(app.exec_())
            except Exception as e:
                context.logger().error("Unexpected Exception: {}".format(e))
                sys.exit(1)

        if args.interactive:
            setup_syntax_completion()
            from ptpython.repl import embed
            print("{app_name} {app_version}".format(app_name=context.config().getName(), app_version=context.config().getVersion()))
            embed(globals=globals(), locals=locals())
            sys.exit(0)

        if not args.encode and not args.decode and not args.script and not args.hash:
            context.logger().error("No action specified!")
            sys.exit(1)

        if not args.file and not args.text:
            context.logger().error("No input specified!")
            sys.exit(1)

        if args.file and args.text:
            context.logger().error("Argument --file and --text can not be used in together.")
            sys.exit(1)

        input = get_input(context, args)

        builder = DecoderPlusPlus(input)
        for name, values in args.ordered_args:
            method_name = values.pop()
            action_type = get_action_type(context, builder, name)
            action_command = get_action_command(context, name, action_type, method_name)
            builder = action_command(*values)

        print(builder.run())
    except Exception as e:
        context.logger().error(e)

