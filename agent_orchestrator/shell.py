from __future__ import annotations

from dataclasses import dataclass
import os
import subprocess
from pathlib import Path
from shutil import which
from typing import Mapping, Sequence


TARGET_REPO_ENV = "AGENT_ORCHESTRATOR_TARGET_REPO"


@dataclass(frozen=True)
class CommandResult:
    args: list[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    def summary(self) -> str:
        return f"exit={self.returncode}; stdout={len(self.stdout)} chars; stderr={len(self.stderr)} chars"


class CommandError(RuntimeError):
    def __init__(self, result: CommandResult):
        self.result = result
        joined = " ".join(result.args)
        super().__init__(f"Command failed with exit {result.returncode}: {joined}\n{result.stderr}")


def resolve_executable(args: Sequence[str]) -> list[str]:
    """Resolve command shims before subprocess execution.

    On Windows, npm-installed CLIs often appear as PowerShell scripts when queried
    from PowerShell, while subprocess without shell=True needs an executable file.
    Prefer .cmd and .exe shims so tools like codex can be launched reliably.
    """
    resolved = list(args)
    if not resolved:
        return resolved

    command = resolved[0]

    if os.path.dirname(command) or os.path.splitext(command)[1]:
        return resolved

    if os.name == "nt":
        for suffix in (".cmd", ".exe"):
            candidate = which(command + suffix)
            if candidate:
                resolved[0] = candidate
                return resolved

    found = which(command)
    if found:
        resolved[0] = found

    return resolved


def effective_cwd(cwd: Path | str | None = None) -> Path | str | None:
    target_repo = os.environ.get(TARGET_REPO_ENV)
    if target_repo and (cwd is None or str(cwd) == "."):
        return Path(target_repo)
    return cwd


def run_command(
    args: Sequence[str],
    *,
    cwd: Path | str | None = None,
    input_text: str | None = None,
    env: Mapping[str, str] | None = None,
    check: bool = False,
) -> CommandResult:
    resolved_args = resolve_executable(args)
    command_cwd = effective_cwd(cwd)
    try:
        completed = subprocess.run(
            resolved_args,
            cwd=str(command_cwd) if command_cwd else None,
            input=input_text,
            text=True,
            encoding="utf-8",
            capture_output=True,
            env=dict(env) if env else None,
        )
    except FileNotFoundError as exc:
        result = CommandResult(
            args=list(resolved_args),
            returncode=127,
            stdout="",
            stderr=f"Executable not found: {resolved_args[0]}\n{exc}",
        )
        if check:
            raise CommandError(result) from exc
        return result

    result = CommandResult(
        args=list(resolved_args),
        returncode=completed.returncode,
        stdout=completed.stdout or "",
        stderr=completed.stderr or "",
    )
    if check and not result.ok:
        raise CommandError(result)
    return result
