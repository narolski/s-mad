# Registered reads of the existing fresh-seed protocol networks (PR1): result

Development data only (our FRGC / colorFERET ladder and splices, and FFHQ, the sprint's development comparison set,
never a benchmark). Networks: the 15 fresh-seed protocol networks (FS1): A plain, B protocol negatives, Sb protocol
negatives plus face-spliced morphs, seeds 403-407, last checkpoint. Registration: `prereg.md` (commits a6e274a,
66c0542, 6ca423a, 4320366; amendments 1-2 after the pre-run review `experiments/reviews/PRERUN_PR1_20261113.md`).

## Part 1: zero-GPU reads Z0, Z1, Z2 (a, c, ρ), Z3, Z4, Z6

Read once on 13 Nov 2026, 09:16-09:20 CET. Reader `src/PR1/pr1_read.py` sha256 `1970e8f2…` (committed at 4320366),
stored scores from the 15 tars (all sha256 pins matched; none missing). Output `z_read.json`, stdout
`z_read_stdout.txt`. Owner's numbers; the results review is pending.

### Z0: the strategist's cited figures, recomputed on the fresh seeds

| Cited figure (source) | Fresh seeds 403-407 | Check |
|---|---|---|
| Sb flags 0 of 100 development S0 seam-only images (seeds 401/402, PN1 prereg.md:778) | 0 of 100 on all five seeds; test S0: 1 of 191 on seed 403, 0 on the others | holds (fresh seeds too) |
| Sb flags 31-41% of development S3 | 31-41% | holds |
| Sb S3 vs S0, 0.86-0.93 | development 0.863-0.927; test 0.882-0.926 | holds (dev); test differs at the low end only |
| Sb S4 vs S3, 0.78-0.82 | development 0.781-0.816; **test 0.716-0.744** | holds (dev); **differs on test** (lower) |
| Sb misses landmark_combined, 26-47% | 25.6-46.8% | holds |
| Sb misses development S4, 15-29% | 15-29% | holds |
| A and B flag development S3, 2-7% | A 2-7%, B 2-5% | holds |

### Z1: does Sb fit its own training splices? (training rows, eval mode, plain logits)

| Seed | 403 | 404 | 405 | 406 | 407 |
|---|---|---|---|---|---|
| training S3 flagged (156 rows) | 0.276 | 0.256 | 0.301 | 0.365 | 0.295 |
| training S4 missed (124 unique rows) | 0.040 | 0.065 | 0.032 | 0.032 | 0.040 |
| development S3 flagged, minus training | +0.054 | +0.054 | +0.089 | +0.045 | +0.065 |
| development S4 missed, minus training | +0.210 | +0.225 | +0.118 | +0.148 | +0.160 |
| training AUC S3 vs S0 / S4 vs S3 | 0.935 / 0.872 | 0.886 / 0.854 | 0.947 / 0.857 | 0.946 / 0.881 | 0.934 / 0.856 |

- Every other training kind is fitted at the own rule on seed 403 (0 errors on R0, R2w, halves, S0, af0 kinds; R4 and
  u50 all flagged). Sb's training errors are its S3 and S4 rows.
- **Registered verdict: "S3 underfit with S4 fit (class weighting or identity; no SL1 without an author decision)"**
  (4 of 5 seeds; seed 404 has training S4 miss 0.065 > 0.05). The "underfit" condition also holds on 5 of 5. The
  amendment-1 order puts the third outcome first.

### Z2: a multi-source development threshold (τ5) and the trade-off

τ5 = the smallest cut-off with ≤ 5% flags in each calibration source (FRGC / colorFERET development photos; the FFHQ
calibration half). Labelled "within the calibration sources" (amendment 1, F3).

| At τ5 (5 seeds) | A | B | Sb |
|---|---|---|---|
| τ5 (logit) | 0.96 to 2.93 | −1.94 to 2.63 | −0.96 to −0.28 |
| G_max: largest flag share on the held-out genuine pools | 0.192-0.218 (history-matched FFHQ) | 0.072-0.100 | 0.049-0.087 |
| landmark_combined missed | 0.41-0.55 | 0.62-0.70 | 0.24-0.39 |
| development S3 flagged | 0.01-0.05 | 0.01-0.05 | 0.32-0.43 |
| development S4 missed | 0.97-0.99 | 0.94-0.99 | 0.15-0.25 |
| **Z2a verdict** (usable: G_max ≤ 0.10 and landmark_combined miss ≤ 0.30) | **no usable operating point** (0 of 5) | **no usable operating point** (0 of 5) | **usable operating point** (4 of 5; seed 403 misses 0.39) |

