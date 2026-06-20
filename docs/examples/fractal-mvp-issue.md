# Beispiel-Issue: Minimaler Python-3.11-Mandelbrot-Renderer

## Ziel

Implementiere einen minimalen, automatisch testbaren Mandelbrot-Fraktal-Renderer mit Python 3.11.

## Scope

- Keine GUI.
- Kein Numba.
- Kein Multithreading.
- Kein Julia-Fraktal im ersten Durchgang.
- Kein interaktives Zoom/Pan.

## Anforderungen

- Projektstruktur mit `core/`, `tests/` und einem kleinen CLI-Einstieg.
- Mandelbrot-Berechnung mit NumPy.
- Farbmapping mit Pillow-kompatibler Ausgabe.
- PNG-Export.
- Ein Kommando erzeugt ein Beispielbild.
- Automatisierte Tests prüfen:
  - Array-Form.
  - Wertebereich.
  - deterministische Bildgröße.
  - erfolgreiche PNG-Dateierzeugung.

## Akzeptanzkriterien

- Python 3.11-kompatibel.
- Tests laufen lokal grün.
- Ein PNG kann lokal erzeugt werden.
- Der PR enthält keine GUI und keine unnötige Komplexität.

## Hinweise

Der spätere MVP kann GUI, Zoom/Pan, Slider, Farbpaletten, Julia-Fraktale und Performance-Optimierung ergänzen.
