# Repository Layout

## Wurzeldateien

- `README.md`: Einstieg und Schnellstart.
- `AGENTS.md`: verbindliche Arbeitsregeln für Codex.
- `pyproject.toml`: Python-Projektmetadaten.
- `requirements.txt`: bewusst leer bis auf Kommentare, weil die Runtime nur Standardbibliothek nutzt.
- `.gitignore`: ignoriert lokale Agentenläufe, virtuelle Umgebungen und Secrets.
- `.editorconfig`: einheitliche Formatregeln.

## `.codex/`

- `.codex/config.toml`: projektbezogene Codex-Defaults.
- `.codex/agents/*.toml`: vorbereitete Rollenagenten für Codex.

## `agent_orchestrator/`

Python-Paket mit der lokalen Orchestrierung.

- `cli.py`: Kommandozeile.
- `orchestrator.py`: Hauptablauf.
- `codex_runner.py`: Aufruf von `codex exec`.
- `git_ops.py`: Git-Wrapper.
- `github_ops.py`: GitHub-CLI-Wrapper.
- `state.py`: lokale Laufzustände.
- `doctor.py`: Umgebungsprüfung.
- `labels.py`: GitHub-Labels.

## `prompts/roles/`

Prompt-Vorlagen für Rollenaufrufe.

## `config/`

Orchestrator-Konfiguration.

## `docs/`

Betrieb, Architektur, Sicherheit, Rollenmodell und Roadmap.

## `scripts/`

Dünne Shell-/PowerShell-Hüllen.

## `.github/`

Issue- und PR-Templates. Keine GitHub Actions.

## `.agent/`

Wird zur Laufzeit lokal erzeugt und nicht eingecheckt.
