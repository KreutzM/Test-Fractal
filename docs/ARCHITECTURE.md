# Architektur

## Komponenten

### Lokaler Orchestrator

Der Orchestrator ist eine Python-3.11-Anwendung. Er trifft keine komplexen fachlichen Entscheidungen, sondern steuert den Ablauf deterministisch.

Er verwaltet:

- Git-Zustand
- GitHub-Issue-Zustand
- Codex-Rollenaufrufe
- lokale Logs
- Testläufe
- Schutzgrenzen
- PR-Erstellung

### Codex CLI

Codex CLI ist der ausführende Agentenmotor.

Der Orchestrator ruft Codex über `codex exec` auf und übergibt Rollenprompts.

### Git

Git ist der dauerhafte Arbeitszustand.

Der Orchestrator erzeugt Branches, prüft Diffs, committed und pushed nur nach erfolgreicher Review-Phase.

### GitHub CLI

`gh` ist die GitHub-Schnittstelle.

Der Orchestrator nutzt `gh` für:

- Issues lesen
- Labels setzen
- Issue-Kommentare schreiben
- PRs erstellen

### Codex-Projektagenten

`.codex/agents/*.toml` definiert projektbezogene Rollen für interaktive Codex-Subagent-Nutzung und spätere Erweiterungen.

Der MVP-Orchestrator verwendet derzeit Rollenprompts aus `prompts/roles/`, weil `codex exec` als stabile Skript-Schnittstelle behandelt wird.

## Datenfluss

1. Issue wird gelesen.
2. Planner erhält Issue und Repo-Kontext.
3. Builder erhält Issue plus Planner-Handoff.
4. Orchestrator prüft Git-Diff und Schutzgrenzen.
5. Tests laufen lokal.
6. Reviewer erhält Issue, Plan, Builder-Zusammenfassung, Testreport und Diff.
7. Orchestrator interpretiert die Review-Entscheidung.
8. Bei Erfolg wird committed, gepusht und ein PR erzeugt.

## Lokaler State

Laufzeitdaten liegen unter `.agent/runs/issue-<nummer>/`.

Diese Daten sind absichtlich nicht versioniert:

- Planner-Ausgabe
- Builder-Ausgabe
- Testreport
- Reviewer-Ausgabe
- state.json

Der PR-Body enthält die wichtigsten Zusammenfassungen.

## Warum Python statt PowerShell

PowerShell wäre für einen Prototyp ausreichend. Python ist hier gewählt, weil Zustandsdateien, JSON, Tests, Fehlerbehandlung, GitHub-Wrapper und spätere Erweiterungen sauberer wartbar sind.

PowerShell bleibt als dünne Startschicht unter `scripts/` vorhanden.
