# Own-crop re-score of the audit rows (RS1): result

Status: **finished, revised after the independent review** (`experiments/reviews/REVIEW_RS1_20261112.md`; revision
12 Nov 2026, about 03:00 CET; amendment 7). Full record: `README.md`; registration: `prereg.md` (amendments 1 to 7).
EER in %, AUC 0 to 1, rates in %, 95% intervals from the two-way person bootstrap (102 FRLL persons, B = 2,000; FEI
subjects and FFHQ images have their own draws). Tables: `rs1_reproduction.csv`, `rs1_history.csv`, `rs1_flags.csv`
(threshold `t5_aligned` = t5 set on the aligned native pool), `rs1_expression.csv`, `rs1_ladder.csv`,
`rs1_ladder_flags.csv`, `rs1_pool_rates.csv` (column `crop_script_fails`), `rs1_shifts.csv`, `rs1_border.csv`,
`rs1_sliver_audit.csv`, `rs1_sliver_summary.csv`, `rs1_review_addons.json`; rendered `/mnt/t7/smad_next/RS1/tables.md`.

## What was done

MADation (LoRA ViT-B/16, LoRA ViT-L/14, FE ViT-B/16, FE ViT-L/14, FS ViT-B/16, FS ViT-L/14) and MixFaceNet-MAD
releases, cropped and scored on one rented RTX 3090 in two crop variants: variant 1 = the authors' SMDD
`image_preprocess.py` run unchanged; variant 2 = the corrected crop (RGB pixels to MTCNN, clamped edges) stored as
PNG. Cells: FRLL-Morphs AMSL, FaceMorpher, OpenCV, WebMorph, StyleGAN2; MorDIFF; six DiM families; corrected MAD22
FaceMorpher, MIPGAN-I, MIPGAN-II, OpenCV, Webmorph; the genuine class is the 204 raw FRLL photos. SelfMAD: its own
dlib crop. Label rule: "reproduced" if |native EER - published| <= max(1.5, 25% of published).

## Amendment 7: the unchanged crop script fails on face-filling files

Line 40 of the script slices `img[round(y1):round(y2), round(x1):round(x2)]`; when the 5% margin puts x1 or y1 below
0 the slice wraps and returns an edge strip or nothing. Exact CPU re-run of the script's arithmetic
(`src/RS1/sliver_audit.py`; malformed = start index below 0, short side below 32 px, or no crop):

| Set | Images | Malformed (strip, empty or no face) |
|---|---|---|
| MorDIFF morphs | 1,000 | 953 (95.3%): 898 of the 945 kept crops are strips (median short side 4 px), 55 empty or no face |
| A43 control arms (A, B, B20, C, C20, D, D20, E) | 102 to 204 each | 85 to 98% |
| FRLL FaceMorpher morphs | 1,222 | 417 (34.1%): all empty and dropped; the 806 kept crops are full faces |
| FRLL OpenCV morphs | 1,221 | 10 (0.8%) |
| FFHQ pools | 2,000 each | 2.9 to 3.3% (no face) |
| every other set (sample of 50) | | 0 to 4% |

Cell rule: a variant-1 cell or pool with more than 5% malformed images in either class is labelled **"release crop
script fails on these files"**, without reproduction label or audit claim: **MorDIFF, the whole MorDIFF ladder, the
stored-small pool, and FRLL FaceMorpher**. There the corrected crop (variant 2) is the only valid row. Deviation from
the review: its count of 439 OpenCV and 572 FaceMorpher strips used the corrected-crop boxes as a proxy; the
script's own detection (BGR pixels) gives different boxes, and the kept OpenCV and FaceMorpher crops are full faces
(median short side 311 and 326 px; ViT-B/16 logits median +6.4 and +9.9, not on the strip plateau near -0.6), so the
variant-1 OpenCV cell (0.8% malformed) is kept.

## Withdrawn

- Variant-1 MorDIFF EER 0.00 against 1.10 and its history effect +3.9: crop artefacts (95% strips).
- The stored-small rates 96% (5%-photo threshold) and 10.8% (release rule), variant 1: strips.
- The whole variant-1 MorDIFF ladder (0.991 / 0.503 / 0.529 / 0.481): strips against real crops, then strips against
  strips.
- The reading "the storage format changes what the detector reads": all A43 and MorDIFF images are PNG in both
  variants; the difference between variants on the ladder is the strip defect (variant 2 restricted to the images
  variant 1 kept gives 0.940 / 0.660 / 0.473).
- Variant-1 MorDIFF rows as evidence of non-reproduction: ViT-L/14 2.95, FE ViT-B/16 2.85, FE ViT-L/14 5.90,
  MixFaceNet-MAD 6.36.

## Corrected statements (the review's wording, adapted where the audit differs)

1. Through its own crop on raw files, the MADation ViT-B/16 release matches its published EER within the registered
   window on AMSL, OpenCV, WebMorph and StyleGAN2 (variant 1), on FaceMorpher and MorDIFF (corrected crop; MorDIFF
   0.55 against 1.10) and on four MAD22 families (FaceMorpher, MIPGAN-I, OpenCV, Webmorph; MIPGAN-II too in the
   corrected crop). When the genuine photos carry the morphs' shrink-and-store history, the EER rises by 12.8 to 19.0
   points on AMSL, WebMorph and MAD22 FaceMorpher (our aligned frames for both genuine arms) and by 12.2 points on
   MorDIFF (raw files, corrected crop). At the threshold that flags 5% of unprocessed raw photos it flags 38 to 56%
   of history-matched FRLL photos (10% of the same aligned photos without history; with the threshold set on the
   aligned photos themselves: 33 to 49% against 5% on AMSL, OpenCV and WebMorph) and 68% on MorDIFF.
