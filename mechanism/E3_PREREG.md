# E3 preregistration: revised generator (margin-driven endings, slow drift, one-off slips), cross-fitted

Frozen before fitting. Program log: `mechanism/PROGRAM.md`. E2 failed with three shared deficits (see PROGRAM.md). E3 adds exactly one component per deficit and re-tests the class.

## Blindness

The Voynich values of the even-bifolio half are known from E2. E3 is therefore cross-fitted:

- **Primary:** fit on even bifolios, test on odd bifolios. For 35 of the 40 phenotype statistics, the odd-half Voynich values have never been computed. Five (T6a near and exact, T7b rate, page MI, consecutive-page excess) were E2 fitting targets.
- **Secondary:** fit on odd bifolios, test on even bifolios (seen in E2).

The phenotype, tolerance rule and pass thresholds are those of E2_PREREG.md.

## Generator HGR2

It keeps E2's HGR (order-3 character automaton per group, restarted per line; quire session mix λ; page tilt σ; recency ρ, τ, e) with these changes.

- **C1, margin-driven line endings.** Training lines end in `$` if margin-bound and `%` if paragraph-final. A generated line uses only the end symbol of its layout line.
  - Length control: when the space left before the target length (the real line's character length) is at most 5 characters, the next token is the final token. Otherwise tokens are generated with end symbols disallowed.
  - The final token is drawn by importance resampling: 20 candidate tokens are sampled from the automaton, and one is chosen with probability proportional to the automaton's probability of the line's end symbol after that candidate.
  - Recency does not apply to final tokens.
- **C2, slow drift.** The page's log-tilt of each glyph performs a random walk from line to line, with step σ_w · N(0, 1).
- **C3, one-off irregularity.**
  - Slips (probability ε per token, one random unit edit) are applied after the token is chosen. The history used by recency stores the intended, unslipped form.
  - Hard pruning threshold m ∈ {1, 2, 3} (1 = no pruning).
  - Choice temperature θ: allowed-transition probabilities are raised to the power 1/θ and renormalised before the tilt.

## Fitting (training half of each direction only)

Ten targets, computed with the frozen code:

- T6a near and exact indices;
- T7b deviant rate and recurrence share (double-coded for the Voynich text);
- page MI;
- consecutive-page excess;
- hapax share;
- type-token ratio;
- T6b slope;
- T3a ρ.

- **Objective:** Σ ((G − V) / max(|V|, f))², with floors f = 0.05 for the T6a indices, 0.02 for T7b recurrence, 0.002 for the T6b slope, and 0 otherwise.
- **Search:** coordinate grid search, 3 passes, in the order m, θ, ε, ρ, τ, e, λ, σ, σ_w.
- **Grids:** m ∈ {1, 2, 3}; θ ∈ {1.0, 1.25, 1.5}; ε ∈ {0, 0.01, 0.02, 0.04, 0.08}; ρ ∈ {0.03, 0.05, 0.08, 0.12}; τ ∈ {4, 8, 16}; e ∈ {0.1, 0.3, 0.6}; λ ∈ {0, 0.25, 0.5}; σ ∈ {0, 0.2, 0.4}; σ_w ∈ {0, 0.05, 0.1, 0.2}.
- Fitted parameters are committed before any test-half phenotype is computed.

## Ablations (primary direction, refitted the same way)

- B1, without C1 (E2 line model);
- B2, without C2 (σ_w = 0);
- B3, without C3 (ε = 0, θ = 1, m = 2 as in E2);
- B0, E2's HGR refitted on the even half.

## Pass rule and interpretation

- **Pass** is judged separately in each direction: full = 40/40, near ≥ 36. The primary direction decides. Seven statistics are fitting targets (T6a × 2, T7b rate, T7b recurrence, page MI, hapax, TTR, T6b, T3a) and are reported separately from the others.
- **HGR2 passes (full or near) in the primary direction:** the class hard grammar with diverse choices, continuous short-range recency on intended forms, slow within-page drift, session reweighting, margin-driven line endings and one-off slips is sufficient for the whole measured phenotype on unseen pages. Its necessary components (by ablation) define the narrowed mechanism class.
- **HGR2 fails:** the remaining failures define what is still missing, and the program continues.
- No statement about meaning or plaintext follows from either outcome.
