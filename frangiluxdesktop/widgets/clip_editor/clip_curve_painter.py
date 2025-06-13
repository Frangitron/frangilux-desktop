from dataclasses import dataclass

import math

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QPainter, QPen, QPalette
from PySide6.QtWidgets import QApplication

from frangiluxlib.components.clip import Clip
from frangiluxlib.components.clip_point import ClipPoint


@dataclass
class ClipCurvePainterInfo:
    rect: QRect
    hovered_point: ClipPoint | None
    selected_point: ClipPoint | None
    palette: QPalette


class ClipCurvePainter:

    def paint(self, clip: Clip, painter: QPainter, info: ClipCurvePainterInfo):
        background_color = info.palette.color(QPalette.ColorRole.Mid).lighter(50)
        curve_color = info.palette.color(QPalette.ColorRole.Mid)
        point_color = info.palette.color(QPalette.ColorRole.Highlight)
        point_color_hovered = info.palette.color(QPalette.ColorRole.Text)

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        time_scale = info.rect.width() / clip.time_configuration.duration
        value_scale = info.rect.height() / 255.0

        for i in range(math.ceil(clip.time_configuration.duration)):
            if i % 2 == 1:
                continue

            background_rect = QRect(int(i * time_scale), 0, int(time_scale), info.rect.height())
            painter.fillRect(background_rect, background_color)

        pen = QPen()
        pen.setWidth(2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setColor(curve_color)
        painter.setPen(pen)
        for index, point in enumerate(clip.points):
            if index == len(clip.points) - 1 and point.time < clip.time_configuration.duration:
                painter.drawLine(
                    int(point.time * time_scale), int(point.value * value_scale),
                    info.rect.width(), int(point.value * value_scale)
                )

            if index == 0 and point.time > 0.0:
                painter.drawLine(
                    0, int(point.value * value_scale),
                    int(point.time * time_scale), int(point.value * value_scale)
                )

            if index < len(clip.points) - 1:
                painter.drawLine(
                    int(point.time * time_scale), int(point.value * value_scale),
                    int(clip.points[index + 1].time * time_scale), int(clip.points[index + 1].value * value_scale)
                )

        pen.setWidth(10)
        for point in clip.points:
            pen.setColor(
                point_color_hovered if point == info.hovered_point or point == info.selected_point
                else point_color
            )
            painter.setPen(pen)

            x = int(point.time * time_scale)
            y = int(point.value * value_scale)
            painter.drawPoint(x, y)

        painter.restore()
