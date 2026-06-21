from __future__ import annotations

import argparse
import os
from pathlib import Path

from .doctor import check_environment
from .labels import ensure_agent_labels
from .orchestrator import run_issue
from .shell import TARGET_REPO_ENV


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent-orchestrator")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("doctor", help="Check local prerequisites and authentication.")
    sub.add_parser("labels", help="Create or update GitHub labels used by the agent workflow.")

    run = sub.add_parser("run", help="Run Planner, Builder, and Reviewer for a GitHub issue.")
    run.add_argument("--issue", type=int, required=True, help="GitHub issue number to process.")
    run.add_argument("--config", default="config/orchestrator.json", help="Path to orchestrator config JSON.")
    run.add_argument("--repo", default=".", help="Target repository working tree for Git, tests, and Codex.")
    run.add_argument("--dry-run", action="store_true", help="Render prompts and flow without calling Codex or changing Git.")
    return parser


def _run_with_target_repo(args: argparse.Namespace) -> int:
    old_target = os.environ.get(TARGET_REPO_ENV)
    repo = Path(args.repo).expanduser().resolve()
    if not repo.exists():
        print(f"Target repository path does not exist: {repo}")
        return 1
    if not repo.is_dir():
        print(f"Target repository path is not a directory: {repo}")
        return 1
    os.environ[TARGET_REPO_ENV] = str(repo)
    try:
        return run_issue(args.issue, config_path=args.config, dry_run=args.dry_run)
    finally:
        if old_target is None:
            os.environ.pop(TARGET_REPO_ENV, None)
        else:
            os.environ[TARGET_REPO_ENV] = old_target


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "doctor":
        ok, messages = check_environment()
        for message in messages:
            print(message)
        return 0 if ok else 1

    if args.command == "labels":
        ensure_agent_labels()
        print("Agent labels ensured.")
        return 0

    if args.command == "run":
        return _run_with_target_repo(args)

    parser.print_help()
    return 2
