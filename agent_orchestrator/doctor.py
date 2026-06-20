from __future__ import annotations

from pathlib import Path
from shutil import which
from .git_ops import ensure_git_repo, current_branch, default_branch
from .github_ops import gh_available, current_repo
from .shell import run_command


def check_environment(cwd: Path | str = ".") -> tuple[bool, list[str]]:
    messages: list[str] = []
    ok = True

    for executable in ["python", "git", "gh", "codex"]:
        if which(executable):
            messages.append(f"OK: {executable} found")
        else:
            ok = False
            messages.append(f"MISSING: {executable} not found on PATH")

    if ensure_git_repo(cwd):
        messages.append(f"OK: git repository detected, current branch: {current_branch(cwd) or '(detached)'}")
        detected_default = default_branch(cwd)
        if detected_default:
            messages.append(f"OK: origin default branch appears to be: {detected_default}")
        else:
            messages.append("WARN: could not detect origin default branch")
    else:
        ok = False
        messages.append("MISSING: current directory is not inside a git repository")

    if which("gh"):
        if gh_available(cwd):
            repo = current_repo(cwd) or "unknown"
            messages.append(f"OK: gh is authenticated, repo: {repo}")
        else:
            ok = False
            messages.append("MISSING: gh is not authenticated. Run: gh auth login")

    if which("codex"):
        version = run_command(["codex", "--version"], cwd=cwd, check=False)
        if version.ok:
            messages.append(f"OK: codex version: {version.stdout.strip() or version.stderr.strip()}")
        else:
            messages.append("WARN: codex is present but --version failed")

    return ok, messages
