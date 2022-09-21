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
import logging
import os
import signal
import sys
import argparse
from collections import namedtuple
from typing import List

# Load fuzzywuzzy while ignoring unnecessary warning about missing levenstein package.
import warnings


with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from fuzzywuzzy import process

from qtpy.QtWidgets import QApplication

# FIX #27: Add 'dpp' to package path if not present. 
#          This may happen when dpp was not installed via setup.py.
DPP_PACKAGE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if DPP_PACKAGE_PATH not in sys.path:
    sys.path.append(DPP_PACKAGE_PATH)


from dpp import app_path
from dpp.core.argparse import OrderedMultiArgs
from dpp.core.argparse import SingleArgs
from dpp.core.context import Context
from dpp.core.decoder_plus_plus import Decoder, Encoder, Hasher, Script, DecoderPlusPlus, Identify
from dpp.core.plugin import PluginType

from dpp.ui.decoder_plus_plus_gui import DecoderPlusPlusDialog, DecoderPlusPlusWindow
from dpp.ui.instance_handler import InstanceHandler

# Abort program execution on ctrl+c
signal.signal(signal.SIGINT, signal.SIG_DFL)


def init_builder(context: 'dpp.core.context.Context'):

    def _init_builder(plugin: 'dpp.core.plugin.plugins.PluginHolder', clazz):
        def list(self, filter_terms=()) -> List[str]:
            codecs = [method for method in dir(self) if not method.startswith("_") and
                    method not in ["list", "decode", "encode", "hash", "script", "run"]]
            return [codec for codec in codecs if all(filter_term in codec for filter_term in filter_terms)]

        # Add list method to clazz.
        setattr(clazz, "list", list)

        # Add plugins to clazz.
        def runner(plugin):

            def sys_exit(exit_code):
                """ Wraps the sys.exit call. Only sys.exit in command line mode. """
                if context.mode() == Context.Mode.COMMAND_LINE:
                    sys.exit(exit_code)

            def show_help():
                """ Shows the plugin config options. """

                def max_length(attr, title):
                    """ :returns the maximum string length of a specific plugin option attribute. """
                    lens = [len(title)]
                    for key in plugin.config.keys():
                        if hasattr(plugin.config.option(key), attr):
                            lens.append(len(str(getattr(plugin.config.option(key), attr))))
                    return max(lens)

                # Print title
                print()
                print(plugin.name)
                print(len(plugin.name) * '=')
                print()

                # Print header
                name_max_length = max_length("key", "Name")
                value_max_length = max_length("value", "Value")
                group_max_length = max_length("group_name", "Group")
                row_format = "{:>" + str(name_max_length) + "}  " + \
                             "{:<" + str(value_max_length) + "}  " + \
                             "{:<" + str(group_max_length) + "}  " + \
                             "{:<8}  " + \
                             "{}"
                print(row_format.format("Name", "Value", "Group", "Required", "Description"))
                print(row_format.format("----", "-----", "-----", "--------", "-----------"))

                # Print rows
                for key in plugin.config.keys():
                    option = plugin.config.option(key)
                    if type(option.value) == type(True):
                        value = "True" if bool(option.value) else "False"
                    else:
                        value = option.value
                    group_name = option.group_name if hasattr(option, "group_name") else ""
                    is_required = "yes" if option.is_required else "no"
                    print(row_format.format(option.key, value, group_name, is_required, option.description))

                print()

            def natural_join(list):
                """ Joins a list of strings (e.g. ["1", "2", "3"] => "1, 2 and 3"). """
                if not list:
                    return ""
                elif len(list) == 1:
                    return f"'{list[0]}'"
                else:
                    joined_list = "' and '".join(["', '".join(list[:-1]), list[-1]])
                    return f"'{joined_list}'"

            def update_plugin_config(config):
                invalid_keys = [key for key in config.keys() if key not in plugin.config.keys()]
                if invalid_keys:
                    invalid_plugin_option = invalid_keys[0]
                    suggestions = [result for result in
                                   process.extract(invalid_plugin_option, plugin.config.keys())]
                    suggestion = 'Did you mean "{}"?'.format(suggestions[0][0]) if suggestions else ""
                    raise Exception("Invalid configuration option {}. {}".format(invalid_plugin_option, suggestion))
                plugin.config.update(config)

            def _runner(self, **kwargs):
                do_show_help = kwargs.pop('help', False)

                update_plugin_config(kwargs)
                if do_show_help:
                    show_help()
                    return sys_exit(0)

                unconfigured_plugin_options = plugin.is_unconfigured()
                if unconfigured_plugin_options:
                    context.logger.error("Can not run '{}'! Missing required option {}.".format(
                        plugin.safe_name, natural_join(unconfigured_plugin_options)))
                    return sys_exit(1)

                self._input_text = plugin.run(self._input_text)
                return self
            return _runner

        setattr(clazz, plugin.method_name, runner(plugin))

    plugins = context.plugins()
    clazz_map = {
        PluginType.ENCODER: Encoder,
        PluginType.DECODER: Decoder,
        PluginType.HASHER: Hasher,
        PluginType.SCRIPT: Script,
        PluginType.IDENTIFY: Identify
    }
    for plugin in plugins.plugins():
        if not plugin.type in clazz_map:
            context.logger.debug(f'Can not load plugin {plugin.safe_name}! Invalid type {plugin.type}!')
            continue

        _init_builder(plugin, clazz_map[plugin.type])


