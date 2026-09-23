# E4 preregistration: is the within-page drift lexical or sublexical?

Frozen before the E4 statistics are computed on the Voynich text. Program log: `mechanism/PROGRAM.md`.

## Question

Voynich lines become less similar with line distance on a page as fast as lines of natural-language text do (T6b slope −0.008; German −0.010), and no glyph-level preference walk reproduced this (E3). Drift can live in two places:

- **Lexical:** which words are used. Topic drift in natural language and a slowly changing working vocabulary both produce it.
- **Sublexical:** how words are built. Drifting writing habits or drifting procedural settings change the glyph composition even of unrelated words. So can a cipher that passes plaintext letter frequencies through to glyphs.

## Statistics

For each page and each pair of lines (i, i + k) with k = 2…8 (k = 1 is excluded to keep token-level recency out):

- **Lexical similarity:** cosine similarity of the two lines' token-type count vectors.
- **Sublexical similarity:** from each line, drop every token whose type lies within unit edit distance 2 of some type in the other line. Then take the cosine similarity of the unit-bigram count vectors (boundary symbols included) of the remaining tokens. Line pairs with fewer than 2 remaining tokens on either side are skipped. This removes exact repeats, near variants and inflection-like families, and compares only how unrelated words are built.
- For each measure, ratio(k) = Σ similarity at distance k / Σ (expected similarity under random line order within the page), pooled over pages. The expectation is the page's mean over all line pairs with k ≥ 2.
- **Slopes:** least-squares slope of ratio(k) over k = 2…8. **L** is the lexical slope, **S** the sublexical slope. Bootstrap over pages, 500 replicates, 95% intervals.
- Voynich: ZL3b paragraph text, certain tokens, pages with at least 6 lines. The same rules apply to all corpora.

## Controls and expected signatures

| Control | Class | Expected L | Expected S |
|---|---|---|---|
| LAT, ITA, GER, ENG (V shape) | content drift, natural language | < 0 | ≈ 0 or clearly weaker than L |
| VB-run: verbose cipher with deterministic homophones on running Latin | plaintext, deterministic encoding | < 0 | calibrated |
| NAIB-run: Naibbe on running Latin | plaintext, randomised encoding | calibrated | calibrated |
| GDRIFT: E3 generator with a glyph-preference walk, σ_w = 0.3 | habit or setting drift | weak | < 0 |
| LDRIFT: tokens drawn from the Voynich type distribution of the page's group, with type log-weights following a random walk over lines (step 0.3) | vocabulary drift | < 0 | ≈ 0 |
| MK-sec | no drift | ≈ 0 | ≈ 0 |

**Calibration requirement:**

- At least three of the four languages show L < 0 (interval below 0).
- GDRIFT shows S < 0 (interval below 0).
- LDRIFT shows L < 0 with an S interval that contains 0 or lies above L's interval.

If this fails, E4 is uninformative.

## Decision

- **Sublexical drift beyond content drift:** the upper bound of S(V) lies below the lowest lower bound of S among the four languages. The text drifts in how words are built more strongly than any natural-language text does through topic change.
- **Lexical-type drift:** the S(V) interval overlaps the language range, and L(V) < 0.
- Each verdict is then compared with the two cipher controls. If VB-run or NAIB-run also shows sublexical drift beyond the languages, that verdict does not separate habit or setting drift from a letter-level cipher, and this is stated.

## Mapping to hypotheses

- **Sublexical drift beyond content drift, not reproduced by the cipher controls:** favours production-level drift (S2 habits or S1a drifting settings) over topic-driven plaintext as the source of the drift.
- **Lexical-type drift:** consistent with content drift (S3) and with vocabulary drift (S2). No separation.
- **Sublexical drift also reproduced by a cipher control:** no separation between S2/S1a and that cipher type, which remains a candidate.
