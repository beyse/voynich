# E6 preregistration: two-route generator (repertoire retrieval + one-off coinage)

Frozen before fitting. Program log: `mechanism/PROGRAM.md`.

## Question

E2/E3 built every word glyph by glyph and failed on hardness together with diversity, on the non-reuse of rare forms, and on within-page drift. E4/E5 located the drift and the page effects in the familiar forms. E6 asks whether a two-route process reproduces the full phenotype on held-out pages where the single-route generator does not:

1. whole familiar forms retrieved from a drifting repertoire;
2. one-off forms coined from a hard grammar and never reused.

## Generator TR (trained on one half)

Per group (Currier language × section with at least 30 training lines, else language, else all):

- **Repertoire:** training types with count ≥ 2 in the group, base weight = training count.
- **Coinage grammar:** order-3 token-internal character automaton on the group's training tokens, pruned at threshold m (transitions seen fewer than m times dropped unless nothing remains). A coinage is resampled (up to 30 times) until it is not in the repertoire.
- **Boundary table:** K[b][a] = P(first unit a | previous token's last unit b) / P(first unit a), from within-line adjacent pairs.
- **Position factors:**
  - Line-initial: P(first unit | line-initial) / P(first unit); a separate factor for the first token of a paragraph.
  - Final: P(last unit | final token of a margin-bound line) / P(last unit | internal); a separate factor for paragraph-final lines.

**Generation on a layout page:**

- **Log-weights:** the log-weight of repertoire type t on a line is log base_t + q_t + p_t + l_t.
  - q is drawn once per quire and group, σ_q · N(0, 1) per type.
  - p is drawn once per page, σ_p · N(0, 1).
  - l is a random walk over the lines of the page, step s_w.
- **Line length:** tokens are produced until at most 5 characters remain before the layout line's length. The next token is the final token.
- **Each token** is a coinage with probability c; otherwise it is retrieved.
  - **Retrieval** with probability ρ copies a recently retrieved token (weight exp(−(k − 1)/τ), exact with probability e, otherwise a repertoire type at unit edit distance 1). Otherwise a repertoire type is drawn ∝ weight × K[previous last unit][first unit] (inside a line) × the position factors that apply.
  - **Coinage** samples from the coinage grammar, accepting candidates with probability ∝ the same boundary and position factors (rejection, 30 tries).
- **Memory:** only retrieved tokens enter the recency history. Coinages are never reused on purpose.
- **Slips:** probability ε of one random unit edit on the written form, not stored in memory.

## Fitting, test and pass rule

- **As in E3:** the same 10 training targets, the objective with floors, 3 passes of coordinate grid search, cross-fitting (primary: fit even, test odd; secondary: fit odd, test even), the 40-statistic phenotype, and the tolerance and pass rule (full 40, near ≥ 36).
- **Grids:** c ∈ {0.1, 0.2, 0.3, 0.4}; σ_q ∈ {0, 0.2, 0.4}; σ_p ∈ {0, 0.2, 0.4, 0.6}; s_w ∈ {0, 0.05, 0.1, 0.2}; ρ ∈ {0, 0.03, 0.05, 0.08}; τ ∈ {4, 8, 16}; e ∈ {0.1, 0.3, 0.6}; ε ∈ {0, 0.01, 0.02}; m ∈ {1, 2}.
- **Direct comparison:** E3's HGR2 results on the same test halves.
- **Ablations (primary direction, refitted):**
  - D1: no coinage route (c = 0);
  - D2: no repertoire variation (σ_q = σ_p = s_w = 0);
  - D3: no recency (ρ = 0);
  - D4: no boundary table (K = 1).

## Interpretation

- **TR near or full pass in the primary direction, and more passes than HGR2:** the two-route process is sufficient for the whole measured phenotype on held-out pages, and single-route glyph construction is not. Components whose ablation fails define the narrowed class.
- **TR fails:** the failing statistics are reported, and the class stays bounded as after E5.
- **Blindness:** the Voynich values of both halves are known from E2/E3. Only the parameters are fitted blind to the test half.
- The result concerns the production process. It does not decide between an explicit rule set, a writer's habits and a plaintext carried by the free choices.
