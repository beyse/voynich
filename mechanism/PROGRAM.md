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
| E2 | Does an explicit hard-grammar + recency + session + slip generator reproduce the full phenotype on held-out bifolios, and which components are necessary? | E2_PREREG.md | preregistered | – |
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