2. MixFaceNet-MAD: +19.6 and +18.5 on AMSL and WebMorph, +21.1 on MorDIFF (corrected crop). Frozen-encoder ViT-B/16:
   +23.6 on MAD22 FaceMorpher and +26.0 on MorDIFF (corrected crop).
3. ViT-L/14: changes of -1.0 to +2.0 points on its reproduced cells; +2.0 [0.6, 4.6] on MAD22 FaceMorpher. Its
   genuine logits are packed (raw photos: median -12.80, SD 0.04), so small effects cannot be excluded (H-new-4
   below: they are not tied at a float32 floor).
4. On the MorDIFF control images (corrected crop), ViT-B/16 separates one-photo diffusion reconstructions from
   stored-small photos (0.94) and flags all of them at the 5% threshold; it separates morphs from reconstructions only
   weakly (0.66) and published from our morphs not at all (0.48); it reads the diffusion pipeline more than the morph.
   The authors' unchanged crop script fails on these face-filling files (edge strips of a few pixels), so it gives no
   valid ladder.
5. ViT-L/14 on MorDIFF (28.0 against 19.26, corrected crop), StyleGAN2 and four MAD22 families do not reproduce.
   Labels near the window edge change with crop variant and machine (detector boxes differ on about 1 image in 10
   between GPU models; identical JPEG crops differed by up to 5.9 logits under another decoder build).
6. The unchanged crop script returns no crop for 34% of FRLL FaceMorpher morphs and an edge strip a few pixels wide
   for 95% of MorDIFF morphs and 85 to 98% of the MorDIFF control images; on FRLL OpenCV it fails on 0.8%. The failing
   variant-1 cells are not used.

## Labels per release (17 cells each)

| Release | Variant 1: reproduced / not / script fails / no published | Variant 2: reproduced / not / no published |
|---|---|---|
| MADation ViT-B/16 (LoRA) | 8 / 1 / 2 / 6 | 9 / 2 / 6 |
| MADation ViT-L/14 (LoRA) | 3 / 6 / 2 / 6 | 5 / 6 / 6 |
| MADation FE ViT-B/16 | 5 / 0 / 2 / 10 | 6 / 0 / 11 |
| MADation FE ViT-L/14 | 5 / 0 / 2 / 10 | 5 / 1 / 11 |
| MADation FS ViT-B/16 | 1 / 4 / 2 / 10 | 0 / 6 / 11 |
| MADation FS ViT-L/14 | 2 / 3 / 2 / 10 | 5 / 1 / 11 |
| MixFaceNet-MAD | 9 / 0 / 2 / 6 | 9 / 2 / 6 |

Near-zero published values (6 or less): with the 1.5-point window a "reproduced" label shows only that the EER is not
much worse than published (for example MAD22 FaceMorpher 0.00 against 0.00).

## Reproduced rows: history-matched genuine photos and flag rates

"aligned" = no raw E7 file exists, so our aligned E7 frames went through the release crop and the effect is aligned
E7 minus aligned native. For StyleGAN2 and MAD22 MIPGAN the E7 rule leaves the photo unchanged (effect 0 by
construction).

