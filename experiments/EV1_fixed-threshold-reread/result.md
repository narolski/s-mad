# Fixed-threshold re-read of existing scores (EV1): result

Owner run, 11 Nov 2026, DGX CPU only, zero GPU. No image was made, re-encoded or written. Pre-registration:
`prereg.md` (written 15:40 before any score value was read) and its Amendment 1 (saved 16:38, before any
amendment item was computed). Code: `src/EV1/` (`ev1_common.py`, `ev1_partA.py`, `ev1_feat.py`, `ev1_partB.py`,
`ev1_partC.py`, `ev1_amend.py`, `ev1_partB2.py`, `ev1_partC2.py`, `ev1_posthoc_gender.py`, `ev1_report.py`).
Large outputs (per-image features of 32,310 images, logs): `/mnt/t7/smad_next/EV1/`. Every command was run on
8 items per pool first (`--smoke`).

**Scope, applies to every table below.** Scores are on our 512-pixel aligned frames (the SelfMAD release with its
own preprocessing excepted). On these frames the releases' published numbers are not reproduced (released
MADation ViT-L/14 on FRLL-Morphs AMSL: 17.7% EER here against 7.26% published). A separate experiment, the
own-crop re-score of the audit rows (RS1), is redoing the key rows through each release's own preprocessing.

**Abbreviations.** FA = false-alarm rate, the share of genuine images flagged. Miss = the share of morphs not
flagged. EER = equal error rate. AUC = area under the ROC curve (0.5 = chance); O = max(AUC, 1 − AUC) for a
single attribute. CP = exact Clopper–Pearson 95% interval. devbona = the 5,033 development genuine photos of
`eval.csv` (FERET/FRGC D-MAD probe photos). E7 = the shrink-and-enlarge history-matched copies of the 204 FRLL
genuine photos, one pool per morph family (`resmatch`). Worst-pool threshold = the lowest threshold that keeps
FA at or below the target on every gated genuine pool. δ = 1 − face-recognition cosine of a morph's two
contributors. ρ = Spearman rank correlation. "Smiling half" = the 102 smiling FRLL genuine photos, which differ
from the neutral ones in expression and in capture detail (review of the expression re-read (C1b)); the effect is not called expression.
E5 variants = the registered benign variants JPEG 90, JPEG 70, JPEG 50, blur1 and resample50 of
`eval.csv`. Intervals are 95% two-way person bootstrap intervals (B = 2,000, seed 20261111) unless marked CP.

Detectors: the 10 release variants (`A12REL`: MADation ViT-B/16, ViT-L/14, FE ViT-B/16, FE ViT-L/14, FS ViT-B/16,
FS ViT-L/14, ViT-B/16 dnorm and dscale (diagnostic variants), SelfMAD (our pipeline), MixFaceNet-MAD (our frames));
the SelfMAD release with its own preprocessing; the MADation-recipe retrains M3 (ViT-B/16, 8 seeds) and M3L
(ViT-L/14, 5 seeds) at the last checkpoint; the other 38 recipe networks as a descriptive block (point
estimates only, see deviations). Thresholds: one per detector, the smallest devbona score with at most 5% (or
10%) of devbona above it; flag = score above it; never refit.

## 0. Checks, deviations, things to know before reading

- **Loader check.** Native EERs reproduce the record: released ViT-L/14 AMSL 17.7, Greedy-DiM 9.8, MorDIFF 28.9;
  released ViT-B/16 MorDIFF 4.9. Releases were read with `logit_noTTA` (it orders rows exactly as `score_noTTA`,
  checked for all 10; it avoids float32 ties at the threshold). Realised devbona FA 4.9 to 5.0% (5% threshold) and
  9.93 to 9.99% (10%) for every network except two in the descriptive block: M1 seed 3 has 275 devbona scores
  saturated at 1.0, so its 5% threshold flags nothing (FA 0 on every pool by construction); M2 seed 2 realises 4.79%.
- **SelfMAD own preprocessing has no devbona row** (registered fallback): its threshold is fitted on the 204 FRLL
  orig photos (FA there 4.9% by construction; labelled "test-fitted"), and it has no jpeg90, jpeg70 or blur1 rows.
- **SelfMAD release in our pipeline** scores devbona photos high: at its devbona threshold it flags at most 3.2%
  of any genuine pool (FEI smiling) but misses 50 to 100% of the morphs of every family (family mean 92.8%).
- **MixFaceNet-MAD release (our frames)** has AUC 0.002 to 0.168 on the FRLL-Morphs FaceMorpher, OpenCV, WebMorph
  and AMSL cells; nothing was flipped (registered). Its own crop branch is suspended.
- **Deviation 1.** The 38-network descriptive block has point estimates only (no intervals): the machine was at
  load 60 to 90 and swap was full; intervals were kept for the 24 primary networks.
- **Deviation 2.** Part C intervals use float32 cached weighted ranks (largest difference to the float64 path
  1.7e-6, checked on 2,000 replicates).
- **Deviation 3.** The Amendment 1 header first carried the time 16:45 by mistake; corrected to the file's save
  time 16:38:52 (first amendment output written 16:43). No other edit.
- **Added after reading (post hoc, not pre-registered):** the identity-dose slope within gender for every family
  (Part C.4), the null-conditional AUC with the best aligned-frame null as the stratifier (Part B.2).
- The re-scored registered MorDIFF genuine frames in the earlier MorDIFF ladder study's files agree with the eval
  file to at most 1.5e-3 (SelfMAD) and 2.4e-6 (MADation), so the devbona thresholds apply to those files.
- FRLL corner statistic (Amendment A3): smiling backdrop noise / neutral = 1.24 (median), smiling noisier in 87 of
  102 persons. This differs from the reviewer's "about five times" because the statistic differs (first
  differences in the four corners, not the reviewer's measure).

