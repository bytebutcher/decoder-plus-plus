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
import json
import logging
import os.path
from abc import abstractmethod
from typing import Callable

from lxml import etree

from dpp.core.exceptions import CodecException
from dpp.core import plugin
from dpp.core.icons import Icon
from dpp.core.plugin.config import options
from dpp.core.plugin.config.ui import Layout
from dpp.core.plugin.config.ui.layouts import HBoxLayout
from dpp.core.plugin.config.ui.widgets import Button, Option


class Plugin(plugin.ScriptPlugin):
    """ Script for transforming various file formats into JSON using jc. """

    class Option(object):
        Format = plugin.config.Label("format", "Format:")

    def __init__(self, context: 'dpp.core.context.Context'):
        # Name, Author, Dependencies
        super().__init__('JSONify', "Thomas Engel", ['jc', 'validators'], context, Icon.EDIT)
        self.config.add(plugin.config.options.ComboBox(
            label=Plugin.Option.Format,
            value='csv',
            values=[
                'acpi',
                'airport',
                'airport-s',
                'arp',
                'asciitable',
                'asciitable-m',
                'blkid',
                'cef',
                'cef-s',
                'chage',
                'cksum',
                'crontab',
                'crontab-u',
                'csv',
                'csv-s',
                'date',
                'df',
                'dig',
                'dir',
                'dmidecode',
                'dpkg-l',
                'du',
                'email-address',
                'env',
                'file',
                'finger',
                'free',
                'fstab',
                'git-log',
                'git-log-s',
                'gpg',
                'group',
                'gshadow',
                'hash',
                'hashsum',
                'hciconfig',
                'history',
                'hosts',
                'id',
                'ifconfig',
                'ini',
                'iostat',
                'iostat-s',
                'ip-address',
                'iptables',
                'iso-datetime',
                'iw-scan',
                'jar-manifest',
                'jobs',
                'jwt',
                'kv',
                'last',
                'ls',
                'ls-s',
                'lsblk',
                'lsmod',
                'lsof',
                'lsusb',
                'm3u',
                'mdadm',
                'mount',
                'mpstat',
                'mpstat-s',
                'netstat',
                'nmcli',
                'ntpq',
                'passwd',
                'pidstat',
                'pidstat-s',
                'ping',
                'ping-s',
                'pip-list',
                'pip-show',
                'plist',
                'postconf',
                'ps',
                'route',
                'rpm-qi',
                'rsync',
                'rsync-s',
                'sfdisk',
                'shadow',
                'ss',
                'stat',
                'stat-s',
                'sysctl',
                'syslog',
                'syslog-s',
                'syslog-bsd',
                'syslog-bsd-s',
                'systemctl',
                'systemctl-lj',
                'systemctl-ls',
                'systemctl-luf',
                'systeminfo',
                'time',
                'timedatectl',
                'timestamp',
                'top',
                'top-s',
                'tracepath',
                'traceroute',
                'ufw',
                'ufw-appinfo',
                'uname',
                'update-alt-gs',
                'update-alt-q',
                'upower',
                'uptime',
                'url',
                'vmstat',
                'vmstat-s',
                'w',
                'wc',
                'who',
                'x509-cert',
                'xml',
                # 'xrandr',  # Does not work correctly.
                'yaml',
                'zipinfo'
            ],
            description="the format of the input text.",
            is_required=True,
        ))
        self._codec = JC()

    def _create_options_layout(self, input_text: str) -> Layout:
        return HBoxLayout(widgets=[
            Option(Plugin.Option.Format),
            Button(
                label="Auto-Detect",
                on_click=lambda event: self._auto_detect_format(self._config, input_text)
            )
        ])

    def _auto_detect_format(self, config, input_text):
        input_format = self._codec.auto_detect_format(config, input_text)
        if input_format:
            config.update({Plugin.Option.Format.key: input_format})

    @property
    def title(self):
        return "{} {}".format("JSONify", self.config.value(Plugin.Option.Format))

    def run(self, input_text: str) -> str:
        return self._codec.run(self.config, input_text)


