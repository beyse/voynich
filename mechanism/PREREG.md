# Preregistration: production-mechanism identification for the Voynich text

Frozen before any test in this document was computed on the Voynich data.
The git commit that first contains this file is the timestamp of the freeze.
Changes after the freeze go into `mechanism/DEVIATIONS.md` with a reason and a note saying whether Voynich results had been seen.

## 1. Question

Two separate questions, each with competing hypotheses treated as co-equal.

**Generation (axis G).** How was the token sequence produced?

- **P, fixed procedure.** Explicit rules plus an external randomiser or schedule (table, grille, wheel, dice, cards). The writer makes no free choices beyond executing the rules. Parameters may change at discrete points (new table, new setting per scribe or section).
- **I, skilled improvisation.** Internalised, soft habits of a writer producing pseudo-text online. Choices are free but habitual. The Timm and Schinner copy-and-modify account is treated as a formalised variant of I, because its source and modification choices are made by the writer.
- **C, plaintext-driven procedure.** Explicit rules whose choices are driven, fully or in part, by a plaintext (verbose or homophonic cipher, code, Naibbe-type system). Natural-language text is the degenerate case of C with an identity mapping.

**Transmission (axis T).** How did the text reach the vellum?

- **D**, composed directly on the page.
- **K-reflow**, copied from a draft whose line breaks differ (running text re-lined).
- **K-same**, copied from a draft with the same line breaks.

Tests based on the transliteration alone cannot separate D from K-same. This is stated in advance and no test below claims to do so.

## 2. Claims policy

- Statistical sufficiency of a model is not historical identification of a mechanism. Only positive, mechanism-specific evidence counts toward identification.
- No result in this project is reported as showing that the text is meaningless or contains no plaintext. The strongest admissible statement about C is that a named variant of C makes a prediction that fails.
- A concrete generator is reconstructed only if the verdict rule in Section 7 favours P.

## 3. Prior knowledge (declared, not counted as new evidence)

From the earlier project in this repository I already know the following about the Voynich text (ZL3b, paragraph text):

1. The coupling between the last glyph of a line and the first glyph of the next line is close to zero (about 3% of within-line boundary coupling).
2. Adjacent tokens are coupled mainly through the boundary glyphs; token-level excess mutual information is low.
3. Glyph statistics drift with folio distance; the drift follows the scribal hand more than the illustration section.
4. No vertical copy signature was found once page-level vocabulary was controlled.
5. The Timm–Schinner copy-and-modify generator lacks the boundary coupling; the Naibbe cipher passes the lzma residual test.
6. Gaskell and Bowern (2022) report that human gibberish shows more word and character repetition, triple repeats, positive word-length autocorrelation and positional biases within lines than meaningful text.

Tests T1 and T4b overlap with items 1 and 4. They are kept because they are now calibrated against human gibberish and a positive device control, which the earlier work did not do. The verdict table marks them as "prior".

## 4. Data, units and leakage audit

**Voynich.** ZL3b (`data/ZL3b-n.txt`), loci of type P (paragraph text). Uncertain commas are joined (baseline of the earlier paper). A token is uncertain if it contains `?` or a rare-glyph code (`@nnn;`). Token-level tests use certain tokens in lines with at least two certain tokens. Line-length tests (T2b) use only lines with no uncertain token and no drawing-gap marker `<->` or `<~>`. Metadata from page headers: hand `$H` (1–5, Davis), quire `$Q`, section `$I`, Currier language `$L`. Page order is file order, which is the current folio order.

**Glyph units.** EVA strings are segmented left to right, longest match first, with `cth ckh cph cfh ch sh` as single units and every other EVA character as one unit. The same segmentation is applied to every EVA-based corpus (Voynich, Timm–Schinner, Markov and device generators, Naibbe output). Latin-alphabet corpora (natural languages, human gibberish) use letters as units. Edit distances are computed on units.

**Second transliteration.** IT2a (Takahashi, `data/IT2a-n.txt`) is aligned to ZL3b by page and line number. Tokens are aligned only when both lines have the same number of tokens. A token is double-coded when both transliterations read it identically.

