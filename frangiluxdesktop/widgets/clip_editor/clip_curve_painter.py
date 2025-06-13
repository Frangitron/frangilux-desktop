import math

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QPainter, QPen

from frangiluxlib.components.clip import Clip
from frangiluxlib.components.clip_point import ClipPoint


class ClipCurvePainter:

    @staticmethod
    def paint(clip: Clip, painter: QPainter, rect: QRect, hovered_point: ClipPoint | None):
        painter.save()

        time_scale = rect.width() / clip.time_configuration.duration
        value_scale = rect.height() / 255.0

        for i in range(math.ceil(clip.time_configuration.duration)):
            if i % 2 == 1:
                continue

            background_rect = QRect(int(i * time_scale), 0, int(time_scale), rect.height())
            painter.fillRect(background_rect, Qt.red)

        pen = QPen()
        pen.setWidth(2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        for index, point in enumerate(clip.points):
            if index == len(clip.points) - 1 and point.time < clip.time_configuration.duration:
                painter.drawLine(
                    int(point.time * time_scale), int(point.value * value_scale),
                    rect.width(), int(point.value * value_scale)
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
            pen.setColor(Qt.green if point == hovered_point else Qt.black)
            painter.setPen(pen)

            x = int(point.time * time_scale)
            y = int(point.value * value_scale)
            painter.drawPoint(x, y)

        painter.restore()
