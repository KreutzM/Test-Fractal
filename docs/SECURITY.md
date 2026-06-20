# Sicherheit

## Nicht-Ziele

Dieses System ist nicht dafür gedacht, untrusted Code aus dem Internet ohne Review auszuführen.

Es ist ein lokales, kontrolliertes Agentenwerkzeug für eigene Repositories.

## Grundregeln

- Kein `danger-full-access`.
- Kein `--yolo`.
- Kein Auto-Merge nach `main`.
- Keine Secrets in Git.
- Keine Änderung an Auth-Dateien.
- Keine GitHub Actions.
- Keine dauerhafte Speicherung von API-Keys.

## Nicht-interaktive Läufe

Der Orchestrator verwendet `ask-for-approval never`, damit ein unbeaufsichtigter Lauf nicht auf UI-Bestätigung wartet.

Kombiniert mit Sandbox-Grenzen bedeutet das:

- Erlaubte Aktionen laufen.
- Nicht erlaubte Aktionen schlagen fehl.
- Der Orchestrator blockiert und schreibt einen Issue-Kommentar.

## Verbotene Pfade

In `config/orchestrator.json` stehen verbotene Pfade wie:

- `.env`
- `.codex/auth.json`
- `secrets/`
- `credentials/`
- `.git/`

Wenn solche Pfade geändert werden, wird der Lauf blockiert.

## Schutzgrenzen

Der Orchestrator prüft:

- maximale Anzahl geänderter Dateien
- maximale Diff-Größe
- Teststatus
- Reviewer-Entscheidung

## Menschlicher Gate

Der finale PR ist standardmäßig ein Draft-PR.

Ein Mensch entscheidet:

- Review akzeptieren
- Änderungen anfordern
- schließen
- mergen
