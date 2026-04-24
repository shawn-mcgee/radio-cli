### Requirements
To install the project dependencies, run the following command
```bash
pip install -r requirements.txt
```

> [!NOTE]
> At the time of writing, project dependencies require Python 3.13. Project works best when leveraging a virtual environment.
>
> ### Configuring a  virtual environment
> ```bash
> python -m venv ./.venv
> ```
>
>
> ### Activating the virtual environment
> ```bash
> ./venv/Scripts/activate
> ```

> [!NOTE]
> This project uses `ffmpeg-python` which requires ffmpeg to be available on the system path. If you are running Windows, check out [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) for more windows-ready builds that you can install with one command.

### Usage

To run the cli, run the following command

```bash
python radio-cli.py
```

To run the gui, run the following command

```bash
python radio-gui.py
```

### Build

To build the gui, run the following command

```bash
pyinstaller --onefile --noconsole --collect-data ytmusicapi radio-gui.py
```