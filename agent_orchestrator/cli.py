from __future__ import annotations

import argparse
from . import __version__
from .doctor import check_environment
from .labels import ensure_agent_labels
from .orchestrator import run_issue


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent-orchestrator")
    parser.add_argument(
        "--version",
        action="version",
        version=__version__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("doctor", help="Check local prerequisites and authentication.")
    sub.add_parser("labels", help="Create or update GitHub labels used by the agent workflow.")

    run = sub.add_parser("run", help="Run Planner, Builder, and Reviewer for a GitHub issue.")
    run.add_argument("--issue", type=int, required=True, help="GitHub issue number to process.")
    run.add_argument("--config", default="config/orchestrator.json", help="Path to orchestrator config JSON.")
    run.add_argument("--dry-run", action="store_true", help="Render prompts and flow without calling Codex or changing Git.")
    return parser


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
        return run_issue(args.issue, config_path=args.config, dry_run=args.dry_run)

    parser.print_help()
    return 2
