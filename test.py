import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput


class SimplePlayer(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Minimal PySide6 Audio Player")
        self.resize(300, 150)

        # UI
        self.layout = QVBoxLayout(self)

        self.label = QLabel("No file loaded")
        self.layout.addWidget(self.label)

        self.load_btn = QPushButton("Load Audio File")
        self.play_btn = QPushButton("Play")
        self.stop_btn = QPushButton("Stop")

        self.layout.addWidget(self.load_btn)
        self.layout.addWidget(self.play_btn)
        self.layout.addWidget(self.stop_btn)

        # Audio setup (IMPORTANT PART)
        self.player = QMediaPlayer()

        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(1.0)  # make sure we hear it

        self.player.setAudioOutput(self.audio_output)

        # State
        self.file_path = None

        # Signals
        self.load_btn.clicked.connect(self.load_file)
        self.play_btn.clicked.connect(self.play_audio)
        self.stop_btn.clicked.connect(self.stop_audio)

        self.player.errorOccurred.connect(self.on_error)

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio File",
            "",
            "Audio Files (*.mp3 *.wav *.ogg *.m4a)"
        )

        if file_path:
            self.file_path = file_path
            self.label.setText(f"Loaded:\n{file_path}")

            print("Loaded file:", file_path)

    def play_audio(self):
        if not self.file_path:
            self.label.setText("No file selected")
            return

        url = QUrl.fromLocalFile(self.file_path)

        self.player.setSource(url)
        self.player.play()

        self.label.setText("Playing...")

        print("State after play:", self.player.playbackState())

    def stop_audio(self):
        self.player.stop()
        self.label.setText("Stopped")

    def on_error(self, error, error_string):
        print("AUDIO ERROR:", error, error_string)
        self.label.setText(f"Error: {error_string}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = SimplePlayer()
    window.show()

    sys.exit(app.exec())