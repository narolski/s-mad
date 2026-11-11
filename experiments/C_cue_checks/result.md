# C1–C4 zero-compute cue checks: result

Owner run, 11 Nov 2026, DGX CPU only. Code `src/C_cue_checks/c_checks.py` (32,310 images, 0 decode
errors), `src/C_cue_checks/probe_check.py`. Outputs `c_checks.json`, `c_checks.log`, `probe_check.json`.
Only headers and decoded pixels were read; nothing was re-encoded or written.

Cells: FRLL-Morphs amsl / facemorpher / opencv / stylegan / webmorph (raw `Datasety/downloads/FRLL-Morphs`,
genuine `frll_base` 102 neutral + 102 smiling; aligned = our 512 eval frames); corrected MAD22
FaceMorpher / MIPGAN-I / MIPGAN-II / OpenCV / Webmorph (raw `marco_owncloud_20261109T103840Z/.../original_sorted`,
204 BonaFide; aligned = `mad22_canonical_E7_inputs_v3_20261109T113746Z/native`); MorDIFF (1,000);
DiM-A, DiM-C, Fast-DiM, Fast-DiM-ODE, Greedy-DiM, Greedy-DiM-S (500 / 499). Every cell's genuine class is
the 102 FRLL persons × {neutral 03, smiling 08}.

## C1 Expression balance

| Cell | Morph expressions | Source | Smiling share morph / genuine | O of expression label alone |
|---|---|---|---|---|
| MAD22c FaceMorpher, MIPGAN-I, MIPGAN-II, OpenCV | 03/03 and 08/08 pairs, about 50 / 50 (500/500; 500/500; 500/499; 489/495) | file names | 0.50 / 0.50 | 0.50 |
| MorDIFF | 500 neutral pairs, 500 smiling pairs | file names | 0.50 / 0.50 | 0.50 |
| **MAD22c Webmorph** | **all 500 neutral (03/03)** | file names | **0.00 / 0.50** | **0.75** |
| **DiM (6 families)** | neutral only ("we only used faces with neutral expressions … category 03", DiM README) | README; probe agrees: 2.6–6.8% of morphs smile-like | ≈0 / 0.50 | ≈0.75 |
| **FRLL-Morphs (5 families)** | not in file names; probe: 1.0–1.5% smile-like (StyleGAN 6.9%) | expression probe, inferred | ≈0 / 0.50 | ≈0.75 (inferred) |

Every morph pair has the same expression on both sides (no mixed 03/08 pairs in any named cell).
Expression probe: logistic regression on a 22 × 36 grey thumbnail of the lower face of the eye-aligned
genuine frames, 5-fold by person, accuracy 0.853 (0.842–0.857); applied unchanged to the morph frames.
Validation on morphs with known expression (`probe_check.json`): AUC of the probe against the
file-name label 0.985 (MorDIFF), 0.977 (MAD22c FaceMorpher), 0.997 (MAD22c OpenCV); it flags 88–97% of
the smiling morphs and 2.2% of the all-neutral MAD22c Webmorph morphs. So the FRLL-Morphs (1.0–6.9%)
and DiM (2.6–6.8%) rates are consistent with neutral-only morphs. Reading: in 11 of 17
cells (DiM ×6, FRLL-Morphs ×5 inferred, MAD22c Webmorph) the genuine class is half smiling and the
morphs are (nearly) all neutral, so "smiling ⇒ genuine" alone separates at AUC up to 0.75. In the other
6 cells expression is balanced.

## C2 Person overlap between training data and test benchmarks

All test cells use the same 102 FRLL persons (genuine class and morph contributors).

