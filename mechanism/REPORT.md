# Production mechanism of the Voynich text: result of the preregistered battery

Preregistration: `mechanism/PREREG.md`, frozen in commit `b67bb47` before any test was run on the Voynich text.
Deviations: `mechanism/DEVIATIONS.md` (entries 1–7, all made before Stage B; entry 6 discloses one early computation of the T1 terms on the Voynich text).
Stage A (controls only) was committed in `f282965` before Stage B (Voynich) was run.
Numbers: `results/mechanism/stageA.json`, `stageB.json`, `posthoc.json`; tables: `python3 -m mechanism.summarize AB`.

## 1. Verdict

**Generation: a bounded, unresolved competition.** No hypothesis meets the preregistered criterion for being favoured. The fixed-procedure hypothesis collects the most support (four tests in its favour), but it is vetoed by the recency test T6a. The text shows local dynamics within the page that no stationary table, automaton or device produces. Improvisation is supported by that test and contradicted by the drift shape and by the behaviour of deviant forms. The tested plaintext-driven variants each fail at least one test.

Several variants are excluded by calibrated tests.

| Excluded variant | Test | Evidence |
|---|---|---|
| Naive improvisation of the kind sampled by Gaskell & Bowern (2022) | T3a, T3b | The Voynich word grammar is harder (zero replication 0.040 vs 0.093) and more rigid (slot consistency 0.868 vs 0.671) than the pooled gibberish sample; natural languages lie with the gibberish (0.075–0.104; 0.66–0.70) |
| Stationary procedures: tables, automata, grilles or devices whose parameters are constant within a page | T6a | Near-repeat decay index 0.153 (95% CI 0.112–0.198) against a highest 99th percentile of 0.116 among six stationary controls |
| Periodic devices with a column or row effect of mixing weight 0.2 or more | T4 | No peak in any periodicity profile; the device control is detected in 10 of 10 seeds at that weight |
| Improvisation with smooth drift across pages | T5 | The step model predicts page distances better than the smooth model (score 0.76; calibration: smooth 1.66, step 0.28) |
| Improvisation that propagates its innovations, as in the copy-and-modify model | T7b | Deviant forms recur in 1.1% of cases (1.7% without double coding), against 32% for the copy-and-modify control |
| Plaintext-driven procedures that preserve plaintext word identity | T7b | Rare forms do not recur (1.1–1.7% vs 5.5–16% in the language controls) and look like slips (33% vs 1.5–10%) |
| The Naibbe cipher as published (random table choice by cards) | T6a | No local recency (index 0.01 and −0.02) |

What survives is a narrow profile: a hard, slot-like word grammar; local recency of ordinary forms within the page; stepwise changes between production units, with the largest jumps at quire boundaries; one-off, slip-like deviations; line-aware endings; and no periodicity. Three concrete mechanism classes remain compatible with it:

- a procedure with a hard slot grammar plus state below the page level, meaning an explicit recency or copy rule, or settings that change every paragraph or line;
- a practised improviser with an internalised hard grammar, who reuses recent forms but does not propagate new ones, with changes between writing sessions;
- a plaintext-driven procedure with rigid tables whose free choices depend on recent output.

The battery cannot separate these three. Following the preregistered rule, no generator was reconstructed.

**Transmission.**

- **Copying with re-lining (K-reflow) is excluded.** Line-final tokens of lines that end at the margin have a different final-glyph distribution from line-internal tokens of the same length (T2a: excess JSD 0.085, p = 0.005; Takahashi transliteration 0.094). Greedily re-lined text shows no such effect.
- **No copying signature was found.** There is no dittography at line breaks (T2c ratio 0.80, no repeated bigram), and none of the 24 annotated corrections is a word-level insertion or deletion (T7a).
- **The preregistered criterion for content adaptation to line width is met, with a caveat.** The slack ratio is lower than for online-written gibberish (T2b: 2.09, CI 1.88–2.32, against 3.90, CI 3.11–4.81). It is still above 1, so Voynich lines are not packed more tightly than greedy wrapping would pack them, and glyph-count width is a noisier proxy for handwritten Latin letters than for Voynich glyphs. The result means "more regular line fill than naive online writers", not proof of word choice driven by space.
- **Direct composition and copying with identical line breaks remain indistinguishable,** as stated in the preregistration.

