# E7 preregistration: can a plaintext hide in the free choices without changing the phenotype?

Frozen before running. Program log: `mechanism/PROGRAM.md`.

## Question

The claims policy forbids "no plaintext" conclusions from text statistics. E7 makes that concrete. A local glyph process makes a free choice at every character. If those choices are driven by a compressed plaintext through arithmetic decoding (a mimic function; Wayner 1992), the output distribution is that of the process itself, and the plaintext can be recovered exactly by anyone who knows the model. E7 checks this on the measured phenotype, rather than asserting it.

## Construction

- **Process.** The order-3 character automaton per (Currier language, section) group of the battery (MK-sec), trained on the whole Voynich paragraph text and generated on the Voynich layout. Its line rules are unchanged: the end symbol is suppressed below 60% of the target length, and lines stop at 140%.
- **Chooser.** Every character choice is made by a chooser over integer counts.
  - **PRNG chooser:** random choice.
  - **Plaintext chooser:** 32-bit arithmetic decoding (Witten, Neal and Cleary) of a plaintext bitstream.
  - The receiver re-runs the process on the generated text and arithmetic-encodes the observed choices, which returns the bitstream.
- **Plaintexts, compressed with lzma:** Caesar (Latin), Dante (Italian), Faust (German).
- **Contrast:** the same three plaintexts as raw UTF-8 bits, without compression.

## Tests

- **Recovery:** the re-encoded bits equal the plaintext bits over the consumed length, apart from at most 64 final bits.
- **Indistinguishability:** the 40-statistic phenotype of E2 for PRNG-driven output (3 seeds) against compressed-plaintext output (3 plaintexts). A statistic agrees if |mean_a − mean_b| ≤ 2 √(sd_a² + sd_b²) + 0.01 |mean_a|. T4 agrees if the peak counts differ by at most one.
- **Contrast:** the same comparison for raw-plaintext output, reported descriptively.
- Also reported: bits consumed per glyph and per token, which is the capacity of the process.

## Interpretation fixed in advance

- **Recovery exact and at least 38 of 40 statistics agreeing:** a plaintext of the reported size can be carried by a Voynich-like local process with no measurable trace in any statistic of the battery. Text statistics cannot separate S3 (plaintext in the free choices) from S1a and S2 for this construction.
- **Otherwise:** the statistics that disagree show where a hidden plaintext would leave traces.
- **Arithmetic coding is modern.** E7 establishes statistical indistinguishability, not historical plausibility. If the raw-bit contrast leaves traces, compression is what hides the plaintext. A medieval encoder without an equivalent step would be more detectable.
