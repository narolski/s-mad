# Texture band profile, two people against one (TB1): registration

Owner: PR1/BD1 owner agent (Opus), on the lead's assignment of 13 Nov 2026. It is built from the IDEAS test draft
`experiments/IDEAS_mechanism-ledger/TEST_texture-band-profile.md` at commit c17ac7d (sha256 `e542490f…`; ledger
entry M2). Registered at the git commit that adds this file. Before that commit, the only computations were:
- a 6-host code test of `src/TB1/tb1_measure.py` (`tb1_feats_limit6.csv`, not looked at);
- mock runs of the reader on random features. These printed the cue-only S4-vs-S3 27-statistic floor on real cues.

Development data only. Nothing enters the frozen method.

**Lead's ruling (13 Nov, in substance).** "FFT band statistics computed in memory are measurements like the existing
hand-made statistics (AS0 precedent), not image operations. No filtered image is stored as data or fed to training."

## 1. Question and hypothesis

- **H-TB1.** At equal blend energy, the difference between two people's warped faces is distributed over spatial
  frequency differently from the difference between two sessions of one person, and a single image shows it.
- **If no,** texture or skin-statistics mechanisms for a second identity are closed at this resolution, and BD1's
  residual beyond D is something other than texture.

## 2. Rows and the half-differences (no image is built)

- **Hosts.** The 291 BD1 hosts (191 test, 100 development; FRGC 235, colorFERET 56), with the FS1 evaluation frames.
- **Deviation from the draft: no warped halves are rebuilt.** As built (AR1 amendment 7b), a splice equals its
  counterpart outside the hull and equals the 50% OpenCV-style morph inside. So S4 − R2w4 = 0.5 (B_w − H_w) inside the
  hull for the two-person case, and S3 − R2w = 0.5 (S_w − H_w) for the same-person case. The half-difference of the
  draft is therefore available from existing images. Equality outside the hull is asserted in the code.
- **Single-image rows:** S4, S3, S0, R2w4, all with the amendment-7b hull from mean(H, B); R0 and R0_61 (stored
  small), with the hull of H's own landmarks. Outer ring: 3 × 3 dilations of the hull until the ring is at least as
  large as the hull.

## 3. Measurement (`src/TB1/tb1_measure.py`, DGX CPU)

- Luminance Y. AS0's octave bands B1-B5 (`as0_measure.band_weights`, imported unchanged), at the ar1_512 nominal IOD
  of 130.51 px (AS0 `iod_nominal.json`). One FFT of the whole frame.
- **P (premise):** E_k = Σ over the hull of b_k(d)², p_k = E_k / Σ E (independent of total energy).
- **S (single image):** r_k = ln(mean over the hull of b_k(Y)² / the same over the ring). This cancels the storage
  history and noise level the two regions share.

## 4. Reads (`src/TB1/tb1_read.py`) and rule

- **P.** Cross-fitted logistic regression on ln p_1..p_5 (5 host folds, `default_rng(20261171)`; the S4 and S3 rows of
  a host share a fold), two-person against same-person half-differences.
  - Out-of-fold AUC overall, and within quintiles of D (primary), D_lin and G (strata with ≥ 10 of each class),
    each beside its pure reference (the statistic alone).
  - Host-bootstrap interval for the within-D AUC.
  - Printed: by database, and within joint D-tertile × G-half strata.
- **S.** The same cross-fitted logistic on r_1..r_5: S4 vs S3, within D quintiles.
  - Controls (same model): R0_61 vs R0, S0 vs R0, R2w4 vs R0, each of which must be ≤ 0.58.
- **Floor.** The best single 27-statistic cue on S4 vs S3, chosen on one host half and scored on the other. The
  ADVERSARY floor is added beside it when published; the read waits if it is announced as pending.
- **Increment.** Per Sb seed 403-407 (stored development scores): out-of-fold AUC of [Sb logit, r] against
  [Sb logit], S4 vs S3.

**Outcome table (fixed now; draft thresholds unchanged):**

| P within D | S within D | S controls | Reading | Next |
|---|---|---|---|---|
| ≥ 0.70 | ≥ 0.65 | all ≤ 0.58 | a two-person texture trace exists and one image shows it | if the increment is ≥ +0.03 on ≥ 4 of 5 seeds: an arm with same-person blends at matched D plus a band-profile target (post-freeze ablation) |
| ≥ 0.70 | < 0.65 | — | the trace exists but is too weak or masked in the composite | report as a measured fact; no arm |
| ≤ 0.62 | any | — | no texture-level second-identity trace beyond blend energy | close M2; BD1's residual is not texture |
| any | any | a control > 0.58 | storage, seam or warp reads as the trace | closed unless stratifiable |

Otherwise "inconclusive (no row of the outcome table)".

**Deviation from the draft: one read of all 291 hosts.** The draft read development hosts first and test hosts once.
Here every rule is fixed before any value, so there is nothing to tune in between. Development and test values are
printed separately.

## 5. Cost and commands

- About 2 minutes of DGX CPU.
- `OMP_NUM_THREADS=2 nice -n 10 .venv-spark/bin/python -I src/TB1/tb1_measure.py`, then
  `... src/TB1/tb1_read.py --out experiments/TB1_texture-band-profile/tb1_read.json`, run once.
- Pins in `src/TB1/SHA256SUMS`.

## 6. Risks (from the draft)

- The hull edge leaks into the low bands. AS0's band weights are reused, but its masking is not, because the masks
  differ.
- colorFERET sessions are further apart in time; the result is printed by database.
- "Equal D" is one-dimensional; joint D × G strata are printed.
