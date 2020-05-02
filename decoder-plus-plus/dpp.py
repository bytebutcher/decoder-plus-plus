#!/usr/bin/env python3
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
import signal
import sys
import argparse
from typing import List

from PyQt5.QtWidgets import QApplication

from core.argparse.ordered_multi_args import OrderedMultiArgs
from core.argparse.single_args import SingleArgs
from core.context import Context
from core.decoder_plus_plus import Decoder, Encoder, Hasher, Script, DecoderPlusPlus
from core.plugin.plugin import PluginType

from ui.decoder_plus_plus_gui import DecoderPlusPlusDialog, DecoderPlusPlusWindow
from ui.single_instance import SingleInstance

# Abort program execution on ctrl+c
signal.signal(signal.SIGINT, signal.SIG_DFL)


def init_builder(context: 'core.context.Context'):

    def _init_builder(plugin: 'core.plugin.plugins.PluginHolder', clazz):
        def list(self) -> List[str]:
            return [method for method in dir(self) if not method.startswith("_") and
                    method not in ["list", "decode", "encode", "hash", "script", "run"]]

        # Add list method to clazz.
        setattr(clazz, "list", lambda this: list(this))

        # Add plugins to clazz.
        def runner(_plugin):
            def _runner(self):
                self._input = _plugin.run(self._input)
                return self
            return _runner

        setattr(clazz, plugin.method_name(), runner(plugin))

    plugins = context.plugins()
    clazz_map = {PluginType.ENCODER: Encoder, PluginType.DECODER: Decoder, PluginType.HASHER: Hasher, PluginType.SCRIPT: Script}
    for plugin in plugins.plugins():
        if not plugin.type() in clazz_map:
            context.logger().debug("Can not load plugin '{}'! Invalid type '{}'!".format(plugin.name(), plugin.type()))
            continue

        _init_builder(plugin, clazz_map[plugin.type()])


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
    if args.file:
        try:
            with open(args.file, "r") as f:
                return f.read()
        except:
            context.logger().error("Error loading {file}. Aborting ...".format(file=args.file))
            sys.exit(1)
    if args.input:
        return args.input


def get_action_type(context, builder, name):
    return getattr(builder, name)


def get_plugin_action(context, action_type_name, action_type_method, method_name):
    try:
        return getattr(action_type_method(), method_name)
    except Exception as e:
        context.logger().error(
            'No {type}-method named "{name}". Aborting ...'.format(type=action_type_name, name=method_name))
        sys.exit(1)


if __name__ == '__main__':
    # Loads logger, config and plugins.
    context = Context("net.bytebutcher.decoder_plus_plus", namespace=locals())

    try:

        # Builders can be used in interactive shell or within the ui's code-view.
        init_builder(context)

        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('-?', '--help', action='store_true',
                            help="show this help message and exit")
        parser.add_argument('input', nargs='?',
                            help="specifies the input-text")
        parser.add_argument('-f', '--file', action=SingleArgs,
                            help="specifies the input-file")
        parser.add_argument('-i', '--interactive', action='store_true',
                            help="drops into an interactive python shell")
        parser.add_argument('--new-instance', action='store_true',
                            help="opens new instance instead of new tab in already running instance.")
        parser.add_argument('--dialog', action='store_true',
                            help="opens a dialog which returns the transformed text when done.")
        parser.add_argument('-e', '--encode', dest="encode", action=OrderedMultiArgs,
                            help="encodes the input using the specified codec(s).")
        parser.add_argument('-d', '--decode', action=OrderedMultiArgs,
                            help="decodes the input using the specified codec(s)")
        parser.add_argument('-h', '--hash', action=OrderedMultiArgs,
                            help="transforms the input using the specified hash-functions")
        parser.add_argument('-s', '--script', nargs='+', action=required_length(1, 2),
                            help="transforms the input using the specified script (optional arguments)")
        parser.add_argument('--debug', action='store_true',
                            help="activates debug mode with extensive logging. Output will be written into dpp.log "
                                 "inside the application directory.")

        args = parser.parse_args()
        if args.help:
            parser.print_help()
            sys.exit(0)

        if args.debug:
            # Enable debug mode for current session.
            context.setDebugMode(True, temporary=True)

        if not args.encode and not args.decode and not args.script and not args.hash and not args.interactive:
            # Start GUI when no other parameters were used.
            try:
                app = QApplication(sys.argv)
                instance = SingleInstance(app, context.getAppID())
                input = get_input(context, args)
                if args.dialog:
                    context.logger().info("Starting Decoder++ Dialog...")
                    ex = DecoderPlusPlusDialog(context, input)
                    sys.exit(app.exec_())
                if instance.isAlreadyRunning():
                    context.logger().info("Application is already running...")
                    if args.new_instance:
                        context.logger().info("Starting Decoder++ GUI in new instance...")
                        ex = DecoderPlusPlusWindow(context, input)
                        sys.exit(app.exec_())
                    else:
                        context.logger().info("Opening new tab in already running instance...")
                        instance.newTab(input)
                        sys.exit(0)
                else:
                    context.logger().info("Starting Decoder++ GUI...")
                    ex = DecoderPlusPlusWindow(context, input)
                    instance.received.connect(ex.newTab)
                    sys.exit(app.exec_())
            except Exception as e:
                context.logger().exception("Unexpected Exception: {}".format(e), exc_info=context.isDebugModeEnabled())
                sys.exit(1)

        if args.interactive:
            setup_syntax_completion()
            import code
            print("Loading {app_name} ({app_version})".format(app_name=context.config().getName(),
                                                              app_version=context.config().getVersion()))
            code.InteractiveConsole(locals=globals()).interact()
            sys.exit(0)

        if not args.encode and not args.decode and not args.script and not args.hash:
            context.logger().error("No action specified!")
            sys.exit(1)

        if not args.file and not args.input:
            context.logger().error("No input specified!")
            sys.exit(1)

        if args.file and args.input:
            context.logger().error("Argument --file and input can not be used together.")
            sys.exit(1)

        input = get_input(context, args)

        builder = DecoderPlusPlus(input)
        for name, values in args.ordered_args:
            method_name = values.pop()
            action_type = get_action_type(context, builder, name)
            plugin_action = get_plugin_action(context, name, action_type, method_name)
            builder = plugin_action(*values)

        print(builder.run())
    except Exception as e:
        context.logger().exception(e, exc_info=context.isDebugModeEnabled())
