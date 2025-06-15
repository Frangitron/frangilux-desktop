from dataclasses import dataclass

import math

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QPainter, QPen

from frangiluxdesktop.palette import Palette
from frangiluxlib.components.clip import Clip
from frangiluxlib.components.clip_point import ClipPoint


@dataclass
class ClipCurvePainterInfo:
    rect: QRect
    hovered_point: ClipPoint | None
    selected_point: ClipPoint | None
    draw_points: bool = True


class ClipCurvePainter:

    def paint(self, clip: Clip, painter: QPainter, info: ClipCurvePainterInfo):
        points = clip.points()
        palette = Palette()

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        time_scale = info.rect.width() / clip.time_configuration.duration
        value_scale = info.rect.height()

        for i in range(math.ceil(clip.time_configuration.duration)):
            if i % 2 == 1:
                continue

            background_rect = QRect(int(i * time_scale), 0, int(time_scale), info.rect.height())
            painter.fillRect(background_rect, palette.background_alternate)

        if not points:
            return

        pen = QPen()
        pen.setWidth(2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setColor(palette.curve)
        painter.setPen(pen)
        for index, point in enumerate(points):
            x = int(point.time * time_scale)
            y = int((1.0 - point.value) * value_scale)

            if index == len(points) - 1 and point.time < clip.time_configuration.duration:
                painter.drawLine(x, y, info.rect.width(), y)

            if index == 0 and point.time > 0.0:
                painter.drawLine(0, y, x, y)

            if index < len(points) - 1:
                x1 = int(points[index + 1].time * time_scale)
                y1 = int((1.0 - points[index + 1].value) * value_scale)
                painter.drawLine(x, y, x1, y1)

        if info.draw_points:
            for point in points:
                x = int(point.time * time_scale)
                y = int((1.0 - point.value) * value_scale)

                pen.setWidth(10)
                pen.setColor(
                    palette.item_selected if point == info.selected_point else palette.primary
                )
                painter.setPen(pen)
                painter.drawPoint(x, y)

                if point == info.hovered_point:
                    pen.setWidth(20)
                    pen.setColor(palette.item_hovered)
                    painter.setPen(pen)
                    painter.drawPoint(x, y)

        pen.setWidth(2)
        pen.setColor(palette.curve)
        painter.setPen(pen)
        x = int(clip.play_position * time_scale)
        painter.drawLine(x, 0, x, info.rect.height())

        painter.restore()
