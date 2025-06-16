from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QGridLayout, QSlider, QProgressBar, QGroupBox

from frangiluxdesktop.widgets.clip_editor.point_reference_editor import PointReferenceEditor
from frangiluxdesktop.widgets.clip_editor.viewport import ClipEditorViewportWidget
from frangiluxlib.components.clip import Clip
from frangiluxlib.components.clip_point import ClipPoint
from frangiluxlib.components.clip_reader import ClipReader
from pyside6helpers.spinbox import SpinBox


class ClipEditorWidget(QGroupBox):
    scrubbed = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Clip Editor")

        self.clip: Clip | None = None

        self.spinbox_clip_length = SpinBox(
            name="Clip length",
            minimum=1,
            maximum=16,
            on_value_changed=self._update_clip
        )

        self.progress_value = QProgressBar()
        self.progress_value.setTextVisible(False)
        self.progress_value.setOrientation(Qt.Vertical)
        self.progress_value.setRange(0, 1000)
        self.progress_value.setValue(500)

        self.point_reference_editor = PointReferenceEditor()
        self.point_reference_editor.ValueChanged.connect(self.repaint)

        self.viewport = ClipEditorViewportWidget()
        self.viewport.pointMoved.connect(self._point_moved)
        self.viewport.scrubbed.connect(self._scrubbed)
        self.viewport.pointSelected.connect(self.point_reference_editor.set_point)

        layout = QGridLayout(self)
        layout.addWidget(self.viewport, 0, 0, 3, 1)
        layout.addWidget(self.progress_value, 0, 1, 3, 1)
        layout.addWidget(self.spinbox_clip_length, 0, 2)
        layout.addWidget(self.point_reference_editor, 1, 2)
        layout.addWidget(QWidget(), 1, 3)
        layout.setColumnStretch(0, 1)
        layout.setRowStretch(2, 1)

        self._suspend_slider_update = False

    def _update_clip(self):
        if self.clip is None:
            return

        if not self._suspend_slider_update:
            self.clip.time_configuration.duration = self.spinbox_clip_length.value()

        self.viewport.set_clip(self.clip)

    def set_clip(self, clip: Clip):
        self._suspend_slider_update = True

        self.clip = clip
        self.spinbox_clip_length.setValue(int(clip.time_configuration.duration))
        self._update_clip()

        self._suspend_slider_update = False

    def _point_moved(self, point: ClipPoint):
        self._update_progress()

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