## Part A. False alarms and misses at one fixed threshold

### Part A.1. False alarms per genuine pool at the 5% development threshold (NIST-style block)

*Scores on our 512-pixel aligned frames (SelfMAD own preprocessing excepted), where published release numbers are not reproduced (released MADation ViT-L/14, FRLL-Morphs AMSL: 17.7% EER here, 7.26% published); the own-crop re-score of the audit rows (RS1) redoes the key rows.*

FA %, **neutral-only (102 photos) headline** / all 204 photos. Paired side changes against the same photos'
FRLL orig in `AM_A2_pool_block.csv` (count flagged only in the pool, count flagged only in orig, persons with a
change, exact McNemar p). Scope statement above applies.

| genuine pool | released MADation ViT-L/14 | released MADation ViT-B/16 | SelfMAD release, own preprocessing (test-fitted) | SelfMAD release, our pipeline |
|---|---|---|---|---|
| **stored-small: photo only stored at the published MorDIFF size (arm E of the earlier MorDIFF ladder study)** | **25.5** / 24.5 [CP 19–31]; +45/−2 photos, 35 persons, p 1.6e-11 | **20.6** / 27.5 [21–34]; +53/−1, 41 persons | **100** / 100 [98–100]; +194/−0, 100 persons | **0.0** / 1.0 |
| FRLL orig | 5.9 / 3.4 | 2.9 / 2.0 | 2.0 / 4.9 (fit pool) | 0.0 / 0.0 |
| JPEG 90 | 6.9 / 3.9 | 2.9 / 2.0 | not scored | 0.0 / 0.0 |
| JPEG 70 | 10.8 / 6.4 | 1.0 / 1.5 | not scored | 0.0 / 0.0 |
| JPEG 50 | 34.3 / 24.0; +43/−1, p 5e-12 | 1.0 / 1.0 | 0.0 / 1.5 | 0.0 / 0.0 |
| blur1 | 5.9 / 3.4 | 4.9 / 4.4 | not scored | 0.0 / 0.0 |
| resample50 | 4.9 / 2.9 | 7.8 / 7.4; +11/−0 | 96.1 / 95.1; +184/−0 | 0.0 / 0.5 |
| same photos, MorDIFF alignment | 13.7 / 9.8 | 3.9 / 3.9 | 11.8 / 14.2 | 0.0 / 0.0 |
| E7, the five FRLL-Morphs pools (range) | 3.9–6.9 / 2.5–3.9 | 2.9–7.8 / 2.0–6.4 | 2.0–83.3 / 4.9–85.3 (StyleGAN pool lowest) | 0.0 / 0.0 |
| E7, MorDIFF pool | 31.4 / 32.8; +62/−2 | 30.4 / 35.8; +69/−0 | 100 / 100 | 0.0 / 0.0 |
| E7, the six DiM pools (range) | 2.9 / 3.4–3.9 | 22.5–25.5 / 30.9–32.8; +59 to +63/−0 | 100 / 100 | 0.0 / 0.0–0.5 |
| FEI neutral / FEI smiling (all) | 0.0 / 0.5 | 0.0 / 2.1 | not scored | 0.0 / 3.2 |
| FFHQ orig; its five E7 pools | 22.1 [20–24]; 18.6–22.1 | 0.3; 0.3–8.8 | not scored | 1.6; 1.6–2.7 |

At the 10% threshold (all photos): released ViT-L/14 JPEG 50 54.9%, E7 MorDIFF 48.0%, FFHQ 34.9%; released
ViT-B/16 resample50 18.1%, E7 MorDIFF 73.5%; SelfMAD own resample50 98.0% (`A1_false_alarms.csv`).

Other rows (all photos, 5%; `A1_false_alarms.csv`): FE ViT-L/14 at most 2.5% on the FRLL variants but 35.8% on the
MorDIFF alignment and 31.4% on E7 MorDIFF; FE ViT-B/16 44.6% on E7 MorDIFF, 10.4% on FEI; ViT-B/16 dnorm up to
60.3% (E7 MorDIFF) and 46.1% (MorDIFF alignment); M3 seeds: E7 MorDIFF 21 to 99%, E7 DiM 23 to 67%, resample50 2 to 36%; M3L seeds:
JPEG 70 8 to 25%, JPEG 50 23 to 50%, MorDIFF alignment 43 to 75%, E7 MorDIFF 59 to 87%; the SelfMAD-style
retrains M4 (descriptive) flag 74 to 100% of every FRLL pool at their devbona threshold.

### Part A.2. Misses per family: native threshold and worst-pool threshold, 5%

*Scores on our 512-pixel aligned frames (SelfMAD own preprocessing excepted), where published release numbers are not reproduced (released MADation ViT-L/14, FRLL-Morphs AMSL: 17.7% EER here, 7.26% published); the own-crop re-score of the audit rows (RS1) redoes the key rows.*

Miss % at the native devbona threshold / at the worst-pool threshold (gated: FRLL orig, JPEG 90, JPEG 70,
resample50, the DiM and MorDIFF copies of orig, the 12 E7 pools, devbona). Family mean over the 12 families.
Worst-pool with the gated FRLL pools restricted to neutral photos (Amendment headline) in the last column.

