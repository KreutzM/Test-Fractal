from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


STATE_ROOT = Path(".agent/runs")
_LAST_STATUS: dict[int, str] = {}
_USAGE_KEYS = (
    "input_tokens",
    "cached_input_tokens",
    "uncached_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
    "total_tokens",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _duration_ms(started_at: str, finished_at: str | None = None) -> int:
    start = datetime.fromisoformat(started_at)
    end = datetime.fromisoformat(finished_at) if finished_at else datetime.now(timezone.utc)
    return int((end - start).total_seconds() * 1000)


def _format_duration(ms: int | None) -> str:
    if ms is None:
        return "unknown"
    seconds = ms / 1000
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes, rem = divmod(seconds, 60)
    if minutes < 60:
        return f"{int(minutes)}m {rem:.0f}s"
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours)}h {int(minutes)}m"


def _metrics_sidecar(path_text: str | None) -> str | None:
    if not path_text:
        return None
    path = Path(path_text)
    sidecar = path.with_suffix(path.suffix + ".metrics.json")
    return str(sidecar) if sidecar.exists() else None


def _safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _cycle_from_output_path(path_text: str | None) -> int | None:
    if not path_text:
        return None
    name = Path(path_text).name
    for marker in ("builder-cycle-", "reviewer-cycle-"):
        if marker not in name:
            continue
        suffix = name.split(marker, 1)[1]
        number = suffix.split(".", 1)[0]
        return _safe_int(number)
    return 0 if name.startswith("planner") else None