| Release | Crop | Cell | Native EER | Published | EER, history-matched genuine (kind) | History effect | Flagged, history-matched: t5 on raw photos / t5 on aligned native (same aligned photos without history) |
|---|---|---|---|---|---|---|---|
| MADation ViT-B/16 (LoRA) | 1 | amsl | 3.92 | 3.85 | 24.42 [19.62, 28.85] (aligned) | 18.96 [14.79, 23.05] (aligned vs aligned) | 53.9 [42.6, 65.2] / 46.1 [30.9, 54.9] (aligned native at raw t5: 10.3 [5.9, 13.7]) |
| MADation ViT-B/16 (LoRA) | 1 | opencv | 1.97 | 2.97 | 6.86 [3.94, 9.72] (aligned) | 3.90 [2.06, 6.58] (aligned vs aligned) | 43.1 [30.9, 52.0] / 33.3 [18.6, 44.6] (aligned native at raw t5: 10.3 [5.9, 13.7]) |
| MADation ViT-B/16 (LoRA) | 1 | webmorph | 2.33 | 3.42 | 15.71 [11.85, 19.13] (aligned) | 12.76 [8.82, 15.79] (aligned vs aligned) | 55.9 [42.6, 64.7] / 44.6 [31.4, 54.9] (aligned native at raw t5: 10.3 [5.9, 13.7]) |
| MADation ViT-B/16 (LoRA) | 1 | stylegan | 18.60 | 17.21 | 18.64 [15.17, 22.61] (aligned) | 0.00 [0.00, 0.00] (aligned vs aligned) | 10.3 [5.9, 13.7] / 4.9 [3.4, 4.9] (aligned native at raw t5: 10.3 [5.9, 13.7]) |
| MADation ViT-B/16 (LoRA) | 1 | mad22_FaceMorpher | 0.00 | 0.0 | 13.66 [9.82, 17.56] (aligned) | 13.61 [9.81, 17.42] (aligned vs aligned) | 97.5 [93.1, 100.0] / 96.1 [88.2, 99.0] (aligned native at raw t5: 10.3 [5.9, 13.7]) |
| MADation ViT-B/16 (LoRA) | 1 | mad22_MIPGAN_I | 40.20 | 33.37 | 40.69 [34.76, 47.08] (aligned) | 0.00 [0.00, 0.00] (aligned vs aligned) | 10.3 [5.9, 13.7] / 4.9 [3.4, 4.9] (aligned native at raw t5: 10.3 [5.9, 13.7]) |
| MADation ViT-B/16 (LoRA) | 1 | mad22_OpenCV | 3.94 | 3.85 | 6.49 [3.40, 9.90] (aligned) | 0.60 [-0.35, 2.27] (aligned vs aligned) | 13.7 [7.8, 17.2] / 7.4 [3.9, 10.3] (aligned native at raw t5: 10.3 [5.9, 13.7]) |
| MADation ViT-B/16 (LoRA) | 1 | mad22_Webmorph | 10.89 | 10.8 | 14.21 [10.69, 18.33] (aligned) | 1.44 [0.00, 4.00] (aligned vs aligned) | 14.2 [6.4, 17.6] / 5.9 [3.4, 10.8] (aligned native at raw t5: 10.3 [5.9, 13.7]) |
| MADation ViT-L/14 (LoRA) | 1 | amsl | 7.90 | 7.26 | 7.31 [4.44, 10.07] (aligned) | -0.54 [-3.36, 2.53] (aligned vs aligned) | 3.9 [1.5, 7.8] / 4.4 [2.0, 8.8] (aligned native at raw t5: 3.4 [1.5, 6.9]) |
| MADation ViT-L/14 (LoRA) | 1 | webmorph | 5.36 | 4.07 | 4.42 [2.42, 7.82] (aligned) | 0.00 [-1.95, 3.44] (aligned vs aligned) | 4.4 [1.5, 8.8] / 5.4 [2.5, 9.8] (aligned native at raw t5: 3.4 [1.5, 6.9]) |
| MADation ViT-L/14 (LoRA) | 1 | mad22_FaceMorpher | 0.49 | 0.4 | 2.48 [0.96, 4.91] (aligned) | 1.98 [0.56, 4.59] (aligned vs aligned) | 17.6 [10.8, 27.5] / 18.6 [11.8, 29.4] (aligned native at raw t5: 3.4 [2.0, 6.9]) |
| MADation FE ViT-L/14 | 1 | mad22_FaceMorpher | 9.80 | 9.77 | 13.22 [9.32, 16.25] (aligned) | 4.41 [1.45, 6.29] (aligned vs aligned) | 6.9 [2.0, 15.7] / 9.8 [4.4, 16.7] (aligned native at raw t5: 4.4 [1.5, 6.4]) |
| MADation FE ViT-L/14 | 1 | mad22_MIPGAN_I | 24.01 | 23.51 | 24.50 [19.21, 28.67] (aligned) | 0.00 [0.00, 0.00] (aligned vs aligned) | 4.4 [1.5, 6.4] / 4.9 [3.4, 4.9] (aligned native at raw t5: 4.4 [1.5, 6.4]) |
| MADation FE ViT-L/14 | 1 | mad22_MIPGAN_II | 22.04 | 21.81 | 20.60 [15.73, 25.51] (aligned) | 0.00 [0.00, 0.00] (aligned vs aligned) | 4.4 [1.5, 6.4] / 4.9 [3.4, 4.9] (aligned native at raw t5: 4.4 [1.5, 6.4]) |
| MADation FE ViT-L/14 | 1 | mad22_OpenCV | 15.67 | 15.89 | 15.22 [10.80, 19.16] (aligned) | 0.50 [-1.11, 1.48] (aligned vs aligned) | 3.9 [2.0, 6.9] / 4.9 [2.9, 5.9] (aligned native at raw t5: 4.4 [1.5, 6.4]) |
| MADation FE ViT-L/14 | 1 | mad22_Webmorph | 25.89 | 26.4 | 25.10 [20.20, 30.30] (aligned) | -0.35 [-1.81, 0.96] (aligned vs aligned) | 4.4 [2.0, 6.9] / 5.9 [3.9, 6.4] (aligned native at raw t5: 4.4 [1.5, 6.4]) |
| MADation FE ViT-B/16 | 1 | mad22_FaceMorpher | 2.97 | 2.89 | 27.97 [23.02, 32.55] (aligned) | 23.56 [19.15, 27.98] (aligned vs aligned) | 81.9 [76.0, 89.7] / 77.9 [62.3, 85.3] (aligned native at raw t5: 8.8 [5.4, 13.7]) |
| MADation FE ViT-B/16 | 1 | mad22_MIPGAN_I | 25.45 | 26.0 | 30.35 [26.41, 34.12] (aligned) | 0.00 [0.00, 0.00] (aligned vs aligned) | 8.8 [5.4, 13.7] / 4.9 [3.9, 4.9] (aligned native at raw t5: 8.8 [5.4, 13.7]) |
| MADation FE ViT-B/16 | 1 | mad22_MIPGAN_II | 34.32 | 34.26 | 37.74 [33.42, 42.22] (aligned) | 0.00 [0.00, 0.00] (aligned vs aligned) | 8.8 [5.4, 13.7] / 4.9 [3.9, 4.9] (aligned native at raw t5: 8.8 [5.4, 13.7]) |
| MADation FE ViT-B/16 | 1 | mad22_OpenCV | 14.72 | 14.88 | 19.21 [15.28, 23.09] (aligned) | 1.65 [0.00, 3.45] (aligned vs aligned) | 10.3 [6.9, 16.2] / 6.4 [4.4, 8.3] (aligned native at raw t5: 8.8 [5.4, 13.7]) |
| MADation FE ViT-B/16 | 1 | mad22_Webmorph | 32.72 | 32.8 | 39.31 [32.91, 45.71] (aligned) | 3.52 [0.70, 6.38] (aligned vs aligned) | 10.8 [7.8, 17.2] / 8.3 [4.4, 10.3] (aligned native at raw t5: 8.8 [5.4, 13.7]) |
| MixFaceNet-MAD | 1 | amsl | 15.16 | 15.18 | 41.19 [37.57, 44.12] (aligned) | 19.62 [15.70, 23.99] (aligned vs aligned) | 40.2 [22.1, 59.8] / 27.0 [20.6, 39.7] (aligned native at raw t5: 9.3 [3.4, 17.2]) |
| MixFaceNet-MAD | 1 | opencv | 4.89 | 4.39 | 11.75 [8.50, 15.65] (aligned) | 5.87 [3.51, 8.73] (aligned vs aligned) | 32.8 [15.7, 46.1] / 19.1 [14.7, 31.4] (aligned native at raw t5: 9.3 [3.4, 17.2]) |
| MixFaceNet-MAD | 1 | webmorph | 12.27 | 12.35 | 35.79 [32.39, 40.20] (aligned) | 18.53 [14.65, 23.68] (aligned vs aligned) | 40.2 [19.1, 59.3] / 28.9 [20.1, 40.7] (aligned native at raw t5: 9.3 [3.4, 17.2]) |
| MixFaceNet-MAD | 1 | stylegan | 9.20 | 8.99 | 13.21 [9.31, 16.73] (aligned) | 0.00 [0.00, 0.00] (aligned vs aligned) | 9.3 [3.4, 17.2] / 4.9 [3.4, 4.9] (aligned native at raw t5: 9.3 [3.4, 17.2]) |
| MixFaceNet-MAD | 1 | mad22_FaceMorpher | 4.90 | 4.6 | 13.32 [9.09, 19.11] (aligned) | 8.37 [5.48, 12.78] (aligned vs aligned) | 86.3 [76.5, 94.1] / 83.3 [75.0, 90.2] (aligned native at raw t5: 8.8 [3.4, 17.6]) |
| MixFaceNet-MAD | 1 | mad22_MIPGAN_I | 16.24 | 16.7 | 21.58 [16.37, 26.39] (aligned) | 0.00 [0.00, 0.00] (aligned vs aligned) | 8.8 [3.4, 17.6] / 4.9 [3.9, 4.9] (aligned native at raw t5: 8.8 [3.4, 17.6]) |
| MixFaceNet-MAD | 1 | mad22_MIPGAN_II | 20.60 | 20.62 | 26.00 [21.22, 30.26] (aligned) | 0.00 [0.00, 0.00] (aligned vs aligned) | 8.8 [3.4, 17.6] / 4.9 [3.9, 4.9] (aligned native at raw t5: 8.8 [3.4, 17.6]) |
| MixFaceNet-MAD | 1 | mad22_OpenCV | 8.38 | 8.33 | 11.88 [7.75, 17.03] (aligned) | 0.55 [-0.44, 2.50] (aligned vs aligned) | 10.3 [3.4, 22.5] / 5.9 [3.4, 7.8] (aligned native at raw t5: 8.8 [3.4, 17.6]) |
| MixFaceNet-MAD | 1 | mad22_Webmorph | 18.17 | 18.2 | 24.11 [18.23, 30.46] (aligned) | 2.53 [0.20, 4.34] (aligned vs aligned) | 11.3 [3.4, 22.5] / 6.4 [2.9, 8.3] (aligned native at raw t5: 8.8 [3.4, 17.6]) |
| MADation FS ViT-B/16 | 1 | mad22_FaceMorpher | 4.95 | 5.38 | 13.66 [8.92, 19.76] (aligned) | 8.27 [5.15, 12.33] (aligned vs aligned) | 67.6 [58.3, 82.8] / 63.2 [51.5, 72.5] (aligned native at raw t5: 8.3 [5.4, 14.2]) |
| MADation FS ViT-L/14 | 1 | mad22_FaceMorpher | 17.62 | 22.63 | 21.19 [17.16, 25.98] (aligned) | 1.59 [-1.14, 4.92] (aligned vs aligned) | 14.7 [10.3, 20.1] / 8.8 [5.9, 16.7] (aligned native at raw t5: 6.9 [3.9, 14.2]) |
| MADation FS ViT-L/14 | 1 | mad22_OpenCV | 23.55 | 30.47 | 26.00 [21.95, 30.39] (aligned) | 0.50 [-1.00, 1.95] (aligned vs aligned) | 8.3 [5.4, 14.7] / 6.4 [4.4, 8.8] (aligned native at raw t5: 6.9 [3.9, 14.2]) |
| MADation ViT-B/16 (LoRA) | 2 | facemorpher | 0.53 | 1.35 | 2.33 [0.91, 3.95] (aligned) | 1.27 [0.00, 2.60] (aligned vs aligned) | 38.2 [30.4, 45.6] / 28.4 [21.1, 38.2] (aligned native at raw t5: 8.3 [5.4, 12.7]) |
| MADation ViT-B/16 (LoRA) | 2 | webmorph | 2.45 | 3.42 | 18.12 [13.71, 21.57] (aligned) | 14.64 [10.37, 17.43] (aligned vs aligned) | 56.4 [48.5, 65.2] / 48.5 [36.8, 58.3] (aligned native at raw t5: 8.3 [5.4, 12.7]) |
| MADation ViT-B/16 (LoRA) | 2 | stylegan | 15.78 | 17.21 | 18.64 [14.72, 22.53] (aligned) | 0.00 [0.00, 0.00] (aligned vs aligned) | 8.3 [5.4, 12.7] / 4.9 [3.9, 4.9] (aligned native at raw t5: 8.3 [5.4, 12.7]) |
| MADation ViT-B/16 (LoRA) | 2 | mordiff | 0.55 | 1.1 | 12.72 [8.79, 17.17] (raw) | 12.18 [8.26, 16.25] | 67.6 [60.3, 75.5] / 97.1 [87.7, 100.0] (aligned native at raw t5: 7.4 [4.4, 11.8]) |
| MADation ViT-B/16 (LoRA) | 2 | mad22_FaceMorpher | 0.00 | 0.0 | 17.62 [12.83, 22.67] (aligned) | 17.62 [12.83, 22.67] (aligned vs aligned) | 98.0 [95.1, 100.0] / 95.6 [91.2, 99.5] (aligned native at raw t5: 8.3 [5.4, 12.7]) |
| MADation ViT-B/16 (LoRA) | 2 | mad22_MIPGAN_I | 39.21 | 33.37 | 43.12 [37.73, 47.93] (aligned) | 0.00 [0.00, 0.00] (aligned vs aligned) | 8.8 [5.4, 13.2] / 5.4 [3.9, 6.4] (aligned native at raw t5: 8.3 [5.4, 12.7]) |
| MADation ViT-B/16 (LoRA) | 2 | mad22_MIPGAN_II | 26.94 | 22.21 | 30.96 [25.57, 36.67] (aligned) | 0.00 [0.00, 0.00] (aligned vs aligned) | 8.8 [5.4, 13.2] / 5.4 [3.9, 6.4] (aligned native at raw t5: 8.3 [5.4, 12.7]) |
| MADation ViT-B/16 (LoRA) | 2 | mad22_OpenCV | 3.00 | 3.85 | 4.79 [2.46, 8.22] (aligned) | 0.35 [-0.25, 1.87] (aligned vs aligned) | 11.8 [7.8, 16.2] / 5.9 [3.9, 10.3] (aligned native at raw t5: 8.3 [5.4, 12.7]) |
| MADation ViT-B/16 (LoRA) | 2 | mad22_Webmorph | 9.80 | 10.8 | 13.76 [9.80, 18.52] (aligned) | 1.88 [0.20, 4.75] (aligned vs aligned) | 12.7 [8.8, 17.2] / 6.9 [4.4, 10.8] (aligned native at raw t5: 8.3 [5.4, 12.7]) |
| MADation ViT-L/14 (LoRA) | 2 | facemorpher | 0.98 | 0.74 | 0.86 [0.07, 1.71] (aligned) | 0.00 [-0.49, 0.54] (aligned vs aligned) | 2.5 [0.5, 4.9] / 2.9 [1.0, 5.9] (aligned native at raw t5: 4.9 [2.0, 6.4]) |
| MADation ViT-L/14 (LoRA) | 2 | opencv | 2.45 | 0.99 | 1.96 [0.56, 4.03] (aligned) | -0.45 [-1.06, 0.49] (aligned vs aligned) | 2.5 [0.5, 4.4] / 2.5 [1.0, 5.4] (aligned native at raw t5: 4.9 [2.0, 6.4]) |
| MADation ViT-L/14 (LoRA) | 2 | webmorph | 5.32 | 4.07 | 3.93 [1.92, 5.92] (aligned) | -0.98 [-3.40, 1.41] (aligned vs aligned) | 2.9 [0.5, 5.9] / 3.4 [1.0, 6.9] (aligned native at raw t5: 4.9 [2.0, 6.4]) |
| MADation ViT-L/14 (LoRA) | 2 | mad22_FaceMorpher | 0.10 | 0.4 | 2.92 [1.03, 4.83] (aligned) | 2.92 [1.03, 4.83] (aligned vs aligned) | 23.5 [16.2, 30.4] / 23.5 [16.7, 33.3] (aligned native at raw t5: 4.9 [2.0, 6.4]) |
| MADation ViT-L/14 (LoRA) | 2 | mad22_Webmorph | 23.02 | 20.4 | 20.59 [16.65, 25.50] (aligned) | -1.44 [-3.00, 0.25] (aligned vs aligned) | 3.9 [1.5, 5.4] / 4.4 [2.9, 6.4] (aligned native at raw t5: 4.9 [2.0, 6.4]) |
| MADation FE ViT-L/14 | 2 | mordiff | 22.08 | 22.85 | 27.92 [22.90, 31.92] (raw) | 5.84 [2.80, 8.35] | 7.8 [4.9, 15.2] / 2.0 [0.5, 4.9] (aligned native at raw t5: 36.3 [27.5, 57.9]) |
| MADation FE ViT-L/14 | 2 | mad22_MIPGAN_I | 23.52 | 23.51 | 23.02 [18.12, 26.94] (aligned) | 0.00 [-1.44, 0.25] (aligned vs aligned) | 4.4 [1.5, 6.9] / 4.9 [3.9, 4.9] (aligned native at raw t5: 4.4 [1.5, 6.9]) |
| MADation FE ViT-L/14 | 2 | mad22_MIPGAN_II | 20.11 | 21.81 | 20.21 [15.27, 24.48] (aligned) | -0.40 [-1.19, 0.25] (aligned vs aligned) | 4.4 [1.5, 6.9] / 4.9 [3.9, 4.9] (aligned native at raw t5: 4.4 [1.5, 6.9]) |
| MADation FE ViT-L/14 | 2 | mad22_OpenCV | 15.67 | 15.89 | 15.22 [10.76, 19.50] (aligned) | 0.00 [-1.49, 1.22] (aligned vs aligned) | 3.9 [1.5, 6.9] / 4.4 [2.9, 5.9] (aligned native at raw t5: 4.4 [1.5, 6.9]) |
| MADation FE ViT-L/14 | 2 | mad22_Webmorph | 24.01 | 26.4 | 23.12 [18.23, 28.01] (aligned) | 0.00 [-1.63, 0.91] (aligned vs aligned) | 4.4 [2.0, 6.9] / 4.9 [3.4, 5.9] (aligned native at raw t5: 4.4 [1.5, 6.9]) |
| MADation FE ViT-B/16 | 2 | mordiff | 18.12 | 17.86 | 44.11 [39.29, 49.04] (raw) | 25.99 [22.10, 30.29] | 52.5 [38.2, 60.3] / 34.3 [27.9, 44.6] (aligned native at raw t5: 52.5 [42.2, 60.8]) |
| MADation FE ViT-B/16 | 2 | mad22_FaceMorpher | 3.47 | 2.89 | 29.46 [24.96, 33.82] (aligned) | 25.00 [20.77, 28.37] (aligned vs aligned) | 86.8 [76.0, 92.6] / 78.4 [67.2, 84.8] (aligned native at raw t5: 11.3 [5.9, 15.7]) |
| MADation FE ViT-B/16 | 2 | mad22_MIPGAN_I | 27.38 | 26.0 | 31.29 [27.39, 35.34] (aligned) | 0.00 [-0.51, 0.44] (aligned vs aligned) | 11.3 [5.9, 15.2] / 4.9 [3.9, 4.9] (aligned native at raw t5: 11.3 [5.9, 15.7]) |
| MADation FE ViT-B/16 | 2 | mad22_MIPGAN_II | 35.37 | 34.26 | 43.14 [38.10, 47.03] (aligned) | 0.00 [0.00, 0.00] (aligned vs aligned) | 11.3 [5.9, 15.2] / 4.9 [3.9, 4.9] (aligned native at raw t5: 11.3 [5.9, 15.7]) |
| MADation FE ViT-B/16 | 2 | mad22_OpenCV | 13.72 | 14.88 | 20.51 [16.40, 24.08] (aligned) | 3.44 [1.39, 6.40] (aligned vs aligned) | 16.7 [6.9, 23.0] / 6.9 [4.4, 9.8] (aligned native at raw t5: 11.3 [5.9, 15.7]) |
| MADation FE ViT-B/16 | 2 | mad22_Webmorph | 35.25 | 32.8 | 43.61 [37.89, 49.95] (aligned) | 1.98 [0.90, 6.08] (aligned vs aligned) | 14.7 [7.4, 19.6] / 6.9 [3.9, 9.3] (aligned native at raw t5: 11.3 [5.9, 15.7]) |
| MixFaceNet-MAD | 2 | amsl | 17.15 | 15.18 | 40.69 [36.92, 44.11] (aligned) | 18.62 [14.47, 23.05] (aligned vs aligned) | 36.3 [28.9, 50.5] / 29.4 [18.6, 38.2] (aligned native at raw t5: 10.8 [6.9, 15.7]) |
| MixFaceNet-MAD | 2 | facemorpher | 2.94 | 3.87 | 6.46 [3.86, 9.82] (aligned) | 2.62 [0.91, 4.46] (aligned vs aligned) | 27.5 [20.1, 38.2] / 18.1 [11.3, 25.0] (aligned native at raw t5: 10.8 [6.9, 15.7]) |
| MixFaceNet-MAD | 2 | opencv | 4.01 | 4.39 | 13.25 [9.79, 16.32] (aligned) | 7.36 [4.30, 9.47] (aligned vs aligned) | 31.9 [24.0, 42.6] / 21.6 [13.2, 30.9] (aligned native at raw t5: 10.8 [6.9, 15.7]) |
| MixFaceNet-MAD | 2 | webmorph | 14.68 | 12.35 | 35.79 [32.25, 39.73] (aligned) | 17.18 [13.39, 21.84] (aligned vs aligned) | 38.2 [29.4, 52.0] / 28.9 [18.1, 37.7] (aligned native at raw t5: 10.8 [6.9, 15.7]) |
| MixFaceNet-MAD | 2 | mordiff | 9.31 | 8.5 | 30.40 [25.88, 35.37] (raw) | 21.09 [17.17, 24.96] | 62.7 [49.5, 76.5] / 55.4 [46.6, 74.0] (aligned native at raw t5: 0.0 [0.0, 0.5]) |
| MixFaceNet-MAD | 2 | mad22_MIPGAN_I | 17.18 | 16.7 | 21.04 [16.63, 25.87] (aligned) | 0.00 [0.00, 0.00] (aligned vs aligned) | 10.8 [6.9, 15.7] / 4.9 [3.9, 4.9] (aligned native at raw t5: 10.8 [6.9, 15.7]) |
| MixFaceNet-MAD | 2 | mad22_MIPGAN_II | 21.10 | 20.62 | 25.01 [20.66, 29.49] (aligned) | 0.00 [0.00, 0.00] (aligned vs aligned) | 10.8 [6.9, 15.7] / 4.9 [3.9, 4.9] (aligned native at raw t5: 10.8 [6.9, 15.7]) |
| MixFaceNet-MAD | 2 | mad22_OpenCV | 9.78 | 8.33 | 13.32 [9.10, 18.60] (aligned) | 1.05 [0.00, 2.84] (aligned vs aligned) | 13.2 [8.3, 19.6] / 6.9 [4.4, 8.8] (aligned native at raw t5: 10.8 [6.9, 15.7]) |
| MixFaceNet-MAD | 2 | mad22_Webmorph | 19.16 | 18.2 | 25.89 [18.63, 30.85] (aligned) | 2.77 [-0.00, 3.91] (aligned vs aligned) | 12.7 [8.3, 19.1] / 5.9 [4.4, 8.3] (aligned native at raw t5: 10.8 [6.9, 15.7]) |
| MADation FS ViT-L/14 | 2 | mad22_FaceMorpher | 20.05 | 22.63 | 22.52 [18.32, 27.40] (aligned) | 2.43 [-1.15, 5.08] (aligned vs aligned) | 9.8 [5.4, 13.7] / 7.8 [3.9, 10.8] (aligned native at raw t5: 7.4 [3.4, 11.3]) |
| MADation FS ViT-L/14 | 2 | mad22_MIPGAN_I | 19.11 | 23.8 | 19.50 [15.71, 23.99] (aligned) | 0.00 [-0.05, 0.00] (aligned vs aligned) | 7.4 [3.4, 11.3] / 4.9 [3.9, 4.9] (aligned native at raw t5: 7.4 [3.4, 11.3]) |
| MADation FS ViT-L/14 | 2 | mad22_MIPGAN_II | 20.70 | 21.81 | 22.04 [17.73, 26.47] (aligned) | 0.00 [0.00, 0.00] (aligned vs aligned) | 7.4 [3.4, 11.3] / 4.9 [3.9, 4.9] (aligned native at raw t5: 7.4 [3.4, 11.3]) |
| MADation FS ViT-L/14 | 2 | mad22_OpenCV | 24.40 | 30.47 | 26.55 [22.21, 31.80] (aligned) | 0.00 [-2.11, 1.24] (aligned vs aligned) | 6.9 [2.9, 10.8] / 4.4 [2.9, 5.4] (aligned native at raw t5: 7.4 [3.4, 11.3]) |
| MADation FS ViT-L/14 | 2 | mad22_Webmorph | 26.43 | 33.6 | 31.39 [25.43, 36.43] (aligned) | 0.99 [-1.46, 2.91] (aligned vs aligned) | 6.4 [2.5, 10.3] / 3.9 [2.5, 5.4] (aligned native at raw t5: 7.4 [3.4, 11.3]) |

