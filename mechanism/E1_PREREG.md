# E1 preregistration: boundary-conditioned recency

Frozen before any E1 statistic is computed on the Voynich text. The commit that first contains this file is the timestamp.
Program log: `mechanism/PROGRAM.md`. Deviations: `mechanism/E1_DEVIATIONS.md`.

## Question

The battery (REPORT.md) found local dynamics within the page: near and exact repeats are more frequent at short token distances (T6a) and line similarity falls with line distance (T6b). Two classes of mechanism can produce this:

- **Discrete sub-page state.** Settings (a procedure's table or parameter choice) or content (a plaintext topic) that stay fixed within a segment (line or paragraph) and change at its boundary. Tokens are exchangeable within a segment.
- **Continuous recency.** The probability of a form rises when it, or a close variant, was used a few tokens earlier, whether by an explicit copy rule or by human priming. It does not depend on segment boundaries.

The first predicts steps at segment boundaries and no decay with distance inside a segment. The second predicts decay inside a segment, including inside a single line, and no steps.

## Data and definitions

- Voynich: ZL3b paragraph text, certain tokens, as in PREREG.md. Paragraphs end at lines with `<$>`.
- For each page, tokens in running order; d = difference of running indices over all certain tokens of the page.
- **Eligible tokens:** line-internal tokens (not the first or last token of a line) in lines that are not the first line of a paragraph. This removes line-initial, line-final and paragraph-first-line effects.
- **Similarity (primary):** s(a, b) = 1 if the unit edit distance is at most 1 (exact or near repeat), else 0. **Secondary:** graded similarity 1 − ED / max(length).
- **Expectation:** for each page, p = mean of s over all ordered pairs of distinct eligible tokens of that page (exact within-page permutation mean).
- **Ratio** for a class of pairs at distance d: R = Σ s / Σ p over all such pairs, pooled over pages.
- **Pair classes:** same line; adjacent lines of the same paragraph (cross-line); different paragraphs of the same page (cross-paragraph); same paragraph, different lines (same-paragraph).

## Statistics

- **WLD, within-line decay:** mean R(same line, d ∈ {2, 3}) − mean R(same line, d ∈ {5, 6, 7}).
- **LS, line step:** weighted mean over d = 2…7 of R(cross-line, d) − R(same line, d); weights min(n_same(d), n_cross(d)).
- **PS, paragraph step:** weighted mean over d = 8…40 of R(cross-paragraph, d) − R(same paragraph, d); weights as above.
- **WPD, within-paragraph decay (secondary):** mean R(same paragraph, d ∈ {8…15}) − mean R(same paragraph, d ∈ {25…40}).
- Uncertainty: bootstrap over pages, 500 replicates, 95% percentile intervals.

## Predictions

| Mechanism | WLD | LS | PS |
|---|---|---|---|
| Settings per line, no recency | ≈ 0 | < 0 | ≈ 0 |
| Settings or topic per paragraph, no recency | ≈ 0 | ≈ 0 | < 0 |
| Continuous recency in running order | > 0 | ≈ 0 | ≈ 0 |
| Continuous recency plus pauses at paragraph ends (human) | > 0 | ≈ 0 | ≤ 0 |
| Stationary procedure (neither) | ≈ 0 | ≈ 0 | ≈ 0 |

Falsifiers:

- **Sub-page settings as the sole source of the local dynamics** are falsified if WLD(V) is above 0 and above the upper 95% bound of both settings controls.
- **Continuous recency as the sole source** is falsified if LS(V) or PS(V) has its 95% interval below 0 and below the lower 95% bound of the recency control.

## Controls and calibration

All controls use the Voynich page, paragraph and line structure (line lengths, paragraph ends) and draw tokens from the Voynich token distribution of the page's (Currier language, section) group, `base`.

- **SET-line(σ):** for each line, draw weights w_init[u] = exp(σ z) and w_fin[u] = exp(σ z'), with z and z' standard normal, per initial and final unit. Tokens of the line are drawn independently with probability ∝ base(t) · w_init[first unit] · w_fin[last unit].
- **SET-para(σ):** the same with one draw per paragraph.
- **REC(ρ, τ, e):** each token is, with probability ρ, derived from a previous token of the page chosen with weight exp(−(distance − 1) / τ). With probability e it is an exact copy; otherwise it is a random type at unit edit distance 1 from the source, chosen ∝ base. With probability 1 − ρ it is drawn from base. There are no segments.
- **MK-sec:** the order-3 automaton of the battery (neither mechanism).
- **Tuning.** σ for each settings control, and ρ, τ, e for REC, are chosen on a small grid so that the near-repeat decay index of T6a comes closest to the known Voynich value (0.153; exact index 0.217). This uses only the already published T6a numbers.
- **Calibration requirement,** checked with 5 seeds per control:
  - SET-line: LS interval below 0 and WLD interval containing 0.
  - SET-para: PS interval below 0 and WLD interval containing 0.
  - REC: WLD interval above 0, and LS and PS intervals containing 0.
  - A falsifier whose control fails its requirement is not applied.

## Outcome mapping

- **Recency only:** WLD above the settings controls, LS and PS not below the recency control. Continuous recency explains the local dynamics, and sub-page settings are not needed.
- **Settings only:** LS or PS below the recency control, WLD not above the settings controls. A discrete sub-page state explains them.
- **Both:** WLD above the settings controls and a step below the recency control.
- **Neither:** undetermined.

A paragraph step together with within-line decay is also what a human with pauses between paragraphs would produce. That case is reported as "both" and not attributed to procedural settings.

## Red-team notes fixed in advance

- Paragraph-first lines carry more gallows glyphs and line edges have special forms. Both are excluded from all pairs.
- Content (topic) changes at paragraph boundaries predict the same PS as procedural settings. A paragraph step does not separate P from C.
- The recency control counts distance in running order. A human might prime by what is visually close (the line above), but the battery already found no column alignment (T4b).
