# Repository Map

Read these files first when orienting yourself:

- `README.md`: quickstart and target architecture.
- `AGENTS.md`: binding agent rules.
- `config/orchestrator.json`: model, labels, limits, test commands, and PR behavior.
- `.codex/config.toml`: project-level Codex configuration.
- `.codex/agents/`: prepared Codex agent roles.
- `prompts/roles/`: role prompts for Planner, Builder, and Reviewer.
- `agent_orchestrator/cli.py`: CLI entry point.
- `agent_orchestrator/orchestrator.py`: main workflow.
- `agent_orchestrator/codex_runner.py`: Codex invocation wrapper.
- `agent_orchestrator/git_ops.py`: Git helpers.
- `agent_orchestrator/github_ops.py`: GitHub CLI helpers.
- `agent_orchestrator/state.py`: local run state.
- `docs/examples/fractal-mvp-issue.md`: first recommended test issue.