## MorDIFF ladder (corrected crop only; A43 control images)

| Release | stored-small vs photo | reconstruction D20 vs stored-small | our morph B20 vs D20 | published vs our morph B20 | flagged at 5%-photo threshold: stored-small / D20 / B20 / published |
|---|---|---|---|---|---|
| MADation ViT-B/16 | 0.890 [0.861, 0.917] | 0.941 [0.918, 0.962] | 0.664 [0.562, 0.754] | 0.481 [0.445, 0.509] | 60.3 / 100 / 100 / 100 |
| MADation FE ViT-L/14 | 0.567 [0.544, 0.594] | 0.748 [0.718, 0.781] | 0.572 [0.497, 0.649] | 0.502 [0.477, 0.526] | 5.4 / 27.5 / 30.5 / 30.0 |
| MADation FE ViT-B/16 | 0.882 [0.859, 0.908] | 0.617 [0.582, 0.654] | 0.440 [0.363, 0.516] | 0.497 [0.469, 0.526] | 54.9 / 68.6 / 64.0 / 60.0 |
| MixFaceNet-MAD | 0.870 [0.834, 0.908] | 0.778 [0.742, 0.819] | 0.489 [0.410, 0.567] | 0.490 [0.458, 0.525] | 58.8 / 85.3 / 87.0 / 86.5 |