**Claims policy.** Nothing here shows that the text is meaningless or free of plaintext. The statistical sufficiency of a model is not the historical identification of a mechanism, and no mechanism was identified.

## 2. Calibration (Stage A)

| Test | Requirement | Outcome |
|---|---|---|
| T1 | Greedily wrapped Latin R ≥ 0.5 | 2.44 (SE 2.75): met, but the statistic is very noisy for letter corpora with weak boundary coupling |
| T2a | Wrapped Latin shows no final-form effect | excess 0.000, p = 0.46: met |
| T2b | Wrapped Latin T within 0.9–1.1 | 0.994 (0.943–1.034): met |
| T4 | Power against the device control | w = 0.1: 2/10 (T4a), 0/10 (T4b), 0/10 (T4c); w = 0.2: 10/10, 5/10, 10/10; w = 0.4: 10/10 in all three. Only false-positive-looking peak: Dante at line distance 2, which is the terza rima rhyme scheme |
| T5 | Smooth drift S > 1, step drift S < 1 | 1.66 and 0.28: met |
| T6a | Stationary controls near 0 | MK-sec 0.022, MK-page −0.022, RUGG −0.059, DEV 0.009 / −0.003 / 0.051: met |

Two preregistered predictions were contradicted by their own controls and are treated accordingly.

- **T6b** predicted no within-page line drift for plaintext-driven text. All four language controls drift within the page (slopes −0.003 to −0.012) because topics shift. T6b is therefore informative only against stationary procedures, not between improvisation and plaintext.
- **T7b** predicted language-like recurrence of rare forms for every plaintext-driven variant. The Naibbe control recurs as rarely as the procedures (2.6–3.7%). T7b therefore excludes only plaintext-driven variants that preserve word identity.

The human gibberish itself did not show significant priming (T6a near index 0.071, CI −0.099 to 0.235) or within-page drift (slope −0.002, CI −0.006 to 0.002). Its documents are short, about 260 words each. The improvisation predictions of T6 are therefore calibrated mainly by the copy-and-modify model, not by human data.

## 3. Results (Stage B) against predictions

