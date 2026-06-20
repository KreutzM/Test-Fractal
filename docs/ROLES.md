# Rollenmodell

## Planner

Planner beantwortet:

„Was genau soll in diesem Durchgang getan werden?“

Erzeugt:

- Minimal-Scope
- Non-goals
- Akzeptanzkriterien
- Teststrategie
- Builder-Handoff

Planner ändert keine Dateien.

## Builder

Builder beantwortet:

„Wie setze ich den geplanten Schritt möglichst klein und testbar um?“

Erzeugt:

- Codeänderungen
- Teständerungen
- kurze Implementierungszusammenfassung

Builder macht keinen Commit und keinen Push.

## Reviewer

Reviewer beantwortet:

„Ist dieser Diff gut genug, um einem Menschen als PR vorgelegt zu werden?“

Erzeugt:

- Review-Befund
- Must-fix-Punkte
- Testbewertung
- Entscheidung

Reviewer ändert keine Dateien.

## Tester später

Tester wird ergänzt, sobald Testdenken nicht mehr im Reviewer nebenbei erledigt werden soll.

Tester ist sinnvoll, wenn er echte Artefakte erzeugt:

- neue Tests
- Reproduktionsfälle
- Testbericht
- Validierungsstrategie

## Holmes später

Holmes ist der Debugger.

Er ist sinnvoll bei:

- roten Tests
- Regressionen
- unbekannter Ursache
- wiederholten Builder-Fehlern

## Architect später

Architect ist die Metaebene für Softwarequalität.

Er ist sinnvoll bei:

- öffentlicher API-Änderung
- neuer Dependency
- größeren Refactorings
- Modulgrenzen
- Performance-/Security-Risiken
- ADR-Bedarf