| detector | AMSL | Face-Morpher | OpenCV | StyleGAN | Web-Morph | MorDIFF | DiM-A | DiM-C | Fast-DiM | Fast-DiM-ODE | Greedy-DiM | Greedy-DiM-S | family mean | family mean, neutral-only gating |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| released ViT-L/14 | 89 / 100 | 0.4 / 1.9 | 1.1 / 2.1 | 98 / 99 | 9 / 29 | 44 / 72 | 80 / 95 | 47 / 78 | 76 / 94 | 63 / 92 | 60 / 99 | 16 / 31 | 48.6 / 66.1 | 62.9 |
| released ViT-B/16 | 82 / 99 | 4.8 / 36 | 5.2 / 29 | 90 / 100 | 27 / 84 | 12 / 61 | 73 / 97 | 28 / 80 | 67 / 97 | 80 / 98 | 100 / 100 | 29 / 63 | 49.8 / 78.8 | 74.5 |
| SelfMAD own (test-fitted) | 0.1 / 100 | 0.2 / 34 | 0.2 / 19 | 33 / 100 | 6.5 / 100 | 0.0 / 100 | 1.8 / 100 | 0.0 / 96 | 6.4 / 100 | 33 / 100 | 18 / 100 | 0.0 / 93 | 8.2 / 86.8 | 85.5 |
| SelfMAD, our pipeline | 100 / 100 | 66 / 66 | 50 / 50 | 100 / 100 | 100 / 100 | 100 / 100 | 100 / 100 | 99 / 99 | 100 / 100 | 100 / 100 | 100 / 100 | 98 / 98 | 92.8 / 92.8 | 92.8 |
| FE ViT-L/14 | 68 / 98 | 6.5 / 33 | 6.9 / 34 | 62 / 97 | 24 / 79 | 34 / 91 | 42 / 95 | 47 / 93 | 64 / 98 | 44 / 91 | 71 / 99 | 29 / 83 | 41.4 / 82.5 | 75.7 |
| M3, seed mean of 8 | 44 / 100 | 3.3 / 48 | 1.4 / 28 | 82 / 100 | 7.3 / 88 | 4.7 / 59 | 12 / 69 | 1.3 / 33 | 8.4 / 56 | 34 / 85 | 99 / 100 | 3.6 / 30 | 25.1 / 66.3 | 59.0 |
| M3L, seed mean of 5 | 0.2 / 39 | 0.0 / 0.5 | 0.3 / 1.1 | 97 / 99 | 0.0 / 5.2 | 36 / 90 | 35 / 86 | 59 / 83 | 78 / 96 | 53 / 91 | 77 / 100 | 55 / 66 | 40.9 / 63.0 | 64.5 |

Worst-pool misses with intervals are in `A2_miss.csv`; for example released
ViT-L/14 FaceMorpher 1.9 [1–4], OpenCV 2.1 [0–5], WebMorph 28.7 [19–43], MorDIFF 72.2 [59–84]. The pool that sets
the worst-pool threshold: E7 MorDIFF (ViT-L/14), E7 Fast-DiM-ODE (ViT-B/16), resample50 (SelfMAD own).

### Part A.3. Crossed table, morph variant × genuine variant (`A3_crossed.csv`, neutral-only: `AM_A3_crossed_neutral.csv`)

*Scores on our 512-pixel aligned frames (SelfMAD own preprocessing excepted), where published release numbers are not reproduced (released MADation ViT-L/14, FRLL-Morphs AMSL: 17.7% EER here, 7.26% published); the own-crop re-score of the audit rows (RS1) redoes the key rows.*

260 cells per detector (75 with the genuine photos more processed than the morphs, "G>M"). AUC with the genuine
class restricted to neutral photos (headline), all photos in brackets, morph orig row:

- Released ViT-L/14: AMSL against JPEG 50 genuine photos 0.191 (0.344); StyleGAN 0.037 (0.076); DiM-A 0.273
  (0.389); FaceMorpher at least 0.997 and OpenCV at least 0.990 in every cell. 10 of 75 G>M cells below 0.5 (all
  photos).
- Released ViT-B/16: AMSL against resample50 0.772 (0.751), against E7 0.801 (0.790); Greedy-DiM against E7 0.066
  (0.064); DiM-A against E7 0.484 (0.438). 4 of 75 G>M cells below 0.5.
- SelfMAD own preprocessing: against resample50 genuine photos 0.164 to 0.973 by family (WebMorph 0.318, StyleGAN
  0.195); against E7 0.030 (Greedy-DiM) to 0.998 (OpenCV). 6 of 24 scored G>M cells below 0.5.
- Released FE ViT-L/14: no G>M cell below 0.5 (lowest 0.842 on AMSL against JPEG 50).

### Part A.4. Ranking and the first falsifier

*Scores on our 512-pixel aligned frames (SelfMAD own preprocessing excepted), where published release numbers are not reproduced (released MADation ViT-L/14, FRLL-Morphs AMSL: 17.7% EER here, 7.26% published); the own-crop re-score of the audit rows (RS1) redoes the key rows.*

Kendall τ-b between the order by native family-mean EER and by worst-pool family-mean miss (12 rows: 10 releases,
M3 and M3L seed means): **0.394** at 5% (p 0.086), 0.515 at 10%; 23 rows (networks separately): 0.423 / 0.565.
Largest rise native → worst-pool: 52.4 points (M3 seed 6); 14 of 23 networks rise by 20 points or more at 5%
(19 of 23 at 10%). Native family-mean EER / worst-pool family-mean miss: M3 8.6% / 66.3%, SelfMAD our pipeline
13.2 / 92.8, ViT-B/16 15.3 / 78.8, FE ViT-L/14 16.3 / 82.5, ViT-L/14 16.7 / 66.1, M3L 17.5 / 63.0.

### Part A.5. Both class policies for the diffusion and GAN controls (Amendment A1; rates only)

*Scores on our 512-pixel aligned frames (SelfMAD own preprocessing excepted), where published release numbers are not reproduced (released MADation ViT-L/14, FRLL-Morphs AMSL: 17.7% EER here, 7.26% published); the own-crop re-score of the audit rows (RS1) redoes the key rows.*

MorDIFF (control images of the earlier MorDIFF ladder study; CP intervals, threshold uncertainty not included).
Policy X = reconstructions left out (worst-pool over camera pools + stored-small). Policy G = reconstructions
counted genuine (also gated). Rates %, native threshold / policy X / policy G:

| detector | stored-small FA | reconstruction FA, 20 steps | reconstruction FA, 100 steps | same-person mix flag, 20 / 100 steps | miss, published MorDIFF (200) | miss, our same-pair morphs, 20 steps | miss, eval MorDIFF (1,000) |
|---|---|---|---|---|---|---|---|
| released ViT-L/14 | 24.5 / 2.5 / 0.5 | 62.3 / 25.5 / 4.9 | 40.7 / 9.3 / 2.0 | 56.9 / 56.9 at native | 39.5 / 73.5 / 94.5 | 37.5 / 69.5 / 96.5 | 44.1 / 72.2 / 94.0 |
| released ViT-B/16 | 27.5 / 2.9 / 0.0 | 96.1 / 35.3 / 4.9 | 42.6 / 3.4 / 0.0 | 62.7 / 17.6 at native | 14.0 / 63.0 / 91.5 | 10.0 / 65.0 / 92.0 | 11.6 / 61.2 / 90.4 |
| SelfMAD own (test-fitted) | 100 / 4.9 / 4.9 | 100 / 0.0 / 0.0 | 100 / 0.0 / 0.0 | 100 / 100 at native | 0.0 / 100 / 100 | 0.0 / 100 / 100 | 0.0 / 100 / 100 |
| released FE ViT-L/14 | 20.6 / 1.5 / 1.5 | 42.6 / 3.9 / 3.9 | 27.5 / 2.9 / 2.9 | 42.2 / 60.8 at native | 35.5 / 92.0 / 92.0 | 35.5 / 91.5 / 91.5 | 33.7 / 90.5 / 90.5 |

StyleGAN3 (H3 set: 423 two-identity morphs, 423 one-identity renders of a third CASIA person, 423 spread-matched
renders): render FA and morph miss %, native / policy X / policy G:

| detector | one-identity render FA | spread-matched render FA | two-identity morph miss |
|---|---|---|---|
| released ViT-L/14 | 72.6 / 60.0 / 4.5 | 68.8 / 56.7 / 5.0 | 36.2 / 51.3 / 96.9 |
| released ViT-B/16 | 77.1 / 54.8 / 1.2 | 87.5 / 69.5 / 5.0 | 15.4 / 40.4 / 97.6 |
| SelfMAD own (test-fitted) | 100 / 57.0 / 5.0 | 99.8 / 40.7 / 2.1 | 0.2 / 64.5 / 99.8 |
| released FE ViT-L/14 | 52.2 / 10.4 / 5.0 | 56.5 / 11.3 / 3.8 | 47.8 / 90.3 / 96.7 |

All detectors and the 10% rows: `AM_A1_class_policies.csv`. Recipe networks have no last-checkpoint scores on
these sets and are not in this block.

## Part B. Null rows

Cells: the 12 scored cells (FRLL-Morphs × 5, MorDIFF, DiM × 6) and the 5 corrected MAD22 cells (null rows only).
Headline genuine class: neutral-only (102 photos) in the 11 imbalanced scored cells and corrected MAD22 Webmorph;
all 204 photos in the balanced cells (MorDIFF, corrected MAD22 FaceMorpher, MIPGAN-I, MIPGAN-II, OpenCV). The
null formerly named "expression label" is the "smiling-half label". Scope statement above applies.

### Part B.1. Null rows and diagnostic cells (`B_null_rows.csv`, `B_cells.csv`, `AM_B_cells_neutral.csv`, `AM_B_splithalf.csv`)

*Scores on our 512-pixel aligned frames (SelfMAD own preprocessing excepted), where published release numbers are not reproduced (released MADation ViT-L/14, FRLL-Morphs AMSL: 17.7% EER here, 7.26% published); the own-crop re-score of the audit rows (RS1) redoes the key rows.*

| cell | best non-content null, O | best aligned-frame null, O | 32 × 32 thumbnail (content null) | best morph-free network AUC (all photos) |
|---|---|---|---|---|
| FRLL-Morphs AMSL | stored width 1.000 | border 1.000 | 1.000 | 1.000 |
| FRLL-Morphs FaceMorpher | stored width 1.000 | border 1.000 | 1.000 | 0.999 |
| FRLL-Morphs OpenCV | stored width 1.000 | border 1.000 | 1.000 | 0.953 |
| FRLL-Morphs StyleGAN | stored width 1.000 | border 1.000 | 0.998 | 0.902 |
| FRLL-Morphs WebMorph | stored width 1.000 | border 0.993 | 0.997 | 1.000 |
| MorDIFF (balanced) | stored width 1.000 | colour, aligned 0.781 | 0.968 | 1.000 |
| DiM-A, DiM-C, Fast-DiM, Fast-DiM-ODE, Greedy-DiM, Greedy-DiM-S | stored width 1.000 | border 0.997–1.000 | 0.997–0.999 | 1.000 |
| corrected MAD22 FaceMorpher, MIPGAN-I, MIPGAN-II (balanced) | stored width 1.000 | border 0.999–1.000 | 0.984–0.998 | not scored |
| corrected MAD22 OpenCV (balanced) | stored width 1.000 | colour, aligned 0.761 | 0.623 | not scored |
| corrected MAD22 Webmorph | chroma subsampling 1.000 | colour, aligned 0.748 (all photos 0.767) | 0.671 (all photos 0.770) | not scored |

Other nulls per cell (all photos; `B_null_rows.csv`): six colour statistics of the aligned frame 0.70–0.996
(stored file 0.63–1.00); smiling-half label 0.750 in the 11 imbalanced scored cells and corrected MAD22 Webmorph,
0.50 elsewhere; 5-attribute file regression 1.000 in the 12 scored cells. With the neutral-only genuine class the headline values are
unchanged to the third decimal except where shown.

