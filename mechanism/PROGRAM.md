# Mechanism program log

Iterative search for the production mechanism. Each experiment is preregistered before its Voynich outcome is computed, calibrated on controls with known mechanisms, run, red-teamed, and used to update the hypothesis space below.

## Hypothesis space after the battery (REPORT.md, commit 123ee76)

Generation:

- **S1, procedure with sub-page state:** a hard slot grammar plus either (a) an explicit recency or copy rule or (b) settings that change every paragraph or line.
- **S2, practised improviser:** an internalised hard grammar, local recency of ordinary forms without propagation of new forms, and changes between sessions.
- **S3, plaintext-driven procedure:** rigid tables, with free choices that depend on recent output.

Transmission: K-reflow excluded. Direct composition (D) versus copying with identical line breaks (K-same) is open.

## Experiments

| # | Question | Preregistration | Status | Outcome |
|---|---|---|---|---|
| E4 | Is the within-page drift lexical (which words) or sublexical (how words are built)? | E4_PREREG.md (ce8bb45) | done | Lexical-type drift with a small sublexical part, as in plain Latin or German. No separation of content from habit drift. The two tested ciphers erase the sublexical part; the Voynich text keeps it. |
| E3 | Does the revised generator (margin-driven endings, slow drift, one-off slips) pass on unseen pages? | E3_PREREG.md (0f50303); fits frozen before test | done | Failure, 33/40 primary (28/31 unfitted), 28/40 secondary. Margin-driven endings confirmed necessary; glyph-level drift and slips cannot produce the within-page drift, hard-yet-diverse grammar or non-reuse of rare forms. |
| E2 | Does an explicit hard-grammar + recency + session + slip generator reproduce the full phenotype on held-out bifolios, and which components are necessary? | E2_PREREG.md (6b109a4), fits frozen before test | done | Failure, 32/40. Recency, hard pruning and session state are necessary; the class lacks margin-driven line endings, slow within-page drift and one-off irregular forms. |
| E1 | Are the local dynamics discrete sub-page settings or continuous recency? | E1_PREREG.md (b5dcb79), E1_DEVIATIONS.md | done (ea64b09 calibration, then Voynich) | Continuous. Settings at line or paragraph level of the size needed for the observed recency are excluded; recency-only is not falsified. |

## E1 result and red team

| Statistic | Voynich ZL3b (95% CI) | Takahashi IT2a | Threshold / controls | Reading |
|---|---|---|---|---|
| Line step, graded | +0.054 (0.026, 0.080) | +0.066 (0.028, 0.100) | settings excluded if lower bound > −0.039; SET-line about −0.08, REC about −0.02, MK +0.015 | Line settings excluded |
| Line step, binary | +0.010 (−0.074, 0.085) | −0.019 (−0.106, 0.055) | threshold −0.067 | Inconclusive |
| Paragraph step | −0.039 (−0.102, 0.019) | −0.034 (−0.100, 0.027) | settings excluded if lower bound > −0.116; SET-para −0.18 to −0.30; REC about 0 | Paragraph settings excluded (marginal) |
| Within-line decay, graded (secondary) | 0.069 (0.037, 0.101) | 0.076 (0.043, 0.101) | all controls −0.05 to +0.01 | Short-range decay inside lines, stronger than any control |
| Within-paragraph decay (secondary) | 0.065 (0.016, 0.110) | 0.074 (0.018, 0.124) | REC 0.03–0.12; SET −0.05 to 0.07 | Like the recency control |

Red team:

- The paragraph-settings exclusion is marginal and tied to the tuned magnitude. Small paragraph effects (point estimate −0.04, which could be pauses or topic) on top of recency are not excluded.
- The binary line step cannot decide. The graded step decides, and both transliterations agree.
- A positive graded line step (tokens across a line break more similar than tokens inside a line at the same distance) also appears weakly in the Markov control (+0.015), so part of it comes from glyph chaining inside lines. The Voynich value is larger.
- Similarity at distances 2–7 is about 1.1–1.3 times the stratified expectation, both within lines and across line breaks. The recency process runs across line breaks, while the glyph-level boundary coupling resets at each line (battery T1). Memory spans lines; the glyph-transition rule does not.