def _read_metric(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _usage_entry(metric_path: Path, metric: dict[str, Any]) -> dict[str, Any] | None:
    raw_usage = metric.get("codex_usage")
    if not isinstance(raw_usage, dict):
        return None
    input_tokens = _safe_int(raw_usage.get("input_tokens"))
    cached_input_tokens = _safe_int(raw_usage.get("cached_input_tokens"))
    output_tokens = _safe_int(raw_usage.get("output_tokens"))
    reasoning_output_tokens = _safe_int(raw_usage.get("reasoning_output_tokens"))
    total_tokens = _safe_int(raw_usage.get("total_tokens")) or input_tokens + output_tokens
    return {
        "role": metric.get("role") or "unknown",
        "cycle": _cycle_from_output_path(metric.get("output_path")),
        "metrics_path": str(metric_path),
        "usage_source": metric.get("usage_source"),
        "input_tokens": input_tokens,
        "cached_input_tokens": cached_input_tokens,
        "uncached_input_tokens": max(input_tokens - cached_input_tokens, 0),
        "output_tokens": output_tokens,
        "reasoning_output_tokens": reasoning_output_tokens,
        "total_tokens": total_tokens,
    }


def _empty_usage_totals() -> dict[str, int]:
    return {key: 0 for key in _USAGE_KEYS}


def _usage_totals(entries: list[dict[str, Any]]) -> dict[str, int]:
    totals = _empty_usage_totals()
    for entry in entries:
        for key in _USAGE_KEYS:
            totals[key] += _safe_int(entry.get(key))
    return totals


def _usage_sort_key(entry: dict[str, Any]) -> tuple[int, int, str]:
    role_order = {"planner": 0, "builder": 1, "reviewer": 2}
    role = str(entry.get("role") or "unknown")
    cycle = entry.get("cycle")
    return (role_order.get(role, 99), _safe_int(cycle), str(entry.get("metrics_path") or ""))


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

    @property
    def events_path(self) -> Path:
        return self.run_dir / "events.jsonl"

    @property
    def run_json_path(self) -> Path:
        return self.run_dir / "run.json"

    @property
    def summary_path(self) -> Path:
        return self.run_dir / "summary.md"

    def save(self) -> None:
        self.updated_at = utc_now()
        if self.run_id is None:
            self.run_id = f"issue-{self.issue}-{self.started_at.replace('-', '').replace(':', '')}"
        if self.status in {"blocked", "ready_for_human"} and self.finished_at is None:
            self.finished_at = self.updated_at
        self.duration_ms = _duration_ms(self.started_at, self.finished_at)
        self.run_log_output = str(self.run_json_path)
        self.events_output = str(self.events_path)
        self.summary_output = str(self.summary_path)

        self.run_dir.mkdir(parents=True, exist_ok=True)
        data = asdict(self)
        self.path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self._append_event(data)
        self._write_run_json(data)
        self._write_summary()
        self._print_status_change()

    def _role_metric_paths(self) -> dict[str, str | None]:
        return {
            "planner": _metrics_sidecar(self.planner_output),
            "builder": _metrics_sidecar(self.builder_output),
            "reviewer": _metrics_sidecar(self.reviewer_output),
        }

    def _is_current_run_metric(self, path: Path) -> bool:
        """Ignore stale metrics left over from previous runs of the same issue."""
        try:
            started = datetime.fromisoformat(self.started_at).timestamp()
            modified = path.stat().st_mtime
        except (OSError, ValueError):
            return False
        return modified >= started - 1

    def _token_usage(self) -> dict[str, Any]:
        entries: list[dict[str, Any]] = []
        for path in sorted(self.run_dir.glob("*.metrics.json")):
            if not self._is_current_run_metric(path):
                continue
            metric = _read_metric(path)
            if metric is None:
                continue
            entry = _usage_entry(path, metric)
            if entry is not None:
                entries.append(entry)
        entries.sort(key=_usage_sort_key)
        return {
            "roles": entries,
            "totals": _usage_totals(entries),
        }

    def _append_event(self, data: dict[str, Any]) -> None:
        event = {
            "ts": self.updated_at,
            "event": "state_saved",
            "issue": self.issue,
            "run_id": self.run_id,
            "status": self.status,
            "cycle": self.cycle,
            "branch": self.branch,
            "duration_ms": self.duration_ms,
            "last_error": self.last_error,
            "pr_url": self.pr_url,
        }
        with self.events_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")

    def _write_run_json(self, data: dict[str, Any]) -> None:
        run_data = {
            **data,
            "duration": _format_duration(self.duration_ms),
            "artifacts": {
                "state": str(self.path),
                "events": str(self.events_path),
                "summary": str(self.summary_path),
                "planner": self.planner_output,
                "builder": self.builder_output,
                "reviewer": self.reviewer_output,
                "tests": self.test_output,
                "role_metrics": self._role_metric_paths(),
            },
            "token_usage": self._token_usage(),
        }
        self.run_json_path.write_text(
            json.dumps(run_data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def _write_summary(self) -> None:
        metrics = self._role_metric_paths()
        token_usage = self._token_usage()
        lines = [
            "# Agent Run Summary",
            "",
            f"- Run ID: `{self.run_id}`",
            f"- Issue: #{self.issue}",
            f"- Status: `{self.status}`",
            f"- Cycle: `{self.cycle}`",
            f"- Branch: `{self.branch}`",
            f"- Duration: {_format_duration(self.duration_ms)}",
            f"- Started: {self.started_at}",
            f"- Updated: {self.updated_at}",
            f"- Finished: {self.finished_at or 'n/a'}",
            f"- Final decision: `{self.final_decision or 'n/a'}`",
            f"- PR: {self.pr_url or 'n/a'}",
            "",
            "## Artifacts",
            "",
            f"- State: `{self.path}`",
            f"- Events: `{self.events_path}`",
            f"- Run JSON: `{self.run_json_path}`",
            f"- Planner: `{self.planner_output or 'n/a'}`",
            f"- Builder: `{self.builder_output or 'n/a'}`",
            f"- Reviewer: `{self.reviewer_output or 'n/a'}`",
            f"- Tests: `{self.test_output or 'n/a'}`",
            "",
            "## Role metrics",
            "",
            f"- Planner: `{metrics['planner'] or 'n/a'}`",
            f"- Builder: `{metrics['builder'] or 'n/a'}`",
            f"- Reviewer: `{metrics['reviewer'] or 'n/a'}`",
        ]
        if token_usage["roles"]:
            lines.extend(
                [
                    "",
                    "## Token usage",
                    "",
                    "| Role | Cycle | Input | Cached | Uncached | Output | Reasoning | Total |",
                    "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
                ]
            )
            for entry in token_usage["roles"]:
                cycle = entry["cycle"] if entry["cycle"] is not None else "n/a"
                lines.append(
                    f"| {entry['role']} | {cycle} | {entry['input_tokens']} | "
                    f"{entry['cached_input_tokens']} | {entry['uncached_input_tokens']} | "
                    f"{entry['output_tokens']} | {entry['reasoning_output_tokens']} | "
                    f"{entry['total_tokens']} |"
                )
            totals = token_usage["totals"]
            lines.append(
                f"| **Total** |  | **{totals['input_tokens']}** | "
                f"**{totals['cached_input_tokens']}** | "
                f"**{totals['uncached_input_tokens']}** | "
                f"**{totals['output_tokens']}** | "
                f"**{totals['reasoning_output_tokens']}** | "
                f"**{totals['total_tokens']}** |"
            )
        if self.last_error:
            lines.extend(["", "## Last error", "", self.last_error])
        self.summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _print_status_change(self) -> None:
        if _LAST_STATUS.get(self.issue) == self.status:
            return
        _LAST_STATUS[self.issue] = self.status
        print(f"[agent] issue #{self.issue} status={self.status} cycle={self.cycle}")

    @classmethod
    def load(cls, issue: int) -> "RunState":
        path = STATE_ROOT / f"issue-{issue}" / "state.json"
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        return cls(**data)

    @classmethod
    def exists(cls, issue: int) -> bool:
        return (STATE_ROOT / f"issue-{issue}" / "state.json").exists()
