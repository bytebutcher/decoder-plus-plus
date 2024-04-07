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
from typing import Union

from qtpy.QtWidgets import QPushButton, QToolButton, QGroupBox, QLabel, QFrame, QWidget, QFormLayout, QLayout, \
    QHBoxLayout, QVBoxLayout

from dpp.core.assertions import assert_type, assert_instance
from dpp.core.icons import icon
from dpp.core.plugin import AbstractPlugin
from dpp.core.plugin.config.options import Boolean, Slider, String, Integer, Group, ComboBox, CodeEditor, Text
from dpp.core.plugin.config.ui import Widget, Layout
from dpp.core.plugin.config.ui.widgets import ToolButton, Button, GroupBox, TextPreview, Frame, Option, Label, HSpace, \
    VSpace
from dpp.core.plugin.config.ui.layouts import FormLayout, VBoxLayout, HBoxLayout
from dpp.ui import VSpacer, HSpacer
from dpp.ui.widget.codec_preview_widget import CodecPreviewWidget
from dpp.ui.widget.code_editor_widget import CodeEditorWidget
from dpp.ui.widget.option_widgets import SliderOptionWidget, StringOptionWidget, GroupOptionWidget, \
    BooleanOptionWidget, OptionWidget, ComboBoxOptionWidget, CodeEditorOptionWidget, TextOptionWidget


class BuilderBase:

    def __init__(self):
        self._logger = logging.getLogger(__name__)


class LayoutBuilder(BuilderBase):

    def __init__(self, widget_builder: 'WidgetBuilder' = None):
        super().__init__()
        self._widget_builder = WidgetBuilder(layout_builder=self) if not widget_builder else widget_builder

    def _get_layout_from_spec(self, layout_spec):
        if isinstance(layout_spec, HBoxLayout):
            layout = QHBoxLayout()
        elif isinstance(layout_spec, VBoxLayout):
            layout = QVBoxLayout()
        elif isinstance(layout_spec, FormLayout):
            layout = QFormLayout()
        else:
            raise Exception(f'Illegal PluginConfig layout of type {type(layout_spec)}!')
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        return layout

    def _add_widgets_to_layout(self, plugin, input_text, widget_spec, layout):
        label, widget = self._widget_builder.build(plugin, input_text, widget_spec)
        if isinstance(layout, QFormLayout):
            if not label:
                label = QLabel()
            layout.addRow(label, widget)
        else:
            if label:
                layout.addWidget(label)
            layout.addWidget(widget)

    def build(self, plugin, input_text, layout_spec: Layout) -> QLayout:
        assert_instance(layout_spec, Layout)
        layout = self._get_layout_from_spec(layout_spec)
        self._logger.debug(f'Building {layout.__class__.__name__} for {plugin.name} plugin ...')
        for widget_spec in layout_spec.widgets:
            self._logger.debug(f'Adding {widget_spec.__class__.__name__} to {layout.__class__.__name__} ...')
            self._add_widgets_to_layout(plugin, input_text, widget_spec, layout)
        return layout


class OptionWidgetBuilder(BuilderBase):

    def __init__(self):
        super().__init__()
        self._widgets = {
            Boolean: BooleanOptionWidget,
            CodeEditor: CodeEditorOptionWidget,
            ComboBox: ComboBoxOptionWidget,
            Group: GroupOptionWidget,
            Integer: StringOptionWidget,
            Slider: SliderOptionWidget,
            String: StringOptionWidget,
            Text: TextOptionWidget,
        }

    def _build(self, plugin: AbstractPlugin, input_text: str, widget_spec: Option):
        # Note: We are using type() instead of instanceof since we really want to check whether the object is a
        #       specific type rather than checking whether the object inherits from some class.
        if type(widget_spec) is Option:
            widget = self._build(plugin, input_text, plugin.config.option(widget_spec.key))
            # Note: Widgets specify whether a label should be shown besides the widget.
            #       For example while Strings show the label besides the widget, Booleans do not do that.
            #       When the Option does not specify whether a label should be shown the information is taken
            #       from the widget (e.g. Slider, String, Integer, ...).
            widget_spec.show_label = widget.show_label if widget_spec.show_label is None else widget_spec.show_label
            return widget

        if type(widget_spec) not in self._widgets:
            raise Exception(f'Can not build widget! Unknown widget specification {type(widget_spec)}!')

        widget = self._widgets[type(widget_spec)](plugin.config, widget_spec)

        # Update config, when option widget value is changes by user.
        widget.onChange.connect(
            lambda option_widget: plugin.config.update({option_widget.getKey(): option_widget.getValue()}))

        return widget

    def build(self, plugin: AbstractPlugin, input_text: str, widget_spec: Option) -> OptionWidget:
        """ Automatically builds the widget for this option. """
        return self._build(plugin, input_text, widget_spec).getWidget()


