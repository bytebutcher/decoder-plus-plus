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
from qtconsole.inprocess import QtInProcessKernelManager
from IPython.lib import guisupport
from qtconsole.rich_jupyter_widget import RichJupyterWidget


class IPythonWidget(RichJupyterWidget):
    """ Convenience class for a live IPython console widget. """

    def __init__(self, banner=None, namespace=None, variables=None, *args,**kwargs):
        super(RichJupyterWidget, self).__init__(*args, **kwargs)
        self.kernel_manager = kernel_manager = QtInProcessKernelManager()
        kernel_manager.start_kernel()

        if banner:
            # Disable the default banner when the user passed a custom one
            kernel_manager.kernel.shell.banner1 = ""
            # Set custom banner
            self.banner = banner

        kernel_manager.kernel.gui = 'qt'
        self.kernel_client = kernel_client = self._kernel_manager.client()
        kernel_client.start_channels()

        if namespace:
            # Set custom namespace if any
            kernel_client.namespace = namespace

        kernel_manager.kernel.shell.push(variables)

        def stop():
            kernel_client.stop_channels()
            kernel_manager.shutdown_kernel()
            guisupport.get_app_qt4().exit()
        self.exit_requested.connect(stop)

    def pushVariables(self,variableDict):
        """ Given a dictionary containing name / value pairs, push those variables to the IPython console widget """
        self.kernel_manager.kernel.shell.push(variableDict)

    def clearTerminal(self):
        """ Clears the terminal """
        self._control.clear()

    def printText(self,text):
        """ Prints some plain text to the console """
        self._append_plain_text(text)

    def executeCommand(self,command):
        """ Execute a command in the frame of the console widget """
        self._execute(command,False)