"stored-small vs photo" mixes DiffAE's tighter framing and size with storage. Raw E7 history effect on MorDIFF
(corrected crop): ViT-B/16 +12.2 [8.3, 16.3], FE ViT-L/14 +5.8 [2.8, 8.4], FE ViT-B/16 +26.0 [22.1, 30.3],
MixFaceNet-MAD +21.1 [17.2, 25.0].

## Release rule (probability of morph > 0.5) with miss rates

Corrected crop, ViT-B/16: unprocessed raw photos 0.0% flagged; raw E7 MorDIFF 2.0%, stored-small 1.5%; at the same
rule it misses 96.0% of AMSL, 99.2% of StyleGAN2 and 79% of WebMorph morphs, so the release rule is not a meaningful
operating point for this release. Every 0.5-rule rate with its miss rate: `rs1_pool_rates.csv` (kind "morph") and
`rs1_review_addons.json` (`F4_miss_at_release_rule`). Paired logit shifts: `rs1_shifts.csv`.

## Hypotheses from the review (existing files, zero GPU; `rs1_review_addons.json`)

- **H-new-1 (published MorDIFF files).** The released ViT-B/16 training log
  (`/mnt/t7/smad_next/AD5/release_logs/vitb16_madation/training.log`, line 10) tests MorDIFF from
  `/workspace/FaceMAD/Protocols/MorDIFF.csv` at `image_size` 224 (interpolation bicubic); the CSV itself is not
  released (`baselines/MADation/src/config.py` line 63 names the same file; `generate_csv.py` builds such CSVs from
  folders `bonafide/<attack>` of an *aligned* copy, line 6). Line 428 (epoch 39) gives MorDIFF EER 0.010978 = Table 1's
  1.10. The logged rates have denominators 1,002 (attacks) and 206 (bona fide) (for example 451/1002 and 73/206 at
  line 20; 11/1002 at line 428), against our 1,000 and 204. So their MorDIFF population differs from ours by 2 + 2
  images; whether their files were `MorDIFF_crop` or another copy cannot be read from the release. Not falsified, not
  confirmed.
