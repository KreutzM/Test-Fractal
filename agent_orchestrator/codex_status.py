from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .run_log import utc_now
from .shell import run_command


def default_status_command(config: dict[str, Any]) -> list[str] | None:
    codex_config = config.get("codex", {}) if isinstance(config, dict) else {}
    command = codex_config.get("status_command")
    if command in (None, False, ""):
        return None
    if isinstance(command, str):
        return [command]
    if isinstance(command, list) and all(isinstance(part, str) for part in command):
        return command
    raise ValueError("codex.status_command must be a string, a list of strings, or null")


def capture_status_snapshot(
    *,
    output_path: Path,
    label: str,
    config: dict[str, Any],
    cwd: Path | str = ".",
) -> dict[str, Any]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = default_status_command(config)
    started_at = utc_now()
    started = time.perf_counter()

    if command is None:
        snapshot = {
            "label": label,
            "available": False,
            "reason": "No codex.status_command configured. Codex /status is currently a TUI command, not a codex exec JSONL event.",
            "started_at": started_at,
            "duration_ms": int((time.perf_counter() - started) * 1000),
            "command": None,
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "parsed": None,
        }
        output_path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return snapshot

    result = run_command(command, cwd=cwd, check=False)
    parsed = _try_parse_json(result.stdout)
    snapshot = {
        "label": label,
        "available": result.ok,
        "reason": None if result.ok else "Configured codex status command failed.",
        "started_at": started_at,
        "duration_ms": int((time.perf_counter() - started) * 1000),
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "parsed": parsed,
    }
    output_path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return snapshot


def write_status_delta(*, before_path: Path, after_path: Path, output_path: Path) -> dict[str, Any]:
    before = _load_json_file(before_path)
    after = _load_json_file(after_path)
    delta = {
        "available": bool(before.get("available")) and bool(after.get("available")),
        "before": str(before_path),
        "after": str(after_path),
        "note": "Raw snapshots are stored verbatim. Structured delta is only available when Codex exposes a stable headless status payload.",
    }
    output_path.write_text(json.dumps(delta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return delta


def _try_parse_json(text: str) -> Any | None:
    stripped = text.strip()
    if not stripped:
        return None
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        return None


def _load_json_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}
