import os.path

from PySide6.QtWidgets import QApplication

from frangiluxlib.components.clip_store import ClipStore
from pyside6helpers import css
from pyside6helpers.main_window import MainWindow

from frangiluxdesktop.widgets.clip_editor.widget import ClipEditorWidget
from frangiluxlib.components.clip import Clip
from frangiluxlib.components.time_configuration import TimeConfiguration, TimeConfigurationMode


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
css.load_onto(app)

clip_editor = ClipEditorWidget()
clip_editor.set_clip(clip_store.clips[0])

main_window = MainWindow(
    settings_tuple=("Frangitron", "Frangilux")
)
main_window.setCentralWidget(clip_editor)
main_window.show()

app.exec()
