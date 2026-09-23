# E2 preregistration: an explicit generator of the surviving class, tested blind

Frozen before the generator is fitted and before any held-out comparison. Program log: `mechanism/PROGRAM.md`.

## Question

After E1, the surviving generation mechanisms share one structure: a hard word grammar, continuous recency across line breaks, state that persists over a production unit, slip-like deviations, and line-bound glyph transitions. E2 asks whether an explicit generator with exactly these components reproduces the full frozen phenotype on held-out manuscript pages, and which components are necessary.

A pass shows sufficiency of a concrete member of the class, not historical identity. It does not decide between S1a (explicit rule), S2 (human habit) and S3 (plaintext-driven choices), which share this structure. That question is E3.

## Split

- Every page header has a bifolio index `$B` within its quire. **Training:** pages with odd `$B`. **Test:** pages with even `$B`. Conjugate leaves stay together. Both halves contain every quire with pages in it and hands 1–3; hands 4 and 5 occur only in training.
- Training: 114 pages, about 17,500 tokens. Test: 93 pages, about 14,900 tokens.
- The generator sees only the training text. For test pages it uses layout and metadata: line lengths in characters, paragraph ends, quire, section, Currier language, hand. It never sees test tokens.

## Generator HGR (hard grammar + recency)

- **Grammar.** An order-3 character automaton over EVA characters, with the space as a character and line start/end symbols, restarted at each line. It uses the counts of the training lines of the page's group (Currier language × section with at least 30 training lines, else language, else all). **Hard pruning:** within each context, transitions seen only once in training are removed, unless nothing else remains.
- **Session state.** For a page in quire q, each next-character distribution is λ times the quire-specific training distribution plus (1 − λ) times the group distribution, for contexts seen in the quire's training lines. On top, a page-level tilt: for each character, a factor exp(σ z) with z standard normal, drawn once per page and applied to all transition weights.
- **Recency.** At each token start, with probability ρ the token is taken from the page's history (running order across lines). The source is chosen with weight exp(−(k − 1)/τ) for a token k positions back. It is copied exactly with probability e; otherwise it is replaced by a training type at unit edit distance 1, chosen ∝ training frequency (the source itself if none exists). The characters then enter the automaton context as if generated.
- **Slips.** Each token, generated or copied, receives with probability ε one random unit edit: substitution, insertion or deletion with equal probability, with units drawn from the training unit frequencies.
- **Line lengths.** The end symbol is suppressed until 60% of the target character length; generation stops at 140%.

## Fitting (training half only)

Six parameters (λ, σ, ρ, τ, e, ε) are chosen by coordinate grid search, two passes, to minimise the summed squared relative deviation from these training targets, all computed with the frozen code on the training half:

- T6a near and exact recency indices (ρ, τ, e);
- T7b deviant rate per 1,000 double-coded tokens (ε);
- page MI from the earlier battery, and the T5 mean consecutive-page excess distance for hands with at least 10 training pages of at least 100 tokens (λ, σ).

Grids: λ ∈ {0, 0.25, 0.5, 0.75}; σ ∈ {0, 0.1, 0.2, 0.4}; ρ ∈ {0, 0.03, 0.05, 0.08, 0.12}; τ ∈ {4, 8, 16}; e ∈ {0.1, 0.3, 0.6}; ε ∈ {0, 0.005, 0.01, 0.02, 0.04}. The fitted parameters are committed before the test comparison.

## Phenotype (40 statistics, computed on the test half)

- **Earlier battery (18):** hapax share, type-token ratio, Zipf slope, mean token length, edge MI, token MI, distance-2 MI, break MI, break edge MI, adjacent edge MI at equal n, space gain, lexicon real, lexicon synthetic, h2, h3, h4, lzma bits per character, page MI.
- **Mechanism battery (18):** T1 R_LB; T2a margin excess; T2a paragraph excess; T2b T (section S pages); T2c ratio; T3a ρ; T3b consistency; T3b monotone share; T3c e1; T3c s1; T4 any peak (binary); T5 S; T6a near index; T6a exact index; T6b slope; T7b rate; T7b recurrence share; T7b slip share.
- **E1 (4):** graded line step, paragraph step, graded within-line decay, within-paragraph decay.
- Voynich test values use the preregistered definitions: T7b double-coded, E1 stratified. Generated corpora carry the test layout (paragraph ends, eligibility flags).

## Tolerance and pass rule

- **SE of the Voynich value:** leave-one-quire-out jackknife over the test quires. **SD of the generator:** across 3 seeds.
- A statistic passes if |G − V| ≤ 2 √(SE_V² + SD_G²) + 0.01 |V|. T4 passes if at most one of the three seeds shows a peak (the Voynich text shows none).
- **Full pass:** all 40 statistics pass. **Near pass:** at least 36. Anything else is reported as a failure with the failing statistics listed.

## Ablations (3 seeds each, same fitting and tolerance)

- A1, no recency (ρ = 0; the other parameters refitted);
- A2, no hard pruning and no slips (ε = 0, all transitions kept);
- A3, no session state (λ = 0, σ = 0);
- A4, no hard pruning, with slips;
- A0, baseline: the order-3 group automaton alone (A1 + A2 + A3).

A component is **necessary** if removing it produces at least one failing statistic that passes in the full model. A component is **dispensable** if its ablation passes everything the full model passes.

## Interpretation fixed in advance

- **Full or near pass:** the class "hard grammar + continuous recency + persistent state + slips + line-bound transitions" is sufficient for everything measured on held-out pages. Its necessary components define the narrowed mechanism class.
- **Failure:** the failing statistics show what the class is missing. The class is revised in a new preregistration, not by tuning against the test half.
- In either case, nothing about plaintext or meaning follows.

## Red-team notes fixed in advance

- The full-manuscript values of most phenotype statistics are known to me. The test half protects against fitting to the evaluated pages, not against design knowledge.
- Several statistics are correlated (the MI family, the entropy family). A pass counts each separately and should not be read as 40 independent confirmations.
- Line lengths of test pages are given to the generator. Statistics driven purely by line length are therefore weak tests.