| Training data | Persons | FRLL persons inside? |
|---|---|---|
| Our retrains, d0 (`train.csv`, `train/smdd`, 40,000) | synthetic (SMDD, StyleGAN2) | no labels; no FRLL path (0 of 69,882 rows match frll/facelab/london/mordiff/dim) |
| Our retrains, d1 / R6 / R8 (`train/*_feret`, `*_frgc`, `arms/r6_frgc`, `arms/r8_*`) | FERET, FRGC | no FRLL path; FRLL (2017, London) vs FERET (1993–96) / FRGC (2002–04): no shared person labels; overlap not checkable without face matching |
| MADation releases | SMDD (`MADTrain` → `smdd_train_cropped.csv`, local config mirror) | synthetic. Note: the training config evaluates MAD22, MorDIFF and all FRLL-Morphs lists during training; which epoch was released is not documented |
| SelfMAD release | not stated in README. Shipped `configs/train_config.json`: `train_dataset: SMDD`, **`saving_strategy: testset_best`** = the epoch with the lowest mean EER over FRGC-, FERET- **and FRLL-Morphs** (`train__.py` l.178, `eval__.py` l.55–82) | if the release was trained with the shipped defaults, its checkpoint was **selected on FRLL-Morphs test persons**. Not verified for the released weights |
| MixFaceNet-MAD release | SMDD (README) | synthetic |
| Pretraining (CLIP for MADation, ImageNet for HRNet / others), SMDD's generator (FFHQ) | web images, no identity labels | not verifiable |

So no audited training set contains FRLL images by path or label. Two exposures remain: the possible
test-set model selection of the SelfMAD release on FRLL-Morphs (code default), and unverifiable web-scale
pretraining. A face-matching search of FRLL persons in FERET/FRGC/SMDD was not run (needs embeddings).

## C3 Colour statistics (per-channel mean and std; AUC; logistic regression 5-fold by person)

O = max(AUC, 1 − AUC) of the best single statistic. LR = mean held-out AUC of a 6-feature logistic
regression, folds by person (test = items with a person in the fold, train = items with no person in it).
"non-zero" = the same statistics over pixels that are not the zero-filled alignment border.

| Cell | Stored file O / LR | Aligned crop O / LR | Aligned, non-zero pixels LR | Zero-border median morph / genuine |
|---|---|---|---|---|
| FRLL-Morphs amsl | 0.98 / 1.00 | 0.71 / 0.85 | 0.76 | 0.053 / 0 |
| FRLL-Morphs facemorpher | 1.00 / 1.00 | 0.99 / 1.00 | 0.98 | 0.260 / 0 |
| FRLL-Morphs opencv | 1.00 / 1.00 | 0.97 / 0.99 | 0.97 | 0.192 / 0 |
| FRLL-Morphs stylegan | 1.00 / 1.00 | 0.82 / 0.90 | 0.89 | 0.032 / 0 |
| FRLL-Morphs webmorph | 0.99 / 1.00 | 0.69 / 0.84 | 0.76 | 0.051 / 0 |
| MAD22c FaceMorpher | 0.99 / 1.00 | 0.70 / 0.84 | 0.82 | 0.054 / 0 |
| MAD22c MIPGAN-I | 1.00 / 1.00 | 0.91 / 0.93 | 0.97 | 0.040 / 0 |
| MAD22c MIPGAN-II | 1.00 / 1.00 | 0.91 / 0.92 | 0.98 | 0.041 / 0 |
| MAD22c OpenCV | **0.58 / 0.63** | 0.67 / 0.77 | 0.77 | 0 / 0 |
| MAD22c Webmorph | **0.60 / 0.65** | 0.66 / 0.77 | 0.77 | 0 / 0 |
| MorDIFF | 1.00 / 1.00 | 0.57 / 0.78 | 0.61 | 0.53 / 0.54 |
| DiM-A / C / Fast / Fast-ODE / Greedy / Greedy-S | 0.99–1.00 / 1.00 | 0.63–0.67 / 0.71–0.84 | 0.61–0.83 | ≈0.033 / 0 |

Reading: on the stored files, colour statistics separate 15 of 17 cells almost perfectly; this mostly
reflects the different canvases (the genuine FRLL files are 1350² studio frames with a large grey
background, the morphs are tighter crops or generator outputs), so it is a framing cue as much as a
colour cue. Only MAD22c OpenCV and Webmorph are near chance on the stored file (0.58–0.65); why (frame or
background kept by those tools) was not examined. On our aligned crops, which is what the detectors read, colour statistics
still separate every cell well above chance (LR 0.71–1.00); with the zero border excluded, 0.61–0.98.
The strongest are the FRLL-Morphs FaceMorpher / OpenCV families (0.97–0.98 without the border) and the
MAD22 MIPGAN cells (0.97–0.98). No detector use is implied.

## C4 Chroma subsampling and colour format (extends A41's file table to the corrected MAD22)

