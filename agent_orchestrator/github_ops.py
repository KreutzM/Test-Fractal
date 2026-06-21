from __future__ import annotations

import json
from pathlib import Path
from .shell import CommandResult, run_command


ORCHESTRATOR_REPO_ROOT = Path.cwd().resolve()


def _github_cwd(cwd: Path | str) -> Path | str:
    if str(cwd) == ".":
        return ORCHESTRATOR_REPO_ROOT
    return cwd


def gh(args: list[str], *, cwd: Path | str = ".", check: bool = True) -> CommandResult:
    return run_command(["gh", *args], cwd=_github_cwd(cwd), check=check)


def gh_available(cwd: Path | str = ".") -> bool:
    result = gh(["auth", "status"], cwd=cwd, check=False)
    return result.ok


def issue_view(issue: int, cwd: Path | str = ".") -> dict:
    result = gh(
        ["issue", "view", str(issue), "--json", "number,title,body,state,url,labels"],
        cwd=cwd,
    )
    return json.loads(result.stdout)


def ensure_label(name: str, color: str, description: str, cwd: Path | str = ".") -> None:
    gh(
        ["label", "create", name, "--color", color, "--description", description, "--force"],
        cwd=cwd,
    )


def add_label_to_issue(issue: int, label: str, cwd: Path | str = ".") -> None:
    gh(["issue", "edit", str(issue), "--add-label", label], cwd=cwd, check=False)


def remove_label_from_issue(issue: int, label: str, cwd: Path | str = ".") -> None:
    gh(["issue", "edit", str(issue), "--remove-label", label], cwd=cwd, check=False)


def comment_issue(issue: int, body: str, cwd: Path | str = ".") -> None:
    gh(["issue", "comment", str(issue), "--body", body], cwd=cwd)


def current_repo(cwd: Path | str = ".") -> str | None:
    result = gh(["repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"], cwd=cwd, check=False)
    if result.ok:
        return result.stdout.strip()
    return None


def pr_view_by_head(branch: str, cwd: Path | str = ".") -> dict | None:
    result = gh(
        ["pr", "view", branch, "--json", "number,url,title,state,headRefName,baseRefName"],
        cwd=cwd,
        check=False,
    )
    if not result.ok or not result.stdout.strip():
        return None
    return json.loads(result.stdout)


def create_pr(
    *,
    title: str,
    body: str,
    base: str,
    head: str,
    draft: bool = True,
    cwd: Path | str = ".",
) -> str:
    args = ["pr", "create", "--title", title, "--body", body, "--base", base, "--head", head]
    if draft:
        args.append("--draft")
    result = gh(args, cwd=cwd)
    return result.stdout.strip()
