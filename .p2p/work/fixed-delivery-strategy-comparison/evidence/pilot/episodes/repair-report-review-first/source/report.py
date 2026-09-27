from pathlib import Path

def save_report(path, text):
    try:
        Path(path).write_text(text, encoding="utf-8")
    except OSError:
        pass
