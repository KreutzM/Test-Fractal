# AGENTS.md

## Grundregeln

- Arbeite niemals direkt auf `main`.
- Erzeuge oder nutze immer einen Branch nach dem Schema `agent/issue-<nummer>` oder `agent/epic-<nummer>`.
- Der finale Merge nach `main` ist menschliche Verantwortung.
- Verwende kleine, reviewbare Änderungen.
- Ändere keine Secrets, Tokens, Credentials oder lokalen Authentifizierungsdateien.
- Füge keine neue Produktionsabhängigkeit hinzu, ohne dies im Ergebnis ausdrücklich als Risiko zu markieren.
- Halte dich an den im Issue beschriebenen Scope.
- Wenn der Scope unklar ist, implementiere die kleinste sinnvolle testbare Variante und dokumentiere Annahmen.
- Kein privates Chain-of-Thought, keine versteckten Gedankengänge und keine langen internen Spekulationen in Dateien schreiben.
- Ergebnisse als klare Zusammenfassung, Testnachweis, Risiken und nächste Schritte dokumentieren.

## Aktive Rollen

### Planner

- Schreibt keinen Produktivcode.
- Zerlegt das Issue in kleine, prüfbare Schritte.
- Definiert Akzeptanzkriterien, Non-goals und Risiken.
- Begrenzt den Scope für einen Ein-Durchgang-Lauf.

### Builder

- Implementiert nur den nächsten geplanten Schritt.
- Macht keine Commits und keinen Push.
- Hält Änderungen klein.
- Aktualisiert Tests, wenn Verhalten geändert wird.
- Dokumentiert Tests und offene Punkte im Abschlussbericht.

### Reviewer

- Prüft Diff, Tests, Scope und Risiken.
- Ändert keinen Code.
- Gibt eine klare Entscheidung aus: approve, request_changes oder block.
- Markiert fehlende Tests, Scope Creep, unnötige Abhängigkeiten und verbotene Pfadänderungen.

## Tests

- Wenn Python-Code geändert wird, führe passende lokale Tests aus oder erkläre, warum keine Tests laufen konnten.
- Standard für dieses Repo ist: `python -m unittest discover -s tests -p "test_*.py"`.
- Für Zielprojekte dürfen andere Testbefehle in `config/orchestrator.json` gesetzt werden.

## Definition of Done

Eine Änderung ist erst fertig, wenn:

- der Scope des Issues adressiert wurde,
- der Diff klein genug für Review ist,
- lokale Tests ausgeführt wurden oder ein Blocker dokumentiert ist,
- keine verbotenen Pfade geändert wurden,
- der Reviewer approve gibt oder menschliches Review ausdrücklich angefordert wird.
