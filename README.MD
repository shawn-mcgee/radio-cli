### Requirements

```bash
pip install -r requirements.txt
```

> [!NOTE]
> This project uses `ffmpeg-python` and requires ffmpeg to be available on the system path

### Usage

```bash
python cli.py
```

> [!NOTE]
> `main.py` is the old entry point, but remains available for testing purposes. It is recommended to use `radio.py` instead.

### Build

```bash
pyinstaller --onefile --noconsole --collect-data ytmusicapi radio-gui.py
```