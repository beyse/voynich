# Revision analyses: pre-specified plan

Written on 23 September 2026 in response to a review of the manuscript, and committed before any of the outcomes below was computed. Four analyses are covered. Their status differs:

- **R1** is a post hoc robustness check prompted by the review. It is labelled as such.
- **R2–R4** have their criteria fixed here, before computation.

What has been seen at the time of writing:

- **Greshko's data.** Only the token counts (33,750 ciphertext tokens after space removal, 34,764 before), the first lines of the files, and the fact that the published table file equals `data/naibbe/naibbe_tables.csv` after normalising line endings and the byte-order mark.
- **Voynich values.** All Voynich values of the 40-statistic phenotype are known from the earlier program.

## R1. Human gibberish per writer (T3a, T3b) — post hoc

**Question.** Does the rigidity contrast (C1) hold for individual writers, not only for their mean?

**Method.**
- **Unit.** T3a and T3b are already computed per document: each gibberish document with at least 150 tokens is one unit, 36 of 38. Here the per-document values are reported individually.
- **Size-matched reference.** For each document with n tokens, contiguous windows of the Voynich paragraph text within one hand are cut to n tokens, at least 50 windows per document where the text allows. T3a and T3b are computed on each window.
- **Percentile.** For each writer we report the percentile of their value within the size-matched Voynich distribution.

**Reading, fixed before computation (T3b slot consistency).**
- **Supported at writer level:** at least 90% of writers lie below the 5th percentile of their size-matched Voynich windows.
- **Weakened:** fewer than 75% do.
- In between, the result is reported as partial.
- T3a is reported descriptively, because per-document zero replication is noisy at these sizes.

## R2. Validation of the Naibbe reimplementation against the author's output

**Material.** From `github.com/greshko/naibbe-cipher`, commit `f2675ec5dd275268bc64dd48ea64fc0e0e9827a2` (retrieved 23 September 2026). These are data files only; the author's code is not executed.
- `encrypted/nathist_output_ciphertext.txt`: the author's ciphertext before random space removal.
- `encrypted/nathist_output_ciphertext_respaced.txt`: the same after space removal.
- `respaced_plaintext/nathist_pre_encryption_respaced_plaintext.txt`: the tokenised plaintext, Pliny, *Natural History* book 16.
- `references/naibbe_tables.csv`.

The files are kept in `data/ref/naibbe_greshko/` (not redistributed) and are fetched by `mechanism/revision.py fetch`.

**R2a. Tokenisation.**
- Share of one-letter tokens in the author's tokenised plaintext, against the 17/36 of our implementation.
- **Criterion:** the author's share lies within ±0.02 of 17/36.

**R2b. Mapping.**
- Align the author's ciphertext (before space removal) token by token with the tokenised plaintext.
- **Criterion:** every ciphertext token is a valid table output for its plaintext token (unigram string for a one-letter token, prefix + suffix for a two-letter token) under at least one table choice. At least 99% of tokens must pass, allowing for edge effects in the files.

**R2c. Table usage.**
- The share of each table, counted over tokens whose table is unambiguous.
- **Criterion:** each share within ±0.03 of the deck proportions 20/52, 8/52, 8/52, 8/52, 4/52, 4/52.

**R2d. Statistics at identical tokenisation.**
- Encipher the author's tokenised plaintext with our table and deck procedure, 5 seeds, with 3% space removal.
- Compute on both, at the author's token count: hapax share, type count, mean token length, glyph h2, boundary MI, token MI, positional entropy T3c (final, initial).
- **Criterion:** the author's value lies within 2 SD + 1% of our seed mean, the tolerance rule of the paper.
- **Outcome:** the reimplementation counts as validated if R2a–R2c pass and at least 6 of the 8 statistics of R2d pass. Any failure is reported, with its consequence for the claims.

## R3. The Naibbe exclusion on the author's own output

- **Input.** The author's final ciphertext, after space removal, is cut as running text into the Voynich page and line shape, like our NAIB-run control. Pages beyond the available text are dropped.
- **Statistics.** On this corpus we compute the statistics that carry the Naibbe exclusion in the paper:
  - T6a near and exact recency;
  - E4 lexical and sublexical drift (L, S);
  - boundary MI, hapax share and page MI (profile);
  - T7b recurrence share.
- **E5.** E5 G and B are computed descriptively. E5 was undetermined for the Voynich text and is no longer used as decisive evidence.
- **Criterion.** "The Naibbe cipher as published" stays in the exclusion table if, for T6a near, boundary MI and page MI, the author's output lies on the same side of the Voynich value as our reimplementation and outside the Voynich 95% interval. The table uses T6a, E4 and the profile statistics. If any of these statistics fails the criterion, the claim is narrowed to the statistics that pass.

## R4. E7 with more runs, and E8: a message carried by the richer generator

### R4a. E7 with 20 runs per condition

- **Process and code.** The same process and code as E7 (`mechanism/e7.py`).
- **Random driving.** PRNG seeds 101–120.
- **Compressed plaintexts.** 20 runs: lzma-compressed Latin, Italian, German and English, each at 5 bit offsets:
  - Latin: 0, 100k, 200k, 300k, 400k;
  - German: 0, 60k, 120k, 180k, 240k;
  - Italian and English: 0, 100k, 200k, 300k, 400k.
- **Raw plaintext bits.** The same 20 offsets, as a secondary condition.

**Primary test.**
- For each of the 39 continuous statistics, a Welch t-test between random driving and compressed plaintext, with Holm correction at α = 0.05. For T4, Fisher's exact test on the peak counts.
- **Prediction:** no statistic differs after correction.
- **Secondary:** the tolerance rule of the paper, and the number of unadjusted p < 0.05 compared with the about 2 expected by chance.
- **Also required:** exact recovery in every message-driven run.

### R4b. E8, a message driven through the E3 generator (HGR2)

**Process.** HGR2 with the primary fitted parameters of E3 (fit on even bifolios), with transition counts from the whole manuscript, generated on the whole manuscript layout.

**Which choices carry the message.** Only choices the receiver can observe carry message bits. All other randomness comes from a key PRNG shared by sender and receiver, which does not change the process's distribution:

| Choice | Source |
|---|---|
| each glyph of a token sampled from the grammar (including the token-ending space) | message |
| which recent form is reused, as one categorical over the output strings of the recency step (source and neighbour steps combined) | message |
| which of the 20 final-word candidates ends the line (identical candidates merged) | message |
| route (recency or grammar), and exact or near reuse | key |
| page tilt and line-to-line random walk | key |
| candidate generation for the final word | key |
| whether a slip occurs; for slipped tokens, the intended token and the slip | key |

**Probabilities.** Floating-point choice probabilities are quantised deterministically to integer counts (resolution 2⁻¹⁶, minimum count 1), identically for sender and receiver.

**Runs.**
- **Baseline:** 20 runs with the message choices also taken from a PRNG. Seeds 201–220 for the message choices and 301–320 for the key.
- **Message-driven:** 20 runs with the lzma plaintexts and offsets of R4a, key seeds 301–320.

**Criteria.**
- Exact recovery in every run.
- The same primary and secondary tests as R4a, with the same prediction.
- The capacity (bits per glyph and per manuscript) is reported.

If either prediction fails, the corresponding statement of the paper is narrowed, not dropped silently.
