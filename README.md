# Voynich: strukturelle Analyse und Mechanismus-Elimination

Statistische Untersuchung des Voynich-Manuskripts auf Basis der Zandbergen-Landini-Transkription (EVA, IVTFF-Format).
Ergebnisbericht: [REPORT.md](REPORT.md).

## Daten
- `data/ZL3b-n.txt`, `data/IT2a-n.txt`: Transkriptionen von voynich.nu (ZL = Zandbergen-Landini, IT = Takahashi).
- `data/ref/` (nicht versioniert): Referenztexte. Anlegen mit
  `curl` von Gutenberg (Faust #2229, Dante #1012, Tolstoi #2600), Caesar von thelatinlibrary.com (Bücher 1-7, HTML-Tags entfernt), hebräische Genesis über die Sefaria-API (Nikkud entfernt). Siehe die Kommandos in `scripts/`.
- `Voynich_Manuscript.pdf` (nicht versioniert): Beinecke-Scan, 209 Bildseiten ohne Textlayer. Zuordnung: PDF-Seite 3 = f1r, danach linear (f12 fehlt) bis Seite 116 = f58v; verifiziert an f26r (S. 51), f27r (S. 53), f58r (S. 115).
- `data/naibbe/naibbe_tables.csv`: Substitutionstafeln der Naibbe-Chiffre aus dem Repository von Michael A. Greshko (github.com/greshko/naibbe-cipher, modifizierte MIT-Lizenz mit Attributionspflicht). Quelle: Greshko, M. A. (2025), "The Naibbe cipher: a substitution cipher that encrypts Latin and Italian as Voynich Manuscript-like ciphertext", Cryptologia, doi:10.1080/01611194.2025.2566408. Die Chiffre selbst ist in `voynich/generators.py` nach der dokumentierten Prozedur neu implementiert.

## Code
- `voynich/ivtff.py`: Parser für IVTFF (Seiten-Metadaten, Locus-Typen, Bereinigung der Inline-Markup).
- `voynich/stats.py`: Entropien, Zipf, Wortstatistik.
- `voynich/subst.py`: homophoner Substitutionslöser mit 4-Gramm-Sprachmodell und Kontrollen.
- `voynich/battery.py`: gemeinsame Testbatterie (Edge-MI, Token-MI, Zeilenreset, Space-Vorhersagbarkeit, Lexikontest, Entropieprofil, Redundanz jenseits eines Ordnung-3-Automaten).
- `voynich/generators.py`: Kandidatenmechanismen in exakt der Zeilen/Wort-Form des Manuskripts (Markov-Automaten mit Sektions- oder Seitendrift, Rugg-Gitter, Timm/Schinner-Kopieren, Verbose-Chiffre, Autokey-Chiffre, Latein-Kontrollen).
- `scripts/`: je ein Experiment pro Datei, alle vom Repo-Wurzelverzeichnis aus starten (`python3 scripts/<name>.py`).

## Reproduktion
```bash
python3 scripts/scripts_mechanisms3.py    # Mechanismus-Batterie (ca. 10 min)
python3 scripts/scripts_markov_hier.py    # Automat mit Seitendrift
python3 scripts/scripts_drift.py          # Drift mit Folio-Abstand
python3 scripts/scripts_naibbe.py         # Naibbe-Chiffre durch die Batterie
python3 scripts/scripts_naibbe_stateful.py # zustandsabhängige Naibbe-Variante
python3 scripts/scripts_takahashi.py      # Kernbatterie auf beiden Transkriptionen
python3 scripts/scripts_oos.py            # Out-of-sample, pro Hand, pro Currier-Sprache
python3 scripts/scripts_hand_by_distance.py # Handeffekt bei festem Folio-Abstand
python3 scripts/scripts_zodiac_labels.py  # Wiederkehr der Labels über Seiten
python3 scripts/scripts_page_colors.py    # Bildmerkmale aus der PDF (benötigt Voynich_Manuscript.pdf, PyMuPDF, Pillow, numpy)
python3 scripts/scripts_text_vs_image.py  # Mantel-Test Text gegen Bild, Positivkontrolle
python3 scripts/scripts_text_vs_image2.py # stratifiziert nach Hand
python3 scripts/scripts_section_within_hand.py # Sektion innerhalb der Hand (mit Folio-Vorbehalt)
```

## Manuskript (Cryptologia-Einreichung)
- `paper/paper.pdf`, `paper/supplement.pdf`: Haupttext und Supplement (englisch); `paper/paper.html`, `paper/supplement.html`: gerenderte, editierbare Quellen; `paper/templates/`: Jinja2-Vorlagen und CSS.
- Jede Zahl im Manuskript stammt aus `paper/numbers.json`, das `paper/extract_numbers.py` aus den Logs in `results/logs/` und den JSON-Ergebnissen erzeugt. Abbildungen: `paper/make_figures.py` (rechnet direkt aus den Daten).
- Neu bauen:
```bash
zsh paper/run_chain1.sh; zsh paper/run_chain2.sh        # alle Analysen, Logs nach results/logs/
python3 scripts/scripts_jackknife.py                     # Konfidenzintervalle (Leave-one-quire-out)
python3 paper/make_figures.py && python3 paper/extract_numbers.py && python3 paper/build_paper.py
```

## Mechanismus-Identifikation (präregistriert, Branch `mechanism-identification`)
- Frage: Prozedur, geübte Improvisation oder klartextgesteuerte Prozedur; getrennt davon direkt auf der Seite komponiert oder aus einer Vorlage kopiert.
- `mechanism/PREREG.md`: eingefrorene Hypothesen, Tests T1–T7, Vorhersagen, Falsifikatoren, Urteilsregeln (Commit `28ae510`). `mechanism/DEVIATIONS.md`: alle Abweichungen mit Zeitpunkt. `mechanism/REPORT.md`: Ergebnis.
- Kontrolle für menschliche Improvisation: Gibberish-Korpus von Gaskell & Bowern (2022) in `data/gibberish/` (Lizenzhinweis in `SOURCE.md`).
- Batterie-Ergebnis: begrenzte, unentschiedene Konkurrenz. Naive Improvisation, stationäre Prozeduren, periodische Geräte (ab Effektstärke 0,2), glatte Drift, propagierende Innovationen, wortbewahrende Chiffren und die Naibbe-Chiffre in der veröffentlichten Form sind ausgeschlossen; Umbruch einer fortlaufenden Vorlage (K-reflow) ist ausgeschlossen.
```bash
python3 -m mechanism.run A        # Stufe A: nur Kontrollen -> results/mechanism/stageA.json
python3 -m mechanism.run B        # Stufe B: Voynich -> results/mechanism/stageB.json
python3 -m mechanism.posthoc      # als post hoc markierte Robustheitsprüfungen
python3 -m mechanism.summarize AB # Tabellen
```
- Anschließendes iteratives Programm (E1–E7, jeweils präregistriert): `mechanism/PROGRAM.md` (Protokoll), `mechanism/SYNTHESIS.md` (Endpunkt). Der Mechanismus ist auf eine durch neun notwendige Eigenschaften definierte Klasse eingegrenzt. Ob die freien Entscheidungen von einer expliziten Regel, von Schreibgewohnheit oder von einer Nachricht getragen wurden, ist aus dem Text nicht entscheidbar; E7 zeigt das konstruktiv (Klartext in den freien Entscheidungen, exakt rückgewinnbar, in 40 Statistiken unsichtbar).
```bash
python3 -m mechanism.e1 A; python3 -m mechanism.e1 B          # E1 Grenz-Rezenz
python3 -m mechanism.e2 fit; python3 -m mechanism.e2 generate; python3 -m mechanism.e2 phenotype; python3 -m mechanism.e2 report
python3 -m mechanism.e3 fit; python3 -m mechanism.e3 generate; python3 -m mechanism.e3 phenotype; python3 -m mechanism.e3 report
python3 -m mechanism.e4 A; python3 -m mechanism.e4 B          # lexikalische vs. sublexikalische Drift
python3 -m mechanism.e5 A; python3 -m mechanism.e5 B          # frequenzaufgelöste Burstiness
python3 -m mechanism.e6 fit; python3 -m mechanism.e6 generate; python3 -m mechanism.e6 phenotype; python3 -m mechanism.e6 report
python3 -m mechanism.e7 run; python3 -m mechanism.e7 tmcheck   # Klartext in freien Entscheidungen
```
