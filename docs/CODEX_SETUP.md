# Codex-Setup

## Authentifizierung

Dieses Repository speichert keinen API-Key.

Für die vorgesehene Nutzung meldest du Codex CLI lokal mit deinem ChatGPT-/Codex-Konto an:

`codex login`

Codex CLI cached die Anmeldung lokal außerhalb dieses Repos.

## Projektkonfiguration

Die Datei `.codex/config.toml` setzt:

- Modell: `gpt-5.4-mini`
- Reasoning: `medium`
- Sandbox: `workspace-write`
- Approval: `on-request` für interaktive Nutzung

Der Orchestrator ruft `codex exec` nicht-interaktiv auf und überschreibt je Rolle:

- Planner: read-only
- Builder: workspace-write
- Reviewer: read-only
- Approval: never

Das bedeutet: Wenn Codex für einen nicht-interaktiven Lauf zusätzliche Rechte bräuchte, soll der Schritt fehlschlagen und der Orchestrator blockieren.

## Projektagenten

Projektagenten liegen unter `.codex/agents/`:

- planner.toml
- builder.toml
- reviewer.toml
- tester.toml
- holmes.toml
- architect.toml

Die ersten drei sind der aktive MVP.

## Rollenprompts

Der lokale Orchestrator nutzt Rollenprompts unter `prompts/roles/`.

Das ist bewusst einfach und stabil:

- Prompt-Datei lesen
- Variablen ersetzen
- `codex exec` starten
- Ausgabe lokal speichern

## Modell

Standardmodell ist `gpt-5.4-mini`.

Bei komplexeren Aufgaben kann später pro Rolle eskaliert werden.
