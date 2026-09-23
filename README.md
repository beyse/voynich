# Constrained, not identifiable: statistical constraints on the production of the Voynich manuscript text

Code, data, analysis plans and results for the paper of the same title by Sebastian Beyer (independent researcher, Vienna; [@BeyerSebastian](https://x.com/BeyerSebastian) on X).

- **Paper:** [`paper/paper.pdf`](paper/paper.pdf), with supplement [`paper/supplement.pdf`](paper/supplement.pdf). This is a preprint, not peer reviewed, and dedicated to the public domain under CC0 1.0 ([`paper/LICENSE.md`](paper/LICENSE.md)).
- **Main result:** a set of production constraints can be recovered from the text. Nine measured properties define a mechanism class, and named alternatives are excluded. But message-carrying and message-free processes of that class cannot be told apart from the text alone. Nothing here shows that the text is meaningless, and nothing decodes it.

The paper has two parts:

1. **An exploratory profile** (Section 3). It was not specified in advance. It applies one information-theoretic battery to the manuscript, language controls and candidate generators, and shows that a local, low-order glyph process with drifting parameters is sufficient.
2. **A pre-specified program** (Sections 4–8). Each analysis plan was committed to this repository before its Voynich outcome was computed; this is not an external registration. The program consists of a calibrated battery T1–T7 and seven follow-up experiments E1–E7. Together they separate procedure, improvisation and plaintext-driven production, test explicit generators on held-out pages, and give a constructive non-identifiability result (E7).

## Repository layout

| Path | Content |
|---|---|
| `data/ZL3b-n.txt`, `data/IT2a-n.txt` | Transliterations from [voynich.nu](https://www.voynich.nu/transcr.html): Zandbergen–Landini ZL3b and Takahashi IT2a (IVTFF, EVA) |
| `data/gibberish/` | Human gibberish corpus of Gaskell & Bowern (2022); licence notice in `SOURCE.md` |
| `data/naibbe/naibbe_tables.csv` | Naibbe cipher tables from [greshko/naibbe-cipher](https://github.com/greshko/naibbe-cipher) (modified MIT licence, attribution required); the cipher itself is reimplemented in `voynich/generators.py` |
| `voynich/` | IVTFF parser, statistics, profile battery and generators |
| `scripts/` | One script per profile analysis; run from the repository root |
| `results/logs/` | Logs of the profile analyses |
| `mechanism/` | Analysis plans (`PREREG.md`, `E1_PREREG.md` … `E7_PREREG.md`, `REVISION_PLAN.md`), deviation logs, code for T1–T7, E1–E7 and the revision analyses, the experiment log `PROGRAM.md`, the synthesis `SYNTHESIS.md` and the commit map `COMMIT_MAP.md` |
| `results/mechanism/` | Results of the pre-specified program (JSON) |
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

Pre-specified program (Sections 4–8):
```bash
python3 -m mechanism.run A; python3 -m mechanism.run B      # battery: controls, then Voynich
python3 -m mechanism.posthoc                                 # post hoc checks, labelled as such
python3 -m mechanism.e1 A; python3 -m mechanism.e1 B
for e in e2 e3 e6; do for s in fit generate phenotype report; do python3 -m mechanism.$e $s; done; done
python3 -m mechanism.e4 A; python3 -m mechanism.e4 B
python3 -m mechanism.e5 A; python3 -m mechanism.e5 B
python3 -m mechanism.e7 run; python3 -m mechanism.e7 tmcheck
python3 -m mechanism.redteam                                 # red-team checks (post hoc)
python3 -m mechanism.revision fetch                          # revision: Greshko's published Naibbe data (data only)
python3 -m mechanism.revision r1; python3 -m mechanism.revision r2; python3 -m mechanism.revision r3
python3 -m mechanism.e7b run                                 # R4a: E7 with 20 runs per condition
python3 -m mechanism.e8 check; python3 -m mechanism.e8 run   # R4b: message through the E3 generator
```

Paper. Every number in the text and tables is computed from the result files at build time:
```bash
python3 paper/make_figures.py && python3 paper/build.py
```

## Pre-specification

Each analysis plan was committed to this repository before the corresponding Voynich outcome was computed. This is prospective specification under version control, not registration in an external registry. The commits are listed in Table S28 of the supplement, and deviations are logged in `mechanism/*DEVIATIONS.md`. The repository was private while the work was done and was published once it was complete. The commit timestamps are therefore the author's record, not entries in an independent registry. Before publication the author e-mail address was replaced in every commit. This changed the commit hashes but not the file contents or dates; `mechanism/COMMIT_MAP.md` maps the old hashes, which older documents may quote, to the published ones.

## Licences and attribution

- Everything the author created in this repository is dedicated to the public domain under CC0 1.0 (see `LICENSE`): the paper, supplement and figures, all code, the analysis plans, logs and results. Attribution is appreciated but not required.
- Third-party data keep their own licences:
- The transliterations are the work of René Zandbergen and Gabriel Landini (ZL3b) and of T. Takahashi (IT2a). voynich.nu distributes them under CC0 ([Licences and copyright](https://www.voynich.nu/roadmap.html#cop)); please acknowledge the source.
- The gibberish corpus and the Naibbe tables are redistributed under their own licences. Both require citation of the source papers:
  - Gaskell & Bowern 2022, CEUR-WS 3313;
  - Greshko 2025, *Cryptologia*, doi:10.1080/01611194.2025.2566408.
- The work was carried out with Claude Opus 5.5 (Anthropic), used through Claude Code. The AI system wrote and ran the analysis code and drafted the paper under the author's direction; see the disclosure section of the paper. The author takes full responsibility for the content.