- **Diagnostic cells (best non-content null below 0.90): 0 of 17**, with all photos and with the neutral-only
  headline. Split-half choice (Amendment A5): the null chosen on either half of the persons is stored width
  (chroma subsampling for corrected MAD22 Webmorph) and scores 1.000 on the other half in every cell, both genuine
  classes: 0 of 17 under both splits; **the count is stable**.
- Secondary count, only the nulls on the aligned frame that the detectors see (colour, border, smiling-half
  label): 3 of 17 below 0.90 (MorDIFF 0.781, corrected MAD22 OpenCV 0.761, corrected MAD22 Webmorph 0.748
  neutral-only). Secondary count, primary rule and every morph-free network below 0.90: 0 of 12 scored cells.
- Morph-free networks (the morph-free study (A47) I-3, last checkpoint): M3 seeds reach EER ≤ 2.6% on 10, 9 and 10
  of the 12 scored cells; M1 seeds on 0, 0 and 1.

### Part B.2. Detector AUC with the neutral-only headline, and excess over the best non-content null (`AM_B_detectors_neutral.csv`, `B_detectors.csv`)

*Scores on our 512-pixel aligned frames (SelfMAD own preprocessing excepted), where published release numbers are not reproduced (released MADation ViT-L/14, FRLL-Morphs AMSL: 17.7% EER here, 7.26% published); the own-crop re-score of the audit rows (RS1) redoes the key rows.*

AUC / EER %, **neutral-only** (all photos in brackets); MorDIFF balanced (all photos only):

| detector | AMSL | FaceMorpher | OpenCV | StyleGAN | WebMorph | MorDIFF | DiM-A | DiM-C | Fast-DiM | Fast-DiM-ODE | Greedy-DiM | Greedy-DiM-S |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| released ViT-L/14 | **0.814 / 24.5** (0.886 / 17.7) | **0.999 / 1.0** (0.999 / 1.0) | **0.997 / 1.1** (0.998 / 1.0) | **0.308 / 65.7** (0.512 / 52.4) | **0.986 / 6.9** (0.992 / 4.9) | 0.803 / 28.9 | **0.779 / 27.4** (0.863 / 22.0) | **0.868 / 21.6** (0.919 / 16.2) | **0.770 / 28.2** (0.858 / 22.6) | **0.867 / 21.6** (0.919 / 15.2) | **0.911 / 13.8** (0.947 / 9.8) | **0.963 / 9.9** (0.977 / 8.8) |
| released ViT-B/16 | **0.909 / 15.5** (0.920 / 15.1) | **0.997 / 2.9** (0.997 / 2.8) | **0.997 / 3.0** (0.997 / 2.9) | **0.849 / 23.3** (0.862 / 23.1) | **0.983 / 6.0** (0.985 / 4.9) | 0.987 / 4.9 | **0.861 / 20.7** (0.872 / 20.6) | **0.977 / 6.8** (0.980 / 6.4) | **0.901 / 16.6** (0.911 / 16.1) | **0.817 / 26.5** (0.829 / 25.9) | **0.436 / 54.9** (0.458 / 54.0) | **0.976 / 8.7** (0.980 / 6.9) |
| SelfMAD own | **0.998 / 1.0** (0.995 / 2.9) | **0.999 / 0.1** (0.999 / 0.4) | **0.999 / 0.1** (0.999 / 0.1) | **0.946 / 12.9** (0.926 / 14.2) | **0.990 / 3.7** (0.978 / 5.9) | 0.993 / 2.5 | **0.996 / 2.0** (0.990 / 3.9) | **0.999 / 1.0** (0.999 / 2.0) | **0.991 / 3.8** (0.978 / 5.8) | **0.959 / 10.8** (0.936 / 13.1) | **0.980 / 6.6** (0.959 / 8.4) | **1.000 / 1.0** (0.999 / 2.0) |
| released FE ViT-L/14 | **0.889 / 20.6** (0.869 / 21.6) | **0.995 / 3.9** | **0.994 / 3.9** | **0.909 / 18.6** (0.892 / 19.2) | **0.978 / 7.9** | 0.699 / 34.8 | **0.940 / 13.8** | **0.925 / 15.8** | **0.895 / 19.5** | **0.930 / 14.7** | **0.880 / 21.8** | **0.962 / 10.7** |
| released FE ViT-B/16 | **0.903 / 17.6** (0.813 / 26.0) | **0.970 / 7.8** (0.928 / 16.7) | **0.967 / 8.7** (0.919 / 18.6) | **0.834 / 24.5** (0.713 / 35.3) | **0.935 / 13.7** (0.869 / 22.5) | 0.655 / 39.7 | **0.928 / 15.6** (0.853 / 23.9) | **0.886 / 19.6** (0.786 / 28.9) | **0.836 / 25.4** (0.727 / 35.2) | **0.873 / 19.7** (0.778 / 29.4) | **0.690 / 36.3** (0.558 / 47.0) | **0.946 / 11.8** (0.890 / 21.0) |
| M3, seed mean of AUC | **0.976** | **0.999** | **0.999** | **0.650** | **0.997** | 0.990 | **0.995** | **0.999** | **0.996** | **0.959** | **0.580** | **0.997** |
| M3L, seed mean of AUC | **0.999** | **1.000** | **1.000** | **0.376** | **1.000** | 0.550 | **0.925** | **0.768** | **0.616** | **0.875** | **0.761** | **0.708** |

Excess over the best non-content null: the best null is 1.000 in all 12 scored cells, so the excess equals
AUC − 1.000 for every detector and cell; its upper 95% bound is at most 0.000 everywhere (for example released
ViT-L/14 AMSL neutral-only −0.186 [−0.244, −0.130]; released ViT-B/16 Greedy-DiM −0.563; SelfMAD own FaceMorpher
−0.000 [−0.002, 0.000]).