**Paragraph ends.** A line is paragraph-final if its raw text contains `<$>`; all other paragraph lines are margin-bound.

**Leakage audit.**

- The transliterators worked from the images. Alternative readings `[a:b]`, uncertain glyphs, braces and inline comments can mark corrected or damaged places. Rules: alternative readings use the first reading; uncertain tokens are dropped from token-level tests and whole lines from line-length tests; the correction annotations (T7a) are the only annotations used as outcome data, and every model used to score them is trained with the annotated lines removed.
- The generators (Markov, table, device, copy-and-modify) are fitted to Voynich statistics. They are used only to calibrate how each test responds to a known mechanism, never as evidence that a mechanism fits.
- Several Voynich properties are known to me (Section 3). New tests were chosen to measure properties I have not computed before: slack tightness, final-form effect conditioned on token length, zero replication, slot rigidity against human gibberish, device periodicity with a positive control, drift shape, recency decay, and the behaviour of double-coded deviant tokens.
- Correction annotations: I have counted them (about 20 `corr?` comments, one erasure note, a few notes on marks above glyphs) but have not looked at their text context before this freeze.

## 5. Controls and their class labels

| Label | Source | G class | T class | Used in |
|---|---|---|---|---|
| GIB | Gaskell & Bowern 2022, 38 handwritten documents, letters | I (naive) | D | all tests where size allows |
| LAT, LATV, ITA, GER, ENG | Caesar, Vulgate, Dante, Faust, War and Peace | C (identity) | K-reflow when greedily wrapped | T1–T7 |
| NAIB-lines, NAIB-run | Naibbe cipher on Latin, independent sentences per line / running text | C | generated line by line | T1, T3–T7 |
| MK-sec | order-3 glyph automaton per (language, section) | P, stationary within section | generated | T3–T7 |
| MK-page | order-3 automaton, page counts interpolated with section counts, λ = 0.5 | P with page-level settings | generated | T4–T7 |
| RUGG | table-and-grille | P | generated | T3–T7 |
| DEV-w | new periodic device: period 5 along the line, row cycle 4 down the page, column- and row-specific token distributions mixed with the global one at weight w ∈ {0.1, 0.2, 0.4} | P, device | generated | T4 (power) |
| DRIFT-smooth, DRIFT-step | order-2 automaton per hand whose parameters move linearly across the hand's pages, or jump once at the midpoint | I-like drift / P-like setting change | generated | T5 (calibration) |
| TS | copy-and-modify after Timm & Schinner 2020 | I (formalised) | generated | T3–T7 |

Generated corpora reproduce the page and line shape of the Voynich paragraph text and carry its page metadata (hand, quire, section).

## 6. Tests

Every test states its statistic, its null, what each hypothesis predicts, and what would falsify each prediction. A test counts toward the verdict only if its calibration requirement is met; otherwise it is reported as uninformative.

### T1. Line-break transparency (prior; axis T and I)

- **Statistic.** R_LB = excess MI between the last unit of line n and the first unit of line n+1, divided by excess MI between the last unit of a token and the first unit of the next token inside lines, with equal numbers of pairs (within-line pairs subsampled). Excess is over the MI of randomly re-paired pairs (20 draws). Uncertainty: leave-one-quire-out jackknife for Voynich, leave-one-document-out for GIB.
- **Predictions.** Any continuously produced stream that is wrapped afterwards (K-reflow; a cipher stream wrapped into lines) gives R_LB ≥ 0.5. Line-unit production gives R_LB < 0.25. Online improvisation without line planning is expected to be transparent (≥ 0.5).
- **Falsifiers.** K-reflow is falsified if R_LB(V) < 0.25 with its interval below 0.5. The claim "line reset is a generic property of improvised writing" is falsified if R_LB(GIB) ≥ 0.5.
- **Calibration.** Latin wrapped greedily must give ≥ 0.5, otherwise the test is uninformative.

### T2. Line-end behaviour (axis T; secondary for G)

