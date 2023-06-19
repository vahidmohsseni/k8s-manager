import os
from pathlib import Path

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", ".uploads")


def file_exists(filename):
    """Check if file exists"""
    try:
        for file in Path(UPLOAD_DIR).glob("*"):
            if file.name == filename:
                return True
    except FileNotFoundError:
        return False


def get_filenames() -> list[str]:
    try:
        return [file.name for file in Path(UPLOAD_DIR).glob("*")]
    except Exception:
        return []
