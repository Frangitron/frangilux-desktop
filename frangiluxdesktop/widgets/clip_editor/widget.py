from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QGridLayout, QProgressBar, QRadioButton, QLineEdit

from frangiluxdesktop.widgets.clip_editor.clip_curve_painter import PointLabelFormat
from frangiluxdesktop.widgets.clip_editor.point_value_editor import PointValueEditor

from frangiluxlib.components.clip.clip import Clip
from frangiluxlib.components.clip.reader import ClipReader
from frangiluxlib.components.clip_point.clip_point import ClipPoint

from pyside6helpers.spinbox import SpinBox
from pyside6helpers.group import make_group

from frangiluxdesktop.widgets.clip_editor.point_reference_editor import PointReferenceEditor
from frangiluxdesktop.widgets.clip_editor.viewport import ClipEditorViewportWidget


class ClipEditorWidget(QWidget):
    scrubbed = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.clip: Clip | None = None

        layout = QGridLayout(self)

        self.viewport = ClipEditorViewportWidget()
        layout.addWidget(self.viewport, 0, 0, 5, 1)

        self.progress_value = QProgressBar()
        self.progress_value.setTextVisible(False)
        self.progress_value.setOrientation(Qt.Vertical)
        self.progress_value.setRange(0, 1000)
        self.progress_value.setValue(500)
        layout.addWidget(self.progress_value, 0, 1, 5, 1)

        self.lineedit_clip_name = QLineEdit()
        self.lineedit_clip_name.setPlaceholderText("Clip name")
        layout.addWidget(self.lineedit_clip_name, 0, 2, 1, 2)

        self.spinbox_clip_length = SpinBox(
            name="Clip length",
            minimum=1,
            maximum=16,
            on_value_changed=self._update_clip
        )
        layout.addWidget(self.spinbox_clip_length, 1, 2, 1, 2)

        self.radio_label_format_float = QRadioButton("Float")
        self.radio_label_format_dmx = QRadioButton("DMX")
        self.radio_label_format_float.setChecked(self.viewport.point_label_format() == PointLabelFormat.Float)
        self.radio_label_format_dmx.setChecked(self.viewport.point_label_format() == PointLabelFormat.Dmx)

        label_format_group = make_group(
            "Point labels",
            [self.radio_label_format_float, self.radio_label_format_dmx]
        )
        layout.addWidget(label_format_group, 2, 2)

        self.point_value_editor = PointValueEditor()
        layout.addWidget(self.point_value_editor, 2, 3)

        self.point_reference_editor = PointReferenceEditor()
        layout.addWidget(self.point_reference_editor, 3, 2, 1, 2)

        layout.addWidget(QWidget(), 4, 2)
        layout.setColumnStretch(0, 10)
        layout.setColumnStretch(2, 1)
        layout.setColumnStretch(3, 1)
        layout.setRowStretch(4, 1)

        self.viewport.pointMoved.connect(self._point_moved)
        self.viewport.scrubbed.connect(self._scrubbed)
        self.viewport.pointSelected.connect(self.point_reference_editor.set_point)
        self.viewport.pointSelected.connect(self.point_value_editor.set_point)
        self.lineedit_clip_name.textChanged.connect(self._update_clip)
        self.radio_label_format_float.clicked.connect(self._update_viewport)
        self.radio_label_format_dmx.clicked.connect(self._update_viewport)
        self.point_value_editor.PointChanged.connect(self._repaint_viewport)
        self.point_reference_editor.PointChanged.connect(self._repaint_viewport)

        self._suspend_widgets_update = False

    def _update_clip(self):
        if self.clip is None:
            return

        if not self._suspend_widgets_update:
            self.clip.time_configuration.duration = self.spinbox_clip_length.value()
            self.clip.name = self.lineedit_clip_name.text()

        self.viewport.set_clip(self.clip)

    def set_clip(self, clip: Clip):
        self._suspend_widgets_update = True

        self.clip = clip
        self.spinbox_clip_length.setValue(int(clip.time_configuration.duration))
        self.lineedit_clip_name.setText(clip.name)
        self._update_clip()

        self._suspend_widgets_update = False

    def _point_moved(self, point: ClipPoint):
        self._update_progress()
        self.point_value_editor.refresh()

    def _scrubbed(self, time: float | None = None):
        if self.clip is None or not self.clip.points():
            return

        if time is not None:
            self.clip.play_position = time % self.clip.time_configuration.duration

        self.scrubbed.emit(time)

        self._update_progress()

    def _update_progress(self):
        value = ClipReader().play_value(self.clip)
        self.progress_value.setValue(int(value * 1000))

    def _update_viewport(self):
        self.viewport.set_point_label_format(PointLabelFormat.Dmx if self.radio_label_format_dmx.isChecked() else PointLabelFormat.Float)
        self.viewport.repaint()

    def _repaint_viewport(self):
        self.viewport.repaint()
