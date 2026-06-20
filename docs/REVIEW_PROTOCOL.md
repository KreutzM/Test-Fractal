# Review Protocol

Reviews in this experiment follow two layers.

## Local review

The local Codex Reviewer runs inside the orchestrator and checks:

- diff
- scope
- tests
- risks

It should stay within the issue scope and the planner handoff.

## GitHub connector review

After a pull request exists, the GitHub connector may additionally inspect:

- PR description
- diff
- agent report
- documented test evidence

The connector may write review comments and may recommend or apply `request changes` for clear must-fix issues.

The connector should use `approve` only for small, low-risk changes.

If the local run did not execute tests itself, the review must say so explicitly and must only evaluate the documented test evidence.

## Merge rule

Merge into `main` remains a human decision.
