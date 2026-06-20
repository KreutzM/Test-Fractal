from __future__ import annotations

from dataclasses import dataclass
import subprocess
from pathlib import Path
from typing import Mapping, Sequence


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


def run_command(
    args: Sequence[str],
    *,
    cwd: Path | str | None = None,
    input_text: str | None = None,
    env: Mapping[str, str] | None = None,
    check: bool = False,
) -> CommandResult:
    completed = subprocess.run(
        list(args),
        cwd=str(cwd) if cwd else None,
        input=input_text,
        text=True,
        capture_output=True,
        env=dict(env) if env else None,
    )
    result = CommandResult(
        args=list(args),
        returncode=completed.returncode,
        stdout=completed.stdout or "",
        stderr=completed.stderr or "",
    )
    if check and not result.ok:
        raise CommandError(result)
    return result
