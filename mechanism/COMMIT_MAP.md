# Commit map

Before the repository was published (23 September 2026), the author e-mail address in every commit was replaced by a GitHub noreply address (`git filter-branch --env-filter`), and commit hashes quoted in commit messages were updated to match. Nothing else was changed:

- **File contents:** every commit has the same tree hash as before the rewrite.
- **Timestamps:** author and committer dates are unchanged.

Commit hashes changed, because a commit hash covers its author line. Preregistration documents written before the rewrite may quote old hashes; this table maps them to the published commits. The tree hash is the same in both columns.

| Old commit | Published commit | Tree | Author date | Subject |
|---|---|---|---|---|
| `79abe49` | `afccbcd` | `9de63c1` | 2026-09-23T03:45:50+02:00 | Voynich information-theoretic analysis and Cryptologia manuscript |
| `28ae510` | `b67bb47` | `7228193` | 2026-09-23T04:09:22+02:00 | Preregister production-mechanism tests (freeze before Voynich outcomes) |
| `2403034` | `f282965` | `480f814` | 2026-09-23T04:25:23+02:00 | Mechanism battery: implementation and Stage A (controls only) |
| `123ee76` | `650abbd` | `3ec4c43` | 2026-09-23T04:32:16+02:00 | Mechanism battery: Stage B (Voynich), post hoc checks and report |
| `b5dcb79` | `889e908` | `5dbfdad` | 2026-09-23T04:41:04+02:00 | E1 preregistration: boundary-conditioned recency (frozen before Voynich outcome) |
| `ea64b09` | `c507641` | `a97094d` | 2026-09-23T04:45:59+02:00 | E1: stratified statistics, tuning and control calibration (before Voynich run) |
| `24b79a6` | `889c0b6` | `54eabed` | 2026-09-23T04:47:51+02:00 | E1 result: local dynamics are continuous, sub-page settings excluded |
| `6b109a4` | `0b40d28` | `f3b89c1` | 2026-09-23T04:49:43+02:00 | E2 preregistration: explicit generator, blind test on held-out bifolios |
| `d00b0c4` | `9f35f1b` | `290555b` | 2026-09-23T04:52:24+02:00 | E2: generator code and parameters fitted on training bifolios (frozen before test comparison) |
| `9ca51a5` | `0bc64e4` | `56ce3fc` | 2026-09-23T04:54:35+02:00 | E2 result: 32/40, class lacks margin-driven endings, slow drift, one-off forms |
| `0f50303` | `ca203c4` | `a9b4dcb` | 2026-09-23T04:55:35+02:00 | E3 preregistration: revised generator, cross-fitted (primary: fit even, test odd) |
| `00efbfd` | `9e9e982` | `a508f07` | 2026-09-23T05:03:28+02:00 | E3: generator code and cross-fitted parameters (frozen before test phenotype) |
| `e46cd8a` | `626259e` | `d985102` | 2026-09-23T05:06:09+02:00 | E3 result: 33/40; margin-driven endings necessary; drift and rare-form reuse unexplained |
| `ce8bb45` | `a647269` | `43b854a` | 2026-09-23T05:07:04+02:00 | E4 preregistration: lexical vs sublexical within-page drift |
| `d37f5f2` | `5146f04` | `477a9a5` | 2026-09-23T05:08:17+02:00 | E4 controls (calibration passes) before Voynich run |
| `338801b` | `b822af6` | `e79a936` | 2026-09-23T05:09:23+02:00 | E4 result: lexical-type drift, no content/habit separation; tested ciphers erase sublexical drift |
| `f3bb895` | `bc6c840` | `5284699` | 2026-09-23T05:10:02+02:00 | E5 preregistration: frequency-resolved burstiness |
| `4dbe022` | `f7c6940` | `2f5bf51` | 2026-09-23T05:11:17+02:00 | E5 controls with quire jackknife (calibration passes) before Voynich run |
| `d8d4270` | `b5a31d3` | `03c3b53` | 2026-09-23T05:12:21+02:00 | E5 result: undetermined gradient; page clustering across all frequency bands |
| `537e93b` | `aadd173` | `b171a0f` | 2026-09-23T05:13:02+02:00 | E6 preregistration: two-route generator |
| `e872229` | `38460c6` | `dac0941` | 2026-09-23T05:18:48+02:00 | E6: two-route generator code and cross-fitted parameters (frozen before test) |
| `cd0edfa` | `d12dade` | `eac2cfa` | 2026-09-23T05:20:54+02:00 | E6 result: two-route generator fails (22/40); boundary rule necessary |
| `6b6e555` | `7b002ad` | `cec4564` | 2026-09-23T05:21:32+02:00 | E7 preregistration: plaintext in free choices (mimic function) |
| `ed074fa` | `23b3870` | `ef9a0ec` | 2026-09-23T05:24:19+02:00 | E7 result: plaintext carried in free choices is recoverable and statistically invisible |
| `705447b` | `25115fd` | `97bf938` | 2026-09-23T05:25:10+02:00 | Synthesis: mechanism class narrowed; executor question shown undecidable from text |
| `90d57b7` | `8c2e4da` | `50a3e14` | 2026-09-23T05:25:20+02:00 | Synthesis: correct E7 reading (mimic function, not compression, hides the message) |
| `922722b` | `355263d` | `ac02435` | 2026-09-23T10:44:22+02:00 | Red-team checks before writing paper 2 (post hoc robustness) |
| `ccd0da4` | `1ed984d` | `77f522b` | 2026-09-23T10:57:31+02:00 | Paper 2: constrained, not identifiable (mechanism program write-up) |
| `a779e97` | `92c7ce2` | `28b5fd6` | 2026-09-23T10:57:42+02:00 | Paper 2: rebuild referencing source commit 1ed984d |
| `1d082c2` | `6a87fe1` | `cc133c2` | 2026-09-23T11:50:39+02:00 | Merge both manuscripts into one self-contained paper |
| `e923eef` | `69df08b` | `c1d94ed` | 2026-09-23T11:50:40+02:00 | Paper: rebuild referencing source commit 6a87fe1 |
