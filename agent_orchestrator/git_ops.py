from __future__ import annotations

from pathlib import Path
import shlex
from .shell import CommandResult, run_command


def git(args: list[str], *, cwd: Path | str = ".", check: bool = True) -> CommandResult:
    return run_command(["git", *args], cwd=cwd, check=check)


def current_branch(cwd: Path | str = ".") -> str:
    return git(["branch", "--show-current"], cwd=cwd).stdout.strip()


def revision(ref: str = "HEAD", cwd: Path | str = ".") -> str | None:
    result = git(["rev-parse", "--verify", ref], cwd=cwd, check=False)
    if result.ok and result.stdout.strip():
        return result.stdout.strip()
    return None


def ensure_git_repo(cwd: Path | str = ".") -> bool:
    result = git(["rev-parse", "--is-inside-work-tree"], cwd=cwd, check=False)
    return result.ok and result.stdout.strip() == "true"


def default_branch(cwd: Path | str = ".") -> str | None:
    result = git(["symbolic-ref", "refs/remotes/origin/HEAD"], cwd=cwd, check=False)
    if result.ok and result.stdout.strip():
        return result.stdout.strip().rsplit("/", 1)[-1]
    return None


def ensure_clean_worktree(cwd: Path | str = ".") -> None:
    status = git(["status", "--porcelain"], cwd=cwd).stdout.strip()
    if status:
        raise RuntimeError(
            "Working tree is not clean. Commit/stash your changes or use a fresh clone before running agents."
        )


def create_or_checkout_branch(branch: str, base_branch: str, cwd: Path | str = ".") -> None:
    existing = git(["branch", "--list", branch], cwd=cwd).stdout.strip()
    if existing:
        git(["checkout", branch], cwd=cwd)
    else:
        git(["fetch", "origin", base_branch], cwd=cwd, check=False)
        git(["checkout", "-B", branch, f"origin/{base_branch}"], cwd=cwd)


def changed_files(cwd: Path | str = ".") -> list[str]:
    result = git(["status", "--porcelain"], cwd=cwd)
    files: list[str] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        files.append(line[3:].strip())
    return files


def _diff_base(base_branch: str, cwd: Path | str = ".") -> str:
    origin_ref = f"origin/{base_branch}"
    result = git(["rev-parse", "--verify", origin_ref], cwd=cwd, check=False)
    if result.ok:
        return origin_ref
    return base_branch


def stage_intent_to_add(cwd: Path | str = ".") -> None:
    # Make new files visible to git diff before the final commit without staging contents yet.
    git(["add", "--intent-to-add", "--all"], cwd=cwd, check=False)


def diff_stat(cwd: Path | str = ".") -> str:
    return git(["diff", "--stat"], cwd=cwd, check=False).stdout


def diff_text(cwd: Path | str = ".", *, max_chars: int = 100_000) -> str:
    text = git(["diff", "--", "."], cwd=cwd, check=False).stdout
    if len(text) > max_chars:
        return text[:max_chars] + "\n\n[diff truncated by orchestrator]\n"
    return text


def diff_line_count(cwd: Path | str = ".") -> int:
    text = git(["diff", "--numstat"], cwd=cwd, check=False).stdout
    total = 0
    for line in text.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            for value in parts[:2]:
                if value.isdigit():
                    total += int(value)
    return total


def branch_diff_stat(base_branch: str, cwd: Path | str = ".") -> str:
    base = _diff_base(base_branch, cwd)
    return git(["diff", "--stat", f"{base}...HEAD"], cwd=cwd, check=False).stdout


def branch_diff_text(base_branch: str, cwd: Path | str = ".", *, max_chars: int = 100_000) -> str:
    base = _diff_base(base_branch, cwd)
    text = git(["diff", f"{base}...HEAD", "--", "."], cwd=cwd, check=False).stdout
    if len(text) > max_chars:
        return text[:max_chars] + "\n\n[diff truncated by orchestrator]\n"
    return text


def branch_diff_line_count(base_branch: str, cwd: Path | str = ".") -> int:
    base = _diff_base(base_branch, cwd)
    text = git(["diff", "--numstat", f"{base}...HEAD"], cwd=cwd, check=False).stdout
    total = 0
    for line in text.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            for value in parts[:2]:
                if value.isdigit():
                    total += int(value)
    return total


def has_changes(cwd: Path | str = ".") -> bool:
    return bool(changed_files(cwd))


def forbidden_changes(files: list[str], forbidden_paths: list[str]) -> list[str]:
    hits: list[str] = []
    for file in files:
        normalized = file.replace("\\", "/")
        for forbidden in forbidden_paths:
            f = forbidden.replace("\\", "/")
            if f.endswith("/"):
                if normalized.startswith(f):
                    hits.append(file)
            elif normalized == f or normalized.startswith(f + "/"):
                hits.append(file)
    return sorted(set(hits))


def commit_all(message: str, cwd: Path | str = ".") -> bool:
    if not has_changes(cwd):
        return False
    git(["add", "--all"], cwd=cwd)
    git(["commit", "-m", message], cwd=cwd)
    return True


def push_branch(branch: str, cwd: Path | str = ".") -> None:
    git(["push", "-u", "origin", branch], cwd=cwd)


def shell_join(args: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in args)
