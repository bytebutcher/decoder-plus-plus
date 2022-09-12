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
from qtpy.QtCore import Signal, Qt
from qtpy.QtGui import QIntValidator
from qtpy.QtWidgets import QFrame, QHBoxLayout, QSlider, QLineEdit


class SliderWidget(QFrame):

    valueChanged = Signal(int)  # slider value

    def __init__(self, value: int, range):
        super().__init__()
        slider_frame_layout = QHBoxLayout()
        self._shift_slider = QSlider(Qt.Horizontal)
        self._shift_slider.setMinimum(range[0])
        self._shift_slider.setMaximum(range[1])
        self._shift_slider.setValue(value)
        self._shift_slider.valueChanged.connect(self._shift_slider_changed)
        slider_frame_layout.addWidget(self._shift_slider)

        self._shift_text = QLineEdit()
        self._shift_text.setText(str(value))
        self._shift_text.setFixedWidth(30)
        self._shift_text.setValidator(QIntValidator(range[0], range[1]))
        self._shift_text.textChanged.connect(self._shift_text_changed)
        slider_frame_layout.addWidget(self._shift_text)

        slider_frame_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(slider_frame_layout)

    def _shift_slider_changed(self, shift):
        if not shift:
            shift = 0
        self._shift_changed(shift)

    def _shift_text_changed(self, shift):
        if not shift:
            shift = 0
        self._shift_changed(int(shift))

    def _shift_changed(self, shift: int):
        shift_text = int(self._shift_text.text())
        shift_slider = self._shift_slider.value()
        if shift_slider == shift_text == shift:
            # Shift actually did not change.
            return

        self._shift_text.blockSignals(True)
        self._shift_slider.blockSignals(True)
        self._shift_slider.setValue(shift)
        self._shift_text.setText(str(shift))
        self._shift_slider.blockSignals(False)
        self._shift_text.blockSignals(False)
        self.valueChanged.emit(shift)

    def setValue(self, value: int):
        assert isinstance(value, int), f'Illegal type! Expected int, got {type(value)}!'
        self._shift_changed(int(value))

    def value(self) -> int:
        return self._shift_slider.value()
