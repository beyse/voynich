# How the Voynich text was produced: the strongest defensible explanation

Endpoint of the mechanism program: the battery (REPORT.md, preregistered in PREREG.md) and experiments E1–E7 (PROGRAM.md, each preregistered before its Voynich outcome was computed). All numbers come from `results/mechanism/`.

## 1. Answer

The production mechanism is narrowed to a **well-defined class**, specified by nine properties, each established by a preregistered and calibrated test (Section 2). Within that class, the remaining question is whether the free choices were made:

- by an explicit rule set with a randomiser (fixed procedure),
- by a practised writer's habits (skilled improvisation), or
- by a message (plaintext-driven procedure).

That question **cannot be decided from the text**. E7 shows it constructively: a manuscript-sized output of a Voynich-like process can carry about 44 KB of compressed plaintext, recoverable exactly, with no measurable trace in any of 40 statistics.

What the evidence does support, as weighing rather than proof:

- **No device.** No periodicity was found, although a device effect of moderate size would have been detected.
- **No detectable content.** The rare forms behave unlike content words, and every tested historical-style cipher family leaves traces that the text lacks.
- **Every necessary component is a known property of human handwriting production:** priming, session-to-session variation, adaptation of the line end to the margin, and slips. A procedure would need each of them as a separate explicit rule.

The most defensible explanation is therefore: **writers composing on the page within a strict, learned word grammar, choosing forms under short-term recency and session-dependent preferences, and fitting the last word of each line to the margin.** Whether a message rode on those choices is undecidable from the text. There is no measurable evidence that one did, and the tested ways of carrying one are excluded.

## 2. The mechanism class

| # | Property | Evidence |
|---|---|---|
| C1 | **Hard, slot-like word grammar**, harder and more rigid than naive human gibberish and natural languages | T3a zero replication 0.040 against gibberish 0.093 and languages 0.075–0.104; T3b slot consistency 0.868 against 0.671 and 0.66–0.70; hard pruning necessary in E2 |
| C2 | **Line-bound glyph transitions.** The first glyph of a word depends on the last glyph of the previous word within a line; the coupling resets at line breaks | Edge MI about 0.14–0.15 bit; break coupling small (T1); an explicit boundary rule is necessary for word-level production (E6: without it, edge MI 0.0005) |
| C3 | **Margin-driven line endings.** The last word is adapted when the line meets the margin, and differently at paragraph ends | T2a margin 0.085 against paragraph end 0.039 (both p = 0.005); without this component line endings and line fill fail (E3) |
| C4 | **Continuous short-range recency** across line and paragraph boundaries | T6a near-repeat index 0.153 above every stationary procedure (99th percentile at most 0.116); E1: no line or paragraph steps of the size settings would need; recency necessary in E2 |
| C5 | **Session and page variation in the weights of shared forms**, step-like at quire boundaries | T5 step score 0.76 (calibration: smooth 1.66, step 0.28); E5 page clustering even of the most frequent forms (1.36, against 1.02–1.22 in languages); session state necessary in E2 |
| C6 | **Within-page drift of natural-language strength**, mainly lexical with a small sublexical part | T6b −0.008; E4 lexical −0.014, sublexical −0.005 |
| C7 | **No local vocabulary.** Locally unique glyph combinations occur once and are not reused | T7b recurrence 1.1% for the whole text, 0.5–0.9% per half (languages 5.5–16%, copy-and-modify 32%, every explicit generator 4–19%); E5 rare-form clustering weaker than content words (gradient 0.25 against 0.66–1.08) |
| C8 | **No device periodicity** | T4, with power from mixing weight 0.2 |
| C9 | **No copying signature**; copying with re-lining excluded | T2c (no dittography), T7a (no word insertions); T2a |

## 3. Excluded

| Variant | Test |
|---|---|
| Naive improvisation (Gaskell & Bowern-type samples) | T3a, T3b |
| Stationary procedures: tables, grilles, automata or devices with parameters constant within a page | T6a |
| Periodic devices with effect size ≥ 0.2 | T4 |
| Smooth drift across pages | T5 |
| Sub-page settings (per line or paragraph) as the source of the local dynamics | E1 |
| Copy-and-modify with propagating innovations and vertical copying (Timm & Schinner as implemented) | T7b, T2c, T4b |
| Word-preserving ciphers and codes | T7b, E5 |
| The Naibbe cipher as published | T6a, E4, E5 |
| Letter-level ciphers of the tested kinds as the source of the drift (they erase the sublexical part) | E4 |
| Copying from a draft with different line breaks | T2a |