- **T2a, final-form effect.** JSD between the distribution of the last unit of line-final tokens and that of line-internal tokens reweighted to the same token-length distribution (strata 1, 2, …, 7, ≥ 8 units). Computed separately for margin-bound and paragraph-final lines. Null: permutation of the "final" label within length strata, 200 permutations. K-reflow predicts no effect in margin-bound lines (p > 0.05). An effect falsifies K-reflow. Line-aware production (D or K-same, any G) allows an effect.
- **T2b, slack tightness.** Voynich pages of section S (stars) and each GIB document. Width W = 90th percentile of the lengths (units, one unit per inter-token space) of eligible margin-bound lines; at least 8 eligible lines per page. Slack = max(0, W − L). Null: the page's eligible tokens in random order, packed greedily into lines of width W (a token opens a new line when it does not fit; an over-long token stands alone), with W' and slack recomputed in the same way; 200 simulations. Statistic T = mean observed slack / mean simulated slack, bootstrap over pages.
  - Greedy wrapping of fixed content (K-reflow, or online writing that only wraps) predicts T ≈ 1.
  - Content chosen to fit the remaining space predicts T < 1.
  - Lines planned as units that stop before the margin predict T > 1.
  - Glyph-count width is a noisy proxy for physical width, which biases T upward for every handwritten corpus. The primary comparison is therefore T(V) against T(GIB), whose writers wrapped online by hand. T(V) < T(GIB) with non-overlapping 95% intervals counts as adaptation beyond naive online writing. T(V) > T(GIB) counts as line planning. Greedily wrapped Latin must give T within 0.9–1.1, otherwise the test is uninformative.
- **T2c, dittography at line breaks.** Rate at which the first token of line n+1 repeats the last token of line n, and the rate of identical consecutive token bigrams across the break (last two of line n equal first two of line n+1). Null: random pairing of lines within the page (200 permutations). Copying from a draft (K-same or K-reflow) predicts an excess from resumption errors. Direct composition predicts none. The test can support K only by an excess; absence bounds the rate and is reported as such.

### T3. Hard constraints and rigidity (axis G)

- **T3a, zero replication.** Unit bigrams inside tokens with boundary symbols. Split each unit of analysis into halves A and B by alternating lines. Candidate cells: count 0 in A and expected count under the independence model of A (row total × column total / grand total) ≥ τ. ρ = Σ observed in B / Σ expected in B (independence model of B) over candidate cells. Matched-size version: consecutive 250-token chunks within a hand (Voynich), within a document (GIB, documents under 150 tokens skipped) or within a text (languages, generators); τ = 3; counts pooled over chunks; bootstrap over chunks. Full-size version for Voynich, per hand, and for languages: τ = 5.
  - P and table-based C predict hard zeros: ρ(V) below the GIB interval and not above the language range.
  - I (naive) predicts ρ(V) inside the GIB interval.
  - Falsifier of table-based P and C: ρ(V) inside or above the GIB interval. Falsifier of naive I: ρ(V) below the GIB interval. Skilled improvisation cannot be falsified by this test because no data on long-practised improvisers exist.
- **T3b, slot rigidity (comparison with Stolfi and Zattera).** A linear order of units maximising the share of within-token ordered unit pairs (u before v at any distance, u ≠ v) consistent with the order; local search from the mean-relative-position order, adjacent swaps and single-unit moves, 20 random restarts. Statistics: consistency share and share of tokens (≥ 2 units) that are monotone in the order. Units with fewer than 5 occurrences in the chunk are ignored. Matched 250-token chunks as in T3a.
  - Slot-table generation (P, table-based C) predicts rigidity above natural languages; naive I predicts the GIB level. Same falsifiers as T3a.
- **T3c, positional entropy (comparison with Kinnison).** Entropy of the unit at positions 1–3 from the token start and 1–3 from the end, divided by the unit entropy. Descriptive only, reported for V, GIB, NAIB and languages.

### T4. Periodicity (axis G, device variants of P)

