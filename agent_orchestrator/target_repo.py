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


def prepare_target_context(config_path: Path | str, repo: Path | str) -> tuple[Path, Path, Path]:
    old_cwd = current_working_directory()
    target_repo = normalize_repo(repo)
    config = Path(config_path)
    absolute_config = config if config.is_absolute() else old_cwd / config
    return old_cwd, target_repo, absolute_config
