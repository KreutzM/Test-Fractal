from __future__ import annotations

from pathlib import Path


def normalize_repo(repo: Path | str) -> Path:
    return Path(repo).expanduser().resolve()