class ToolButtonWidgetBuilder(BuilderBase):

    def build(self, plugin: AbstractPlugin, input_text: str, widget_spec: ToolButton) -> QWidget:
        widget = QToolButton()
        widget.setText(widget_spec.label)
        widget.setToolTip(widget_spec.description)
        widget.clicked.connect(widget_spec.on_click)
        if widget_spec.icon:
            widget.setIcon(icon(widget_spec.icon))
        return widget


class ButtonWidgetBuilder(BuilderBase):

    def build(self, plugin: AbstractPlugin, input_text: str, widget_spec: Button) -> QWidget:
        widget = QPushButton(widget_spec.label)
        widget.setText(widget_spec.label)
        widget.setToolTip(widget_spec.description)
        widget.clicked.connect(widget_spec.on_click)
        if widget_spec.icon:
            widget.setIcon(icon(widget_spec.icon))
        return widget


class LabelWidgetBuilder(BuilderBase):
    """ Builds a label from a widget specification. """

    def build(self, plugin: AbstractPlugin, input_text: str, widget_spec: Label) -> QWidget:
        return QLabel(widget_spec.label)


class HSpaceWidgetBuilder(BuilderBase):
    """ Builds a horizontal spacer from a widget specification. """

    def build(self, plugin: AbstractPlugin, input_text: str, widget_spec: Label) -> QWidget:
        return HSpacer()


class VSpaceWidgetBuilder(BuilderBase):
    """ Builds a vertical spacer from a widget specification. """

    def build(self, plugin: AbstractPlugin, input_text: str, widget_spec: Label) -> QWidget:
        return VSpacer()


class GroupBoxWidgetBuilder(BuilderBase):

    def build(self, plugin: AbstractPlugin, input_text: str, widget_spec: GroupBox) -> QWidget:
        group_box = QGroupBox(widget_spec.label)
        group_box.setStyleSheet("""
        QGroupBox {
            border: 1px solid silver;
            border-radius: 6px;
            margin-top: 6px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 7px;
            padding: 0px 5px 0px 5px;
        }
        """)
        return group_box


class FrameWidgetBuilder(BuilderBase):
    class NoMarginsFrame(QFrame):

        def setLayout(self, layout: 'QLayout') -> None:
            layout.setContentsMargins(0, 0, 0, 0)
            super().setLayout(layout)

    def build(self, plugin: AbstractPlugin, input_text: str, widget_spec: Frame) -> QWidget:
        return FrameWidgetBuilder.NoMarginsFrame()


class TextPreviewWidgetBuilder(BuilderBase):

    def build(self, plugin: AbstractPlugin, input_text: str, widget_spec: TextPreview) -> QWidget:
        return CodecPreviewWidget(plugin, input_text)


class CodeEditorWidgetBuilder(BuilderBase):

    def build(self, plugin: AbstractPlugin, input_text: str, widget_spec: CodeEditor) -> QWidget:
        return CodeEditorWidget(plugin, input_text)


class LabelBuilder(BuilderBase):

    def build(self, plugin: AbstractPlugin, input_text: str, widget_spec: Widget) -> QWidget:
        label = None
        if widget_spec.label and widget_spec.show_label:
            assert_type(widget_spec.label, str)
            label = QLabel()
            label.setText(widget_spec.label)
        return label


class WidgetBuilder(BuilderBase):

    def __init__(self, label_builder: LabelBuilder = None, layout_builder: LayoutBuilder = None):
        super().__init__()
        self._label_builder = LabelBuilder() if not label_builder else label_builder
        self._layout_builder = LayoutBuilder(widget_builder=self) if not layout_builder else layout_builder
        self._widget_builders = {
            Button: ButtonWidgetBuilder(),
            Frame: FrameWidgetBuilder(),
            GroupBox: GroupBoxWidgetBuilder(),
            HSpace: HSpaceWidgetBuilder(),
            Label: LabelWidgetBuilder(),
            Option: OptionWidgetBuilder(),
            TextPreview: TextPreviewWidgetBuilder(),
            ToolButton: ToolButtonWidgetBuilder(),
            VSpace: VSpaceWidgetBuilder(),
        }

    def build(self, plugin: AbstractPlugin, input_text: str, widget_spec) -> Union[str, QWidget]:
        if type(widget_spec) not in self._widget_builders:
            raise Exception(f'Can not build widget! Unknown widget specification {type(widget_spec)}!')

        widget = self._widget_builders[type(widget_spec)].build(plugin, input_text, widget_spec)
        label = self._label_builder.build(plugin, input_text, widget_spec)

        if hasattr(widget_spec, 'layout') and widget_spec.layout:
            assert_instance(widget_spec.layout, Layout)
            layout = self._layout_builder.build(plugin, input_text, widget_spec.layout)
            widget.setLayout(layout)

        return label, widget