| Cell | Morph format | Genuine format | O (subsampling) | O (container·subsampling·mode·progressive) |
|---|---|---|---|---|
| FRLL-Morphs ×5 | JPEG 4:2:0, RGB | JPEG 4:2:0, RGB | 0.50 | 0.50 |
| MAD22c FaceMorpher, OpenCV | JPEG 4:2:0 | JPEG 4:2:0 | 0.50 | 0.50 |
| **MAD22c Webmorph** | **JPEG 4:4:4** (PIL sampling 0), all 500 | JPEG 4:2:0, all 204 | **1.00** | **1.00** |
| MAD22c MIPGAN-I / II | PNG (no subsampling) | JPEG 4:2:0 | 1.00 (with the container) | 1.00 |
| MorDIFF, DiM ×6 | PNG | JPEG 4:2:0 | 1.00 (with the container) | 1.00 |

Mode is RGB everywhere; no ICC profiles; no progressive JPEG. The corrected MAD22 reproduces A41's
old-subset finding: chroma subsampling alone separates Webmorph perfectly, and nowhere else is it
separate from the container. In the lossless-morph cells (MIPGAN, MorDIFF, DiM), "no chroma
subsampling" is part of the PNG-vs-JPEG cue and leaves a pixel trace (full-resolution chroma in morphs
only).

## Proposed edits to `08_CUE_MATRIX.md` (status cells; not applied)

- **Row 13b (Chroma subsampling):** "In the files?" → "O = 1.000 in MAD22 Webmorph, confirmed on the
  corrected MAD22 (500 morphs 4:4:4 vs 204 photos 4:2:0); in MIPGAN-I/II, MorDIFF and DiM it coincides
  with PNG vs JPEG (O = 1.000 jointly); 0.500 in FRLL-Morphs, MAD22 FaceMorpher/OpenCV (C4)". Status
  stays **PRESENT, USE UNTESTED**.
- **Row 13c (Pixel colour statistics):** "In the files?" → "Yes: on our aligned crops per-channel
  mean/std separate every cell (6-feature LR 0.71–1.00 by person; 0.61–0.98 without the zero border);
  stored files 0.58–1.00, framing-confounded (C3)". Status **UNKNOWN → PRESENT, USE UNTESTED**.
- **Row 14 (Identity overlap):** "In the files?" → "No FRLL image in any audited training set by path
  or label (SMDD synthetic; our retrains FERET/FRGC; C2). Possible test-set model selection: the
  SelfMAD code default `testset_best` picks the epoch on FRLL-Morphs EER (release not verified).
  Face-matching search not run". Status **UNKNOWN → ABSENT (by label; face matching not run)**, with a
  new sub-row 14b "Checkpoint selection on test persons (SelfMAD release)": **UNKNOWN (code default
  says yes; release not verified)**.
- **Row 15 (Expression):** "In the files?" → "Yes in 11 of 17 cells: DiM ×6 (README: neutral only),
  FRLL-Morphs ×5 (probe: ≤ 7% smile-like) and MAD22 Webmorph (names: 500 neutral) have neutral morphs
  against a 50% smiling genuine class (O of the label ≈ 0.75); balanced in MAD22 FaceMorpher, MIPGAN-I/II,
  OpenCV and MorDIFF (O 0.50) (C1)". Status **UNKNOWN → PRESENT, USE UNTESTED** for the 11 cells,
  **ABSENT** for the 6 balanced cells (split into 15a / 15b).

## Not verifiable / caveats

- FRLL-Morphs morph expression is inferred (probe 85% on genuine photos, AUC 0.98–1.00 on named
  morphs); not stated in the FRLL-Morphs README or file names.
- C3 on stored files mixes colour with canvas and background; no colour-matched control was run.
- C2 identity overlap is by labels and paths only; the SelfMAD release's actual training run, and the
  MADation release epoch, are not documented in what I read.
- The person-grouped CV places morph test items in every fold that holds one of their contributors, so
  folds overlap; the per-fold AUCs are in `c_checks.json`.

## Correction, 11 Nov 2026 ~17:40 (after the independent review)

The expression count above is wrong by one: **12 of 17 cells** are imbalanced (DiM ×6 + FRLL-Morphs ×5 +
MAD22 Webmorph) and **5** are balanced (MAD22 FaceMorpher, MIPGAN-I, MIPGAN-II, OpenCV, MorDIFF). The
proposed row-15 edit should read "12 of 17". Full record: `README.md`.
