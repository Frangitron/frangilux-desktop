from PySide6.QtWidgets import QWidget, QGridLayout

from frangiluxlib.components.clip.store import ClipStore
from pyside6helpers.group import make_group

from frangiluxdesktop.widgets import ClipEditorWidget, LayerEditorWidget


class CentralWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QGridLayout(self)

        self._clip_editor = ClipEditorWidget()
        self._clip_editor.set_clip(ClipStore().clips[0])
        layout.addWidget(make_group(
            "Clip editor",
            [self._clip_editor]
        ), 0, 0)

        self._layer_editor = LayerEditorWidget()
        layout.addWidget(make_group(
            "Layer editor",
            [self._layer_editor]
        ), 0, 1)