## 4. Sufficiency

Explicit generators of the class were fitted on one half of the manuscript (bifolio parity) and tested on the other half against 40 statistics:

| Generator | Held-out pass |
|---|---|
| Hard grammar + recency + session state (E2) | 32/40 |
| + margin-driven endings, slips, drift (E3, best) | 33/40 (28/31 unfitted); secondary direction 28/40 |
| Two-route: repertoire retrieval + coinage (E6) | 22/40 |

The ablations identify recency, hard pruning, session state, margin-driven endings and the boundary rule as necessary. No explicit generator reproduced C7 (non-reuse of rare forms), C6 at full strength, or the line-fill slack at the same time as everything else. The class is therefore defined by necessary properties, and no member reproducing all 40 statistics has been found. C6 and C7 are the concrete open specifics of the mechanism.

## 5. Which executor?

- **Indistinguishability (E7).**
  - The order-3 glyph process, driven by arithmetic decoding of compressed Latin, Italian or German, returns its plaintext with 0 bit errors.
  - It carries 1.9 bits per glyph, or 10 bits per word.
  - All 40 statistics agree with the randomly driven process; the one apparent difference vanished with 8 runs per condition (p = 0.83). Even raw, uncompressed plaintext bits changed only 1 of 40 statistics.
  - Any stochastic production process can be driven this way. "No plaintext" cannot be shown from text statistics, and a plaintext cannot be detected by them if it is encoded like this.
- **What the evidence weighs:**
  - No device footprint (C8).
  - The needed components (C3, C4, C5, C6) are standard properties of human writing. A rule set would have to specify each explicitly, including a continuously drifting preference.
  - A message would have to be encoded so that it creates no local vocabulary (C7), no content-like clustering of rare forms (E5) and no loss of sublexical drift (E4). Every historical-style cipher tested fails at least one of these. A mimic-function encoding passes: the message is arithmetically decoded into the process's choices, and E7 shows this works even without compression. That technique is anachronistic.
- **Explicit rule set versus habit** cannot be separated by the text at all. The same generator describes both. Only physical or historical evidence could decide it.

## 6. Transmission

Copying with re-lining is excluded (T2a), and no copying signature was found (T2c, T7a). The line-final forms depend on whether the line ends at the margin (C3), so the last word was chosen knowing where this page's line ends. The simplest reading is composition directly on the page. Copying from a draft with the same lines and margins is not excluded.

## 7. What could go further

These need evidence other than the transliterated text:

- **Practised improvisation.** Volunteers writing an invented script over weeks: do C1 and C7 emerge with practice?
- **Execution experiment.** Volunteers following a written rule set, to see which components need explicit rules.
- **Physical evidence from high-resolution or multispectral images.** Pen and ink changes at the predicted session boundaries (C5 steps at quires), glyph compression at the margin (C3), erasures and corrections coded blind to predictions.
- **Historical sources.** Word-grammar tables or instructions of this kind.
- **The open specifics C6 and C7.** A generator that reproduces them together would complete the sufficiency part.

## 8. Relation to prior work

- **Timm & Schinner (2020):** local recency confirmed; propagating innovations and vertical copying absent.
- **Gaskell & Bowern (2022):** naive gibberish is too soft and too little rigid; their caveat about skilled, long-term production is where the open question lies.
- **Stolfi; Zattera (2022):** slot rigidity quantified (C1).
- **Rozanova & Temerev (2026):** boundary coupling and line-bound units confirmed (C2).
- **Greshko (2025), Kinnison (2026):** ciphers reproduce the positional entropy profile, but the Naibbe cipher lacks recency, drift and page effects.
- **Wayner (1992):** mimic functions make the plaintext question undecidable from statistics (E7).

## 9. Claims policy

Nothing here shows that the text is meaningless or free of plaintext. Statistical sufficiency is not historical identification. The class is established by necessary properties, and the choice between rule, habit and message is shown to be undecidable from the text, not decided.
