#!/usr/bin/env sh
set -eu
ISSUE="${1:-}"
if [ -z "$ISSUE" ]; then
  echo "Usage: scripts/run-agent.sh ISSUE_NUMBER" >&2
  exit 2
fi
python -m agent_orchestrator run --issue "$ISSUE"
