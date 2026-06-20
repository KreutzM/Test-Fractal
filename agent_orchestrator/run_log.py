from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import math
import time
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def compact_utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return math.ceil(len(text) / 4)


def elapsed_ms(started: float) -> int:
    return int((time.perf_counter() - started) * 1000)


def format_duration(ms: int | None) -> str:
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


@dataclass
class StepRecord:
    name: str
    status: str
    started_at: str
    duration_ms: int
    cycle: int | None = None
    role: str | None = None
    details: dict[str, Any] = field(default_factory=dict)


class RunLogger:
    def __init__(
        self,
        run_dir: Path,
        *,
        issue_number: int,
        issue_title: str,
        branch: str,
        base_branch: str,
        model: str,
        max_cycles: int,
        dry_run: bool,
        echo: bool = True,
    ) -> None:
        self.run_dir = run_dir
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.run_id = f"issue-{issue_number}-{compact_utc_now()}"
        self.issue_number = issue_number
        self.issue_title = issue_title
        self.branch = branch
        self.base_branch = base_branch
        self.model = model
        self.max_cycles = max_cycles
        self.dry_run = dry_run
        self.echo = echo
        self.started_at = utc_now()
        self._started_perf = time.perf_counter()
        self.finished_at: str | None = None
        self.final_status: str | None = None
        self.final_decision: str | None = None
        self.last_error: str | None = None
        self.pr_url: str | None = None
        self.base_sha: str | None = None
        self.head_sha: str | None = None
        self.steps: list[StepRecord] = []
        self.events_path = self.run_dir / "events.jsonl"
        self.run_json_path = self.run_dir / "run.json"
        self.summary_path = self.run_dir / "summary.md"
        self.events_path.write_text("", encoding="utf-8")
        self.event(
            "run_started",
            issue=issue_number,
            issue_title=issue_title,
            branch=branch,
            base_branch=base_branch,
            model=model,
            max_cycles=max_cycles,
            dry_run=dry_run,
        )
        self.console(f"issue #{issue_number} -> branch {branch}")

    @property
    def duration_ms(self) -> int:
        return elapsed_ms(self._started_perf)

    def console(self, message: str) -> None:
        if self.echo:
            print(f"[agent] {message}")

    def event(self, event: str, *, level: str = "info", **fields: Any) -> None:
        record = {"ts": utc_now(), "level": level, "event": event, **fields}
        with self.events_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    def add_step(
        self,
        name: str,
        *,
        status: str,
        started_at: str,
        duration_ms: int,
        cycle: int | None = None,
        role: str | None = None,
        **details: Any,
    ) -> None:
        clean_details = {key: value for key, value in details.items() if value is not None}
        self.steps.append(
            StepRecord(
                name=name,
                status=status,
                started_at=started_at,
                duration_ms=duration_ms,
                cycle=cycle,
                role=role,
                details=clean_details,
            )
        )
        self.event(
            "step_finished",
            name=name,
            status=status,
            duration_ms=duration_ms,
            cycle=cycle,
            role=role,
            **clean_details,
        )

    def role_started(self, role: str, *, cycle: int | None, prompt: str, output_path: Path) -> tuple[str, float]:
        started_at = utc_now()
        started = time.perf_counter()
        prompt_chars = len(prompt)
        self.event(
            "role_started",
            role=role,
            cycle=cycle,
            model=self.model,
            prompt_chars=prompt_chars,
            prompt_tokens_estimate=estimate_tokens(prompt),
            output_path=str(output_path),
        )
        suffix = "" if cycle is None else f" cycle {cycle}"
        self.console(f"{role}{suffix} started...")
        return started_at, started

    def role_finished(
        self,
        role: str,
        *,
        cycle: int | None,
        started_at: str,
        started: float,
        status: str,
        returncode: int,
        prompt: str,
        output_text: str,
        output_path: Path,
    ) -> None:
        duration = elapsed_ms(started)
        self.add_step(
            role,
            status=status,
            started_at=started_at,
            duration_ms=duration,
            cycle=cycle,
            role=role,
            returncode=returncode,
            output_path=str(output_path),
            prompt_chars=len(prompt),
            prompt_tokens_estimate=estimate_tokens(prompt),
            output_chars=len(output_text),
            output_tokens_estimate=estimate_tokens(output_text),
        )
        suffix = "" if cycle is None else f" cycle {cycle}"
        self.console(f"{role}{suffix} {status} in {format_duration(duration)} -> {output_path}")

    def finish(
        self,
        *,
        status: str,
        final_decision: str | None = None,
        pr_url: str | None = None,
        last_error: str | None = None,
        base_sha: str | None = None,
        head_sha: str | None = None,
    ) -> None:
        self.finished_at = utc_now()
        self.final_status = status
        self.final_decision = final_decision
        self.pr_url = pr_url
        self.last_error = last_error
        self.base_sha = base_sha
        self.head_sha = head_sha
        level = "error" if last_error else "info"
        self.event(
            "run_finished",
            level=level,
            status=status,
            final_decision=final_decision,
            pr_url=pr_url,
            last_error=last_error,
            duration_ms=self.duration_ms,
            base_sha=base_sha,
            head_sha=head_sha,
        )
        self.write_run_json()
        self.write_summary_md()
        self.console(f"run summary: {self.summary_path}")

    def as_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "issue": self.issue_number,
            "issue_title": self.issue_title,
            "status": self.final_status,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_ms": self.duration_ms,
            "duration": format_duration(self.duration_ms),
            "branch": self.branch,
            "base_branch": self.base_branch,
            "base_sha": self.base_sha,
            "head_sha": self.head_sha,
            "pr_url": self.pr_url,
            "model": self.model,
            "max_cycles": self.max_cycles,
            "dry_run": self.dry_run,
            "final_decision": self.final_decision,
            "last_error": self.last_error,
            "events_path": str(self.events_path),
            "summary_path": str(self.summary_path),
            "steps": [
                {
                    "name": step.name,
                    "status": step.status,
                    "started_at": step.started_at,
                    "duration_ms": step.duration_ms,
                    "duration": format_duration(step.duration_ms),
                    "cycle": step.cycle,
                    "role": step.role,
                    **step.details,
                }
                for step in self.steps
            ],
        }

    def write_run_json(self) -> Path:
        self.run_json_path.write_text(
            json.dumps(self.as_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return self.run_json_path

    def write_summary_md(self) -> Path:
        lines = [
            "# Agent Run Summary",
            "",
            f"- Run ID: `{self.run_id}`",
            f"- Issue: #{self.issue_number} — {self.issue_title}",
            f"- Status: `{self.final_status}`",
            f"- Decision: `{self.final_decision or 'n/a'}`",
            f"- Branch: `{self.branch}`",
            f"- PR: {self.pr_url or 'n/a'}",
            f"- Model: `{self.model}`",
            f"- Duration: {format_duration(self.duration_ms)}",
            f"- Started: {self.started_at}",
            f"- Finished: {self.finished_at or 'n/a'}",
            "",
            "## Timeline",
            "",
            "| Step | Cycle | Status | Duration | Details |",
            "|---|---:|---|---:|---|",
        ]
        for step in self.steps:
            detail_bits = []
            if "decision" in step.details:
                detail_bits.append(f"decision={step.details['decision']}")
            if "changed_files" in step.details:
                detail_bits.append(f"files={step.details['changed_files']}")
            if "diff_lines" in step.details:
                detail_bits.append(f"diff_lines={step.details['diff_lines']}")
            if "commit_sha" in step.details:
                detail_bits.append(f"commit={str(step.details['commit_sha'])[:12]}")
            if "output_path" in step.details:
                detail_bits.append(f"output={step.details['output_path']}")
            details = ", ".join(detail_bits)
            cycle = "" if step.cycle is None else str(step.cycle)
            lines.append(
                f"| {step.name} | {cycle} | {step.status} | {format_duration(step.duration_ms)} | {details} |"
            )
        if self.last_error:
            lines.extend(["", "## Last error", "", f"```text\n{self.last_error}\n```"])
        lines.extend(["", "## Artifacts", "", f"- Events: `{self.events_path}`", f"- Run JSON: `{self.run_json_path}`"])
        self.summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return self.summary_path

    def pr_metadata_markdown(self) -> str:
        return (
            "## Run metadata\n\n"
            f"- Run ID: `{self.run_id}`\n"
            f"- Model: `{self.model}`\n"
            f"- Cycles used: `{max((step.cycle or 0) for step in self.steps) if self.steps else 0}`\n"
            f"- Duration: `{format_duration(self.duration_ms)}`\n"
            f"- Decision: `{self.final_decision or 'n/a'}`\n"
            f"- Summary: `{self.summary_path}`\n"
            f"- Events: `{self.events_path}`\n"
        )
