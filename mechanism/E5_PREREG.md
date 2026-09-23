# E5 preregistration: frequency-resolved burstiness

Frozen before any E5 statistic is computed on the Voynich text. Program log: `mechanism/PROGRAM.md`.

## Question

Content drift (topic) makes rare content words the burstiest: a name or technical term appears several times on the page about its subject and nowhere else. A writer who drifts through a repertoire of familiar forms and coins one-off forms produces clustering among the familiar forms, but not among the rare ones. Does the Voynich text show content-like clustering of its rare types?

## Statistic

- **Types and bands:** types are assigned to frequency bands by corpus count: R (2–4), M (5–19), F (20–99), VF (≥ 100).
- **Groups:** hand × section for the Voynich text. Controls carry the Voynich page metadata, and the same groups are used.
- **Observed:** O_t = number of pairs of occurrences of type t on the same page.
- **Null:** tokens are permuted within their group, keeping page sizes. Exactly, E_t = Σ_g C(n_tg, 2) · Σ_{p∈g} N_p(N_p − 1) / (N_g(N_g − 1)).
- **Band index:** B_band = Σ_t O_t / Σ_t E_t over the band's types.
- **Primary: gradient G = ln B_R − ln B_F.** It is positive when rare types cluster more than frequent ones.
- **Uncertainty:** bootstrap over pages, 500 replicates, with band membership fixed from the full corpus.

## Controls

- **LAT, ITA, GER, ENG** in the Voynich page shape (content).
- **VB-run:** deterministic verbose cipher on running Latin (content, word identity preserved).
- **NAIB-run:** Naibbe on running Latin (content, homophonic).
- **LDRIFT:** a random walk over the weights of all types (vocabulary drift), step 0.3, as in E4.
- **REP:** repertoire drift with one-off coinage.
  - The repertoire is the 300 most frequent types of the page's group, with a random walk on their log-weights (step 0.3 per line).
  - Each token is, with probability c, a coinage: a token sampled from an order-3 token-internal glyph automaton of the group, rejected if it belongs to the repertoire. Otherwise it is drawn from the repertoire.
  - c is the share of Voynich tokens whose type is outside the top 300 of its group.
- **HGR2:** the E3 generator with its primary fitted parameters, trained and generated on the full Voynich layout.
- **MK-sec:** no drift.

**Calibration requirement:** at least three of the four languages show G > 0 (interval above 0), and NAIB-run shows B_R closer to 1 than the languages do. Otherwise E5 is uninformative.

## Decision

- **Content-like rare-type burstiness:** the G(V) interval lies above 0 and overlaps the language range.
- **No content-like burstiness:** the upper bound of G(V) is below the smallest lower bound of G among the languages.
- Either verdict is compared with LDRIFT and REP. If a non-content control reproduces the Voynich pattern, the verdict does not separate content from that mechanism, and this is stated.

## Mapping to hypotheses

- **Content-like burstiness, not reproduced by REP:** evidence for a content-driven distribution of rare forms, which is a plaintext signature (S3 with word identity preserved, or natural language), unless LDRIFT also reproduces it.
- **No content-like burstiness:** the rare forms do not behave like content words. This disfavours natural-language text and word-preserving ciphers as the source, and is consistent with repertoire drift plus coinage (S2 or S1a) or with homophonic encoding of rare units.