Null-conditional AUC. Registered version (quintiles of the best per-image null, stored width): a stratum with
≥ 5 of each class exists only in MorDIFF (one stratum), where width still separates the classes inside the
stratum, so it is not a matched comparison; there the release values differ from the raw AUC by up to 0.25
(FE ViT-B/16 0.906 against 0.654; ViT-L/14 0.885 against 0.803). Post hoc version (best aligned-frame null as the
stratifier): the border fraction leaves one usable stratum in 11 cells; MorDIFF has five strata (colour), where
ViT-L/14 0.792 against 0.803, ViT-B/16 0.984 against 0.987, SelfMAD own 0.994 against 0.993 (`B_detectors.csv`).

### Part B.3. Smiling half (Amendment A3; `B_expression.csv`, `AM_A3_neutral_above_smiling.csv`, `AM_corner_check.json`)

*Scores on our 512-pixel aligned frames (SelfMAD own preprocessing excepted), where published release numbers are not reproduced (released MADation ViT-L/14, FRLL-Morphs AMSL: 17.7% EER here, 7.26% published); the own-crop re-score of the audit rows (RS1) redoes the key rows.*

EER % with the genuine class all / neutral-only / smiling-only, released ViT-L/14: AMSL 17.7 / 24.5 / 7.9,
StyleGAN 52.4 / 65.7 / 34.3, DiM-A 22.0 / 27.4 / 10.8, Greedy-DiM 9.8 / 13.8 / 5.8, MorDIFF 28.9 / 31.4 / 26.3.
Released ViT-B/16: within 2 points in 9 of 12 cells (largest WebMorph 6.0 / 2.9 neutral against smiling).
SelfMAD own: neutral-only lower than all photos in 11 of 12 cells, equal in OpenCV (AMSL 1.0 against 2.9).

Within-person share of persons whose neutral photo scores above their own smiling photo (ties half; 95% person
bootstrap). FEI was checked first: its neutral and smiling backdrops have equal corner noise (median ratio 0.99;
smiling noisier in 44% of 187 persons), while FRLL does not (ratio 1.24; 85% of 102).

| detector | FRLL orig | stored-small | JPEG 50 | resample50 | MorDIFF alignment | E7 AMSL | E7 MorDIFF | E7 DiM-A | FEI (equal backdrop) |
|---|---|---|---|---|---|---|---|---|---|
| released ViT-L/14 | 0.99 [0.97, 1.00] | 0.70 [0.61, 0.78] | 0.89 | 0.95 | 0.79 | 0.93 | 0.53 [0.43, 0.63] | 0.78 | 0.41 [0.34, 0.48] |
| released ViT-B/16 | 0.58 [0.48, 0.68] | 0.33 | 0.48 | 0.41 | 0.53 | 0.50 | 0.34 | 0.25 | 0.39 [0.32, 0.45] |
| SelfMAD own | 0.48 [0.38, 0.59] | 0.25 | 0.44 | 0.41 | 0.42 | 0.39 | 0.46 | 0.46 | not scored |
| SelfMAD, our pipeline | 0.31 | 0.25 | 0.38 | 0.16 | 0.41 | 0.15 | 0.36 | 0.29 | 0.41 [0.34, 0.49] |
| released FE ViT-L/14 | 0.34 | 0.29 | 0.33 | 0.35 | 0.21 | 0.36 | 0.28 | 0.39 | 0.15 [0.10, 0.20] |
| released FE ViT-B/16 | 0.09 | 0.14 | 0.04 | 0.08 | 0.10 | 0.08 | 0.16 | 0.08 | 0.26 [0.20, 0.32] |
| MixFaceNet-MAD (our frames) | 0.47 | – | 0.40 | 0.42 | 0.53 | 0.43 | 0.56 | 0.47 | 0.94 [0.91, 0.97] |
| M3 seeds (range) | 0.67–0.97 | – | 0.71–0.97 | 0.26–0.82 | 0.66–0.93 | 0.32–0.89 | 0.42–0.71 | 0.11–0.66 | 0.20–0.53 |
| M3L seeds (range) | 1.00–1.00 | – | 0.93–0.98 | 0.99–1.00 | 0.94–0.99 | 0.99–1.00 | 0.78–0.92 | 0.97–1.00 | 0.08–0.18 |

All E5 variants, all 12 E7 pools and the remaining releases: `AM_A3_neutral_above_smiling.csv`.

## Part C. Identity dose inside the morph class

### Part C.1. Which names expose the pair, and the oracle power check (run before any detector score was loaded)

*Scores on our 512-pixel aligned frames (SelfMAD own preprocessing excepted), where published release numbers are not reproduced (released MADation ViT-L/14, FRLL-Morphs AMSL: 17.7% EER here, 7.26% published); the own-crop re-score of the audit rows (RS1) redoes the key rows.*

Every family exposes the contributor pair in the file name: FRLL-Morphs and DiM as `AAA_BBB` (no expression; DiM
neutral by its README, FRLL-Morphs neutral by the expression probe of the cue checks (C1)), MorDIFF as `morph_AAA_EE_and_BBB_EE` (with
expression). 10 FRLL-Morphs self-pairs were excluded. Gender is not in any file name; for MorDIFF it is in the
release's folder names. Oracle = 1 − the lower cosine of the morph to its two contributors (glintr100).