- **Z2c (the strategist's "same score band", Sb):** AUC of landmark_combined morphs against development S3:
  0.667, 0.795, 0.711, 0.710, 0.724 (intervals 0.59-0.73 up to 0.74-0.85). **Registered verdict: "inconclusive"**
  (not ≤ 0.65 on 4 seeds, not ≥ 0.80 on 4). At the cut-off flagging 10% / 20% of development S3, Sb misses
  61.5-90.2% / 48.0-75.6% of landmark_combined morphs.
- **Z2-ρ (TT1 H-new-4 extended, "across recipes; effective n about 3"):** x = own-rule flags on 2,000 FFHQ genuine
  photos, y = mean own-rule miss over three development attack pools. ρ = **+0.557** (permutation p 0.034; within-arm
  permutation p 0.089; arm-mean ρ +0.5; within arms A +0.6, B +0.6, Sb −0.4). **Registered verdict: "falsified"**
  (ρ ≥ 0). Arm means: x A 0.082, B 0.056, Sb 0.040; y A 0.318, B 0.322, Sb 0.082. At τ5 (printed only): ρ +0.693.
- Z2b (TT1-FS F̄) and Z2b-τ5 (unseen sources) wait for the TT1 owner's read.

### Z3: tool transfer (test ladder, 191 hosts, native rows)

- Engine of the training rows (fact check): every ladder R4 row of A (132), B (443) and Sb (435) is OpenCV-style; every
  S0 / S3 / S4 row is OpenCV-style; the AF0 morphs use AF0's Delaunay/OpenCV-style engine.
- AUC(R4 vs R2w) and AUC(R4 vs R0) are **1.0000 for both engines, every arm and seed**, on test and development
  hosts; Δ = 0 and Δ_R0 = 0 on every network. Own-rule misses of R4: 0 to 0.5% for both engines.
- **Registered verdict: "no engine gap" for A, B and Sb (5 of 5).** Stated as a fact: every number in this contrast
  is at the ceiling (AUC 1.000, misses ≤ 0.5%), so the contrast has no room to show a gap on whole-frame ladder morphs.
- FFHQ (printed): landmark_complete vs its resmatch pool 0.97-0.997 for every arm; landmark_combined A 0.69-0.76,
  B 0.65-0.71, Sb 0.81-0.89.

### Z4: one-person rows (test ladder, own rule, OpenCV-style decides)

| Row (SA1) | A | B | Sb |
|---|---|---|---|
| 6: warp-only R2w flagged | 0% (5 seeds); R4 vs R2w 1.000 → **not flagged** | 0%; 1.000 → **not flagged** (trained negative) | 0-0.5%; 1.000 → **not flagged** (trained negative) |
| 7: same-person morph R3 flagged | 94.8-99.5%; R4 vs R3 0.72-0.75 → **flagged like a morph** | 90.6-95.3%; 0.75-0.79 → **flagged like a morph** | 83.2-88.5%; 0.80-0.85 → **flagged like a morph** |
| 7: mirror self-morph R3m flagged | 97.9-99.5%; R4 vs R3m 0.77-0.79 → **flagged like a morph** | 94.8-97.4%; 0.79-0.83 → **flagged like a morph** | 95.8-96.9%; 0.80-0.84 → **flagged like a morph** |
| 8: same-person splice S3 flagged | 2.1-5.8% → **not flagged** | 0.5-3.7% → **not flagged** | 37.2-48.2%; S4 vs S3 0.72-0.74 → **inconclusive** (trained negative) |
| 9: seam-only S0 flagged | 0-0.5%; S4 vs S0 0.75-0.83 → **inconclusive** | 0%; 0.68-0.78 → **inconclusive** | 0-0.5%; S4 vs S0 0.985-0.994 → **seam-only not flagged** (trained negative) |

### Z6: softness (lapvar_face strata, test ladder, opencv R4 vs R2w)

- Stratified AUC (strata with ≥ 10 rows of each class, covering 60% of the rows) = **1.000 for every arm and seed**;
  deciles 1.000. lapvar_face alone gives 0.772 (direction-free). **Registered verdict: "not softness alone" for A, B,
  Sb** (5 of 5). Stated as a fact: the unstratified AUC is also 1.000, so stratification cannot lower a ceiling it
  does not reach; the read says that within sharpness strata the ranking stays perfect.
- Printed: within-class ρ(logit, log lapvar_face) for Sb s403: R0 −0.31, R2w −0.31, R3 +0.03, R4 +0.24, S0 −0.19,
  S3 −0.06, S4 +0.07. Stratified S4 vs S3 for Sb s403: 0.739 (lapvar_face alone 0.503).

## Facts that contradict or qualify the strategist's three facts (section 0 of the strategist report)

1. "Sb flags 0 of 100 seam-only images": cited from seeds 401/402. It **holds on the fresh seeds** (0 of 100 on all
   five; test 1 of 191 once).
2. "S4 against S3 is 0.78-0.82": holds on the 100 development hosts; on the 191 test hosts it is **0.716-0.744**.
3. "The S3 flags and the landmark misses sit in the same score band": the registered test (Z2c) is
   **inconclusive** (0.667-0.795). Sb's training S3 rows are flagged nearly as often as development S3 (26-37% against
   31-41%), while its training S4 rows are fit (3-7% missed).
4. Within the calibration sources, Sb is the only arm with a usable operating point at τ5 (4 of 5 seeds). The
   H-new-4 trade-off (lower genuine flags bought with more misses) is falsified across recipes (ρ +0.56).

## What could not be verified

- Z3 and Z6 are read at the ceiling (all AUCs 1.000).
- Z2a is in-source by design; the unseen-source line (Z2b-τ5) waits for TT1-FS.
- Training-row logits are plain (no flip average stored).
- Z5 waits for the C2P and MS1 owners' reads.

## Part 2: GD0, GD1, GD2 (scoring on pn1fs)

Not yet run (job after the TT1-FS block on pn1fs).