- **T4a, lag profile inside lines.** For lags k = 2…8, the rate at which tokens t and t+k in the same line share the final unit, and the rate at which they share the initial unit, each divided by its mean under within-line token permutation (100 permutations). A device of period p predicts a local maximum at k = p that exceeds both neighbours and the null by 3 standard errors. Smooth processes predict monotone decay toward 1.
- **T4b, column alignment (prior).** Line pairs (i, i+d), d = 1…3, on the same page; token positions j from 1 to min(length) − 2 (first and last excluded). Similarity = shares final unit and initial unit. Ratio of aligned pairs (j, j) to offset pairs (j, j ± 1, j ± 2). A column device predicts > 1; otherwise ≈ 1.
- **T4c, line cycle.** Cosine similarity of unit-bigram vectors of lines i and i+k on the same page, k = 1…12, divided by the mean under within-page line permutation. A row cycle q predicts a local peak at k = q.
- **Power.** DEV-w with w ∈ {0.1, 0.2, 0.4}, 10 seeds each. A Voynich null result excludes device variants only down to the smallest w detected in ≥ 8 of 10 seeds.
- **Falsifier of device-P.** No peak in T4a, T4b or T4c where DEV at that effect size is detected with power ≥ 0.8. Falsifier of non-device hypotheses: a significant peak.

### T5. Drift shape (axis G)

- Per hand, pages in folio order with ≥ 100 certain tokens. Page vector: unit-bigram counts inside tokens with boundaries. Excess distance E_ij = JSD(i, j) − mean JSD of two multinomial samples of sizes n_i and n_j drawn from the pooled distribution of i and j (20 draws). r = rank distance in the hand's page sequence.
- **Statistics.** (i) Leave-one-page-out prediction error of a smooth model E = a + b·r against a step model E = a + c·[block(i) ≠ block(j)], with contiguous blocks found by optimal segmentation into K = 2…6 blocks, K chosen inside the training fold by the same cross-validation. Score S = MSE(step) / MSE(smooth). (ii) Gini coefficient of consecutive excess distances E(i, i+1). (iii) Share of the top decile of consecutive jumps that fall on quire or section boundaries.
- **Predictions.** P with setting changes: step model better (S < 1), high Gini, jumps anywhere. I: smooth model better (S > 1), low Gini. C with topic-driven vocabulary: steps at section boundaries.
- **Calibration.** DRIFT-smooth must give S > 1 and DRIFT-step S < 1 on the same page structure, otherwise the test is uninformative. Folio order is not the original order in places; this weakens both models equally.

### T6. Writer dynamics (axis G)

- **T6a, recency profile.** Within a page (GIB: document), tokens in running order across lines. For token distance d = 2…40: exact-repeat rate and near-repeat rate (unit edit distance exactly 1), each divided by its mean under within-page token permutation (50 permutations). Decay index DI = mean ratio over d = 2…5 minus mean ratio over d = 21…40, for exact and near repeats. Bootstrap over pages.
  - Stationary procedures (MK-sec, MK-page, RUGG, DEV) predict DI ≈ 0.
  - I (GIB, and TS by construction) predicts DI > 0 for near repeats.
  - C and natural language: calibrated on the language controls and NAIB; no fixed prediction beyond the control values.
  - Priming is declared present if DI_near(V) exceeds the 99th bootstrap percentile of every stationary P control. Falsifier of stationary P: priming present. Falsifier of I: DI_near(V) inside the P range while GIB shows priming.
- **T6b, within-page line drift.** From the T4c profile, the slope of the normalised line similarity over k = 1…8. I predicts a negative slope (drift within a writing session); stationary P and C predict ≈ 0.
- **T6c, hand specificity.** DI and slope per hand with ≥ 20 pages; between-hand heterogeneity against the bootstrap spread. Descriptive.

### T7. Errors and corrections

- **T7a, annotated corrections (coded independently by the ZL transliterators).** Events: inline comments containing `corr`, `eras`, `above`, `inser`, `added`. For each event: type (glyph-level or token-level insertion/deletion), position class of the affected unit when determinable (token-initial, internal, final), and the percentile of the annotated token's log-probability under an order-2 unit Markov model trained on all paragraph lines except annotated ones.
  - P predicts corrections at rule-bearing positions, dominated by token-initial units after a boundary (where boundary coupling lives), with corrected tokens of typical probability.
  - K predicts token-level insertions or deletions (omitted or doubled words).
  - I predicts glyph-level repairs at arbitrary positions.
  - Power is low (n ≈ 20–25). The test counts only if a pattern is extreme: at least 75% of events in one position or type class with binomial p < 0.01 against the base rate of that class.