def setup_syntax_completion():
    try:
        import readline
    except ImportError:
        pass
    else:
        import rlcompleter
        readline.parse_and_bind("tab: complete")


def setup_excepthook(logger):
    """
    Setup the excepthook which logs uncaught exceptions instead of throwing them around.
    @see https://fman.io/blog/pyqt-excepthook/
    """
    def _excepthook(exc_type, exc_value, exc_tb):
        enriched_tb = _add_missing_frames(exc_tb) if exc_tb else exc_tb
        logger.debug("Uncaught exception", exc_info=(exc_type, exc_value, enriched_tb))

    def _add_missing_frames(tb):
        result = fake_tb(tb.tb_frame, tb.tb_lasti, tb.tb_lineno, tb.tb_next)
        frame = tb.tb_frame.f_back
        while frame:
            result = fake_tb(frame, frame.f_lasti, frame.f_lineno, result)
            frame = frame.f_back
        return result

    fake_tb = namedtuple(
        'fake_tb', ('tb_frame', 'tb_lasti', 'tb_lineno', 'tb_next')
    )

    sys.excepthook = _excepthook


def get_input_text(context, args):
    if args.file:
        try:
            with open(args.file, "r") as f:
                return f.read()
        except:
            context.logger.error("Error loading {file}. Aborting ...".format(file=args.file))
            sys.exit(1)
    if args.input:
        return args.input


def get_action_type(context, builder, name):
    return getattr(builder, name)


def get_plugin_action(context, action_type_name, action_type_method, method_name):
    try:
        return getattr(action_type_method(), method_name)
    except Exception as e:
        plugin_names = [name[:name.rindex('_')] for name in context.plugins().safe_names()]
        suggestions = [result for result in process.extract(method_name, plugin_names)]
        suggestion = 'Did you mean "{}"?'.format(suggestions[0][0]) if suggestions else ""
        context.logger.error(
            'No {type} named "{name}". {suggestion}'.format(
                type=action_type_name, name=method_name, suggestion=suggestion))
        sys.exit(1)


def get_plugin_config(context, arguments):
    result = {}
    for argument in arguments:
        sep_index = argument.find('=')
        if sep_index < 1:
            context.logger.error('Invalid argument specification! Expected key=value, got {}'.format(argument))
            sys.exit(1)

        # Parse key=value into name and value
        name = argument[:sep_index]
        value = argument[sep_index+1:]

        # Handle boolean values
        if value == "True" or value == "False":
            value = value == "True"

        result[name] = value
    return result


