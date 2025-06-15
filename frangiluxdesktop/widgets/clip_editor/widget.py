from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QGridLayout, QSlider, QProgressBar

from frangiluxdesktop.widgets.clip_editor.viewport import ClipEditorViewportWidget
from frangiluxlib.components.clip import Clip


class ClipEditorWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.clip: Clip | None = None

        self.slider_clip_length = QSlider(Qt.Horizontal)
        self.slider_clip_length.setRange(0, 6000)
        self.slider_clip_length.setValue(4300)
        self.slider_clip_length.valueChanged.connect(self._update_clip)

        self.slider_play_head = QSlider(Qt.Horizontal)
        self.slider_play_head.setRange(0, 1000)
        self.slider_play_head.valueChanged.connect(self._update_play_head)

        self.progress_value = QProgressBar()
        self.progress_value.setOrientation(Qt.Vertical)
        self.progress_value.setRange(0, 1000)
        self.progress_value.setValue(500)

        self.viewport = ClipEditorViewportWidget()
        self.viewport.pointMoved.connect(self._update_play_head)

        layout = QGridLayout(self)
        layout.addWidget(self.slider_clip_length, 0, 0)
        layout.addWidget(self.viewport, 1, 0)
        layout.addWidget(self.slider_play_head, 2, 0)
        layout.addWidget(self.progress_value, 1, 1)

        self._suspend_slider_update = False

    def _update_clip(self):
        if self.clip is None:
            return

        self._update_play_head()

        if not self._suspend_slider_update:
            self.clip.time_configuration.duration = self.slider_clip_length.value() / 1000.0

        self.viewport.set_clip(self.clip)

    def set_clip(self, clip: Clip):
        self._suspend_slider_update = True

        self.clip = clip
        self.slider_clip_length.setValue(int(clip.time_configuration.duration * 1000))
        self._update_clip()

        self._suspend_slider_update = False

    def _update_play_head(self):
        if self.clip is None or not self.clip.points():
            return

        time = (self.slider_play_head.value() / 1000.0) * self.clip.time_configuration.duration
        self.clip.play_position = time
        value = self.clip.play_value()
        self.progress_value.setValue(int(value * 1000))

        self.viewport.repaint()