- **H-new-2 (ViT-B/16 reads DiffAE decoding).** Corrected crop: 100-step reconstructions D flagged 98.5% [95.6, 100]
  and D20 100% at t5; same-person mixes C20 vs D20 0.609 [0.562, 0.661]. Not falsified (falsifier: D under 50% or
  C20 vs D20 above 0.65).
- **H-new-3 (AMSL reproduction depends on the extra JPEG generation).** JPEG-minus-PNG logit shift, ViT-B/16: AMSL
  morphs +0.30, FRLL photos +0.02 (WebMorph +0.71, OpenCV -0.22). The AMSL morph shift is larger than the photo
  shift: not falsified.
- **H-new-4 (ViT-L/14 blind to history by saturation).** 0% of genuine scores are tied at a float32 value (falsifier:
  under 20% tied): **falsified** as stated; the genuine logits are packed (SD 0.04) but distinct, and the AMSL history
  shift is about 0 in both halves of the genuine scores (+0.006 and -0.012 logit).

## SelfMAD release (HRNet-W18), its own dlib crop

Two runs, never compared with each other: (A) existing scores on WCSS (A41 x7 raw files; A32-RSX and A43 frames);
(B) RS1 scores on the DGX of raw, stored and dataset files (raw FRLL photos, raw MorDIFF, raw E7 MorDIFF, the A43
stored control images, FEI, FFHQ). Run B gives the same MorDIFF EER as run A (1.49; raw E7 45.20).