| family | stratum | n | median δ | oracle ρ [95%] | status |
|---|---|---|---|---|---|
| FRLL-Morphs AMSL, FaceMorpher, OpenCV, StyleGAN, WebMorph | neutral | 2,175 / 1,219 × 4 | 0.962–0.963 | – | no power (no oracle embeddings) |
| MorDIFF | neutral / smiling | 500 / 500 | 0.884 / 0.889 | 0.522 [0.41, 0.61] / 0.484 [0.36, 0.59] | power |
| DiM-C | neutral | 500 | 0.884 | 0.515 [0.39, 0.62] | power |
| Greedy-DiM | neutral | 500 | 0.884 | 0.628 [0.52, 0.71] | power |
| Greedy-DiM-S | neutral | 500 | 0.884 | 0.532 [0.41, 0.63] | power |
| DiM-A | neutral | 500 | 0.884 | – (secondary, 100 morphs of another file: 0.579 [0.30, 0.74]) | no power (no oracle embeddings) |
| Fast-DiM, Fast-DiM-ODE | neutral | 500 / 499 | 0.884 | – | no power (no oracle embeddings) |

Contributor distances agree with the embeddings of the landmark ladder study (AR1) at Pearson 0.95 to 0.98.

### Part C.2. Detector slopes ρ(score, δ) [95%] (`C_dose.csv`)

*Scores on our 512-pixel aligned frames (SelfMAD own preprocessing excepted), where published release numbers are not reproduced (released MADation ViT-L/14, FRLL-Morphs AMSL: 17.7% EER here, 7.26% published); the own-crop re-score of the audit rows (RS1) redoes the key rows.*

| detector | AMSL | FaceMorpher | OpenCV | StyleGAN | WebMorph | MorDIFF neutral | MorDIFF smiling | DiM-C | Greedy-DiM | Greedy-DiM-S | DiM-A, Fast-DiM, Fast-DiM-ODE |
|---|---|---|---|---|---|---|---|---|---|---|---|
| released ViT-L/14 | +0.09 [0.00, 0.18] | +0.17 [0.05, 0.27] | +0.18 [0.05, 0.28] | −0.09 [−0.21, 0.03] | +0.13 [0.02, 0.24] | +0.14 [−0.03, 0.29] | +0.16 [0.01, 0.30] | +0.08 [−0.07, 0.23] | +0.13 [−0.04, 0.28] | +0.18 [0.02, 0.34] | +0.04, −0.00, +0.07 |
| released ViT-B/16 | +0.09 | +0.11 [0.00, 0.23] | +0.10 | +0.04 | +0.09 | +0.10 [−0.06, 0.26] | +0.06 | +0.11 [−0.04, 0.26] | −0.05 [−0.20, 0.11] | +0.15 [−0.01, 0.30] | +0.13, +0.03, −0.12 |
| SelfMAD own | +0.03 | +0.02 | +0.05 | −0.07 | −0.04 | +0.07 [−0.08, 0.22] | −0.04 | −0.04 [−0.20, 0.13] | −0.06 [−0.20, 0.09] | +0.17 [0.03, 0.31] | +0.06, +0.04, −0.08 |
| M3 seeds (range) | 0.00 to +0.07 | +0.15 to +0.17 | +0.13 to +0.18 | −0.04 to +0.07 | +0.05 to +0.10 | +0.05 to +0.16 | +0.02 to +0.15 | +0.08 to +0.17 | −0.08 to +0.11 | +0.05 to +0.11 | |
| M3L seeds (range) | −0.07 to +0.03 | +0.16 to +0.19 | +0.18 to +0.21 | −0.12 to −0.05 | +0.04 to +0.08 | 0.00 to +0.06 | +0.03 to +0.11 | 0.00 to +0.05 | −0.07 to +0.07 | +0.13 to +0.16 | |

### Part C.3. Controls (Amendment A4): the same computation for the morph-free networks and for file size (`AM_C_controls.csv`)

*Scores on our 512-pixel aligned frames (SelfMAD own preprocessing excepted), where published release numbers are not reproduced (released MADation ViT-L/14, FRLL-Morphs AMSL: 17.7% EER here, 7.26% published); the own-crop re-score of the audit rows (RS1) redoes the key rows.*

Strata where a control's 95% interval excludes 0: stored file size in DiM-C, ρ −0.223 [−0.359, −0.068]; morph-free
M3 seed 2 and seed 3 in FRLL-Morphs StyleGAN, −0.114 [−0.210, −0.003] and −0.126 [−0.221, −0.021]. Reading as
registered: **in DiM-C and in FRLL-Morphs StyleGAN the dose test can be produced by construction** (a control has a
slope). In the other 10 families and in all four MorDIFF expression × gender strata neither control has a slope
(all six morph-free networks and file size have intervals that include 0). All control slopes found are negative.

### Part C.4. MorDIFF by expression and gender (Amendment A4), and every family by gender (post hoc)

*Scores on our 512-pixel aligned frames (SelfMAD own preprocessing excepted), where published release numbers are not reproduced (released MADation ViT-L/14, FRLL-Morphs AMSL: 17.7% EER here, 7.26% published); the own-crop re-score of the audit rows (RS1) redoes the key rows.*

MorDIFF, 250 morphs per stratum (all MorDIFF pairs are same-gender), ρ [95%]:

| detector | neutral, female | neutral, male | smiling, female | smiling, male |
|---|---|---|---|---|
| released ViT-L/14 | +0.06 [−0.16, 0.27] | −0.03 [−0.25, 0.20] | +0.05 [−0.14, 0.24] | +0.01 [−0.20, 0.22] |
| released ViT-B/16 | −0.01 | +0.02 | −0.08 | −0.01 |
| SelfMAD own | +0.08 | +0.01 | −0.08 | −0.10 |
| M3 seeds (range) | +0.01 to +0.10 | −0.10 to +0.01 | −0.08 to +0.03 | −0.09 to +0.03 |
| M3L seeds (range) | −0.03 to +0.02 | +0.03 to +0.07 | +0.04 to +0.09 | +0.01 to +0.05 |