| Test | Voynich (ZL3b) | Takahashi (IT2a) | Key controls | Reading |
|---|---|---|---|---|
| T1 break / within coupling | R = 0.22 (SE 0.26); 0.023 vs 0.107 bit | 0.18 (0.18) | GIB 1.10 (0.32); MK-sec −0.14; TS 1.10 | Below 0.25, interval not below 0.5: K-reflow falsifier not triggered. Gibberish writers show no line reset |
| T2a final form, margin-bound | 0.085, p = 0.005 | 0.094, p = 0.005 | GIB 0.003 (p 0.02); wrapped Latin 0.000 | K-reflow falsified |
| T2a final form, paragraph-final | 0.039, p = 0.005 | – | GIB 0.034 (p 0.01) | Line-aware endings in both line types |
| T2b slack | 2.09 (1.88–2.32) | – | GIB 3.90 (3.11–4.81); wrapped Latin 0.99 | Preregistered adaptation criterion met (caveat in Section 1) |
| T2c dittography | ratio 0.80, p = 0.77; 0 bigrams | – | TS 1.38, p = 0.01 | No copying signature |
| T3a zero replication | 0.040 (0.038–0.043) | 0.039 | GIB 0.093 (0.077–0.115); languages 0.075–0.104; NAIB 0.037–0.039; MK 0.052 | Hard zeros; naive improvisation falsified |
| T3b slot consistency / monotone share | 0.868 / 0.554 | 0.885 / 0.591 | GIB 0.671 / 0.24; languages 0.66–0.70 / 0.12–0.35; NAIB 0.86 / 0.61 | Rigid slot order; naive improvisation falsified |
| T3c final-position entropy (share) | 0.63 | – | NAIB 0.65; MK 0.67; languages 0.78–0.91; GIB 0.98 | Collapse reproduced by cipher and automata, not by gibberish or languages |
| T4 periodicity | no peaks; column z 1.0, 1.7, −0.5 | no peaks | device detected from w = 0.2 | Device variants with w ≥ 0.2 excluded |
| T5 drift shape | S = 0.76; hands 1.07 / 0.59 / 0.68 | 0.82 | smooth 1.66; step 0.28; MK-sec 0.62 | Step-like; largest jumps at quire or section boundaries (hands 2 and 3: all top-decile jumps) |
| T6a recency, near repeats | 0.153 (0.112–0.198) | 0.143 | stationary P max 99th pct 0.116; TS 0.34; ENG 0.10; NAIB ≈ 0 | Local dynamics present; stationary procedures falsified |
| T6a recency, exact repeats | 0.217 (0.131–0.303) | 0.211 | TS 0.56; GER 0.42; MK 0.02–0.05 | As above |
| T6b within-page line drift | slope −0.0083 (−0.0096 to −0.0073) | −0.0082 | MK ≈ 0; languages −0.003 to −0.012; TS −0.062 | Against stationary procedures only |
| T6c hands 1 / 2 / 3 | near index 0.160 / 0.169 / 0.141; slopes −0.010 / −0.009 / −0.007 | – | – | The same local dynamics in every main hand |
| T7a annotated corrections | 24 events, all glyph-level; 19 of 22 scored tokens below the median probability (p = 0.0009) | – | – | Position test uninformative (see below); no word-level insertions |
| T7b deviant tokens (double-coded) | rate 14.7‰; recurrence 1.1%; slip share 33% | recurrence 1.8%; slip 29% | TS 32% / 33%; MK 7.7–9.2% / 29–30%; languages 5.5–16% / 1.5–10%; NAIB 2.6–3.7% / 17–21% | One-off, slip-like deviations |

**T7a position test.** The preregistered position analysis found 20 of 24 comments after the last glyph of a token (binomial p < 10⁻¹⁰), which formally meets the "extreme pattern" rule. Inspection after unblinding shows that the ZL transliteration places its comment after the affected word (for example `otey<!corr?>`), so the position of the comment identifies the word, not the glyph. The test is reported as uninformative. The corrected words are atypical, but that is expected both for words altered by a correction and for words whose overwritten reading merges two versions.

## 4. Scoring under the preregistered rule

\+ = prediction met and at least one competitor falsified; 0 = consistent but not discriminating or uninformative; − = falsifier triggered.

| Test | P, fixed procedure | I, skilled improvisation | C, plaintext-driven |
|---|---|---|---|
| T3a hard zeros | + | 0 (naive I −) | + (table-based) |
| T3b rigidity | + | 0 (naive I −) | + (table-based) |
| T4 periodicity | 0 (device P −) | 0 | 0 |
| T5 drift shape | + | − | 0 (quire and section boundaries not separated by the statistic) |
| T6a recency | − (stationary P) | + | 0 |
| T6b line drift | − (stationary P) | 0 | 0 |
| T7b deviants | + | − | − (word-preserving C only) |
| **Total** | **4 +, 2 −** | **1 +, 2 −** | **2 +, 1 −** |

P has at least two more + than each competitor, but it carries a − from T6a, and the rule requires no − from T3, T5 or T6a. I and C do not reach the margin. The result is therefore the bounded unresolved competition of Section 1.

## 5. Post hoc checks (not preregistered; re-runs of preregistered statistics)

- **Takahashi transliteration.** Every verdict-driving result replicates (table in Section 3).
- **Deviants without double coding.** Recurrence is 1.7%, the clustering ratio 0.97 and the slip share 27%. The primary clustering ratio of 0.028 rests on three recurring types and is not interpreted.
- **Drift jumps by boundary type.** Few boundaries exist per hand, so this is descriptive only.
  - Hand 2: mean consecutive excess 0.080 at quire-only changes (n = 3), 0.106 at quire-and-section changes (n = 2), 0.028 at section-only changes (n = 3) and 0.030 elsewhere (n = 26).
  - Hand 1: 0.169 at the single section-only change, 0.082–0.084 at quire changes, 0.058 elsewhere.
  - Hand 3: 0.105 at quire-and-section changes (n = 2), 0.035 elsewhere.
  - Within-quire, within-section neighbours still differ far more than in the section automaton (0.03–0.06 against 0.004–0.011), so there is page-level variation in addition to the steps.
  - In hand 2 the steps follow the quire, a physical production unit, and not the change of illustration section, which weakly disfavours topic-driven variation.

