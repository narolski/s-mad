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

### Z2b and Z2b-τ5: the threshold on unseen genuine sources (registered; read once at about 11:30 after the TT1 owner's commit b82163c)

Reader `src/PR1/z2b_read.py` (committed at 7222d71 before the TT1 read existed). Input: `tt1_read_fs.json` (sha256
434208c6…; TT1 gate 15/15 byte-identical) and the per-row TT1 logits in `TT1_A100_pn1fs_fs.tar` (sha256 verified).
Output `z2b_read.json`. The TT1-FS read is not yet reviewed by its own reviewer.
- **Z2b-τ5:** each network's τ5 (from part 1) applied to the 7 unseen-source families. G_unseen = largest family
  flag share.
  - A: 0.018, 0.112, 0.040, 0.008, 0.044 (largest LFW/CALFW; AgeDB on seed 406) → registered label "usable on unseen
    sources" (4 of 5 ≤ 0.10), which means **genuine flags ≤ 10% on unseen sources, genuine side only**. At τ5, A misses
    41-55% of landmark_combined morphs (Z2a).
  - B: 0.005, 0.007, 0.005, 0.022, 0.028 → same label (5 of 5), genuine side only. At τ5, B misses 62-70% of
    landmark_combined (Z2a).
  - Sb: 0.088, 0.163, 0.042, 0.060, 0.117 (largest CFP-FF every seed) → **"inconclusive"** (3 of 5 ≤ 0.10).
  - Sb's τ5 is below its own rule (0) on every seed, so calibrating on FFHQ raises its CFP-FF flags (0.042-0.163 at
    τ5 against 0.034-0.134 at the own rule; post hoc, reviewer). Sb meets both Z2a and Z2b-τ5 on seeds 405 and 406
    only (2 of 5; post hoc). **F10 is not answered by these reads.**
  - The TF32 mismatch (≤ 0.035 logit) cannot change any verdict: Sb seed 407 would need about 82 CFP-FF rows to cross,
    and only 59 TT1 rows of any family lie within 0.035 above their τ5 (reviewer's count).
- **Z2b-ρ** (x = TT1 F̄, y = mean own-rule miss over three development attack pools, 15 networks): ρ = −0.346
  (permutation p 0.21; within-arm p 0.76; arm-mean ρ −0.5). **Registered verdict: "weak (not decided)"**, across
  recipes.

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

### Z5: storage evasion of morphs (A, B, Sb copied from PN1 c2p_read.json, commit 0cb89c5, provisional pending C2P-R; SbM3 read here from the MS1 fits' own stored scores, not provisional)

**Provisional.** The C2P post-result review (e2af82c) quarantines the hold-out scores of every gate-failed network
until a re-scoring (C2P-R) is read. Z5 will be re-copied from the C2P-R read. No quarantined score was opened here.

Formula and rule of C2P.4 (H-new-1). Only networks that passed the C2P gate count (denominator 5). No value was
computed here, so no extra look at the hold-out was taken.
- **A:** "not available". The C2P gate (L40S, TF32 off) failed for all five A networks on the max condition (max
  |Δlogit| 0.119-0.249 > 0.10).
- **B:** "inconclusive" (C2P's verdict). Only seed 405 passed: Δm_att fm61 +0.060, amsl112 −0.0003.
- **Sb:** "falsified" (C2P's verdict; no evasion). Four seeds passed: Δm_att fm61 +0.056, +0.105, +0.061, +0.071;
  amsl112 −0.024, +0.041, −0.012, +0.005.
- **Three-source arm (SbM3):** read once at about 14:47, after the MS1 read was committed and reviewed (reader
  `src/PR1/z5_read.py` committed at 1d2c359; output `z5_sbm3_read.json`). Scores are each MS1 fit's own stored
  hold-out scores from its own L40S; nothing was rescored. 150 / 149 morph pairs, SD from 300 native photos.
  Δm_att at fm61: +0.007, −0.009, +0.022, −0.001, +0.010; at amsl112: +0.009, +0.002, +0.025, −0.101, +0.009.
  **Registered verdict: "falsified"** (no evasion at the rule: ≥ −0.10 on 5 of 5 seeds at fm61 and 4 of 5 at
  amsl112). Seed 406 at amsl112 is −0.101, driven by 2 of 149 morphs that flip from +3.0 / +1.2 to −1.7 / −3.1; that
  seed's median is +0.010. Misses on native / stored morphs: 0.7-1.3% / 0.7-2.0%.
  - Scope: FFHQ is a trained source of SbM3. Its training set holds 200 fm61 stored copies of FFHQ u50 morphs from the
    same engine and the same shrink-and-enlarge operator (MS1 prereg 3.3), so the fm61 read is in-distribution except
    for the persons. amsl112, an untrained size, is the informative half.
  - Native misses are 0.7-1.3% (AUC ≥ 0.999), so the test can only detect large evasion. SbM3's smaller native-genuine
    SD (0.43-0.65 against 0.84-1.19 for Sb) makes the standardised test stricter for it.
  - This is a PR1 measurement, not the C2P.4 freeze requirement. Review `experiments/reviews/REVIEW_PR1_Z5_20261113.md`:
    accept with corrections (all numbers recomputed and matched).
  - Printed beside, MS1's own Sb refits (L40S, no rule; FFHQ untrained for Sb): fm61 +0.056 to +0.103; amsl112 −0.024
    to +0.041.
- AB1 (ablation experiment, five new seeds on H100, commit 8109cad) has read the storage test for A, B and Sb. It is
  not used here, because Z5 is defined on the fresh-seed networks. It will be cited beside Z5 once its review is
  applied.

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
- Z5 for A, B and Sb waits for the C2P-R read.

## Part 2: GD0, GD1, GD2 (new scoring on pn1fs; read once at about 11:45)

Results review (Opus) `experiments/reviews/REVIEW_PR1_PART2_20261113.md`: accept with corrections; every number recomputed and matched (gate max |Δ| 0 on 15 of 15); corrections applied below.

- **Platform and gate:** rented A100 pn1fs (GPU-5bd20020, the card that trained and stored these networks), TF32 on,
  batch 64, manifest order. The job ran 10:01-10:15 host time (11:01-11:15 CET) under the FS1 queue lock after
  TT1-FS and TT1-X. Gate on all 19,797 FS1 evaluation rows: **15 of 15 passed, all byte-identical (max |Δ| 0)**.
  Every GD logit is finite. Result tar `PR1_GD_pn1fs.tar` sha256 `bf560f53…`, two verified copies
  (`/mnt/t7/smad_next/PR1/results/`, `results_copy2/`). Reader `src/PR1/gd_read.py` (`7373a0ef…` at 6ca423a,
  amendment-1 version in `src/PR1/SHA256SUMS`). Output `gd_read.json`, `gd_read_stdout.txt`.
- **Baseline check:** the rebuilt amendment-15 baselines reproduce `baseline27.json` exactly (124/312, 248/624;
  0.8138695, 0.8144465).

### GD0: FFHQ-Morphs StyleGAN and DiffAE families (morphs against their history-matched genuine pools)

Label (amendment 1, F2): StyleGAN morph against camera photo; the GAN render cue is not separated.

| AUC (seeds 403-407) | A | B | Sb | 27-stat s-lad / b-lad | best single statistic |
|---|---|---|---|---|---|
| stylegan_wplus | 0.919, 0.972, 0.944, 0.958, 0.939 | 0.871, 0.971, 0.926, 0.936, 0.852 | 0.952, 0.984, 0.972, 0.990, 0.983 | 0.886 / 0.909 | 0.876 (band power .125-.25) |
| stylegan_w | 0.861, 0.927, 0.875, 0.910, 0.874 | 0.725, 0.901, 0.798, 0.835, 0.711 | 0.881, 0.937, 0.896, 0.967, 0.942 | 0.897 / 0.913 | 0.910 (same) |
| diffae (printed) | 0.649-0.735 | 0.676-0.741 | 0.686-0.760 | 0.638 / 0.666 | 0.755 (noise_std) |

- **Sb (decides):** both StyleGAN families pass the registered AUC ≥ 0.80 bar ("transfers"). wplus is beyond the
  27-statistic baseline on 5 of 5 seeds (Sb − s-lad +0.066 to +0.104). w is not beyond it (≥ +0.05 on 1 seed) and is
  above the best single statistic on only 3 of 5. This is StyleGAN morph against camera photo. It is **not shown to be
  morph detection**: Sb flags 78-90% of one-photo MIPGAN renders (GD2). Descriptively and across sets (post hoc,
  reviewer), Sb's stylegan_wplus morph logits do not exceed its one-photo-render logits (AUC 0.39, 0.51, 0.61, 0.45,
  0.61; medians about +3.1 against +3.2). **H-GD0 is supported only in this sense; it is not evidence for GAN
  benchmark cells.**
- A (printed): wplus "transfers" (beyond the baseline on 4 of 5), w "transfers" (not beyond). B: wplus "transfers"
  (not beyond), w "inconclusive". Same coupling qualifier.
- Own-rule misses, Sb: wplus 2.2-11.3%, w 6.7-24.0%, diffae 57-70%. Genuine resmatch flags, Sb 2.2-5.1%; A
  6.8-11.0%. AUC against native FFHQ genuine photos is within 0.01 of the resmatch AUC for StyleGAN (the StyleGAN
  resmatch copies are near native size). For DiffAE it is +0.03 to +0.11 for A and −0.03 to −0.09 for B and Sb.

### GD1: DG1 diffusion ladder (test hosts; 256 px DiffAE frames, not the networks' E7 frame)

| AUC | A | B | Sb |
|---|---|---|---|
| X vs REC (two-person mix vs reconstruction) | 0.526-0.659 | 0.459-0.558 | 0.529-0.595 |
| REC vs G (reconstruction vs camera photo, same frame) | 0.969-0.996 | 0.924-0.989 | 0.990-0.996 |
| SAME vs REC | 0.317-0.470 | 0.241-0.300 | 0.206-0.269 |
| X vs SAME | 0.642-0.737 | 0.682-0.752 | 0.778-0.846 |

- **Registered verdict: "render path used" for A, B and Sb (5 of 5)**, within the 256 px DiffAE frame; it does not
  carry over to E7 frames. REC vs G ≥ 0.92 on every network. X vs REC ≤ 0.60 on 3 seeds for A, 5 for B, 5 for Sb.
  A's verdict carries "history-confounded". The frame alone raises camera-photo flags to 2.4-52%.
- Printed: latent mixes score below the reconstruction (Sb SAME vs REC 0.21-0.27, MIR vs REC 0.28-0.37). Two-person
  mixes rank above same-person mixes (X vs SAME Sb 0.78-0.85; A 0.64-0.74; B 0.68-0.75). On DiffAE, only Sb seed 407
  (0.760) reaches the single statistic noise_std (0.755) in GD0.
- Own-rule flags (frame-confounded): REC 89-100%, SAME 71-100%, X 93-100% for every arm. G (camera photos in the
  DiffAE frame): A 18-52%, B 12-40%, Sb 2.4-10%. Stored test R0 native: 0% for every network.

### GD2: AG1 MIPGAN controls (E7 frames; persons outside PN1 training and validation)

Rows: R0 227, R2 238, R2s 119, R3 119, R3m 119, R4 74.

| | A | B | Sb |
|---|---|---|---|
| R2 (MIPGAN render of one photo) flagged | 57-72% | 30-67% | 78-90% |
| R4 (two-person MIPGAN) flagged | 99-100% | 90-100% | 100% |
| R3 (same-person MIPGAN) flagged | 88-98% | 77-96% | 98-100% |
| R0 camera flagged | 0% | 0% | 0-0.4% |
| AUC R4 vs R2 | 0.733-0.871 | 0.811-0.909 | 0.864-0.932 |
| AUC R4 vs R3 | 0.530-0.627 | 0.583-0.667 | 0.619-0.690 |
| AUC R2 vs R0 | 0.957-0.985 | 0.911-0.978 | 0.992-0.998 |

- **Registered verdict: "inconclusive" for A, B and Sb.** R2 is flagged ≥ 50% on 5 of 5 seeds for A and Sb (B 3 of
  5), but AUC(R4 vs R2) > 0.65 on every seed, so the amended "flagged like a morph" branch is not met. R2 flags are
  not ≤ 10% on any seed.
- Descriptive (post hoc, reviewer): most of R4's lead over R2 also appears without a second identity (Sb R3 vs R2
  0.79-0.83, R3m vs R2 0.74-0.81, against R4 vs R2 0.86-0.93). The identity step R4 vs R3 is 0.62-0.69 (A 0.53-0.63,
  B 0.58-0.67), matching AG1's released detectors. At the own rule, Sb raises a false alarm on 78-90% of one-photo
  MIPGAN renders.
- R4 has only 74 rows; partners of many hosts are training persons and were excluded.


## Part 3: amendment 4, GD control table and cue floors (post hoc; registered at 6b3af89, 12:10:23; read once at 12:11:47)

Results review (Opus) `experiments/reviews/REVIEW_PR1_PART3_20261113.md`: accept with corrections; floors, all 18 verdicts and the part-A sample recomputed and matched; corrections applied.

Reader `src/PR1/gd_extra.py`; output `gd_extra.json`, `gd_extra_stdout.txt`. Cues: GD2 with `cues27.py` unchanged;
GD1 through `cue_floor._cue_one` (the networks' loader view at 512 px) plus file size. Times (git and file mtimes):
an 8-row cue smoke run wrote its files at 12:09:33-35; the full cues finished at 12:11:03 (GD1) and 12:11:34 (GD2),
after the registration commit (12:10:23); the reader ran once at 12:11:47. The network AUCs of these contrasts were
known from part 2, so the contrasts and the rule were chosen with them in view.

### Part B: is each network contrast beyond the 27-statistic floor? (rule: network − F ≥ +0.05 on ≥ 4 of 5)

F = max(best single statistic on the same images, s-lad, b-lad).

| Contrast | F (component) | A | B | Sb |
|---|---|---|---|---|
| GD1 X vs REC | 0.705 (file size of the 256 px file; 0.689 without it, verdicts unchanged) | 0.53-0.66 → not beyond | 0.46-0.56 → not beyond | 0.53-0.60 → not beyond |
| GD1 REC vs G | 0.996 (band power > .5) | 0.97-1.00 → not beyond by the rule (ceiling: the +0.05 bar is unreachable; no information) | 0.92-0.99 → same (ceiling) | 0.991-0.996 → same (ceiling; margins −0.005 to +0.00003, a tie) |
| GD1 X vs SAME | 0.730 (noise_std_face) | 0.64-0.74 → not beyond | 0.68-0.75 → inconclusive | 0.778, 0.821, 0.778, 0.846, 0.822 (network − F +0.048 to +0.116; seeds 403 and 405 miss the bar by 0.002 and 0.0015) → **inconclusive** (3 of 5) |
| GD2 R2 vs R0 | 0.902 (s-lad) | 0.96-0.99 (margin +0.055 to +0.083) → **beyond** | 0.91-0.98 (margin +0.009 to +0.075; seed 407 below the bar) → **beyond** | 0.992-0.998 (margin +0.090 to +0.095) → **beyond** |
| GD2 R4 vs R2 | 0.911 (b-lad) | 0.73-0.87 → not beyond | 0.81-0.91 → not beyond | 0.86-0.93 → not beyond |
| GD2 R4 vs R3 | 0.702 (b-lad) | 0.53-0.63 → not beyond | 0.58-0.67 → not beyond | 0.62-0.69 → not beyond |

- Printed, Sb, within quintiles of the best single statistic: GD1 X vs SAME 0.71-0.79; GD2 R4 vs R3 0.64-0.73; GD2 R2
  vs R0 0.99-1.00; GD1 REC vs G 0.97-0.99.
- In words: the networks exceed the simple-statistic floor only for one-photo MIPGAN render against camera photo
  (A, B and Sb, ≥ 4 of 5 seeds). They do not exceed it for two-person against same-person MIPGAN (R4 vs R3), MIPGAN
  morph against one-photo render (R4 vs R2), or DiffAE latent mix against reconstruction (X vs REC). GD1 X vs SAME is
  inconclusive for B and Sb and not beyond for A. REC vs G is at the ceiling.
- R4 and R3 also differ in simple statistics (b-lad 0.70), so the networks' 0.53-0.69 shows no identity sensitivity
  beyond pixel cues (R4 has 74 rows).
- F's best-single component is chosen on the same images and is optimistic. The GD2 R4 vs R3 and R4 vs R2 verdicts
  rest on the ladder-trained b-lad and are unaffected. A cross-fitted floor would move only Sb's GD1 X vs SAME
  (0.721; post hoc, reviewer), and that verdict stays inconclusive under the registered rule.

### Part A: printed control table (no rule)

- GD2 controls (Sb; A; B): R3 vs R2 0.79-0.83; 0.70-0.79; 0.74-0.82. R3m vs R2 0.74-0.81; 0.66-0.78; 0.70-0.80.
  R3 vs R3m 0.51-0.56; 0.48-0.54; 0.47-0.54. R2s vs R0 0.99-1.00; 0.96-0.99; 0.90-0.98.
- GD1 (Sb): X vs MIR 0.69-0.76; SAME vs REC 0.21-0.27; MIR vs REC 0.28-0.37.
- Cross-set (different sources and generators; descriptive): FFHQ stylegan_wplus morphs against GD2 one-photo
  MIPGAN renders R2: Sb 0.39-0.61, A 0.45-0.69, B 0.50-0.81. Against GD2 camera photos: 0.99-1.00 for every arm.
  Median logits for Sb: wplus morphs +3.06 to +3.18, R2 renders +2.88 to +3.23, R4 +3.37 to +3.42, R0 −3.48 to −3.53.
- Joint operating point per seed (Z2a usable AND Z2b-τ5 G_unseen ≤ 0.10):
  - At τ5: Sb seeds 405 and 406 (2 of 5); A and B none.
  - At the cut-off max(τ5, 0): Sb seeds 406 and 407 (2 of 5); A and B none. Sb's misses at the own rule are
    0.256-0.468, and seed 404's unseen flags are 0.134.
  - H-new-3 of the part-2 review (joint pass on ≥ 4 of 5 at max(τ5, 0)) is not met. max(τ5, 0) equals the own rule
    for every Sb seed. Changing the cut-off from τ5 to max(τ5, 0) does not raise Sb's joint pass (2 of 5 under
    both), so these reads give no evidence for the F10 change.

### Wording for GAN and diffusion results (proposed by the reviewer, for use before any sealed read)

"On development MIPGAN controls, our networks separate GAN re-renders of a single genuine photo from camera photos
beyond a 27-statistic floor, and flag 30-90% of them as morphs at the own rule. They do not separate two-person from
same-person MIPGAN renders, or MIPGAN morphs from one-photo renders, beyond that floor, nor diffusion latent mixes
from reconstructions. Scores on GAN- or diffusion-based benchmark cells may therefore reflect detection of
re-synthesis rather than of a second identity, and we do not claim them as morph-specific." Not to be written: "detects
GAN/diffusion morphs".
