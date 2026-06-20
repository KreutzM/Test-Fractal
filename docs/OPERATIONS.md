# Betrieb

## Einmalige Einrichtung

1. Python 3.11 installieren.
2. Git installieren.
3. GitHub CLI installieren.
4. Codex CLI installieren.
5. Mit Codex anmelden: `codex login`.
6. Mit GitHub anmelden: `gh auth login`.
7. Repo clonen.
8. Umgebung prüfen: `python -m agent_orchestrator doctor`.
9. Labels anlegen: `python -m agent_orchestrator labels`.

## Einen Agentenlauf starten

1. GitHub-Issue erstellen.
2. Label `agent-run` setzen.
3. Lokal starten: `python -m agent_orchestrator run --issue <nummer>`.
4. Ergebnis-PR prüfen.
5. Manuell mergen oder Änderungen anfordern.

## Dry Run

`python -m agent_orchestrator run --issue <nummer> --dry-run`

Der Dry Run rendert Prompts und legt lokalen State an, ruft aber Codex nicht produktiv auf.

## Arbeit Ã¼ber den GitHub-Connector

FÃ¼r Evaluation oder Review Ã¼ber den GitHub-Connector zuerst diese Dokumente lesen:

- `docs/GITHUB_CONNECTOR_WORKFLOW.md`
- `docs/REPO_MAP.md`
- `docs/LABELS.md`
- `docs/REVIEW_PROTOCOL.md`

## Logs

Lokale Logs liegen unter `.agent/runs/issue-<nummer>/`.

Wichtige Dateien:

- `state.json`
- `planner.md`
- `builder-cycle-1.md`
- `tests-cycle-1.txt`
- `reviewer-cycle-1.md`

## Häufige Probleme

### `gh` ist nicht angemeldet

Lösung: `gh auth login` ausführen.

### Codex ist nicht angemeldet

Lösung: `codex login` ausführen und mit ChatGPT anmelden.

### Arbeitsverzeichnis ist nicht clean

Der Orchestrator startet standardmäßig nur aus einem sauberen Worktree. Vorher committen oder stashen.

### Tests schlagen fehl

Bei `max_cycles = 1` wird der Lauf blockiert. Erhöhe `max_cycles`, wenn Builder automatische Fixzyklen versuchen soll.

### Reviewer gibt request_changes

Bei `max_cycles = 1` wird blockiert. Bei höheren Zyklen erhält Builder das Reviewer-Feedback im nächsten Zyklus.

## Empfohlene Arbeitsweise

Für den Anfang:

- ein Issue
- ein Branch
- ein Planner-Durchgang
- ein Builder-Durchgang
- ein Reviewer-Durchgang
- ein Draft-PR
- menschlicher Merge

Erst wenn das stabil funktioniert, sollten Tester, Holmes, Architect oder parallele Branches ergänzt werden.
