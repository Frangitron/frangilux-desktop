from PySide6.QtWidgets import QWidget, QGridLayout, QListWidget


class LayerEditorWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layers_list = QListWidget()

        layout = QGridLayout(self)
        layout.addWidget(self.layers_list, 0, 0)
