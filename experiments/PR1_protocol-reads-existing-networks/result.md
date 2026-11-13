# Registered reads of the existing fresh-seed protocol networks (PR1): result

Development data only (our FRGC / colorFERET ladder and splices, and FFHQ, the sprint's development comparison set,
never a benchmark). Networks: the 15 fresh-seed protocol networks (FS1): A plain, B protocol negatives, Sb protocol
negatives plus face-spliced morphs, seeds 403-407, last checkpoint. Registration: `prereg.md` (commits a6e274a,
66c0542, 6ca423a, 4320366; amendments 1-2 after the pre-run review `experiments/reviews/PRERUN_PR1_20261113.md`).

## Part 1: zero-GPU reads Z0, Z1, Z2 (a, c, ρ), Z3, Z4, Z6

Read once on 13 Nov 2026, 09:16-09:20 CET. Reader `src/PR1/pr1_read.py` sha256 `1970e8f2…` (committed at 4320366),
stored scores from the 15 tars (all sha256 pins matched; none missing). Output `z_read.json`, stdout
`z_read_stdout.txt`. Results review (Opus) `experiments/reviews/REVIEW_PR1_PART1_20261113.md`: accept with corrections; every number recomputed independently and matched; corrections applied below.

### Z0: the strategist's cited figures, recomputed on the fresh seeds

| Cited figure (source) | Fresh seeds 403-407 | Check |
|---|---|---|
| Sb flags 0 of 100 development S0 seam-only images (seeds 401/402, PN1 prereg.md:778) | 0 of 100 on all five seeds; test S0: 1 of 191 on seed 403, 0 on the others | holds (fresh seeds too) |
| Sb flags 31-41% of development S3 | 31-41% | holds |
| Sb S3 vs S0, 0.86-0.93 | development 0.863-0.927; test 0.882-0.926 | holds (dev); test differs at the low end only |
| Sb S4 vs S3, 0.78-0.82 | development 0.781-0.816; **test 0.716-0.744** | holds (dev); **differs on test** (lower) |
| Sb misses landmark_combined, 26-47% | 25.6-46.8% | holds |
| Sb misses development S4, 15-29% | 15-29% | holds |
| A and B flag development S3, 2-7% | A 2-7%, B 2-5% | holds for A; the reader prints "differs" for B only because B's top end (5%) is below the cited joint range's 7% |

### Z1: does Sb fit its own training splices? (training rows, eval mode, plain logits)

| Seed | 403 | 404 | 405 | 406 | 407 |
|---|---|---|---|---|---|
| training S3 flagged (156 rows) | 0.276 | 0.256 | 0.301 | 0.365 | 0.295 |
| training S4 missed (124 unique rows) | 0.040 | 0.065 | 0.032 | 0.032 | 0.040 |
| development S3 flagged, minus training | +0.054 | +0.054 | +0.089 | +0.045 | +0.065 |
| development S4 missed, minus training | +0.210 | +0.225 | +0.118 | +0.148 | +0.160 |
| training AUC S3 vs S0 / S4 vs S3 | 0.935 / 0.872 | 0.886 / 0.854 | 0.947 / 0.857 | 0.946 / 0.881 | 0.934 / 0.856 |

- On all five seeds every other training kind is fitted at the own rule (0 errors on R0, R2w, halves, S0, af0 kinds;
  R4 and u50 all flagged). Sb's training errors are its S3 and S4 rows.
- **Registered verdict: "S3 underfit with S4 fit (class weighting or identity; no SL1 without an author decision)"**
  (4 of 5 seeds; seed 404 has training S4 miss 0.065 > 0.05). The "underfit" condition also holds on 5 of 5. The
  amendment-1 order puts the third outcome first.
- **What Z1 does and does not license.** Sb fits every other training kind on all five seeds, so it is not generally
  underfit. Its same-person splice flags are as high on training rows as on new hosts (26-37% against 31-41%), and
  its S4-vs-S3 ranking is imperfect even on training rows (AUC 0.85-0.88; test 0.72-0.74). Its two-person splice
  misses are a generalisation gap (3-6% on training rows against 15-29% on development hosts). Z1 therefore gives no
  support for training longer (SL1). It also does not show that a data change (SE1) will help. Choosing between them
  needs an author decision.

### Z2: a multi-source development threshold (τ5) and the trade-off

