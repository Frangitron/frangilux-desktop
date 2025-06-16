import os.path

from PySide6.QtWidgets import QApplication

from frangiluxlib.components.clip.clip import Clip
from frangiluxlib.components.clip_point.reference_store import ClipPointReferenceStore
from frangiluxlib.components.clip.store import ClipStore
from frangiluxlib.components.time_configuration import TimeConfiguration, TimeConfigurationMode

from pyside6helpers import css
from pyside6helpers.main_window import MainWindow

from frangiluxdesktop.palette import Palette
from frangiluxdesktop.widgets import ClipEditorWidget, LayerEditorWidget

clip_store = ClipStore()
if not os.path.exists("clips.json"):
    clip = Clip(
        name="test",
        time_configuration=TimeConfiguration(
            duration=4.3,
            mode=TimeConfigurationMode.Tempo
        )
    )
    clip_store.clips = [clip]
    clip_store.save()
else:
    clip_store.load()

app = QApplication([])
app.setApplicationName("Frangilux")
app.aboutToQuit.connect(clip_store.save)
app.aboutToQuit.connect(ClipPointReferenceStore().save)

css.load_onto(app)
Palette().init()

reference_store = ClipPointReferenceStore()
reference_store.load()

clip_editor = ClipEditorWidget()
clip_editor.set_clip(clip_store.clips[0])

layer_editor = LayerEditorWidget()
layer_editor.show()

main_window = MainWindow(
    settings_tuple=("Frangitron", "Frangilux")
)
main_window.setCentralWidget(clip_editor)
main_window.show()

app.exec()
