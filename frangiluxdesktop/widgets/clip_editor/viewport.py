import math

from PySide6.QtCore import QRect, QPoint, Signal
from PySide6.QtGui import QPainter, Qt, QPen
from PySide6.QtWidgets import QWidget

from frangiluxdesktop.widgets.clip_editor.clip_curve_painter import ClipCurvePainter, ClipCurvePainterInfo
from frangiluxlib.components.clip import Clip
from frangiluxlib.components.clip_point import ClipPoint


class ClipEditorViewportWidget(QWidget):
    pointSelected = Signal(ClipPoint)
    pointCreated = Signal(ClipPoint)

    hover_distance = 30

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)

        self._clip: Clip | None = None
        self._time_scale = 1.0
        self._value_scale = 1.0
        self._hovered_point: ClipPoint | None = None
        self._selected_point: ClipPoint | None = None
        self._lock_value = 0.0
        self._lock_time = 0.0
        self._modifiers = None
        self._curve_painter = ClipCurvePainter()

    def set_clip(self, clip: Clip):
        self._clip = clip
        self.repaint()

    def paintEvent(self, event):
        if self._clip is None or self._clip.time_configuration.duration == 0:
            return

        self._time_scale = event.rect().width() / self._clip.time_configuration.duration
        self._value_scale = event.rect().height() / 255.0

        painter = QPainter(self)
        self._curve_painter.paint(
            clip=self._clip,
            painter=painter,
            info=ClipCurvePainterInfo(
                rect=event.rect(),
                hovered_point=self._hovered_point,
                selected_point=self._selected_point,
                palette=self.palette()
            )
        )

    def mouseMoveEvent(self, event):
        if self._clip is None or self._clip.time_configuration.duration == 0:
            return

        if event.buttons() & Qt.MouseButton.LeftButton and self._hovered_point is not None:
            self._modifiers = event.modifiers()
            self._move_point(event.pos())
            return

        self._hovered_point = None
        for point in self._clip.points:
            point_pos = QPoint(
                int(point.time * self._time_scale),
                int(point.value * self._value_scale)
            )
            distance = (event.pos() - point_pos).manhattanLength()
            if distance <= self.hover_distance:
                self._hovered_point = point
                break

        self.repaint()

    def mousePressEvent(self, event):
        if self._clip is None or self._clip.time_configuration.duration == 0:
            return

        if event.modifiers() & Qt.KeyboardModifier.AltModifier and self._hovered_point is not None:
            self._clip.points.remove(self._hovered_point)
            self.repaint()

        if self._hovered_point is not None:
            self._selected_point = self._hovered_point
            self.pointSelected.emit(self._hovered_point)
            self._lock_time = self._hovered_point.time
            self._lock_value = self._hovered_point.value
            return
        else:
            self._selected_point = None

        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            time = event.pos().x() / self._time_scale
            value = event.pos().y() / self._value_scale

            self._lock_time = time
            self._lock_value = value

            new_point = ClipPoint(
                time=time,
                value=value
            )
            self._clip.add_point(new_point)
            self.pointCreated.emit(new_point)

        self.repaint()

    def _move_point(self, pos: QPoint):
        time = pos.x() / self._time_scale
        time = max(0.0, min(time, self._clip.time_configuration.duration))

        value = pos.y() / self._value_scale
        value = max(0.0, min(value, 255.0))

        if self._modifiers & Qt.KeyboardModifier.ControlModifier:
            self._hovered_point.time = time
            self._hovered_point.value = self._lock_value
        elif self._modifiers & Qt.KeyboardModifier.ShiftModifier:
            self._hovered_point.time = self._lock_time
            self._hovered_point.value = value
        else:
            self._hovered_point.time = time
            self._hovered_point.value = value

        self._clip.sort()
        self.repaint()
