from PySide6.QtWidgets import QApplication

from frangiluxlib.components.clip_point.reference_store import ClipPointReferenceStore
from frangiluxlib.components.clip.store import ClipStore
from frangiluxlib.components.layer.store import LayerStore

from pyside6helpers import css
from pyside6helpers.main_window import MainWindow

from frangiluxdesktop.palette import Palette
from frangiluxdesktop.widgets.central_widget import CentralWidget


app = QApplication([])
app.setOrganizationName("Frangitron")
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

#
# Layers
LayerStore().load()

#
# Main Window
main_window = MainWindow()
main_window.setCentralWidget(CentralWidget())
main_window.show()

app.exec()
