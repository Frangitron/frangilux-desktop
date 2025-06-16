from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGroupBox, QCheckBox, QGridLayout, QLineEdit, QComboBox, QPushButton

from frangiluxlib.reactive_channels import ReactiveChannels
from frangiluxlib.components.clip_point.clip_point import ClipPoint
from frangiluxlib.components.clip_point.reference_store import ClipPointReferenceStore

from pyside6helpers import combo
from pythonhelpers.reactive import Reactive, Observer


class PointReferenceEditor(QGroupBox):
    PointChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._reference_store = ClipPointReferenceStore()
        self._point: ClipPoint | None = None
        self._suspend_update = False

        self.setTitle("Point reference")

        self.combobox_reference = QComboBox()
        Reactive().add_observer(Observer(
            channel=ReactiveChannels.References,
            callback=lambda references: combo.update(self.combobox_reference, list(references.keys()))
        ))
        self.combobox_reference.currentIndexChanged.connect(self._update_point)

        self.button_free = QPushButton("Free reference")
        self.button_free.clicked.connect(self._free)

        self.checkbox_reference_edit = QCheckBox("Allow reference edition")
        self.checkbox_reference_edit.stateChanged.connect(self._update_point)
        self.checkbox_reference_edit.setEnabled(False)

        self.lineedit_new_reference_name = QLineEdit()
        self.lineedit_new_reference_name.setPlaceholderText("New reference name")
        self.lineedit_new_reference_name.returnPressed.connect(self._new_reference)
        self.lineedit_new_reference_name.textChanged.connect(lambda text: self.button_new_reference.setEnabled(text != ""))

        self.button_new_reference = QPushButton("Make reference")
        self.button_new_reference.clicked.connect(self._new_reference)
        self.button_new_reference.setEnabled(False)

        layout = QGridLayout(self)
        layout.addWidget(self.combobox_reference, 0, 0)
        layout.addWidget(self.button_free, 0, 1)
        layout.addWidget(self.checkbox_reference_edit, 1, 0, 1, 2)
        layout.addWidget(self.lineedit_new_reference_name, 2, 0)
        layout.addWidget(self.button_new_reference, 2, 1)

        self.setEnabled(False)
        self.setFixedWidth(250)

    def set_point(self, point: ClipPoint | None):
        self.setEnabled(point is not None)
        self._point = point

        if point is None:
            return

        self._suspend_update = True
        self.checkbox_reference_edit.setChecked(self._point.is_reference_editable)
        self.button_free.setEnabled(self._point.is_reference)
        self.checkbox_reference_edit.setEnabled(self._point.is_reference)
        if self._point.is_reference:
            self.combobox_reference.setCurrentIndex(self.combobox_reference.findText(self._point.reference_name))
        else:
            self.combobox_reference.setCurrentIndex(-1)

        self._suspend_update = False

    def _update_point(self):
        if self._point is None or self._suspend_update:
            return

        self._point.is_reference = self.combobox_reference.currentIndex() >= 0
        self.button_free.setEnabled(self._point.is_reference)
        self.checkbox_reference_edit.setEnabled(self._point.is_reference)

        text =  self.combobox_reference.currentText()
        self._point.reference_name = text if text else None

        if self._point.reference_name is not None:
            self._point.value = self._reference_store.get(self._point)

        self._point.is_reference_editable = self.checkbox_reference_edit.isChecked()

        self.PointChanged.emit()

    def _new_reference(self):
        if self._point is None:
            return

        name = self.lineedit_new_reference_name.text()
        if name == "":
            return

        self._reference_store.new(name, self._point)
        self._point.reference_name = name
        self._point.is_reference = True

        self.set_point(self._point)  # FIXME meh

        self.lineedit_new_reference_name.setText("")
        self.PointChanged.emit()

    def _free(self):
        if self._point is None:
            return

        self.combobox_reference.setCurrentIndex(-1)  # Will trigger point update
        self.PointChanged.emit()