## Hypothesis space after E1

- S1(b), sub-page settings as the source of the local dynamics: excluded at the required magnitude.
- Remaining: continuous recency within a hard grammar. It can be an explicit copy rule (S1a), human priming (S2) or recency-dependent choices in a plaintext system (S3).
- Next (E2): an explicit generator of this class (hard grammar, continuous recency, session state, slips, line rules), fitted on half the quires and tested blind on the other half against the full frozen phenotype, with ablations to show which components are necessary.

## E2 result and red team

Test half, 40 statistics, tolerance 2·√(SE_V² + SD_G²) + 1% (table: `results/mechanism/e2/report.txt`).

| Model | Pass | Fails |
|---|---|---|
| HGR (full) | 32 | hapax, TTR, space gain, lexicon real, T2a paragraph, T2b slack, T6b slope, T7b recurrence |
| A1 no recency | 27 | + h2, h3, T6a near and exact, T7b slip |
| A2/A4 no pruning | 33 | d2 MI, T3a ρ (+ the four universal fails below) |
| A3 no session | 29 | + d2 MI, T3a ρ, T6a near |
| A0 plain automaton | 32 | d2 MI, page MI, T3a ρ, T6a near (+ universal fails) |

Universal fails, shared by every model:

- **Line endings tied to the margin (T2a paragraph, T2b).** Voynich: final-form excess 0.094 at margin-bound line ends against 0.037 at paragraph ends. Generators: 0.13–0.18 at both. The automaton's end symbol makes every line end special, and its length control (60–140% of target) fills lines far more loosely than the writer (slack 9.5 against 1.96).
- **Slow within-page drift (T6b).** Voynich −0.0082; generators −0.001 to −0.002. The recency range (8 tokens) is too short to produce it.
- **Rare forms never reused (T7b recurrence).** Voynich 0.5% (double-coded); generators 9–19%.

Necessary components, by the preregistered rule:

- **Recency:** without it, h2, h3, T6a and T7b slip fail.
- **Hard pruning:** without it, d2 MI and T3a fail.
- **Session state:** without it, d2 MI, T3a and T6a near fail.

Hard pruning in its simple form, however, costs lexical diversity. The unpruned automaton passes hapax share, TTR, space gain and the lexicon test; the pruned one does not. The text is hard-constrained and diverse at the same time.

Reading: the failures point to three properties of the production process. The last word of a line is adapted when the line meets the margin, not at every line end. Glyph preferences drift slowly across a page. Unusual forms occur once and are not taken up again, so recency acts on established forms only. All three are revised into the class in E3, preregistered separately. E2's test half is not used for any tuning.

## E3 result and red team

Primary direction: fitted on even bifolios, tested on odd (table: `results/mechanism/e3/report.txt`).

| Model | Pass | Unfitted pass | Fails |
|---|---|---|---|
| HGR2 | 33/40 | 28/31 | token MI, lexicon synthetic, T2b, T3a, T6b, T7b rate, T7b recurrence |
| B1 without margin-driven endings | 32 | 27 | hapax, T2a margin, T2a paragraph, T2b (8.07 against 2.27), T3a, T6b, T7b recurrence, T7b slip |
| B2 without drift | 32 | 27 | as HGR2, plus T2c |
| B3 without slips, temperature or free pruning | 27 | 25 | hapax, TTR, space gain, h2–h4, T2b, T3a, T6a × 2, T6b, T7b recurrence, T7b slip |
| B0, E2 class | 26 | 22 | as B3, plus lexicon real, lzma, T2a margin |
| Secondary HGR2 (fit odd, test even) | 28 | 24 | – |

