"""Locate the content and scene modules used by the video scripts."""
import os
import sys
from pathlib import Path


def configure_source():
    default = Path(__file__).resolve().parents[1] / "templates"
    source = Path(os.environ.get("VIDEO_SOURCE_DIR", default)).expanduser().resolve()
    missing = [name for name in ("content.py", "scenes.py") if not (source / name).is_file()]
    if missing:
        raise SystemExit(f"VIDEO_SOURCE_DIR={source} 缺少：{', '.join(missing)}")
    sys.path.insert(0, str(source))
    return source
