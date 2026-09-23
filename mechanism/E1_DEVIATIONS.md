# E1 deviations

## Before the E1 Voynich statistics were computed

1. **Tuning grid extended.** The preregistered grid did not bracket the T6a targets: SET-para jumps from 0.04 to 0.30 between σ = 0.5 and 1.0, and every REC point exceeds the targets (lowest: near 0.186, exact 0.98). The grid was extended with σ ∈ {0.6, 0.7, 0.8} for SET-para and ρ ∈ {0.02, 0.03, 0.05, 0.08}, τ ∈ {8, 15, 30}, e ∈ {0.05, 0.1, 0.2} for REC. The criterion is unchanged: closest to the published Voynich T6a indices (near 0.153, exact 0.217), with near weighted first.
2. **Position-stratified expectation.** The Markov control, which has no settings and no recency, showed a line step of about −0.05 (binary) and +0.03 (graded) in the first calibration run. Its line-position structure extends beyond the first and last tokens, so pairs across a line break pair late positions with early ones. The Voynich text has strong position effects. The expectation of each pair is therefore computed within the page and within position classes: offset from the line start (1 or ≥ 2), offset from the line end (1 or ≥ 2), and whether the line is paragraph-final. Binary: exact mean over pairs of distinct eligible tokens of the page with the same class pair. Graded: mean over up to 25 sampled pairs of that class pair on the page, falling back to the page mean.
3. **Inference through the steps.** With tuned effect sizes, the decay statistics WLD and WPD lack power: the recency control's WLD interval contains 0 in 5 of 5 seeds, failing its calibration requirement, and its WPD interval excludes 0 in 2 of 5. The step statistics separate the controls clearly (SET-line LS about −0.24, SET-para PS about −0.27, REC about 0). The falsifiers are therefore stated on the steps, which is the logically equivalent route given that the page-level recency index of 0.153 is known to be real (T6a):
   - **Settings as sole source, at the magnitude needed for the observed recency index:** falsified for line settings if the lower 95% bound of LS(V) exceeds the largest upper bound of LS across SET-line seeds; for paragraph settings, the same with PS and SET-para.
   - **Recency as sole source:** falsified if the upper 95% bound of LS(V) or PS(V) is below the smallest lower bound across REC seeds.
   - The graded LS is used as a second, more precise line-step statistic with the same rule. WLD and WPD are reported as underpowered secondary statistics.
   - Calibration after the change must show MK-sec with steps near 0, SET-line LS < 0, SET-para PS < 0, and REC steps containing 0.
   - **Thresholds from the stratified calibration (5 seeds each), fixed before the Voynich run:**
     - Line settings falsified if the lower bound of LS(V) > −0.067; graded, if the lower bound of LS_graded(V) > −0.039.
     - Paragraph settings falsified if the lower bound of PS(V) > −0.116.
     - Recency-only falsified if the upper bound of LS(V) < −0.164, of LS_graded(V) < −0.077, or of PS(V) < −0.068.
     - The Markov control has residual mean steps of −0.035 (LS) and −0.02 (PS), with intervals mostly containing 0.
