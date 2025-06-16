from PySide6.QtWidgets import QApplication

from frangiluxlib.components.clip_point.reference_store import ClipPointReferenceStore
from frangiluxlib.components.clip.store import ClipStore
from frangiluxlib.components.layer.store import LayerStore

from pyside6helpers import css
from pyside6helpers.main_window import MainWindow

from frangiluxdesktop.palette import Palette
from frangiluxdesktop.widgets import ClipEditorWidget, LayerEditorWidget


app = QApplication([])
app.setApplicationName("Frangilux")
app.aboutToQuit.connect(ClipStore().save)
app.aboutToQuit.connect(ClipPointReferenceStore().save)
app.aboutToQuit.connect(LayerStore().save)

css.load_onto(app)
Palette().init()

#
# Clips & References
ClipStore().load()
reference_store = ClipPointReferenceStore()
reference_store.load()

clip_editor = ClipEditorWidget()
clip_editor.set_clip(ClipStore().clips[0])

#
# Layers
LayerStore().load()
layer_editor = LayerEditorWidget()

#
# Main Window
main_window = MainWindow(
    settings_tuple=("Frangitron", "Frangilux")
)
main_window.setCentralWidget(layer_editor)
main_window.show()

app.exec()