## 6. Mandatory comparisons

- **Timm & Schinner (2020).** The copy-and-modify control reproduces the hard grammar (0.027) and produces local recency, but at twice the Voynich strength (0.34 against 0.153). It also produces strong copying across the line break (T2c 1.38; column z = 16) and propagating innovations (recurrence 32%). The Voynich text shows none of these three. A copy rule restricted to existing grammatical forms, without vertical copying, would remain compatible.
- **Gaskell & Bowern (2022).** Their gibberish reproduces many low-level statistics, as they report. On the constraint level it does not: it is softer, less rigid, shows no final-position entropy collapse and no line reset. Their caveat about short samples applies. Long-practised improvisation is the one competitor for which no data exist, and it is the main reason the verdict stays open.
- **Stolfi; Zattera (2022).** T3b quantifies the slot structure they describe. With the best single ordering of units, 86.8% of ordered unit pairs inside Voynich tokens are consistent and 55% of tokens are fully monotone, against 66–70% and 12–35% for natural languages. This rigidity is the strongest single argument for a table-like word grammar, but a practised writer could internalise it.
- **Rozanova & Temerev (2026).** Boundary coupling inside lines is confirmed (0.107–0.171 bit depending on estimator). The coupling across line breaks is small but, with the page-conditional estimator, not clearly zero (0.023 bit, ratio 0.18–0.22 with wide intervals). It stays well below that of gibberish writers.
- **Greshko (2025), Naibbe.** The Naibbe cipher matches the Voynich text on hard zeros, rigidity and the final-position entropy collapse. It fails on local recency. A Naibbe-type system whose table choice depends on recent output instead of cards is not excluded.
- **Kinnison (2026).** The final-position entropy collapse (Voynich 0.63) is reproduced by the Naibbe cipher (0.65) and the automata (0.67), and by none of the natural languages (0.78–0.91) or the gibberish (0.98). As Kinnison reports, it discriminates against natural-language text and naive gibberish, not between procedure and cipher.

## 7. Limitations

- **Skilled improvisation lacks a calibration corpus.** The human gibberish documents are short, written in the Latin alphabet by modern writers, and did not show the dynamics the improvisation hypothesis predicts. That hypothesis is calibrated mainly by a formal model.
- **Some procedure variants were not tested.** No control had settings changing below the page level, or an explicit recency rule inside a hard grammar. These variants are exactly the ones the result leaves open.
- **T1 is imprecise.** The page-conditional estimator is the only one of three that is valid under writer heterogeneity, but it is noisy on short pages.
- **T2b uses glyph counts, not physical widths.** Measuring line fill on the images needs higher-resolution scans than the local facsimile (about 1100 × 1500 pixels per page).
- **The correction data are thin.** They rest on 24 annotations made for reading purposes, not for codicology.
- **Page order is the current binding order,** which departs from the writing order in places.

## 8. What would resolve the remaining competition

Each item below is a candidate for a new preregistration, not part of this battery.

1. **Recency across paragraph boundaries.** Token-level recency should decay smoothly across a paragraph break. Paragraph-level settings would produce a step there. This separates "procedure with sub-page settings" from both "recency rule" and "improvisation".
2. **A practised-improvisation experiment.** Volunteers write many pages in an invented script over several sessions. If hard zeros and slot rigidity at the Voynich level emerge with practice, rigidity stops favouring procedures.
3. **An execution experiment.** Volunteers follow a small written rule set: a slot table, a recency rule and a per-session setting. Their output shows whether it reproduces the full profile, including slip-like deviations.
4. **Physical measurements on high-resolution images.** Glyph compression near the right margin, and erasures under multispectral imaging, coded blind to the model predictions.