def main():
    # Abort program execution on ctrl+c
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Loads logger, config and plugins.
    context = Context('net.bytebutcher.decoder_plus_plus', app_path)

    # Enable debug mode for current session.
    if '--debug' in sys.argv:
        context.setDebugMode(True, temporary=True)

    if '--trace' in sys.argv:
        context.setTraceMode(True)

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
        parser.add_argument('--new-instance', action='store_true',
                            help="opens new instance instead of new tab in already running instance.")
        parser.add_argument('--dialog', action='store_true',
                            help="opens a dialog which returns the transformed text when done.")
        parser.add_argument('-l', '--list-codecs', nargs='*', metavar="FILTER_TERM",
                            help="lists all available codecs or those matching the filter terms.")
        parser.add_argument('-e', '--encode', dest="encode", action=OrderedMultiArgs,
                            help="encodes the input using the specified codec(s).")
        parser.add_argument('-d', '--decode', action=OrderedMultiArgs,
                            help="decodes the input using the specified codec(s)")
        parser.add_argument('-h', '--hash', action=OrderedMultiArgs,
                            help="transforms the input using the specified hash-functions")
        parser.add_argument('-s', '--script', nargs='+', action=OrderedMultiArgs, metavar="OPTION=VALUE",
                            help="transforms the input using the specified script (optional arguments)")
        parser.add_argument('--debug', action='store_true',
                            help="activates debug mode with additional logging.")
        parser.add_argument('--trace', action='store_true',
                            help="activates trace mode with extensive logging.")

        args = parser.parse_args()
        if args.help:
            parser.print_help()
            sys.exit(0)

        if args.script and not args.file and not args.input:
            scripts = [arg[1] for arg in args.ordered_args if arg[0] == 'script']
            args.input = scripts.pop(-1).pop(-1)

        # Start GUI when no other parameters were used.
        if not args.encode and not args.decode and not args.script and not args.hash and not type(args.list_codecs) == list:
            # Setup excepthook to handle uncaught exceptions.
            setup_excepthook(context.logger)
            # Update application mode
            context.setMode(Context.Mode.GUI_MODERN)
            try:
                app = QApplication(sys.argv)
                instance_handler = InstanceHandler(app, context.getAppID())
                input_text = get_input_text(context, args)
                if args.dialog:
                    context.logger.info("Starting Decoder++ Dialog...")
                    ex = DecoderPlusPlusDialog(context, input_text)
                    sys.exit(app.exec_())
                if instance_handler.isAlreadyRunning():
                    context.logger.info("Application is already running...")
                    if args.new_instance:
                        context.logger.info("Starting Decoder++ GUI in new instance...")
                        ex = DecoderPlusPlusWindow(context, input_text)
                        sys.exit(app.exec_())
                    else:
                        context.logger.info("Opening new tab in already running instance...")
                        instance_handler.newTab(input_text)
                        sys.exit(0)
                else:
                    context.logger.info("Starting Decoder++ GUI...")
                    ex = DecoderPlusPlusWindow(context, input_text)
                    # Handle commandline input from users during runtime.
                    instance_handler.received.connect(ex.newTab)
                    sys.exit(app.exec_())
            except Exception as err:
                context.logger.debug(f'Unexpected Exception: {err}', exc_info=True)
                sys.exit(1)

        if type(args.list_codecs) == list:
            filter_terms = args.list_codecs
            row_format = "{:<20}  {}"
            print()
            print(row_format.format("Codec", "Type"))
            print(row_format.format("-----", "----"))
            for plugin in context.plugins():
                plugin_name = plugin.method_name.lower()
                plugin_type = plugin.type.lower()
                if filter_terms:
                    has_match = True
                    for filter_term in filter_terms:
                        filter_term = filter_term.lower()
                        if filter_term not in plugin_name and filter_term not in plugin_type:
                            has_match = False
                            break
                    if not has_match:
                        continue
                print(row_format.format(plugin_name, plugin_type))
            print()
            sys.exit(0)

        if not args.encode and not args.decode and not args.script and not args.hash:
            context.logger.error("No action specified!")
            sys.exit(1)

        if not args.file and not args.input:
            context.logger.error("No input specified!")
            sys.exit(1)

        if args.file and args.input:
            context.logger.error("Argument --file and input can not be used together.")
            sys.exit(1)

        # Command line usage
        context.setMode(Context.Mode.COMMAND_LINE)
        input_text = get_input_text(context, args)
        builder = DecoderPlusPlus(input_text)
        for name, values in args.ordered_args:
            if not values:
                # No input supplied (e.g. dpp --script search_and_replace)
                parser.print_help()
                sys.exit(1)
            method_name = values.pop(0)
            action_type = get_action_type(context, builder, name)
            plugin_action = get_plugin_action(context, name, action_type, method_name)
            show_plugin_help = "help" in values
            plugin_config = get_plugin_config(context, filter(lambda x: x != "help", values))
            if show_plugin_help: plugin_config["help"] = True
            builder = plugin_action(**plugin_config)

        print(builder.run())
    except Exception as err:
        context.logger.error(err)
        context.logger.debug(err, exc_info=True)


if __name__ == '__main__':
    main()
