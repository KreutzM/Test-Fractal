from __future__ import annotations

import os
from pathlib import Path


def normalize_repo(repo: Path | str) -> Path:
    path = Path(repo).expanduser().resolve()
    return path


def current_working_directory() -> Path:
    return Path(os.getcwd()).resolve()