- **T7b, double-coded deviant tokens.** Deviant: a double-coded token containing a unit trigram (with boundaries) that occurs in no other quire of the ZL text. For controls, deviance is defined against the other quire-sized blocks of the same corpus (Voynich quire labels carried over). Statistics: deviant rate per 1,000 tokens; recurrence share (types occurring ≥ 2 times in their quire); clustering ratio (median distance between consecutive occurrences divided by the median under random placement within the quire, 100 permutations); slip share (deviant tokens at unit edit distance 1 from a token with ≥ 5 occurrences in the same quire).
  - P with slips: recurrence share and clustering like the stationary P controls, high slip share.
  - I: recurrence share above the P controls and clustering ratio < 1, as in TS.
  - C: recurrence share above the P controls, clustering weaker than I (topic-level recurrence), low slip share, as in the language controls.
  - Double-coding requires equal token counts in both transliterations, which removes lines with disputed spaces. This is reported with the result.

## 7. Verdict rules

For each test that passes calibration, each hypothesis receives + (its prediction met and at least one competitor's falsified), 0 (consistent but not discriminating) or − (its falsifier triggered).

**Axis G.**

- **P favoured** if P has at least two more + than each competitor and no − from T3, T5 or T6a.
- **I favoured** under the same rule for I. **Strong evidence for skilled improvisation** additionally requires priming (T6a) and a smooth drift (T5) together with the falsifier of stationary P.
- **C favoured** under the same rule for C.
- Otherwise the result is a **bounded unresolved competition**. The report then lists which variants of each hypothesis are excluded (for example "device P with effect size ≥ w", "stationary P", "naive I", "C without topic drift").

**Axis T.**

- K-reflow is excluded if T1 or T2a triggers its falsifier.
- Adaptation of content to line width is established if T2b gives T(V) < T(GIB) with non-overlapping intervals.
- K-same versus D remains open unless T2c shows an excess of dittography (supports K) or T7a shows token-level insertions (supports K).

**Conditional reconstruction.** Only if P is favoured: infer the smallest rule set (slot automaton, boundary rule, line rule, setting parameters per hand) on quires with odd index in file order. Before evaluating, commit predictions for the even-index quires (line-initial and line-final unit distributions, deviant rate, hapax share, boundary coupling, slack T) with tolerances. Otherwise no generator is reconstructed.

## 8. Mandatory comparisons

| Work | Claim | Where it enters |
|---|---|---|
| Timm & Schinner 2020 | copy-and-modify generation | TS control in T3–T7; T6a and T4b test its priming and vertical-copy signatures |
| Gaskell & Bowern 2022 | human gibberish reproduces low-level Voynich statistics | GIB is the I calibration in T1–T3 and T6; T1, T2b and T3 add line-level and constraint-level comparisons they could not make |
| Stolfi; Zattera 2022 | rigid within-token grammar or slot structure | T3b quantifies rigidity against GIB and languages |
| Rozanova & Temerev 2026 | boundary coupling; units are not letters, words, spaces | T1 and T2 build on the boundary and line findings |
| Greshko 2025 (Naibbe) | a historically executable cipher yields Voynich-like text | NAIB is the C calibration in T1 and T3–T7 |
| Kinnison 2026 | verbose ciphers reproduce the positional entropy collapse | T3c reports the profile for V, GIB, NAIB and languages |

## 9. Novelty claim

The contribution claimed is the hypothesis-separation framework (two axes, co-equal hypotheses, calibrated falsifiers) and any exclusions it produces. The idea that the text could come from a generator is not claimed as new.

## 10. Stopping rule

The battery is T1–T7 as defined here. No further metrics are added after the freeze. Controls run first (Stage A), then the Voynich data (Stage B), then the verdict (Stage C). Stage D (reconstruction) runs only under the condition in Section 7.