| Cell (run A) | Native EER [95%] | Published | Label (all photos) | Neutral-only EER | Label (neutral-only) |
|---|---|---|---|---|---|
| FRLL AMSL | 2.44 [0.94, 4.86] | 0.99 | reproduced | 0.97 | reproduced |
| FRLL FaceMorpher | 0.98 [0.07, 1.68] | 0.00 | reproduced | 0.21 | reproduced |
| FRLL OpenCV | 0.37 [0.00, 0.56] | 0.00 | reproduced | 0.08 | reproduced |
| FRLL WebMorph | 7.36 [4.93, 10.78] | 3.45 | not reproduced | 4.91 | reproduced |
| FRLL StyleGAN2 | 16.60 [12.26, 22.07] | 10.34 | not reproduced | 12.59 | reproduced |
| Greedy-DiM | 6.39 [3.26, 9.56] | 7.60 | reproduced | 3.07 | not reproduced |
| MorDIFF | 1.49 [0.00, 3.46] | none | no published number | 0.99 | no published number |
| DiM-A | 4.41 [1.86, 6.75] | none | no published number | 2.77 | no published number |

History-matched genuine photos (run A): raw E7 files raise the EER from 6.39 to 87.23 on Greedy-DiM (+80.8 [76.0,
85.5], reproduced row), from 1.49 to 45.20 on MorDIFF, from 4.41 to 69.50 on DiM-A. On the FRLL landmark cells only our
aligned E7 frames exist (labelled "aligned-frame E7"): aligned native -> aligned E7 AMSL 4.91 -> 49.02 (+44.1 [38.3,
48.9]), FaceMorpher 1.51 -> 8.34 (+6.8), OpenCV 0.49 -> 6.30 (+5.8), WebMorph 15.79 -> 71.00 (+55.2); for StyleGAN2
the E7 rule leaves the photo unchanged.

