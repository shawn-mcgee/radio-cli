from gui.types.playlist import Playlist
from gui.types.song     import Song
from gui.types.result   import Result

import gui.services.gs as gs
import gui.services.yt as yt

import sys
import os
import threading
import random
import json
from pathlib import Path
from PySide6.QtCore import Signal, QObject, Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QCheckBox, QComboBox, QMessageBox
)
import pygame

# -----------------------------
# Worker class
# -----------------------------
class RadioWorker(QObject):
    status_update = Signal(str)
    now_playing   = Signal(str)
    next_song     = Signal(str)
    finished      = Signal()

    def __init__(self, playlist_id):
        super().__init__()
        self.playlist_id = playlist_id
        self._stop_flag = threading.Event()
        self._skip_flag = threading.Event()
        pygame.mixer.init()

    def stop(self):
        self._stop_flag.set()

    def skip(self):
        self._skip_flag.set()
    
    def run(self):
        playlist_result = gs.fetch_playlist(self.playlist_id)
        if not playlist_result.ok:
            self.status_update.emit(f"❌ Playlist '{self.playlist_id}' is unavailable!")
            return
        playlist = playlist_result.value.songs
        if not playlist:
            self.status_update.emit(f"❌ Playlist '{self.playlist_id}' has no approved songs!")
            return

        while not self._stop_flag.is_set():
            random.shuffle(playlist)
            for i, song in enumerate(playlist):
                if self._stop_flag.is_set():
                    pygame.mixer.music.stop()
                    break
                
                self.next_song.emit(str(song))
                
                self.status_update.emit(f"🔎 Resolving '{song}'...")
                result = yt.resolve_video_id(song)
                if not result.ok:
                    self.status_update.emit(f"❌ Unable to resolve '{song}', skipping ...")
                    continue
                video_id = result.value

                self.status_update.emit(f"⬇️ Downloading '{song}'...")
                result = yt.download_audio(video_id)
                if not result.ok:
                    self.status_update.emit(f"❌ Unable to download '{song}', skipping ...")
                    continue

                self.status_update.emit(f"🔃 Converting '{song}'...")
                result = yt.convert_audio(video_id)
                if not result.ok:
                    self.status_update.emit(f"❌ Unable to convert '{song}', skipping ...")
                    continue

                
                if pygame.mixer.music.get_busy():
                  self.status_update.emit(f"⌛ Waiting for current song to finish playing...")
                  while pygame.mixer.music.get_busy():
                    if self._stop_flag.is_set() or self._skip_flag.is_set():
                        pygame.mixer.music.stop()
                        self._skip_flag.clear()
                        break
                    pygame.time.delay(100)

                self.now_playing.emit(str(song))
                self.status_update.emit(f"▶️ Playing '{song}'...")
                pygame.mixer.music.load(f"./radio/{video_id}.ogg")
                pygame.mixer.music.play()

        self.finished.emit()

# -----------------------------
# Main UI class
# -----------------------------
class RadioApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PTEC Radio")
        self.resize(400, 300)

        self.config_file = Path("radio.json")
        self.load_config()

        # Layouts
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Playlist selector
        self.playlist_dropdown = QComboBox()
        playlist_ids = gs.fetch_playlist_ids()
        if not playlist_ids.ok:
            raise Exception(f"Unable to fetch playlist ids: {playlist_ids.error}")  
        playlist_ids = playlist_ids.value

        self.playlist_dropdown.addItems(playlist_ids)

        if self.config.get("playlist_id") in playlist_ids:
            idx = playlist_ids.index(self.config["playlist_id"])
            self.playlist_dropdown.setCurrentIndex(idx)

        self.autoplay_checkbox = QCheckBox("Automatically start on next launch")
        self.autoplay_checkbox.setChecked(self.config.get("autoplay", False))

        self.main_layout.addWidget(QLabel("Select Playlist:"))
        self.main_layout.addWidget(self.playlist_dropdown)
        self.main_layout.addWidget(self.autoplay_checkbox)

        # Play button
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.start_radio)
        self.main_layout.addWidget(self.play_button)

        # Status / now playing
        self.status_label = QLabel("Idle")
        self.current_song_label = QLabel("Now Playing: ---")
        self.next_song_label    = QLabel("Next Song: ---")
        self.main_layout.addWidget(self.status_label)
        self.main_layout.addWidget(self.current_song_label)
        self.main_layout.addWidget(self.next_song_label)

        # Stop / Skip buttons
        self.buttons_layout = QHBoxLayout()
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_radio)
        self.skip_button = QPushButton("Skip")
        self.skip_button.clicked.connect(self.skip_song)
        self.buttons_layout.addWidget(self.stop_button)
        self.buttons_layout.addWidget(self.skip_button)
        self.main_layout.addLayout(self.buttons_layout)

        self.worker_thread = None
        self.worker = None

        # Auto-play if selected
        if self.autoplay_checkbox.isChecked():
            self.start_radio()

    # -----------------------------
    # Config helpers
    # -----------------------------
    def load_config(self):
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                self.config = json.load(f)
        else:
            self.config = {}

    def save_config(self):
        self.config["autoplay"] = self.autoplay_checkbox.isChecked()
        self.config["playlist_id"] = self.playlist_dropdown.currentText()
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)

    # -----------------------------
    # Radio control
    # -----------------------------
    def start_radio(self):
        # Save config
        self.save_config()

        if self.worker_thread and self.worker_thread.is_alive():
            QMessageBox.warning(self, "Already Running", "Radio is already running!")
            return

        playlist_id = self.playlist_dropdown.currentText()
        self.worker = RadioWorker(playlist_id)
        self.worker.status_update.connect(self.update_status)
        self.worker.now_playing.connect(self.update_current)
        self.worker.next_song.connect(self.update_next)
        self.worker.finished.connect(self.radio_finished)

        self.worker_thread = threading.Thread(target=self.worker.run, daemon=True)
        self.worker_thread.start()
        self.status_label.setText("Radio started...")

    def stop_radio(self):
        if self.worker:
            self.worker.stop()
            self.status_label.setText("Stopping radio...")

    def skip_song(self):
        if self.worker:
            self.worker.skip()
            self.status_label.setText("Skipping current song...")

    # -----------------------------
    # Signal handlers
    # -----------------------------
    def update_status(self, text):
        self.status_label.setText(text)

    def update_current(self, text):
        self.current_song_label.setText(f"🔊 Now Playing: {text}")

    def update_next(self, text):
        self.next_song_label.setText(f"🔜 Next Song: {text}")

    def radio_finished(self):
        self.status_label.setText("Radio stopped.")
        self.current_song_label.setText("💤 Now Playing: ---")
        self.next_song_label.setText("💤 Next Song: ---")