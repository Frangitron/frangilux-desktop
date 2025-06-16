from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGroupBox, QVBoxLayout

from frangiluxlib.components.clip_point.clip_point import ClipPoint
from frangiluxlib.components.clip_point.reference_store import ClipPointReferenceStore
from pyside6helpers.spinbox import SpinBox, DoubleSpinBox


class PointValueEditor(QGroupBox):

    PointChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._point: ClipPoint | None = None
        self._suspend_update = False

        self.setTitle("Point value")

        self.spinbox_dmx = SpinBox(
            name="DMX",
            minimum=0,
            maximum=255,
            single_step=1
        )
        self.spinbox_dmx.valueChanged.connect(self._dmx_changed)

        self.spinbox_float = DoubleSpinBox(
            name="Float",
            minimum=0.0,
            maximum=1.0,
            single_step=0.01
        )
        self.spinbox_float.valueChanged.connect(self._float_changed)

        layout = QVBoxLayout(self)
        layout.addWidget(self.spinbox_dmx)
        layout.addWidget(self.spinbox_float)

        self.setEnabled(False)

    def set_point(self, point: ClipPoint | None):
        self._point = point
        self.refresh()

    def refresh(self):
        if self._point is None:
            self.setEnabled(False)
            self.spinbox_dmx.setValue(0)
            self.spinbox_float.setValue(0.0)
        else:
            self.setEnabled(True)
            self.spinbox_dmx.setValue(int(self._point.value * 255))
            self.spinbox_float.setValue(self._point.value)

    def _dmx_changed(self):
        if self._point is None or self._suspend_update:
            return

        self._suspend_update = True
        self.spinbox_float.setValue(self.spinbox_dmx.value() / 255)
        self._suspend_update = False

        self._update_point()

    def _float_changed(self):
        if self._point is None or self._suspend_update:
            return

        self._suspend_update = True
        self.spinbox_dmx.setValue(int(self.spinbox_float.value() * 255))
        self._suspend_update = False

        self._update_point()

    def _update_point(self):
        if self._point is None:
            return

        self._point.value = self.spinbox_dmx.value() / 255.0
        if self._point.is_reference and self._point.is_reference_editable:
            ClipPointReferenceStore().set(self._point, self._point.value)

        self.PointChanged.emit()
