import os
import logging
from pathlib import Path
from datetime import datetime

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", ".uploads")


logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y/%m/%d %H:%M:%S"
)
logger = logging.getLogger("waitress")
logger.setLevel(logging.INFO if os.environ.get("ENV") == "prod" else logging.DEBUG)


def file_exists(filename: str):
    """Check if file exists"""
    try:
        for file in Path(UPLOAD_DIR).glob("*"):
            if file.name == filename:
                return True
    except FileNotFoundError:
        return False


def get_filenames() -> list[str]:
    try:
        return [
            {
                "id": file.name.split(".")[0],
                "modified_at": datetime.fromtimestamp(file.stat().st_mtime),
                "created_at": datetime.fromtimestamp(file.stat().st_ctime),
                "size_in_bytes": file.stat().st_size,
                "extension": file.suffix,
            }
            for file in Path(UPLOAD_DIR).glob("*")
        ]
    except Exception:
        return []
