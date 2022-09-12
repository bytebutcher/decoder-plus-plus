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
from typing import Callable


class Signal:
    """ A custom implementation of the Qt Signal without the class required to inherit from QObject.

    Usage:

    class FooBar:

        onChange = Singal('str')

        def __init__(self):
            self._foo = 'bar'

        @property
        def foo(self):
            return self._foo

        @foo.setter
        def foo(self, value):
            self._foo = value
            self.onChange.emit(self._foo)


    bar = FooBar()
    bar.onChange.connect(lambda foo: print(foo))

    """

    def __init__(self, *args):
        self._args = args
        self._callbacks = []

    def connect(self, callback: Callable):
        self._callbacks.append(callback)

    def emit(self, *args):
        assert len(args) == len(self._args), f'Invalid number of arguments! Expected {len(self._args)}, got {len(args)}!'
        for callback in self._callbacks:
            callback(*args)


class Listener:
    """ A set of global signals to emit or connect to. """

    # Signals that a new tab should be created with the specified input text
    newTabRequested = Signal(str, str)  # title, input_text

    # Signals that the selected frame changed (e.g. to update the hex view)
    selectedFrameChanged = Signal(str, str, str)  # tab_id, frame_id, input_text

    # Signals that the text inside the codec frame changed (e.g. to update the hex view)
    textChanged = Signal(str, str, str)  # tab_id, frame_id, input_text

    # Signals that the text selection inside the codec frame changed (e.g. to update the hex view)
    textSelectionChanged = Signal(str, str, str)  # tab_id, frame_id, input_text

    # Signals that text of a codec frame should be changed to the specified text (e.g. when hex view was edited by user)
    textSubmitted = Signal(str, str, str)  # tab_id, frame_id, input_text

    def __init__(self, context: 'core.context.Context'):
        super(__class__, self).__init__()
        # Logs each event when being triggered
        self.newTabRequested.connect(lambda title, input_text:
                                     context.logger.trace("newTabRequested({})".format(input_text)))
        self.selectedFrameChanged.connect(lambda tab_id, frame_id, input_text:
                                          context.logger.trace(
                                              "selectedFrameChanged({}, {}, {})".format(tab_id, frame_id, input_text)))
        self.textChanged.connect(lambda tab_id, frame_id, input_text:
            context.logger.trace("textChanged({}, {}, {})".format(tab_id, frame_id, input_text)))
        self.textSelectionChanged.connect(lambda tab_id, frame_id, input_text:
            context.logger.trace("textSelectionChanged({}, {}, {})".format(tab_id, frame_id, input_text)))
        self.textSubmitted.connect(lambda tab_id, frame_id, input_text:
            context.logger.trace("textSubmitted({}, {}, {})".format(tab_id, frame_id, input_text)))
