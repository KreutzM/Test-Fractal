from __future__ import annotations

import os
from pathlib import Path

from . import codex_runner
from . import state as state_module


def normalize_repo(repo: Path | str) -> Path:
    path = Path(repo).expanduser().resolve()
    return path


def current_working_directory() -> Path:
    return Path(os.getcwd()).resolve()


def switch_working_directory(path: Path) -> None:
    os.chdir(path)