τ5 = the smallest cut-off with ≤ 5% flags in each calibration source (FRGC / colorFERET development photos; the FFHQ
calibration half). Labelled "within the calibration sources" (amendment 1, F3).

| At τ5 (5 seeds) | A | B | Sb |
|---|---|---|---|
| τ5 (logit) | 0.96 to 2.93 | −1.93 to 2.63 | −0.96 to −0.28 |
| G_max: largest flag share on the held-out genuine pools | 0.192-0.218 (history-matched FFHQ) | 0.072-0.100 | 0.049-0.087 |
| landmark_combined missed | 0.41-0.55 | 0.62-0.70 | 0.24-0.39 |
| development S3 flagged | 0.01-0.05 | 0.01-0.05 | 0.32-0.43 |
| development S4 missed | 0.97-0.99 | 0.94-0.99 | 0.15-0.25 |
| **Z2a verdict** (usable: G_max ≤ 0.10 and landmark_combined miss ≤ 0.30) | **no usable operating point** (0 of 5) | **no usable operating point** (0 of 5) | **usable operating point** (4 of 5; seed 403 misses 0.39) |

Within the calibration sources only. G_max leaves out the protocol-genuine one-person images, and at τ5 Sb still flags
32-43% of development S3. A fails on its history-matched FFHQ copies (19-22% flagged).