Post hoc (not pre-registered, `PH_gender_*.csv`): gender of all 102 FRLL persons taken from the MorDIFF folders (no
conflict). Every FRLL-Morphs and DiM pair is same-gender too. Within gender the oracle keeps power (ρ 0.44 to 0.65
in the eight powered strata). Within gender the released ViT-L/14 slopes are FaceMorpher +0.02 / +0.09, OpenCV
+0.07 / +0.06, WebMorph +0.09 / +0.08, AMSL +0.03 / +0.02, Greedy-DiM-S +0.09 / +0.17 (female / male); every one
of its 26 within-gender intervals includes 0. Across the three named releases one within-gender interval excludes 0
(SelfMAD own, Greedy-DiM-S female, +0.23 [0.02, 0.41]). M3L within gender: FaceMorpher +0.06 to +0.14, OpenCV
+0.06 to +0.15.

## Falsifiers, applied as registered

*Scores on our 512-pixel aligned frames (SelfMAD own preprocessing excepted), where published release numbers are not reproduced (released MADation ViT-L/14, FRLL-Morphs AMSL: 17.7% EER here, 7.26% published); the own-crop re-score of the audit rows (RS1) redoes the key rows.*

| falsifier (verbatim source in `prereg.md`) | measured | reading |
|---|---|---|
| Evaluation idea 0: metric dropped if τ ≥ 0.8 and no network rises by ≥ 20 points | τ = 0.394; 14 of 23 networks rise ≥ 20 points (max 52.4) | metric kept |
| Evaluation idea 0, own detector: FA > 10% on a gated pool at the 5% threshold | no own detector exists | not applicable; existing networks over the bar: 47 of 62 (e.g. ViT-L/14 1 pool, ViT-B/16 7 pools, SelfMAD own 13, M3 7–13, M3L 2–3) |
| Evaluation idea 1: dropped if ≥ 10 of 17 cells are diagnostic | 0 of 17 (all photos, neutral-only headline, and both split-half choices); 3 of 17 if only aligned-frame nulls count | not dropped by this clause; count stable under the split |
| Evaluation idea 1: or if on every cell with overlap each release's null-conditional AUC is within 0.03 of its raw AUC | overlap only in MorDIFF (one stratum, still separated by width inside it); differences up to 0.25 (FE ViT-B/16 0.906 vs 0.654) | not met |
| Evaluation idea 1: expression row crossed out if neutral-only and smiling-only EERs are within 2 points for every release | released ViT-L/14 AMSL 24.5 / 7.9, StyleGAN 65.7 / 34.3; released ViT-B/16 within 2 points in 9 of 12 cells | not crossed out (row renamed "smiling half", per the C1b review) |
| Evaluation idea 1 prediction: morph-free M3 at 0.0–2.6% EER on 11–12 of 17 cells | 10, 9, 10 of the 12 scored cells (seeds 1–3); M1: 0, 0, 1 | stated |
| Invariance idea 0 (audit): with oracle power, ρ ≤ 0.10 and upper bound < 0.20 for ViT-L/14 release and M3L on all four FRLL landmark families | no oracle embeddings for any FRLL-Morphs family | not applicable: power not shown. Descriptive: the condition holds in 1 of 4 families for the release (AMSL), 2 of 4 for each M3L network |
| Identity idea 1: upper bound ≤ +0.10 in every generator family = no identity reading there | powered generator strata: MorDIFF neutral and smiling, DiM-C, Greedy-DiM, Greedy-DiM-S. Upper bound ≤ 0.10 in 0 of 5 strata for ViT-L/14, ViT-B/16, FE ViT-L/14, FE ViT-B/16, dnorm, dscale and 11 of the 13 M3 / M3L networks; 1 of 5 (Greedy-DiM) for SelfMAD in both pipelines, M3 seed 3 and M3L seed 2; 2 of 5 for MixFaceNet-MAD; 3 of 5 for FS ViT-L/14 and FS ViT-B/16 | sentence holds for no detector in every powered generator family; "no identity reading there" holds per stratum as listed (`C_partC.json`) |
| Identity idea 1: oracle ρ < 0.3 voids a family | oracle ρ 0.48–0.63 where computable | DiM-C, Greedy-DiM, Greedy-DiM-S, MorDIFF not void; the other 8 families without an oracle |
| Amendment A4: a control slope means the dose test can be produced by construction | DiM-C (file size), FRLL-Morphs StyleGAN (two morph-free networks) | stated for those two families |

## What could not be verified

- No scores on each release's own crop (except SelfMAD); RS1 is redoing that. All release rows are on our frames.
- SelfMAD own preprocessing: no development pool, no JPEG 90 / 70 or blur1 rows, no FEI or FFHQ scores; its
  thresholds are test-fitted.
- Oracle power for the five FRLL-Morphs families, DiM-A (beyond 100 morphs), Fast-DiM and Fast-DiM-ODE: no morph
  embeddings exist; computing them (about 8,500 images through the existing glintr100 route) needs the route's
  onnxruntime provider set to CPU or a GPU slot; not done (task restricted the oracle to existing embeddings).
- Corrected MAD22: null rows only; no detector score exists on it. The old `eval.csv` MAD22 subset was never read.
- FFHQ has no identity labels (CP by image); its classes share people (manifest note). Recipe networks have no
  last-checkpoint FFHQ scores.
- FRLL-Morphs morph expression is inferred, not documented; DiM expression from its README.
- The smiling half differs from the neutral half in capture detail (file size, backdrop noise); no analysis here
  separates expression from detail. On FEI, whose two sets pass the backdrop check, the within-person share is
  reported in B3.
- In the logistic nulls a morph's second contributor can appear in the training folds (the fold rule of the colour cue check (C3)).
- Intervals of the worst-pool misses in A5 (CP) ignore the uncertainty of the threshold.