What E3 establishes:

- **Margin-driven line endings are necessary.** Without them the final-form statistics and line fill fail. With them, T2a margin (0.046 against 0.079) and T2a paragraph (0.054 against 0.043) pass, and the slack ratio falls from about 8 to 2.6 (Voynich 2.3). The final word of a line is chosen for the margin, and paragraph ends are treated differently from margin ends.
- **Slow drift is not a glyph-level preference walk.** The fitted step (0.05) leaves the T6b slope at −0.002 against the Voynich −0.008. That value is as strong as topic drift in natural language (German −0.0096, Italian −0.012).
- **Diversity comes from grammatical novelty, not slips.** Slips reproduce hapax share and TTR but soften the hard zeros (T3a 0.057 against 0.042) and double the deviant rate (49 against 23). The text is diverse while staying hard.
- **Rare forms are not reused.** Every variant recurs its rare forms at 5–18%, against 0.9% in the Voynich text.
- **Token MI turns negative with margin-driven endings (−0.039 against +0.059).** This is an artefact of the final-token resampling, not diagnosed further.

Blindness from here on: the Voynich values of both halves have now been computed. Further generator comparisons can be preregistered but are no longer blind at the level of the Voynich values.

## Hypothesis space after E3

The necessary components found so far are a hard grammar, continuous recency, session state and margin-driven line endings. Two properties remain unreproduced, and they bear directly on the remaining alternatives:

- **Within-page drift of natural-language strength.** It could be content drift (plaintext, S3), which should be *lexical*: which words recur. Or it could be habit drift (S2, or drifting procedural settings, S1a), which should be *sublexical*: how words are built, visible even among different word types.
- **Non-reuse of rare forms.** Natural-language text and deterministic codes reuse rare words (5–16%). Human coinage without memory of the coined form, or homophonic encoding of rare units, would not.

Next (E4): decompose the within-page drift into lexical and sublexical parts, with calibrated controls.

## E4 result and red team

Slopes of line similarity over line distance 2–8 (95% CI):

| Corpus | Lexical L | Sublexical S |
|---|---|---|
| Voynich | −0.0142 (−0.0275, −0.0022) | −0.0052 (−0.0085, −0.0023) |
| LAT | −0.0115 | −0.0028 (−0.0045, −0.0011) |
| ITA (terza rima) | −0.0147 | −0.0121 (−0.0153, −0.0088) |
| GER | −0.0252 | −0.0043 (−0.0070, −0.0015) |
| ENG | −0.0128 | +0.0003 (−0.0031, 0.0040) |
| VB-run, deterministic verbose cipher on Latin | −0.0092 | +0.0002 (−0.0020, 0.0022) |
| NAIB-run, Naibbe on Latin | +0.0076 | −0.0015 (−0.0043, 0.0012) |
| GDRIFT, glyph habit walk | −0.0517 | −0.0148 |
| LDRIFT, vocabulary walk | −0.0398 | +0.0007 |
| MK-sec | −0.0042 | −0.0007 |

- **Preregistered verdict: lexical-type drift.** The sublexical slope overlaps the language range, and the "beyond content drift" bar (below −0.0153) is set by Dante's rhyme scheme, which is structural rather than topical. Content drift and vocabulary or habit drift are not separated.
- **By-product (a comparison of preregistered statistics, stated as such):** both ciphers remove the sublexical drift that their Latin plaintext has (Latin −0.0028; ciphers +0.0002 and −0.0015). The Voynich interval lies below the deterministic cipher's interval. A letter-level cipher of the tested kinds is therefore a poor match for the Voynich drift. Unenciphered content, or production-level drift, fits better.
- The magnitudes of the synthetic drift controls were not tuned to the Voynich text, so their slopes show directions only.

Next (E5): frequency-resolved burstiness. Content drift makes rare words the burstiest; a drifting repertoire with one-off coinages does not.
