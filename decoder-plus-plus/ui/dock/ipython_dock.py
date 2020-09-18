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
#
import os

import qtawesome
from PyQt5.QtWidgets import QWidget, QFrame, QHBoxLayout

from core.decoder_plus_plus import DecoderPlusPlus
from ui.widget.dock_widget import DockWidget
from ui.widget.ipython_widget import IPythonWidget


class IPythonDock(DockWidget):
    """ A widget to interact with an IPython console. """

    class Printer(object):
        """ Allows printing to the console while correctly interpreting newlines. """

        def __init__(self, lines):
            self.__lines = lines

        def __repr__(self):
            return "\n".join(self.__lines)

    def __init__(self, context: 'core.context.Context', parent: QWidget):
        super(IPythonDock, self).__init__("IPython Console", qtawesome.icon("fa.terminal"), parent)
        self._context = context
        widget = IPythonWidget(
            banner=os.linesep.join([
                'Decoder++ IPython Console v{version}'.format(version=self._context.getAppVersion()),
                'Type "copyright", "credits", "license" or "help" for more information.',
                'Type "encoders()", "decoders()", "hashes()" or "scripts()" to show a list of codecs.',
                'Type "usage()" to show general usage information.'
            ]),
            namespace=self._context.namespace(),
            variables={
                "usage": IPythonDock.Printer([
                    'dpp(<input>).',
                    '   encode().base64().base32().',
                    '   decode().base32().',
                    '   hash().md5().',
                    '   script().clone().',
                    '   run()'
                ]),
                "encoders": IPythonDock.Printer(DecoderPlusPlus("").encode().list()),
                "decoders": IPythonDock.Printer(DecoderPlusPlus("").decode().list()),
                "hashes": IPythonDock.Printer(DecoderPlusPlus("").hash().list()),
                "scripts": IPythonDock.Printer(DecoderPlusPlus("").script().list()),
                "dpp": DecoderPlusPlus
            })
        widget.console_height = 1
        self.addWidget(widget)