- **Z2c (the strategist's "same score band", Sb):** AUC of landmark_combined morphs against development S3:
  0.667, 0.795, 0.711, 0.710, 0.724 (intervals 0.59-0.73 up to 0.74-0.85). **Registered verdict: "inconclusive"**
  (not ≤ 0.65 on 4 seeds, not ≥ 0.80 on 4). At the cut-off flagging 10% / 20% of development S3 (cut-off = the
  90% / 80% quantile of development S3 logits, `numpy.quantile` default; another quantile definition gives 63.9-90.2%
  at 10%), Sb misses 61.5-90.2% / 48.0-75.6% of landmark_combined morphs, against 24-47% at its own rule.
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
- **Registered verdict: "no engine gap" for A, B and Sb (5 of 5), read at the ceiling.** Every AUC is 1.000 and
  misses are ≤ 0.5%, so the read cannot show a gap. It gives no evidence that our training engine transfers beyond
  whole-frame ladder morphs, and it does not decide the second-engine arm (#6). The largest transfer gap we have, FFHQ
  landmark_complete 0.97-0.997 against landmark_combined 0.65-0.89, is a composition contrast, not an engine
  contrast.
- FFHQ (printed): landmark_complete vs its resmatch pool 0.97-0.997 for every arm; landmark_combined A 0.69-0.76,
  B 0.65-0.71, Sb 0.81-0.89.

### Z4: one-person rows (test ladder, own rule, OpenCV-style decides)

| Row (SA1) | A | B | Sb |
|---|---|---|---|
| 6: warp-only R2w flagged | 0% (5 seeds); R4 vs R2w 1.000 → **not flagged** | 0%; 1.000 → **not flagged** (trained negative) | 0-0.5%; 1.000 → **not flagged** (trained negative) |
| 7: same-person morph R3 flagged | 94.8-99.5%; R4 vs R3 0.72-0.75 → **flagged like a morph** | 90.6-95.3%; 0.75-0.79 → **flagged like a morph** | 83.2-88.5%; 0.80-0.85 → **flagged like a morph** |
| 7: mirror self-morph R3m flagged | 97.9-99.5%; R4 vs R3m 0.77-0.79 → **flagged like a morph** | 94.8-97.4%; 0.79-0.83 → **flagged like a morph** | 95.8-96.9%; 0.80-0.84 → **flagged like a morph** |
| 8: same-person splice S3 flagged | 2.1-5.8% → **not flagged** | 0.5-3.7% → **not flagged** | 37.2-48.2%; S4 vs S3 0.72-0.74 → **inconclusive** (trained negative) |
| 9: seam-only S0 flagged | 0-0.5%; S4 vs S0 0.75-0.83 → **inconclusive** (0-0.5% seam-only flags; weak S4 detection) | 0%; 0.68-0.78 → **inconclusive** (0% seam-only flags; the inconclusive verdict comes from weak S4 detection: 91-98% of S4 missed) | 0-0.5%; S4 vs S0 0.985-0.994 → **seam-only not flagged** (trained negative) |

### Z6: softness (lapvar_face strata, test ladder, opencv R4 vs R2w)

- **Registered verdict: "not softness alone" for A, B, Sb (5 of 5), at the ceiling.** It rests on one statistic
  (lapvar_face), the strata cover 60% of the rows (the dropped strata are the most softness-separable), and R2w is a
  trained negative of B and Sb. Stratified AUC 1.000 for every arm and seed; deciles 1.000; lapvar_face alone 0.772.
- Not saturated: Sb's S4-vs-S3 AUC within lapvar strata is 0.71-0.75 on all five seeds (lapvar alone 0.50), so
  lapvar softness does not explain that separation.
- Printed: within-class ρ(logit, log lapvar_face) for Sb s403: R0 −0.31, R2w −0.31, R3 +0.03, R4 +0.24, S0 −0.19,
  S3 −0.06, S4 +0.07. Stratified S4 vs S3 for Sb s403: 0.739 (lapvar_face alone 0.503).

### Amendment 3 reads (post hoc, registered at 90caa9e before computing; `z1b_read.json`, reader `src/PR1/z1b_read.py`)

- **Z1b-1, host memorisation (Sb):** the training S3 rows flagged (40-57 of 156 per seed) are largely the same rows
  on every seed. Jaccard overlap / chance, mean per seed: 4.05, 4.31, 4.00, 3.65, 4.21. **Registered verdict:
  "supported"** (≥ 3.0 on 5 of 5). Median S4-minus-S3 logit margin on the same host: training 3.96-4.94, test hosts
  1.08-1.79.
- **Z1b-2, ranking, not weighting (Sb):** at the cut-off flagging 5% of training S3, training S4 misses are 0.758,
  0.774, 0.766, 0.734, 0.726. **Registered verdict: "supported"** (≥ 0.30 on 5 of 5).
- **Z1b-3, development against test S4 vs S3 (Sb):** development minus test +0.044 to +0.072. The 95% host-bootstrap
  interval holds 0 on 4 of 5 seeds (seed 406: +0.009 to +0.139). **Registered label: "sampling-compatible".**
- **Z3b, engine contrast on R4 vs same-person morph (test ladder, 191 hosts):** Δ3 = AUC(R4 vs R3) opencv minus
  facemorpher. Sb +0.029, +0.006, +0.011, +0.017, +0.011; B +0.012 to +0.028; A −0.001 to +0.018. Δ3m (mirror) −0.009
  to +0.014 for all arms. **Registered verdict: "inconclusive" for A, B, Sb** (Sb: 0 seeds ≥ 0.03, 1 seed ≤ 0.01).

## Checks of the strategist's three facts (section 0 of the strategist report)

1. "Sb flags 0 of 100 seam-only images": cited from seeds 401/402. It **holds on the fresh seeds** (0 of 100 on all
   five; test 1 of 191 once).
2. "S4 against S3 is 0.78-0.82": holds on the 100 development hosts; on the 191 test hosts it is **0.716-0.744**. The
   development ladder was the selection set for the recipe (PN1 rule), so the test value is the better estimate. No
   development or test splice host or partner is among the 156 training persons (reviewer's check).
3. "Same score band": the registered test is **inconclusive** (AUC 0.667-0.795; neither ≤ 0.65 nor ≥ 0.80 on 4 seeds).
   The bands are not identical. The strategist's practical point holds for thresholds: cutting S3 flags to 10% / 20%
   raises landmark_combined misses from 24-47% to 61.5-90.2% / 48.0-75.6%.

Other results bearing on the strategist's plan (not one of its facts): Sb's own training S3 rows are flagged nearly as
often as development S3 (26-37% against 31-41%) while its training S4 rows are fit (Z1). Across recipes (3 arms), Sb
is better on both axes of the H-new-4 trade-off (arm-mean ρ +0.5 on 3 points; within-arm p 0.089). This is not
evidence about a trade-off within a recipe.

## What could not be verified

- Z3 and Z6 are read at the ceiling (all AUCs 1.000).
- Z2a is in-source by design; the unseen-source line (Z2b-τ5) waits for TT1-FS.
- Training-row logits are plain (no flip average stored).
- Z5 waits for the C2P and MS1 owners' reads.

## Part 2: GD0, GD1, GD2 (scoring on pn1fs)

Not yet run (job after the TT1-FS block on pn1fs).
