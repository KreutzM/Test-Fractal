# Status Labels

These labels track the lifecycle of a local agent run:

- `agent-run`: issue is queued for a local agent run.
- `agent-running`: local run is in progress.
- `agent-blocked`: the run stopped and needs a human decision.
- `agent-ready-for-human`: branch or draft PR is ready for human review.
- `agent-failed`: an unexpected error occurred.
- `agent-done`: the task is complete.

Standard flow:

`agent-run` -> `agent-running` -> `agent-ready-for-human` -> `agent-done`

Error flow:

`agent-running` -> `agent-blocked`

or

`agent-running` -> `agent-failed`