Release rule (probability of morph > 0.5), run B: raw FRLL photos 0.0% flagged, raw E7 MorDIFF photos 26.0 [18.1,
33.8], stored-small photos 56.9 [49.0, 65.2], MorDIFF morphs 26.5 [19.3, 34.8]; FEI frames 33.3 (neutral) and 40.1
(smiling); FFHQ photos 17.7 -> 48.1 with the DiffAE-matched history. Paired logit shifts (run B): raw E7 vs its photo
+5.06 [4.84, 5.27] (100% of photos rise), stored-small vs photo +6.04 [5.77, 6.30] (100%), FFHQ history copies +2.37
[2.26, 2.48] (89.5%).

MorDIFF ladder, run B (AUC, higher rung positive): stored-small photo vs photo 0.999 [0.998, 1.000]; reconstruction
D20 vs stored-small 0.465 [0.429, 0.499]; our morph B20 vs reconstruction D20 0.334 [0.260, 0.407]; published vs our
morph B20 0.463 [0.424, 0.493]. The MorDIFF row has no published number for SelfMAD.

SelfMAD rows with both genuine-class definitions: `rs1_reproduction.csv` (columns `neutral_only_eer`,
`neutral_label`) and `rs1_expression.csv` (native and history-matched EER, neutral-only and smiling-only) for every
SelfMAD row.

## Findings on the measurement itself

- The unchanged SMDD crop script fails on face-filling files (strips or nothing): 95% of MorDIFF morphs, 85 to 98% of
  the MorDIFF control images, 34% of FRLL FaceMorpher (empty).
- JPEG decoder build: identical JPEG crops differed by up to 5.9 logits (conda vs PyPI Pillow 10.2.0); with the same
  build they agree within 0.19 logit.
- The crop step's JPEG re-save changes logits by a median of 0.003 to 0.86 by release, up to 16 on single images.
- Detector boxes differ between GPU models on about 1 image in 10 (scores then differ by up to 9.5 logits).
- Release crops of the raw files carry no black border; on our aligned MorDIFF frames the crop keeps 5 to 8% black.

## Deviations and what could not be verified

- Platform history: amendments 1 to 6 (Athena smoke only; production on one rented RTX 3090; Athena gate
  descriptive). Reused A46 crops and the JPEG-re-encoding corrected crop are not result rows.
- Aligned-frame E7 rows (FRLL landmark families, MAD22, four DiM families) use our aligned frames for both genuine
  arms; raw E7 files exist only for MorDIFF, DiM-A and Greedy-DiM.
- No multiplicity correction (about 7 releases x 17 cells x 2 variants x 5 pools); the headline effects have lower
  bounds of 8.8 points or more; FaceMorpher +1.85 [0.11, 3.44] would not survive a correction.
- Published values from the arXiv HTML; CVF PDFs not opened; published genuine populations not verified (MorDIFF:
  1,002 / 206 in the authors' log against our 1,000 / 204).
- Crop files existed only on the rented machine; their sha256 lists:
  `/mnt/t7/smad_next/RS1/results_rented/prod_v{1,2}_rented/crops_sha256.txt`.
- Compute: Athena smoke jobs 3544220 (0:06:52), 3545836 (0:02:37, cancelled), 3545869 (0:03:34), account
  plgrestorearc-gpu-a100; production jobs 3545884, 3545918/19, 3545970/71, 3545972/73 never started. Rented RTX
  3090 about 2.5 h at 0.44 USD/h (rented and released by the lead). DGX shared GPU about 2.5 h; the sliver audit and
  the review additions are CPU only.
