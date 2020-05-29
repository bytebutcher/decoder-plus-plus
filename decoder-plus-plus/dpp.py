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

# Load fuzzywuzzy while ignoring unnecessary warning about missing levenstein package.
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from fuzzywuzzy import process

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

            def _show_help():
                """ Shows the plugin config options. """

                def _max_length(attr, title):
                    """ :returns the maximum string length of a specific plugin option attribute. """
                    lens = [len(title)]
                    for key in _plugin.config().keys():
                        lens.append(len(str(getattr(_plugin.config().get(key), attr))))
                    return max(lens)

                # Print title
                print(len(_plugin.name()) * '=')
                print(_plugin.name())
                print(len(_plugin.name()) * '=')
                print()

                # Print header
                name_max_length = _max_length("name", "Name")
                value_max_length = _max_length("value", "Value")
                row_format = "{:>" + str(name_max_length) + "}  {:<" + str(value_max_length) + "}  {:<8}  {}"
                print(row_format.format("Name", "Value", "Required", "Description"))
                print(row_format.format("----", "-----", "--------", "-----------"))

                # Print rows
                for key in _plugin.config().keys():
                    option = _plugin.config().get(key)
                    if type(option.value) == type(True):
                        value = "True" if bool(option.value) else "False"
                    else:
                        value = option.value
                    is_required = "yes" if option.is_required else "no"
                    print(row_format.format(option.name, value, is_required, option.description))

            def _natural_join(list):
                """ Joins a list of strings (e.g. ["1", "2", "3"] => "1, 2 and 3"). """
                if not list:
                    return ""
                elif len(list) == 1:
                    return list[0]
                else:
                    return " and ".join([", ".join(list[:-1]), list[-1]])

            def _configure(config):
                invalid_plugin_options = [key for key in config if key not in _plugin.config().keys()]
                if invalid_plugin_options:
                    invalid_plugin_option = invalid_plugin_options[0]
                    suggestions = [result for result in process.extract(invalid_plugin_option, _plugin.config().keys())]
                    suggestion = 'Did you mean "{}"?'.format(suggestions[0][0]) if suggestions else ""
                    context.logger().error("Can not run '{}'! Invalid option {}. {}".format(
                        _plugin.name(safe_name=True), invalid_plugin_option, suggestion))
                    sys.exit(1)

                _plugin.config().update(config)

                unconfigured_plugin_options = _plugin.is_unconfigured()
                if unconfigured_plugin_options:
                    context.logger().error("Can not run '{}'! Missing required option {}.".format(
                        _plugin.name(safe_name=True), _natural_join(unconfigured_plugin_options)))
                    sys.exit(1)

            def _runner(self, **kwargs):
                if "help" in kwargs.keys():
                    _show_help()
                    sys.exit(0)
                if _plugin.is_configurable() and _plugin.is_unconfigured():
                    _configure(kwargs)
                self._input = _plugin.run(self._input)
                return self
            return _runner

        setattr(clazz, plugin.method_name(), runner(plugin))

    plugins = context.plugins()
    clazz_map = {PluginType.ENCODER: Encoder, PluginType.DECODER: Decoder, PluginType.HASHER: Hasher, PluginType.SCRIPT: Script}
    for plugin in plugins.plugins():
        if not plugin.type() in clazz_map:
            context.logger().debug("Can not load plugin '{}'! Invalid type '{}'!".format(plugin.name(safe_name=True), plugin.type()))
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
        plugin_names = [name[:name.rindex('_')] for name in context.plugins().names(safe_names=True)]
        suggestions = [result for result in process.extract(method_name, plugin_names)]
        suggestion = 'Did you mean "{}"?'.format(suggestions[0][0]) if suggestions else ""
        context.logger().error(
            'No {type} named "{name}". {suggestion}'.format(
                type=action_type_name, name=method_name, suggestion=suggestion))
        sys.exit(1)


def get_plugin_config(arguments):
    result = {}
    for argument in arguments:
        sep_index = argument.find('=')
        if sep_index < 1:
            context.logger().error('Invalid argument specification! Expected key=value, got {}'.format(argument))
            sys.exit(1)

        # Parse key=value into name and value
        name = argument[:sep_index]
        value = argument[sep_index+1:]

        # Handle boolean values
        if value is "True" or value is "False":
            value = value is "True"

        result[name] = value
    return result


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
        parser.add_argument('-s', '--script', nargs='+', action=OrderedMultiArgs,
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

        # Command line usage
        input = get_input(context, args)

        builder = DecoderPlusPlus(input)
        for name, values in args.ordered_args:
            method_name = values.pop(0)
            action_type = get_action_type(context, builder, name)
            plugin_action = get_plugin_action(context, name, action_type, method_name)
            show_plugin_help = "help" in values
            plugin_config = get_plugin_config(values) if not show_plugin_help else {"help": True}
            builder = plugin_action(**plugin_config)

        print(builder.run())
    except Exception as e:
        context.logger().exception(e, exc_info=context.isDebugModeEnabled())
