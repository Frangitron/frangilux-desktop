from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGroupBox, QCheckBox, QVBoxLayout, QLineEdit, QComboBox, QPushButton

from frangiluxlib.components.clip_point import ClipPoint
from frangiluxlib.components.clip_point_reference_store import ClipPointReferenceStore

from pyside6helpers import combo


class PointEditor(QGroupBox):
    ValueChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._reference_store = ClipPointReferenceStore()
        self._point: ClipPoint | None = None
        self._suspend_update = False

        self.setTitle("Selected point")

        self.checkbox_reference = QCheckBox("Reference")
        self.checkbox_reference.stateChanged.connect(self._update_point)

        self.checkbox_reference_edit = QCheckBox("Edit reference")
        self.checkbox_reference_edit.stateChanged.connect(self._update_point)

        self.combobox_reference = QComboBox()
        self.combobox_reference.addItems(self._reference_store.references_names())
        self.combobox_reference.currentIndexChanged.connect(self._update_point)

        self.lineedit_new_reference_name = QLineEdit()
        self.button_new_reference = QPushButton("Make reference")
        self.button_new_reference.clicked.connect(self._new_reference)

        layout = QVBoxLayout(self)
        layout.addWidget(self.checkbox_reference)
        layout.addWidget(self.combobox_reference)
        layout.addWidget(self.checkbox_reference_edit)
        layout.addWidget(self.lineedit_new_reference_name)
        layout.addWidget(self.button_new_reference)

        self.setEnabled(False)
        self.setFixedWidth(200)

    def set_point(self, point: ClipPoint | None):
        self.setEnabled(point is not None)
        self._point = point

        if point is None:
            return

        self._suspend_update = True
        self.checkbox_reference.setChecked(self._point.is_reference)
        self.checkbox_reference_edit.setChecked(self._point.is_reference_editable)
        self.combobox_reference.setCurrentIndex(self.combobox_reference.findText(self._point.reference_name))
        self._suspend_update = False

    def _update_point(self):
        if self._point is None or self._suspend_update:
            return

        self._point.is_reference = self.checkbox_reference.isChecked()
        text =  self.combobox_reference.currentText()
        self._point.reference_name = text if text else None

        if self._point.reference_name is not None:
            self._point.value = self._reference_store.get(self._point)

        self._point.is_reference_editable = self.checkbox_reference_edit.isChecked()

        self.ValueChanged.emit()

    def _new_reference(self):
        if self._point is None:
            return

        name = self.lineedit_new_reference_name.text()
        if name == "":
            return

        self._reference_store.new(name, self._point)
        self._point.reference_name = name
        self._point.is_reference = True

        combo.update(self.combobox_reference, self._reference_store.references_names())
        self.set_point(self._point)  # FIXME meh
