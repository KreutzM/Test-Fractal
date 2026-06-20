# Vollständiger Plan für das Git-Repo

## Ziel

Dieses Repository ist die lokale Steuerzentrale für ein Multi-Agent-System mit Codex CLI.

Es soll nach dem Clone sofort prüfbar und startbar sein:

- `python -m agent_orchestrator doctor` prüft die lokale Umgebung.
- `python -m agent_orchestrator labels` legt GitHub-Labels an.
- `python -m agent_orchestrator run --issue <nummer>` startet Planner, Builder und Reviewer.

## Grundprinzip

GitHub bleibt Control Plane. Dein lokaler Rechner bleibt Compute Plane.

GitHub wird genutzt für:

- Issues
- Labels
- Branches
- Pull Requests
- Kommentare
- menschliches Review

GitHub wird nicht genutzt für:

- Actions
- Runner-Minuten
- Artifacts
- Cache
- automatische Merges nach `main`

## Empfohlene Repo-Struktur

`agent_orchestrator/` enthält die Python-Orchestrierung.

`.codex/` enthält Codex-Projektkonfiguration und vorbereitete Projektagenten.

`prompts/roles/` enthält die Rollenprompts, die der Orchestrator an `codex exec` übergibt.

`config/orchestrator.json` enthält Modelle, Branchschema, Labels, Limits, Testbefehle und PR-Regeln.

`docs/` enthält Architektur, Betriebsanleitung, Rollenmodell, GitHub-Workflow und Beispiele.

`scripts/` enthält dünne Startskripte für PowerShell und POSIX-Shell.

`tests/` enthält lokale Tests für die Orchestrator-Basislogik.

`.agent/` wird lokal zur Laufzeit angelegt und ist ignoriert.

## Aktiver MVP-Workflow

1. Ein GitHub-Issue erhält das Label `agent-run`.
2. Du startest lokal: `python -m agent_orchestrator run --issue <nummer>`.
3. Der Orchestrator liest das Issue mit `gh issue view`.
4. Der Orchestrator erstellt den Branch `agent/issue-<nummer>`.
5. Planner läuft read-only.
6. Builder läuft mit Workspace-Schreibrechten.
7. Der Orchestrator führt lokale Testbefehle aus.
8. Reviewer läuft read-only.
9. Bei Approve werden Änderungen committed und gepusht.
10. Der Orchestrator erstellt einen Draft-PR nach `main`.
11. Das Issue wird auf `agent-ready-for-human` gesetzt.
12. Du reviewst und mergst manuell.

## Rollen

### Planner

Planner ist die Scope-Kontrolle.

Er schreibt keinen Produktivcode, sondern erzeugt:

- Ziel
- Minimal-Scope
- Non-goals
- Akzeptanzkriterien
- Teststrategie
- Builder-Handoff

### Builder

Builder ist die Umsetzung.

Er schreibt Code und Tests, aber:

- kein Commit
- kein Push
- kein Merge
- keine Branchwechsel

### Reviewer

Reviewer ist die unabhängige Prüfung.

Er liest Diff, Tests und Plan, ändert aber keine Dateien.

Er endet mit genau einer Entscheidung:

- `REVIEW_DECISION: approve`
- `REVIEW_DECISION: request_changes`
- `REVIEW_DECISION: block`

### Tester später

Tester wird erst ergänzt, wenn er echte Testartefakte erzeugt:

- neue Tests
- Repro-Fälle
- Testberichte
- Coverage-/Regressionsevidenz

### Holmes später

Holmes wird bei roten Tests, Regressionen oder wiederholtem Builder-Scheitern aktiviert.

### Architect später

Architect wird bei API-Änderungen, neuen Abhängigkeiten, größeren Refactorings oder Qualitätsrisiken aktiviert.

## Branching

MVP:

`main -> agent/issue-<nummer> -> PR nach main`

Später für größere Epics:

`main -> agent/epic-<nummer> -> finaler PR nach main`

und darunter:

`agent/epic-<nummer> -> agent/issue-<nummer>-builder`

## Labels

- `agent-run`: Issue ist bereit für lokalen Agentenlauf.
- `agent-running`: Lauf läuft lokal.
- `agent-blocked`: Lauf braucht menschliche Entscheidung.
- `agent-ready-for-human`: PR oder Ergebnis ist bereit für Review.
- `agent-failed`: Unerwarteter Fehler.
- `agent-done`: Agentenarbeit wurde akzeptiert.

## Sicherheitsgrenzen

- Kein Push nach `main`.
- Kein Auto-Merge.
- Kein `danger-full-access`.
- Keine Secrets ändern.
- Keine GitHub Actions.
- Maximale Datei- und Diffgrenzen.
- Nicht-interaktive Codex-Läufe sollen bei fehlender Berechtigung fehlschlagen, nicht Rechte eskalieren.

## Modellstrategie

Vorerst wird `gpt-5.4-mini` für alle aktiven Rollen verwendet.

Empfohlene Startwerte:

- Planner: medium reasoning
- Builder: medium reasoning
- Reviewer: high reasoning

Spätere Eskalation:

- Builder auf stärkeres Modell, wenn Tests wiederholt scheitern.
- Reviewer auf stärkeres Modell, wenn Sicherheits-, Architektur- oder API-Risiken auftreten.

## Nächste Ausbaustufen

### Stufe 1

MVP mit Planner, Builder, Reviewer und einem Zyklus.

### Stufe 2

Mehrere Builder-/Reviewer-Fixzyklen.

### Stufe 3

Tester-Rolle als eigenständiger Validierer.

### Stufe 4

Holmes bei Fehlern.

### Stufe 5

Architect bei Architektur-/Dependency-Risiken.

### Stufe 6

Epic-Branch und interne Sub-PRs.

### Stufe 7

Webhook-Server oder lokaler Polling-Daemon.
