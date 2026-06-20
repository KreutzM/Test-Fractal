from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_CONFIG_PATH = Path("config/orchestrator.json")


class ConfigError(ValueError):
    pass


def load_config(path: Path | str = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(f"Config file not found: {config_path}")
    data = json.loads(config_path.read_text(encoding="utf-8"))
    validate_config(data)
    return data


def validate_config(data: dict[str, Any]) -> None:
    required = ["model", "base_branch", "work_branch_prefix", "max_cycles", "labels", "codex"]
    missing = [key for key in required if key not in data]
    if missing:
        raise ConfigError(f"Missing required config keys: {', '.join(missing)}")
    if not isinstance(data["max_cycles"], int) or data["max_cycles"] < 1:
        raise ConfigError("max_cycles must be an integer >= 1")
    if not isinstance(data.get("test_commands", []), list):
        raise ConfigError("test_commands must be a list of shell commands")