class JC:
    """ Codec for transforming various file formats into JSON using jc. """

    class ParserBase:

        def __init__(self, input_format: str, input_text: str):
            self._logger = logging.getLogger(__name__)
            self._input_format = input_format
            self._input_text = input_text
            self._output_text = ""

        def pre_check(self) -> bool:
            """ Checks the input text whether it conforms to a specific format. """
            try:
                for line in self._input_text.splitlines():
                    if not self.pre_check_line(line):
                        return False
                return True
            except Exception as err:
                self._logger.trace(err)
                return False

        @abstractmethod
        def pre_check_line(self, line) -> bool:
            ...

        def post_check(self) -> bool:
            """ Checks the output text whether it conforms to a specific format. """
            output_text = self.parse()
            if '"unparsable"' in output_text:
                return False
            return True

        def check(self) -> bool:
            """ Checks the input/output text whether it conforms to a specific format. """
            if self.pre_check():
                return self.post_check()
            return False

        def _check_true(self, callback: Callable) -> bool:
            """ Executes the callback. Returns either the return value of the callback, or False on exception. """
            try:
                return callback()
            except:
                return False

        def parse(self) -> str:
            """ Parses the input text and returns a json representation. """
            if not self._output_text:
                import jc
                self._output_text = json.dumps(jc.parse(self._input_format, self._input_text))
            return self._output_text

    class Parser(ParserBase):

        def __init__(self, input_format: str, input_text: str, callback: Callable = None):
            super().__init__(input_format, input_text)
            self._callback = callback

        def check(self) -> bool:
            if self._callback:
                return self._callback()
            return self.post_check()

    class CsvParser(ParserBase):

        def pre_check(self) -> bool:
            """ Check that for all lines do have the same number of colons. """
            expected_number_of_colons = -1
            for line in self._input_text.splitlines():
                if line.startswith('#'):
                    continue

                number_of_colons = line.count(',')
                if number_of_colons == 0:
                    return False

                is_expected_number_of_colons_initialized = expected_number_of_colons != -1
                if not is_expected_number_of_colons_initialized:
                    expected_number_of_colons = number_of_colons
                    continue

                does_number_of_colons_differ = expected_number_of_colons != number_of_colons
                if does_number_of_colons_differ:
                    return False

            is_number_of_colons_initialized = expected_number_of_colons != -1
            return is_number_of_colons_initialized

    class DuParser(ParserBase):

        def pre_check_line(self, line) -> bool:
            if line.startswith('#'):
                # du has no comments
                return False
            size, file = line.split()
            if not os.path.isfile(file):
                return False
            return True

    class FstabParser(ParserBase):

        def pre_check_line(self, line: str) -> bool:
            if line.startswith('#'):
                # fstab may have comments
                return True

            # Test whether split works. Expecting six parts. Throws exception otherwise.
            _file_system, _mount_point, _fs_type, _options, _dump, _pass = line.split()
            return True

    class IpAddressParser(ParserBase):

        def pre_check(self) -> bool:
            import validators
            return \
                self._check_true(lambda: validators.ip_address.ipv4(self._input_text)) or \
                self._check_true(lambda: validators.ip_address.ipv6(self._input_text))

    class LsParser(ParserBase):

        def pre_check_line(self, line: str) -> bool:
            return os.path.isfile(line) or os.path.isdir(line)

    class XmlParser(ParserBase):

        def pre_check(self) -> bool:
            return self._check_true(lambda: etree.fromstring(self._input_text) != None)

    class YamlParser(ParserBase):

        def pre_check(self) -> bool:
            from ruamel import yaml
            return self._check_true(lambda: yaml.safe_dump(self._input_text) != None)


    def __init__(self):
        import validators
        self._logger = logging.getLogger(__name__)
        self._auto_detect_skip_list = [
            'airport-s',
            'asciitable',
            'gpg',
            'hash',
            'pip-list',
            'systemctl',
            'systemctl-lj',
            'systemctl-ls',
            'systemctl-luf',
            'uname'
        ]
        self._pre_validators = {
            'csv': lambda input_text: JC.CsvParser('csv', input_text),
            'df': lambda input_text: JC.Parser('df', input_text, callback=lambda: 'Filesystem' in input_text and 'Size' in input_text),
            'du': lambda input_text: JC.DuParser('du', input_text),
            'free': lambda input_text: JC.Parser('free', input_text, callback=lambda: 'total' in input_text and 'Mem:' in input_text),
            'fstab': lambda input_text: JC.FstabParser('fstab', input_text),
            'email-address': lambda input_text: JC.Parser('email-address', input_text, callback=lambda: validators.email(input_text)),
            'lsmod': lambda input_text: JC.Parser('lsmod', input_text, callback=lambda: 'Module' in input_text and 'Size' in input_text),
            'lsof': lambda input_text: JC.Parser('lsof', input_text, callback=lambda: 'NODE NAME' in input_text),
            'ls': lambda input_text: JC.LsParser('ls', input_text),
            'ip-address': lambda input_text: JC.IpAddressParser('ip-address', input_text),
            'ntpq': lambda input_text: JC.Parser('ntpq', lambda: '==========' in input_text),
            'ps': lambda input_text: JC.Parser('ps', lambda: 'PID' in input_text),
            'url': lambda input_text: JC.Parser('url', lambda: validators.url(input_text)),
            'xml': lambda input_text: JC.XmlParser('xml', input_text),
            'yaml': lambda input_text: JC.YamlParser('yaml', input_text)
        }

    def validate_input_format(self, input_format, input_text) -> bool:
        try:
            return self._pre_validators[input_format](input_text)
        except Exception as err:
            self._logger.trace(err)
            return False

    def auto_detect_format(self, config, input_text) -> str:
        """
        Tries to auto-detect the format.
        :param config: the configuration containing all available formats.
        :param input_text: the input string.
        :return: the auto-detected format or None if no format could be detected.
        """
        self._logger.debug(f'Looking for matching formats for "{input_text}" ...')
        input_formats = config.option(Plugin.Option.Format).values
        best_candidate_input_format = ''
        best_candidate_output_text = ''
        for input_format in input_formats:
            try:
                self._logger.debug(f'Checking for {input_format} ...')
                if input_format in self._auto_detect_skip_list:
                    self._logger.debug(f'Skipping {input_format} ...')
                    continue
                if input_format in self._pre_validators:
                    parser = self._pre_validators[input_format](input_text)
                else:
                    parser = JC.Parser(input_format, input_text)

                if not parser.check():
                    self._logger.debug(f'Input text seems not to be {input_format}! Skipping ...')
                    continue

                output_text = parser.parse()
                self._logger.debug(f'Transforming to {input_format} succeeded!')

                if len(output_text) > len(best_candidate_output_text):
                    self._logger.debug(f'Choosing {input_format} temporarily as best candidate ...')
                    best_candidate_output_text = output_text
                    best_candidate_input_format = input_format
            except:
                self._logger.debug(f'Transforming to {input_format} failed!')
                continue

        return best_candidate_input_format

    def _run(self, input_format, input_text):
        import jc
        return json.dumps(jc.parse(input_format, input_text))

    def run(self, config, input_text):
        """
        Transforms the input text to JSON.
        :param config: the input parameters.
        :param input_text: the input string.
        :return: JSON.
        """
        input_format = config.value(Plugin.Option.Format)
        try:
            return self._run(input_format, input_text)
        except Exception as err:
            self._logger.debug(err, exc_info=True)
            raise CodecException(f'Transforming input from {input_format} to JSON failed!')
