# Look-alike pair search (LA1): DRAFT registration (not in force)

Draft for the author's decisions listed in `plan.md`. It is registered (moved into `prereg.md`) only after those
decisions and a pre-run check. Nothing is computed before then.

- **Question (measurement only).** How many cross-identity photo pairs, from labelled development or training
  sources, reach glintr100 cosine ≥ 0.60, ≥ 0.70 and ≥ 0.77 after quality filters and the automatic label-noise control
  (`plan.md` sections 3 and 5)?
- **Sources.**
  - CelebA-HQ with official CelebA identity labels (once obtained).
  - MUCT; NIST MEDS (pair lists only, no images).
  - Optionally FRGC / colorFERET PN1-training persons.
  - Every closed set is excluded, with the overlap checks of `plan.md` section 1.
- **Embeddings.** `src/AR1/fr.py` unchanged; the existing CelebA-HQ embeddings `MS1/celebahq/emb_*.npz` are reused.
  New embeddings on WCSS in a `$TMPDIR` venv built from staged wheels. Gate: per-image cosine ≥ 0.999 against the
  DGX embedding on 8 images per source.
- **Search.** Exact all-pairs across identities, blocked per source. The best image pair and the count above 0.6 are
  kept per identity pair.
- **Rule (go / no-go for a later matched arm, `plan.md` section 4).**
  - **Go:** ≥ 100 identity pairs at cosine ≥ 0.60 pass all filters, each with a same-person counterpart within
    ±0.03 cosine.
  - **No-go:** < 30.
  - Otherwise: an evaluation-only contrast.
  - Counts at ≥ 0.70 and ≥ 0.77 are printed.
- **Outputs.** `pairs.csv` and a summary; no images.
- **Pre-stated expectation (from calibration).** Tens to a few hundred CelebA-HQ identity pairs at 0.60; few at 0.77.
  The uncertainty spans two orders of magnitude.
- **Cost.** 0 GPU for CelebA-HQ. About 0.2 H100-hour, or 2 CPU-hours, for MUCT + MEDS. Up to about 1 H100-hour with
  the FRGC / colorFERET training images.

- **Revised after the pre-run check** (see plan.md, "Revision after the pre-run check"). Labels come via
  `data-celeb-aligned/split.csv` plus the CelebA-HQ mapping (author). The label-noise control is image-level, and
  every threshold is fixed on labelled CelebA. MUCT is dropped. Counterparts are matched from the same source. The go
  rule counts disjoint pairs: go ≥ 100, no-go < 50. LA1-0 tail calibration is proposed as the first registered step.
