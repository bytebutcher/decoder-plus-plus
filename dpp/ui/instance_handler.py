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
from qtpy.QtCore import QObject, Signal
from qtpy.QtNetwork import QLocalServer, QLocalSocket


class InstanceHandler(QObject):
    """ Makes sure that only one instance of this application can be run. """

    received = Signal(str)

    def __init__(self, parent, name):
        super(__class__, self).__init__(parent)
        self._parent = parent
        self._name = name
        self._timeout = 1000
        self._socket = QLocalSocket(self)
        self._socket.connectToServer(self._name)
        self._is_already_running = self._socket.waitForConnected(self._timeout)
        if not self.isAlreadyRunning():
            self._server = QLocalServer(self)
            self._server.newConnection.connect(self._receive_data)
            self._server.removeServer(self._name)
            self._server.listen(self._name)

    def _send_data(self, data=None):
        """ Sends model to an server-application. """
        if not data:
            data = ""
        self._socket.write(data.encode())
        self._socket.waitForBytesWritten(self._timeout)
        self._socket.disconnectFromServer()

    def _receive_data(self):
        """ Receives model from an client-application. """
        socket = self._server.nextPendingConnection()
        if socket.waitForReadyRead(self._timeout):
            # Emit transmitted model.
            self.received.emit(socket.readAll().data().decode("utf-8", "surrogateescape"))
        else:
            # When no model was transmitted just emit empty string.
            self.received.emit("")

    def newTab(self, input_text):
        """ Opens a new tab in an already running instance. """
        self._send_data(input_text)

    def isAlreadyRunning(self) -> bool:
        """ Returns True when an instance of the application is already running, otherwise False. """
        return self._is_already_running
