# GitHub-Workflow

## GitHub bleibt Control Plane

Dieses System nutzt GitHub für sichtbare, auditierbare Zustände.

GitHub speichert:

- Issue-Auftrag
- Labels
- Branch
- Pull Request
- Kommentare
- finale menschliche Entscheidung

## Kein GitHub Actions

Dieses Repo verwendet bewusst keine GitHub Actions.

Alle Rechenarbeit läuft lokal:

- Codex CLI
- Tests
- Orchestrator
- Git-Kommandos

## Issue-Konvention

Ein gutes Agenten-Issue enthält:

- Ziel
- Kontext
- Scope
- Non-goals
- Akzeptanzkriterien
- Testhinweise
- Einschränkungen

## Label-Konvention

- `agent-run`: Queue.
- `agent-running`: Lokal in Bearbeitung.
- `agent-blocked`: Menschlicher Eingriff nötig.
- `agent-ready-for-human`: Ergebnis liegt vor.
- `agent-done`: Mensch hat akzeptiert.

## PR-Konvention

Ein Agent-PR sollte enthalten:

- Link zum Issue
- Planner-Zusammenfassung
- Builder-Zusammenfassung
- Testreport
- Reviewer-Zusammenfassung
- expliziten Hinweis auf menschlichen Merge-Gate

## Branch-Konvention

MVP:

`agent/issue-<nummer>`

Später:

`agent/epic-<nummer>`

## Merge-Regel

Nur Menschen mergen nach `main`.

Agents und Orchestrator dürfen vorbereiten, aber nicht final integrieren.
