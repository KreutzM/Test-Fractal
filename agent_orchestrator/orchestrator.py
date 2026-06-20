from __future__ import annotations

from pathlib import Path
import shlex
from .codex_runner import run_codex_role
from .codex_status import capture_status_snapshot, write_status_delta
from .config import load_config
from .git_ops import (
    branch_diff_stat,
    branch_diff_text,
    changed_files,
    commit_all,
    create_or_checkout_branch,
    current_branch,
    diff_line_count,
    ensure_clean_worktree,
    forbidden_changes,
    has_changes,
    push_branch,
    stage_intent_to_add,
)
from .github_ops import (
    add_label_to_issue,
    comment_issue,
    create_pr,
    issue_view,
    pr_view_by_head,
    remove_label_from_issue,
)
from .shell import run_command
from .state import RunState


def _run_shell_command(command: str, cwd: Path | str = ".") -> tuple[int, str]:
    # Windows users run this through Python; shell=True intentionally supports configured test commands.
    result = run_command(_shell_args(command), cwd=cwd, check=False)
    combined = ""
    if result.stdout:
        combined += result.stdout
    if result.stderr:
        combined += "\n[stderr]\n" + result.stderr
    return result.returncode, combined


def _shell_args(command: str) -> list[str]:
    # Use PowerShell on Windows, POSIX shell elsewhere.
    import os

    if os.name == "nt":
        return ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command]
    return ["/bin/sh", "-lc", command]


def _test_report(config: dict, cwd: Path | str = ".") -> tuple[bool, str]:
    commands = config.get("test_commands", [])
    if not commands:
        return True, "No test commands configured."
    blocks: list[str] = []
    all_ok = True
    for command in commands:
        code, output = _run_shell_command(command, cwd=cwd)
        blocks.append(f"$ {command}\nexit={code}\n{output.strip()}")
        if code != 0:
            all_ok = False
    return all_ok, "\n\n".join(blocks)


def _capture_codex_status(state: RunState, config: dict, label: str) -> None:
    capture_status_snapshot(
        output_path=state.run_dir / f"codex-status-{label}.json",
        label=label,
        config=config,
    )


def _write_codex_status_delta(state: RunState) -> None:
    write_status_delta(
        before_path=state.run_dir / "codex-status-before.json",
        after_path=state.run_dir / "codex-status-after.json",
        output_path=state.run_dir / "codex-status-delta.json",
    )


def _review_decision(text: str) -> str:
    lowered = text.lower()
    for decision in ["approve", "request_changes", "block"]:
        marker = f"review_decision: {decision}"
        if marker in lowered:
            return decision
    if "request changes" in lowered:
        return "request_changes"
    if "block" in lowered or "blocked" in lowered:
        return "block"
    return "request_changes"


def _issue_body(issue: dict) -> str:
    labels = ", ".join(label.get("name", "") for label in issue.get("labels", []))
    return (
        f"Issue #{issue['number']}: {issue['title']}\n"
        f"URL: {issue.get('url', '')}\n"
        f"State: {issue.get('state', '')}\n"
        f"Labels: {labels}\n\n"
        f"Body:\n{issue.get('body') or ''}\n"
    )


def _common_variables(
    issue: dict,
    state: RunState,
    *,
    base_branch: str = "main",
    planner: str = "",
    builder: str = "",
    tests: str = "",
) -> dict[str, str]:
    return {
        "issue_number": str(issue["number"]),
        "issue_title": issue["title"],
        "issue_markdown": _issue_body(issue),
        "branch": state.branch,
        "cycle": str(state.cycle),
        "planner_output": planner,
        "builder_output": builder,
        "test_report": tests,
        "diff_stat": branch_diff_stat(base_branch),
        "diff_text": branch_diff_text(base_branch, max_chars=100_000),
        "current_branch": current_branch(),
    }


