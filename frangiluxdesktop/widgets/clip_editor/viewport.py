from PySide6.QtCore import QPoint, Signal
from PySide6.QtGui import QPainter, Qt, QPen
from PySide6.QtWidgets import QWidget

from frangiluxlib.components.clip import Clip
from frangiluxlib.components.clip_point import ClipPoint
from frangiluxlib.components.clip_point_reference_store import ClipPointReferenceStore
from frangiluxlib.components.clip_reader import ClipReader

from frangiluxdesktop.palette import Palette
from frangiluxdesktop.widgets.clip_editor.clip_curve_painter import (
    ClipCurvePainter,
    ClipCurvePainterInfo,
    PointLabelFormat
)


class ClipEditorViewportWidget(QWidget):
    pointSelected = Signal(ClipPoint)
    pointCreated = Signal(ClipPoint)
    pointMoved = Signal(ClipPoint)
    scrubbed = Signal(float)

    hover_distance = 30

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)

        self._clip: Clip | None = None
        self._clip_reader = ClipReader()

        self._hovered_point: ClipPoint | None = None
        self._lock_time = 0.0
        self._lock_value = 0.0
        self._modifiers = None
        self._selected_point: ClipPoint | None = None
        self._time_scale = 1.0
        self._value_scale = 1.0
        self._mouse_pos: QPoint = QPoint(0, 0)
        self._draw_value = False
        self._draw_time = False

        self._curve_painter = ClipCurvePainter()

    def set_clip(self, clip: Clip):
        self._clip = clip
        self.repaint()

    def paintEvent(self, event):
        if self._clip is None or self._clip.time_configuration.duration == 0:
            return

        self._time_scale = event.rect().width() / self._clip.time_configuration.duration
        self._value_scale = event.rect().height()

        painter = QPainter(self)
        # painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        self._curve_painter.paint(
            clip=self._clip,
            painter=painter,
            info=ClipCurvePainterInfo(
                rect=event.rect(),
                hovered_point=self._hovered_point,
                selected_point=self._selected_point
            )
        )

        pen = QPen()
        pen.setColor(Palette().curve)
        painter.setPen(pen)
        if self._draw_value:
            painter.drawLine(0, self._mouse_pos.y(), event.rect().width(), self._mouse_pos.y())
        if self._draw_time:
            painter.drawLine(self._mouse_pos.x(), 0, self._mouse_pos.x(), event.rect().height())

    def mouseMoveEvent(self, event):
        self._mouse_pos = event.pos()

        if self._clip is None or self._clip.time_configuration.duration == 0:
            return

        if event.buttons() & Qt.MouseButton.LeftButton and self._hovered_point is not None:
            self._modifiers = event.modifiers()
            self._move_point(event.pos())
            return

        if event.buttons() & Qt.MouseButton.LeftButton:
            self.scrubbed.emit(event.pos().x() / self._time_scale)
            self.repaint()
            return

        self._hovered_point = None
        for point in self._clip.points():
            point_pos = QPoint(
                int(point.time * self._time_scale),
                int((1.0 - self._clip_reader.point_value(point)) * self._value_scale)
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
            self._clip.remove_point(self._hovered_point)
            self.repaint()

        self.pointSelected.emit(self._hovered_point)
        if self._hovered_point is not None:
            self._selected_point = self._hovered_point
            self._lock_time = self._hovered_point.time
            self._lock_value = self._hovered_point.value
            self.repaint()
            return

        elif self._selected_point is not None:
            self._selected_point.is_reference_editable = False
            self._selected_point = None

        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            time = event.pos().x() / self._time_scale
            value = 1.0 - (event.pos().y() / self._value_scale)

            self._lock_time = time
            self._lock_value = value

            new_point = ClipPoint(
                time=time,
                value=value
            )
            self._clip.add_point(new_point)
            self.pointCreated.emit(new_point)

        self.repaint()

    def mouseReleaseEvent(self, event):
        self._draw_value = False
        self._draw_time = False

    def _move_point(self, pos: QPoint):
        # FIXME use a renamed version of PointReader to update values and check if reference ?
        self._draw_value = False
        self._draw_time = False

        time = pos.x() / self._time_scale
        time = max(0.0, min(time, self._clip.time_configuration.duration))

        value = 1.0 - (pos.y() / self._value_scale)
        value = max(0.0, min(value, 1.0))

        if self._modifiers & Qt.KeyboardModifier.ControlModifier or (self._selected_point.is_reference and not self._selected_point.is_reference_editable):
            self._draw_time = True
            self._hovered_point.time = time
            self._hovered_point.value = self._lock_value

        elif self._modifiers & Qt.KeyboardModifier.ShiftModifier:
            self._draw_value = True
            self._hovered_point.time = self._lock_time
            self._hovered_point.value = value
            if self._selected_point.is_reference and self._selected_point.is_reference_editable:
                ClipPointReferenceStore().set(self._selected_point, value)

        else:
            self._draw_value = True
            self._draw_time = True
            self._hovered_point.time = time
            self._hovered_point.value = value
            if self._selected_point.is_reference and self._selected_point.is_reference_editable:
                ClipPointReferenceStore().set(self._selected_point, value)

        self._clip.sort()
        self.repaint()
        self.pointMoved.emit(self._hovered_point)

    def set_point_label_format(self, format_: PointLabelFormat):
        self._curve_painter.options.point_label_format = format_
        self.repaint()

    def point_label_format(self) -> PointLabelFormat:
        return self._curve_painter.options.point_label_format
