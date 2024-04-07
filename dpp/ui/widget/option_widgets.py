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
from typing import List

from qtpy.QtCore import Signal, QObject
from qtpy.QtWidgets import QCheckBox, QComboBox, QLineEdit, QRadioButton

from dpp.ui.widget.code_editor_widget import CodeEditorWidget
from dpp.ui.widget.slider_widget import SliderWidget
from dpp.ui.widget.text_widget import TextWidget


class OptionWidget(QObject):
    """ Wraps a widget (e.g. QLineEdit, QCheckBox) representing a configuration option (e.g. String, Boolean). """

    onChange = Signal('PyQt_PyObject')  # option

    def __init__(self, widget, option, config, set_value_callback, get_value_callback, on_change_signal, show_label):
        """ Initializes the option widget.
        :param widget: the widget to wrap which should represent the option.
        :param option: the option to represent.
        :param config: the configuration where the option is stored.
        :param set_value_callback: a callback to set a value of the widget representing the option.
        :param get_value_callback: a callback which returns the value of the widget representing the option.
        :param on_change_signal: a signal which is emitted when the value of the widget representing the option has changed.
        :param show_label: an indicator whether the option widget should show a label.
        """
        super().__init__()
        self._option = option
        self._key = option.key
        self._name = option.name
        self._config = config
        self._widget = widget
        self._set_value_callback = set_value_callback
        self._get_value_callback = get_value_callback
        self.setValue(option.value)
        self._config.onChange.connect(self._on_config_change)
        self.show_label = show_label
        widget.setToolTip(option.description)
        on_change_signal.connect(lambda event: self.onChange.emit(self))

    def getKey(self):
        """ Returns the configuration key/id. """
        return self._key

    def getName(self):
        """ Returns the human-readable name of the option. """
        return self._name

    def getValue(self):
        """ Returns the value stored within the widget. """
        return self._get_value_callback()

    def getWidget(self):
        """ Returns the widget representing the configuration option. """
        return self._widget

    def getConfig(self):
        """ Returns the complete plugin configuration. """
        return self._config

    def setValue(self, value):
        """ Sets the value inside the widget. """
        self._set_value_callback(value)

    def getOption(self):
        """ Returns the configuration option. """
        return self._option

    def _on_config_change(self, keys: List[str]):
        """ Checks whether this widget is affected by the configuration change and updates the value accordingly. """
        if self.getKey() in keys and self.getValue() != self._config.value(self.getKey()):
            self.setValue(self._config.value(self.getKey()))

    def validate(self, input_text) -> str:
        """ Validates the configuration entry in association with the input text. """
        return self._config.validate(self._option, input_text)


class StringOptionWidget(OptionWidget):

    def __init__(self, config, option):
        widget = QLineEdit(str(option.value))
        super().__init__(widget, option, config, lambda text: widget.setText(str(text)), widget.text,
                         widget.textChanged, show_label=True)

    def validate(self, input_text) -> str:
        """ Validates the configuration entry in association with the input text. """
        if super().validate(input_text):
            self._widget.setStyleSheet('QLineEdit { color: red }')
        else:
            self._widget.setStyleSheet('')


class TextOptionWidget(OptionWidget):

    def __init__(self, config, option):
        widget = TextWidget(option.value, read_only=option.read_only, wrap_lines=option.wrap_lines)
        super().__init__(widget, option, config, widget.setText, widget.text,
                         widget.textChanged, show_label=False)


class BooleanOptionWidget(OptionWidget):

    def __init__(self, config, option):
        widget = QCheckBox(option.name)
        super().__init__(widget, option, config, widget.setChecked, widget.isChecked, widget.clicked, show_label=False)


class GroupOptionWidget(OptionWidget):

    def __init__(self, config, option):
        widget = QRadioButton(option.name)
        super().__init__(widget, option, config, widget.setChecked, widget.isChecked, widget.clicked, show_label=False)


class ComboBoxOptionWidget(OptionWidget):

    def __init__(self, config, option):
        widget = QComboBox()
        for value in option.values:
            widget.addItem(value)
        super().__init__(widget, option, config, widget.setCurrentText, widget.currentText, widget.currentIndexChanged,
                         show_label=True)


class SliderOptionWidget(OptionWidget):

    def __init__(self, config, option):
        widget = SliderWidget(option.value, option.range)
        super().__init__(widget, option, config, widget.setValue, widget.value, widget.valueChanged, show_label=True)


class CodeEditorOptionWidget(OptionWidget):

    def __init__(self, config, option):
        widget = CodeEditorWidget(option.value)
        super().__init__(widget, option, config, widget.setText, widget.text, widget.textChanged, show_label=False)
