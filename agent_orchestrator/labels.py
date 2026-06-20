from __future__ import annotations

from pathlib import Path
from .config import load_config
from .github_ops import ensure_label


LABEL_DEFINITIONS = {
    "agent-run": ("0E8A16", "Queue this issue for a local agent run."),
    "agent-running": ("1D76DB", "A local agent run is currently active."),
    "agent-blocked": ("D93F0B", "The local agent run hit a blocker."),
    "agent-ready-for-human": ("8250DF", "Agent output is ready for human review."),
    "agent-failed": ("B60205", "The local agent run failed unexpectedly."),
    "agent-done": ("5319E7", "Agent work was completed and accepted."),
}


def ensure_agent_labels(config_path: str = "config/orchestrator.json", cwd: Path | str = ".") -> None:
    config = load_config(config_path)
    labels = set(config["labels"].values())
    for label in labels:
        color, description = LABEL_DEFINITIONS.get(label, ("6E7781", "Local agent workflow label."))
        ensure_label(label, color, description, cwd=cwd)