def _builder_commit_message(config: dict, issue_number: int, issue_title: str, cycle: int) -> str:
    base = config["commit_message_template"].format(issue=issue_number, title=issue_title)
    return f"{base} (builder cycle {cycle})"


def run_issue(issue_number: int, *, config_path: str = "config/orchestrator.json", dry_run: bool = False) -> int:
    config = load_config(config_path)
    issue = issue_view(issue_number)
    branch = f"{config['work_branch_prefix']}{issue_number}"
    state = RunState(issue=issue_number, branch=branch)
    state.save()
    _capture_codex_status(state, config, "before")
    state.save()

    labels = config["labels"]
    if not dry_run:
        add_label_to_issue(issue_number, labels["running"])
        remove_label_from_issue(issue_number, labels["queue"])

    try:
        if not dry_run:
            ensure_clean_worktree()
            create_or_checkout_branch(branch, config["base_branch"])

        state.status = "planning"
        state.save()
        planner_path = state.run_dir / "planner.md"
        planner_result = run_codex_role(
            role="planner",
            variables=_common_variables(issue, state, base_branch=config["base_branch"]),
            model=config["model"],
            sandbox=config["codex"]["planner_sandbox"],
            approval=config["codex"]["approval"],
            output_path=planner_path,
            extra_args=config["codex"].get("extra_args", []),
            dry_run=dry_run,
        )
        planner_text = planner_path.read_text(encoding="utf-8") if planner_path.exists() else planner_result.stdout
        state.planner_output = str(planner_path)
        state.save()
        if not planner_result.ok:
            raise RuntimeError(f"Planner failed: {planner_result.stderr}")

        review_feedback = ""
        builder_text = ""
        test_text = ""
        reviewer_text = ""
        for cycle in range(1, config["max_cycles"] + 1):
            state.cycle = cycle
            state.status = "building"
            state.save()

            builder_path = state.run_dir / f"builder-cycle-{cycle}.md"
            builder_result = run_codex_role(
                role="builder",
                variables={
                    **_common_variables(issue, state, base_branch=config["base_branch"], planner=planner_text, tests=test_text),
                    "review_feedback": review_feedback,
                },
                model=config["model"],
                sandbox=config["codex"]["builder_sandbox"],
                approval=config["codex"]["approval"],
                output_path=builder_path,
                extra_args=config["codex"].get("extra_args", []),
                dry_run=dry_run,
            )
            builder_text = builder_path.read_text(encoding="utf-8") if builder_path.exists() else builder_result.stdout
            state.builder_output = str(builder_path)
            state.save()
            if not builder_result.ok:
                raise RuntimeError(f"Builder failed: {builder_result.stderr}")

            if not dry_run:
                stage_intent_to_add()
            files = changed_files() if not dry_run else []
            forbidden = forbidden_changes(files, config.get("forbidden_paths", []))
            if forbidden:
                raise RuntimeError(f"Forbidden paths changed: {', '.join(forbidden)}")
            max_changed = config.get("limits", {}).get("max_changed_files", 999999)
            if len(files) > max_changed:
                raise RuntimeError(f"Too many files changed: {len(files)} > {max_changed}")
            max_lines = config.get("limits", {}).get("max_diff_lines", 999999)
            lines = diff_line_count() if not dry_run else 0
            if lines > max_lines:
                raise RuntimeError(f"Diff too large: {lines} changed lines > {max_lines}")

            state.status = "testing"
            state.save()
            tests_ok, test_text = _test_report(config)
            test_path = state.run_dir / f"tests-cycle-{cycle}.txt"
            test_path.write_text(test_text + "\n", encoding="utf-8")
            state.test_output = str(test_path)
            state.save()
            if not tests_ok:
                review_feedback = "Tests failed. Fix the failing tests or implementation.\n\n" + test_text
                if cycle < config["max_cycles"]:
                    continue
                raise RuntimeError("Tests failed after maximum cycles. See local .agent/runs logs.")

            if not dry_run and has_changes():
                message = _builder_commit_message(config, issue_number, issue["title"], cycle)
                committed = commit_all(message)
                if committed:
                    push_branch(branch)

            state.status = "reviewing"
            state.save()
            reviewer_path = state.run_dir / f"reviewer-cycle-{cycle}.md"
            reviewer_result = run_codex_role(
                role="reviewer",
                variables=_common_variables(
                    issue,
                    state,
                    base_branch=config["base_branch"],
                    planner=planner_text,
                    builder=builder_text,
                    tests=test_text,
                ),
                model=config["model"],
                sandbox=config["codex"]["reviewer_sandbox"],
                approval=config["codex"]["approval"],
                output_path=reviewer_path,
                extra_args=config["codex"].get("extra_args", []),
                dry_run=dry_run,
            )
            reviewer_text = reviewer_path.read_text(encoding="utf-8") if reviewer_path.exists() else reviewer_result.stdout
            state.reviewer_output = str(reviewer_path)
            state.save()
            if not reviewer_result.ok:
                raise RuntimeError(f"Reviewer failed: {reviewer_result.stderr}")

            decision = _review_decision(reviewer_text)
            state.final_decision = decision
            state.save()
            if decision == "approve":
                break
            if decision == "block":
                raise RuntimeError("Reviewer blocked the change. See reviewer output.")
            review_feedback = "Reviewer requested changes. Address this feedback:\n\n" + reviewer_text
        else:
            raise RuntimeError("Maximum cycles reached without reviewer approval.")

        state.status = "publishing"
        state.save()
        if not dry_run:
            push_branch(branch)

        pr = None if dry_run else pr_view_by_head(branch)
        if pr:
            pr_url = pr["url"]
        elif dry_run:
            pr_url = f"DRY RUN: would create PR from {branch} to {config['base_branch']}"
        else:
            pr_title = config["pr"]["title_template"].format(issue=issue_number, title=issue["title"])
            pr_body = _pr_body(issue, state, planner_text, builder_text, test_text, reviewer_text, config)
            pr_url = create_pr(
                title=pr_title,
                body=pr_body,
                base=config["base_branch"],
                head=branch,
                draft=bool(config["pr"].get("draft", True)),
            )

        _capture_codex_status(state, config, "after")
        _write_codex_status_delta(state)
        state.pr_url = pr_url
        state.status = "ready_for_human"
        state.save()

        if not dry_run:
            add_label_to_issue(issue_number, labels["ready"])
            remove_label_from_issue(issue_number, labels["running"])
            comment_issue(
                issue_number,
                f"Agent run finished. Status: ready_for_human. Branch: `{branch}`. PR: {pr_url}",
            )
        print(f"Agent run finished. PR: {pr_url}")
        return 0
    except Exception as exc:
        try:
            _capture_codex_status(state, config, "after")
            _write_codex_status_delta(state)
        except Exception:
            pass
        state.status = "blocked"
        state.last_error = str(exc)
        state.save()
        if not dry_run:
            add_label_to_issue(issue_number, labels["blocked"])
            remove_label_from_issue(issue_number, labels["running"])
            try:
                comment_issue(issue_number, f"Agent run blocked. Reason: {exc}")
            except Exception:
                pass
        print(f"Agent run blocked: {exc}")
        return 1


def _pr_body(issue: dict, state: RunState, planner: str, builder: str, tests: str, reviewer: str, config: dict) -> str:
    footer = config.get("pr", {}).get("body_footer", "")
    return (
        f"## Agent PR\n\n"
        f"Issue: #{issue['number']}\n\n"
        f"## Planner summary\n\n{planner[:6000]}\n\n"
        f"## Builder summary\n\n{builder[:6000]}\n\n"
        f"## Test report\n\n{tests[:6000]}\n\n"
        f"## Reviewer summary\n\n{reviewer[:6000]}\n\n"
        f"## Human gate\n\n"
        f"This PR must be reviewed by a human before merge.\n\n"
        f"{footer}\n"
    )
