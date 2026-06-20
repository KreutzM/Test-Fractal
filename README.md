# Codex Local Multi-Agent Orchestrator

Lokales, GitHub-Actions-freies Multi-Agent-System für Codex CLI.

Dieses Repository stellt eine startbereite Orchestrator-Schicht bereit, die Codex CLI mehrfach mit klar getrennten Rollen startet:

- Planner: macht aus einem GitHub-Issue einen engen Umsetzungsplan.
- Builder: setzt den nächsten Schritt im lokalen Git-Workspace um.
- Reviewer: prüft Diff, Scope, Tests und Risiken.
- Tester, Holmes und Architect sind vorbereitet, aber im Standardfluss noch nicht aktiv.

Das System ist bewusst lokal gebaut:

- keine GitHub Actions
- keine GitHub-Artefakte
- keine GitHub-Runner-Minuten
- keine GitHub-Compute-Kosten
- GitHub dient nur als Issue-, Branch-, PR- und Review-Oberfläche
- Codex CLI läuft lokal mit deinem ChatGPT-/Codex-Login
- GitHub wird über `gh` gesteuert

## Zielarchitektur

Der Orchestrator selbst ist kein KI-Agent. Er ist eine deterministische Ablaufmaschine.

Der Ablauf ist:

1. GitHub-Issue lesen.
2. Arbeitsbranch `agent/issue-<nummer>` erstellen.
3. Codex als Planner starten.
4. Codex als Builder starten.
5. Lokale Testbefehle ausführen.
6. Codex als Reviewer starten.
7. Bei Bedarf Builder-Fixzyklen starten.
8. Änderungen committen und pushen.
9. Pull Request nach `main` erstellen.
10. Issue/PR mit Labels und Kommentaren aktualisieren.

Der Mensch entscheidet weiterhin über den finalen Merge nach `main`.

## Voraussetzungen

Installiert und angemeldet:

- Python 3.11 oder neuer
- Git
- GitHub CLI `gh`
- Codex CLI
- Codex-Login über ChatGPT, zum Beispiel Plus/Pro/Business/Enterprise

Du brauchst für dieses Setup keinen OpenAI-API-Key, solange Codex CLI bereits über deinen ChatGPT-Account angemeldet ist.

Prüfe deine Umgebung nach dem Clone mit:

`python -m agent_orchestrator doctor`

## Schnellstart nach dem Clone

1. Repository clonen.
2. In das Repository wechseln.
3. Codex einmal anmelden, falls noch nicht geschehen: `codex login`.
4. GitHub CLI anmelden, falls noch nicht geschehen: `gh auth login`.
5. Prüfen: `python -m agent_orchestrator doctor`.
6. Labels im GitHub-Repo anlegen: `python -m agent_orchestrator labels`.
7. Ein GitHub-Issue mit Label `agent-run` erstellen.
8. Agentenlauf starten: `python -m agent_orchestrator run --issue 123`.

Auf Windows kannst du alternativ die PowerShell-Hülle nutzen:

`./scripts/run-agent.ps1 -Issue 123`

## Erster empfohlener Test

Für den ersten End-to-End-Test eignet sich ein kleines, automatisch testbares Python-Projekt, zum Beispiel:

„Implementiere mit Python 3.11 einen minimalen Mandelbrot-Fraktal-Renderer ohne GUI. Verwende NumPy und Pillow. Erzeuge per Kommando ein PNG-Bild. Lege Tests für Array-Form, Wertebereich, deterministische Ausgabegröße und erfolgreiche Bilddateierzeugung an. Keine GUI, kein Numba, kein Multithreading im ersten Durchgang.“

Dazu gibt es eine vorbereitete Vorlage unter `docs/examples/fractal-mvp-issue.md`.

## Wichtige Sicherheitsregeln

- Agents dürfen nicht direkt nach `main` pushen.
- Agents dürfen nicht selbst mergen.
- Der Orchestrator erstellt nur Branches und PRs.
- Der finale Merge nach `main` bleibt menschliche Entscheidung.
- Der Orchestrator nutzt standardmäßig `workspace-write` und `ask-for-approval never` für nicht-interaktive Codex-Läufe. Wenn Codex zusätzliche Berechtigungen bräuchte, soll der Lauf fehlschlagen statt unbegrenzt Rechte zu eskalieren.
- `danger-full-access` und `--yolo` sind bewusst nicht Teil dieses Repos.

## Rollenmodell

Die aktiven Rollen in Version 0.1 sind:

- Planner
- Builder
- Reviewer

Vorbereitete Rollen für spätere Erweiterung:

- Tester
- Holmes
- Architect

Die Codex-Projektagenten liegen unter `.codex/agents/`. Der lokale Orchestrator ruft Codex aktuell über Rollenprompts unter `prompts/roles/` auf. Die TOML-Agentendateien sind zusätzlich für interaktive Codex-Nutzung und spätere Subagent-Flows vorbereitet.

## Konfiguration

Die Orchestrator-Konfiguration liegt in:

`config/orchestrator.json`

Wichtige Werte:

- `model`: Standard ist `gpt-5.4-mini`.
- `base_branch`: Standard ist `main`.
- `work_branch_prefix`: Standard ist `agent/issue-`.
- `max_cycles`: Standard ist `1`.
- `test_commands`: Standard ist Python-Unittest für dieses Repo.
- `limits.max_changed_files`: Schutzgrenze für Agenten-Diffs.
- `forbidden_paths`: Pfade, die Agents nicht ändern sollen.

Die Codex-Projektkonfiguration liegt in:

`.codex/config.toml`

Für Connector-basierte Evaluation und Review sind die Leitfäden in `docs/GITHUB_CONNECTOR_WORKFLOW.md`, `docs/REPO_MAP.md`, `docs/LABELS.md` und `docs/REVIEW_PROTOCOL.md` relevant.

## Typische Kommandos

Umgebung prüfen:

`python -m agent_orchestrator doctor`

Labels anlegen oder aktualisieren:

`python -m agent_orchestrator labels`

Agentenlauf starten:

`python -m agent_orchestrator run --issue 123`

Trockenlauf ohne Codex-Aufrufe:

`python -m agent_orchestrator run --issue 123 --dry-run`

Lokale Tests des Orchestrators:

`python -m unittest discover -s tests -p "test_*.py"`

## Was dieses Repo noch nicht tut

Version 0.1 ist bewusst klein. Sie ist startbereit, aber nicht überladen.

Noch nicht enthalten:

- Webhook-Server
- parallele Agentenläufe
- Merge in interne Epic-Branches
- persistente Datenbank
- Dashboard
- OpenRouter-Providerprofile
- automatische Tester-/Holmes-/Architect-Eskalation als Standardfluss

Diese Dinge sind dokumentiert und können schrittweise ergänzt werden.
