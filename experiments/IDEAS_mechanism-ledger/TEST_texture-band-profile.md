# Draft test design: texture band profile of two people against one [TB1]

Draft by the ideas and literature role (IDEAS), 13 Nov 2026, about 19:05 CET (machine clock; committed in 6db5154 at 19:07). **Not registered; nothing run.** Ledger entry M2.

**Status (19:58 CET, 13 Nov): taken up as `experiments/TB1_texture-band-profile/`; premise held (0.758 within D) but the
profile's gain over band energy and landmark displacement was +0.010 [−0.006, +0.021], registered verdict "falsified"
(amendment 2; REVIEW_TB1_PREMISE, REVIEW_TB1_A2). The mid-band prediction of this draft was contradicted. Kept as the
record of the proposal.**

## Question

At equal blend energy, is the difference between two people's warped faces distributed over spatial frequency
differently from the difference between two sessions of one person? If yes, a blend of two people carries an
anatomy-level texture trace that a same-person blend does not, and a within-image statistic can try to read it. If no,
every texture or skin-statistics mechanism for a second identity is closed at this resolution, and BD1's residual
beyond D is something other than texture.

## Data (development only)

- Landmark ladder hosts as in BD1 (291 FRGC / colorFERET hosts, 191 test and 100 development; the development hosts are
  read first and the test hosts once, with the rule fixed in between).
- For each host: the two warped halves of the two-person splice (host H and partner B warped to the two-person
  geometry; R2w4 is the host half) and of the same-person splice (H and S warped to their geometry). These exist as
  protocol negatives (the morph's own warped halves); any missing half is rebuilt with the approved `h1_build.py`
  warp, unchanged, and stored as lossless PNG.
- The single-image rows: S4, S3, S0, R0, R0_61 (stored small), R2w4.
- Masks: the landmark hull of amendment 7b (BD1), and an outer ring of the same area outside the hull.

## Measurement (in memory, no image written)

- Luminance only (colour is BD1's D_dc and D_lin, used as covariates).
- Band images by FFT with the five octave bands of AS0 (`experiments/AS0_mirror-asymmetry/prereg.md`, "Bands":
  half-power wavelengths IOD to IOD/32, partition weights), computed on the hull-masked image with the same window.
- Oracle P: for each host, half-difference d = H_w − X_w inside the hull (X = B for two-person, S for same-person);
  band energies E_1..E_5 of d; profile p_k = E_k / Σ E_k (independent of total energy by construction).
- Single-image S: for the image itself, band energies inside the hull and in the outer ring; statistic
  r_k = ln(E_k,inside / E_k,outside), which cancels storage history and sensor noise level that the two regions share.

## Reads

1. **P (premise):** cross-fitted logistic on (p_1..p_5), two-person against same-person half-differences, host-disjoint
   folds, within quintiles of D (BD1), D_lin and the geometry gap G. AUC with host bootstrap.
2. **S (single image):** AUC of a cross-fitted logistic on (r_1..r_5) for S4 vs S3 within D quintiles; controls R0_61
   vs R0, S0 vs R0, R2w4 vs R0 (all must be ≤ 0.58). TB1 uses splices because there the outer ring is a clean host
   reference; full-frame R4 and R3 have no clean outer reference and are out of scope of S (P covers them only through
   their halves).
3. **Floor and increment:** the best single 27-statistic cue on the same rows (cross-fitted) and Sb's logit (existing
   development scores, seeds 403-407); increment of [Sb logit, r] over [Sb logit].

## Outcome table (fixed before reading)

| P within D | S within D | S controls | Reading | Next |
|---|---|---|---|---|
| ≥ 0.70 | ≥ 0.65 | ≤ 0.58 | a two-person texture trace exists and one image shows it | if the increment is ≥ +0.03 on ≥ 4 of 5 seeds: arm with same-person blends at matched D as negatives plus an auxiliary band-profile target (about 6 H100-hours) |
| ≥ 0.70 | < 0.65 | — | the trace exists but is too weak or masked in the composite | stop; report as a measured physical fact (premise), no arm |
| ≤ 0.62 | any | — | no texture-level second-identity trace beyond blend energy | close M2 and the round-3 layer-count line; BD1's residual is then not texture (points to identity features, RI1, or to construction) |
| any | any | a control > 0.58 | storage, seam or warp reads as the trace | closed unless stratifiable |

## Cost

0 GPU. About 291 hosts x (4 halves + 6 single images) x 5 bands: about 3 CPU-hours on the DGX with the OMP and nice
settings, or one `lem-cpu-short` task (one tar in, one tar out).

## Risks the reviewer should check

- The hull mask's edge leaks into the low bands; AS0's window and mask handling should be reused unchanged.
- Same-person sessions in colorFERET are further apart in time than in FRGC; report by database (BD1 found cos_HS and
  database not separable in the least-similar quintile).
- The premise uses pairs Sb never saw only on test hosts; development hosts are part of the arm's training split
  logic only through the ladder, not through Sb's training rows (check against the PN1 split files).
- "Equal blend energy" by D quintiles is one-dimensional; print P also within joint D x G strata.
