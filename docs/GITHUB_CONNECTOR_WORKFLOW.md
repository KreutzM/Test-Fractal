# GitHub Connector Workflow

The GitHub connector is used to evaluate, coordinate, document, analyze issues, and review pull requests in this experiment.

It may inspect:

- issues
- pull requests
- repository files
- diffs
- comments and review threads

It must not:

- claim that local tests were run when they were not
- start Codex CLI locally
- develop the actual target software
- merge into `main`
- replace the local orchestrator

The local orchestrator remains responsible for local execution, state, prompts, Git operations, and test execution.

The human makes the final decision on scope and merge.
