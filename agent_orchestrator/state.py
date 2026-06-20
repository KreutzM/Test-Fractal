from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


STATE_ROOT = Path(".agent/runs")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class RunState:
    issue: int
    branch: str
    status: str = "initialized"
    cycle: int = 0
    started_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    finished_at: str | None = None
    duration_ms: int | None = None
    run_id: str | None = None
    final_decision: str | None = None
    base_sha: str | None = None
    head_sha: str | None = None
    planner_output: str | None = None
    builder_output: str | None = None
    reviewer_output: str | None = None
    test_output: str | None = None
    run_log_output: str | None = None
    events_output: str | None = None
    summary_output: str | None = None
    last_error: str | None = None
    pr_url: str | None = None

    @property
    def run_dir(self) -> Path:
        return STATE_ROOT / f"issue-{self.issue}"

    @property
    def path(self) -> Path:
        return self.run_dir / "state.json"

    def save(self) -> None:
        self.updated_at = utc_now()
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(asdict(self), indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, issue: int) -> "RunState":
        path = STATE_ROOT / f"issue-{issue}" / "state.json"
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        return cls(**data)

    @classmethod
    def exists(cls, issue: int) -> bool:
        return (STATE_ROOT / f"issue-{issue}" / "state.json").exists()
