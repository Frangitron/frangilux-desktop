from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QSlider

from pythonhelpers.singleton_metaclass import SingletonMetaclass


class Palette(metaclass=SingletonMetaclass):

    def __init__(self):
        self.primary: QColor | None = None

        self.background_alternate: QColor | None = None
        self.curve: QColor | None = None
        self.item_hovered: QColor | None = None
        self.item_selected: QColor | None = None

    def init(self):
        widget = QSlider()
        self.primary = widget.palette().color(QPalette.ColorRole.Highlight)

        self.background_alternate = QColor(255, 255, 255, 15)
        self.curve = QColor(128, 128, 128)
        self.item_hovered = QColor(255, 255, 255, 50)
        self.item_selected = QColor(255, 255, 255)
