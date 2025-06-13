from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QGridLayout, QSlider

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

        self.viewport = ClipEditorViewportWidget()

        layout = QGridLayout(self)
        layout.addWidget(self.slider_clip_length, 0, 0)
        layout.addWidget(self.viewport, 1, 0)

    def _update_clip(self):
        self.clip.time_configuration.duration = self.slider_clip_length.value() / 1000.0
        self.viewport.set_clip(self.clip)

    def set_clip(self, clip: Clip):
        self.clip = clip
        self._update_clip()
