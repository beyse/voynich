# Constrained, not identifiable: how the Voynich manuscript text was produced

Code, data, preregistrations and results for the paper of the same title by Sebastian Beyer (independent researcher, Vienna; [@BeyerSebastian](https://x.com/BeyerSebastian) on X).

- **Paper:** [`paper/paper.pdf`](paper/paper.pdf), with supplement [`paper/supplement.pdf`](paper/supplement.pdf)
- **Main result:** the production mechanism of the Voynich text is tightly constrained: nine properties define it, and named alternatives are excluded. But whether its remaining free choices carry a message cannot be identified from the text alone. Nothing here shows that the text is meaningless, and nothing decodes it.

The paper has two parts:

1. **An exploratory profile** (Section 3). It is not preregistered. It applies one information-theoretic battery to the manuscript, language controls and candidate generators, and shows that a local, low-order glyph process with drifting parameters is sufficient.
2. **A preregistered program** (Sections 4–8). It consists of a calibrated battery T1–T7 and seven follow-up experiments E1–E7. Together they separate procedure, improvisation and plaintext-driven production, test explicit generators on held-out pages, and give a constructive non-identifiability result (E7).

## Repository layout

| Path | Content |
|---|---|
| `data/ZL3b-n.txt`, `data/IT2a-n.txt` | Transliterations from [voynich.nu](https://www.voynich.nu/transcr.html): Zandbergen–Landini ZL3b and Takahashi IT2a (IVTFF, EVA) |
| `data/gibberish/` | Human gibberish corpus of Gaskell & Bowern (2022); licence notice in `SOURCE.md` |
| `data/naibbe/naibbe_tables.csv` | Naibbe cipher tables from [greshko/naibbe-cipher](https://github.com/greshko/naibbe-cipher) (modified MIT licence, attribution required); the cipher itself is reimplemented in `voynich/generators.py` |
| `voynich/` | IVTFF parser, statistics, profile battery and generators |
| `scripts/` | One script per profile analysis; run from the repository root |
| `results/logs/` | Logs of the profile analyses |
| `mechanism/` | Preregistrations (`PREREG.md`, `E1_PREREG.md` … `E7_PREREG.md`), deviation logs, code for T1–T7 and E1–E7, the experiment log `PROGRAM.md` and the synthesis `SYNTHESIS.md` |
| `results/mechanism/` | Results of the preregistered program (JSON) |
| `paper/` | Paper sources: templates, build script, figure script, number extraction |
| `REPORT.md` | Earlier working report on the profile (German), superseded by the paper |

## Data not included

- **Reference texts** in `data/ref/`:
  - Project Gutenberg: Goethe, *Faust* (#2229); Dante, *Commedia* (#1012); Tolstoy, *War and Peace* (#2600).
  - Caesar, *De bello Gallico*, books 1–7, from thelatinlibrary.com, with HTML tags removed.
  - Genesis in Hebrew from the Sefaria API, with vowel points removed.
- **Facsimile** `Voynich_Manuscript.pdf`: the Beinecke Library's digital reproduction of MS 408. Only the illustration features (`scripts/scripts_page_colors.py`) need it. PDF page 3 is f1r, then pages run linearly to page 116 = f58v, with f12 missing.

## Reproduction

Everything uses Python 3 with numpy, matplotlib, PyMuPDF (`fitz`) and Jinja2.

Profile analysis (Section 3). Logs go to `results/logs/`, and the numbers are extracted into `paper/numbers.json`:
```bash
zsh paper/run_chain1.sh; zsh paper/run_chain2.sh
python3 scripts/scripts_jackknife.py
python3 paper/extract_numbers.py
```

Preregistered program (Sections 4–8):
```bash
python3 -m mechanism.run A; python3 -m mechanism.run B      # battery: controls, then Voynich
python3 -m mechanism.posthoc                                 # post hoc checks, labelled as such
python3 -m mechanism.e1 A; python3 -m mechanism.e1 B
for e in e2 e3 e6; do for s in fit generate phenotype report; do python3 -m mechanism.$e $s; done; done
python3 -m mechanism.e4 A; python3 -m mechanism.e4 B
python3 -m mechanism.e5 A; python3 -m mechanism.e5 B
python3 -m mechanism.e7 run; python3 -m mechanism.e7 tmcheck
python3 -m mechanism.redteam                                 # red-team checks (post hoc)
```

Paper. Every number in the text and tables is computed from the result files at build time:
```bash
python3 paper/make_figures.py && python3 paper/build.py
```

## Preregistration

Each preregistration was committed to this repository before the corresponding Voynich outcome was computed. The commits are listed in Table S28 of the supplement, and deviations are logged in `mechanism/*DEVIATIONS.md`. The repository was private while the work was done and was published once it was complete. The commit timestamps are therefore the author's record, not entries in an independent registry.

## Licences and attribution

- The transliterations are the work of René Zandbergen and Gabriel Landini (ZL3b) and of T. Takahashi (IT2a). voynich.nu distributes them under CC0 ([Licences and copyright](https://www.voynich.nu/roadmap.html#cop)); please acknowledge the source.
- The gibberish corpus and the Naibbe tables are redistributed under their own licences. Both require citation of the source papers:
  - Gaskell & Bowern 2022, CEUR-WS 3313;
  - Greshko 2025, *Cryptologia*, doi:10.1080/01611194.2025.2566408.
- The analyses, code and drafts were prepared with the assistance of an AI system (Claude, Anthropic). The author verified the results and takes full responsibility for the content.
