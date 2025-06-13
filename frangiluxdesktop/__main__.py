from PySide6.QtWidgets import QApplication

from pyside6helpers import css
from pyside6helpers.main_window import MainWindow

from frangiluxdesktop.widgets.clip_editor.widget import ClipEditorWidget
from frangiluxlib.components.clip import Clip
from frangiluxlib.components.time_configuration import TimeConfiguration, TimeConfigurationMode


clip = Clip(
    name="test",
    time_configuration=TimeConfiguration(
        duration=4.3,
        mode=TimeConfigurationMode.Tempo
    )
)


app = QApplication([])
css.load_onto(app)

clip_editor = ClipEditorWidget()
clip_editor.set_clip(clip)

main_window = MainWindow(
    settings_tuple=("Frangitron", "Frangilux")
)
main_window.setWindowTitle("Frangilux")
main_window.setCentralWidget(clip_editor)
main_window.show()

app.exec()
