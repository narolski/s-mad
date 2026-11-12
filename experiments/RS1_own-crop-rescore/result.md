# Own-crop re-score of the audit rows (RS1): result

Status: **finished** (12 Nov 2026, 01:40 CET). Full record: `README.md`; registration: `prereg.md` (amendments 1 to
6). EER in %, AUC 0 to 1, rates in %, 95% intervals from the two-way person bootstrap (102 FRLL persons, B = 2,000;
FEI subjects and FFHQ images have their own draws). Tables: `rs1_reproduction.csv`, `rs1_history.csv`,
`rs1_flags.csv`, `rs1_expression.csv`, `rs1_ladder.csv`, `rs1_ladder_flags.csv`, `rs1_pool_rates.csv`,
`rs1_shifts.csv`, `rs1_border.csv`, `rs1_results.json`; rendered: `/mnt/t7/smad_next/RS1/tables.md`.

## What was done

MADation (LoRA ViT-B/16, LoRA ViT-L/14, FE ViT-B/16, FE ViT-L/14, FS ViT-B/16, FS ViT-L/14) and MixFaceNet-MAD
releases, all cropped and scored on ONE rented machine (RTX 3090; amendments 5, 6), in two crop variants:
**variant 1 (primary)** = the authors' SMDD crop script `image_preprocess.py` run unchanged (BGR pixels to MTCNN,
unbounded slice, JPEG inputs re-saved as JPEG); **variant 2 (secondary)** = the corrected crop (RGB to MTCNN, clamped
edges) stored as PNG. Then the release adapters (BGR, (x - 0.5) / 0.5, 224). Cells: FRLL-Morphs AMSL / FaceMorpher /
OpenCV / WebMorph / StyleGAN2, MorDIFF, six DiM families, corrected MAD22 (FaceMorpher, MIPGAN-I, MIPGAN-II, OpenCV,
Webmorph), all with the 204 raw FRLL photos as the genuine class. SelfMAD: its own dlib crop, existing WCSS scores plus
new DGX scores. Label: "reproduced" if |native EER - published| <= max(1.5, 25% of published) (MADation arXiv
2501.03800v3 Tables 1 to 3; SelfMAD arXiv 2504.05504 Table II); otherwise "our pipeline, published number not
reproduced" ("not reproduced" below); "no published number" where none exists. Only reproduced rows carry claims.

## Which rows reproduce

Labels per release (17 cells each; 6 to 11 cells have no published number):

| Release | Variant 1 reproduced / not / none | Variant 2 reproduced / not / none |
|---|---|---|
| MADation ViT-B/16 (LoRA) | 10 / 1 / 6 | 9 / 2 / 6 |
| MADation ViT-L/14 (LoRA) | 4 / 7 / 6 | 5 / 6 / 6 |
| MADation FE ViT-B/16 | 5 / 1 / 11 | 6 / 0 / 11 |
| MADation FE ViT-L/14 | 5 / 1 / 11 | 5 / 1 / 11 |
| MADation FS ViT-B/16 | 1 / 5 / 11 | 0 / 6 / 11 |
| MADation FS ViT-L/14 | 3 / 3 / 11 | 5 / 1 / 11 |
| MixFaceNet-MAD | 10 / 1 / 6 | 9 / 2 / 6 |

Not reproduced in variant 1 (selection): ViT-L/14 MorDIFF 2.95 against 19.26 (variant 2: 28.02, also not reproduced), ViT-L/14
StyleGAN2 39.2 against 24.96, ViT-L/14 MAD22 MIPGAN-I / MIPGAN-II / OpenCV / Webmorph, ViT-B/16 MAD22 MIPGAN-II 28.4
against 22.2, FE ViT-B/16 MorDIFF 2.85 against 17.86 and FE ViT-L/14 MorDIFF 5.90 against 22.85 (both reproduce in
variant 2: 18.12 and 22.08), MixFaceNet MorDIFF 6.36 against 8.50 (variant 2: 9.31, reproduced). The unchanged script
drops 416 of 1,222 FRLL FaceMorpher morphs (34%) and 55 of 1,000 MorDIFF morphs; those cells are computed without them
(counts in `rs1_reproduction.csv`).

## Reproduced rows: history-matched genuine photos and flag rates

"aligned" = no raw E7 file exists for the cell, so our aligned E7 frames went through the release crop; the history
effect is then aligned E7 minus aligned native. For StyleGAN2 and MAD22 MIPGAN the E7 rule leaves the photo unchanged
(morphs larger than photos), so the effect is 0 by construction. Flag rates at the threshold that flags 5% of the
native raw photos.

| Detector | Var. | Cell | Native EER | Published | EER with history-matched genuine (kind) | History effect | Flagged at 5%-photo threshold: history-matched / stored-small |
|---|---|---|---|---|---|---|---|
| MADation ViT-B/16 (LoRA) | 1 | amsl | 3.92 | 3.85 | 24.42 [19.62, 28.85] (aligned) | 18.96 [14.79, 23.05] (aligned) | 53.9 [42.6, 65.2] / 96.2 [93.1, 98.9] |
| MADation ViT-B/16 (LoRA) | 1 | facemorpher | 0.56 | 1.35 | 2.84 [1.01, 4.47] (aligned) | 1.85 [0.11, 3.44] (aligned) | 37.7 [24.5, 46.1] / 96.2 [93.1, 98.9] |
| MADation ViT-B/16 (LoRA) | 1 | opencv | 1.97 | 2.97 | 6.86 [3.94, 9.72] (aligned) | 3.90 [2.06, 6.58] (aligned) | 43.1 [30.9, 52.0] / 96.2 [93.1, 98.9] |
| MADation ViT-B/16 (LoRA) | 1 | webmorph | 2.33 | 3.42 | 15.71 [11.85, 19.13] (aligned) | 12.76 [8.82, 15.79] (aligned) | 55.9 [42.6, 64.7] / 96.2 [93.1, 98.9] |
| MADation ViT-B/16 (LoRA) | 1 | stylegan | 18.60 | 17.21 | 18.64 [15.17, 22.61] (aligned) | 0.00 [0.00, 0.00] (aligned) | 10.3 [5.9, 13.7] / 96.2 [93.1, 98.9] |
| MADation ViT-B/16 (LoRA) | 1 | mordiff | 0.00 | 1.1 | 3.93 [1.48, 7.35] (raw) | 3.93 [1.48, 7.35] | 74.9 [58.7, 81.9] / 96.2 [93.1, 98.9] |
| MADation ViT-B/16 (LoRA) | 1 | mad22_FaceMorpher | 0.00 | 0.0 | 13.66 [9.82, 17.56] (aligned) | 13.61 [9.81, 17.42] (aligned) | 97.5 [93.1, 100.0] / 96.2 [93.1, 98.9] |
| MADation ViT-B/16 (LoRA) | 1 | mad22_MIPGAN_I | 40.20 | 33.37 | 40.69 [34.76, 47.08] (aligned) | 0.00 [0.00, 0.00] (aligned) | 10.3 [5.9, 13.7] / 96.2 [93.1, 98.9] |
| MADation ViT-B/16 (LoRA) | 1 | mad22_OpenCV | 3.94 | 3.85 | 6.49 [3.40, 9.90] (aligned) | 0.60 [-0.35, 2.27] (aligned) | 13.7 [7.8, 17.2] / 96.2 [93.1, 98.9] |
| MADation ViT-B/16 (LoRA) | 1 | mad22_Webmorph | 10.89 | 10.8 | 14.21 [10.69, 18.33] (aligned) | 1.44 [0.00, 4.00] (aligned) | 14.2 [6.4, 17.6] / 96.2 [93.1, 98.9] |
| MADation ViT-L/14 (LoRA) | 1 | amsl | 7.90 | 7.26 | 7.31 [4.44, 10.07] (aligned) | -0.54 [-3.36, 2.53] (aligned) | 3.9 [1.5, 7.8] / 91.4 [86.6, 95.3] |
| MADation ViT-L/14 (LoRA) | 1 | facemorpher | 0.92 | 0.74 | 0.99 [0.08, 2.26] (aligned) | 0.00 [-0.91, 1.27] (aligned) | 3.4 [1.5, 6.9] / 91.4 [86.6, 95.3] |
| MADation ViT-L/14 (LoRA) | 1 | webmorph | 5.36 | 4.07 | 4.42 [2.42, 7.82] (aligned) | 0.00 [-1.95, 3.44] (aligned) | 4.4 [1.5, 8.8] / 91.4 [86.6, 95.3] |
| MADation ViT-L/14 (LoRA) | 1 | mad22_FaceMorpher | 0.49 | 0.4 | 2.48 [0.96, 4.91] (aligned) | 1.98 [0.56, 4.59] (aligned) | 17.6 [10.8, 27.5] / 91.4 [86.6, 95.3] |
| MADation FE ViT-L/14 | 1 | mad22_FaceMorpher | 9.80 | 9.77 | 13.22 [9.32, 16.25] (aligned) | 4.41 [1.45, 6.29] (aligned) | 6.9 [2.0, 15.7] / 86.0 [76.3, 94.1] |
| MADation FE ViT-L/14 | 1 | mad22_MIPGAN_I | 24.01 | 23.51 | 24.50 [19.21, 28.67] (aligned) | 0.00 [0.00, 0.00] (aligned) | 4.4 [1.5, 6.4] / 86.0 [76.3, 94.1] |
| MADation FE ViT-L/14 | 1 | mad22_MIPGAN_II | 22.04 | 21.81 | 20.60 [15.73, 25.51] (aligned) | 0.00 [0.00, 0.00] (aligned) | 4.4 [1.5, 6.4] / 86.0 [76.3, 94.1] |
| MADation FE ViT-L/14 | 1 | mad22_OpenCV | 15.67 | 15.89 | 15.22 [10.80, 19.16] (aligned) | 0.50 [-1.11, 1.48] (aligned) | 3.9 [2.0, 6.9] / 86.0 [76.3, 94.1] |
| MADation FE ViT-L/14 | 1 | mad22_Webmorph | 25.89 | 26.4 | 25.10 [20.20, 30.30] (aligned) | -0.35 [-1.81, 0.96] (aligned) | 4.4 [2.0, 6.9] / 86.0 [76.3, 94.1] |
| MADation FE ViT-B/16 | 1 | mad22_FaceMorpher | 2.97 | 2.89 | 27.97 [23.02, 32.55] (aligned) | 23.56 [19.15, 27.98] (aligned) | 81.9 [76.0, 89.7] / 93.5 [88.9, 97.4] |
| MADation FE ViT-B/16 | 1 | mad22_MIPGAN_I | 25.45 | 26.0 | 30.35 [26.41, 34.12] (aligned) | 0.00 [0.00, 0.00] (aligned) | 8.8 [5.4, 13.7] / 93.5 [88.9, 97.4] |
| MADation FE ViT-B/16 | 1 | mad22_MIPGAN_II | 34.32 | 34.26 | 37.74 [33.42, 42.22] (aligned) | 0.00 [0.00, 0.00] (aligned) | 8.8 [5.4, 13.7] / 93.5 [88.9, 97.4] |
| MADation FE ViT-B/16 | 1 | mad22_OpenCV | 14.72 | 14.88 | 19.21 [15.28, 23.09] (aligned) | 1.65 [0.00, 3.45] (aligned) | 10.3 [6.9, 16.2] / 93.5 [88.9, 97.4] |
| MADation FE ViT-B/16 | 1 | mad22_Webmorph | 32.72 | 32.8 | 39.31 [32.91, 45.71] (aligned) | 3.52 [0.70, 6.38] (aligned) | 10.8 [7.8, 17.2] / 93.5 [88.9, 97.4] |
| MixFaceNet-MAD | 1 | amsl | 15.16 | 15.18 | 41.19 [37.57, 44.12] (aligned) | 19.62 [15.70, 23.99] (aligned) | 40.2 [22.1, 59.8] / 80.1 [56.8, 94.1] |
| MixFaceNet-MAD | 1 | facemorpher | 4.44 | 3.87 | 7.27 [4.47, 12.68] (aligned) | 2.47 [1.06, 5.49] (aligned) | 26.5 [11.8, 40.7] / 80.1 [56.8, 94.1] |
| MixFaceNet-MAD | 1 | opencv | 4.89 | 4.39 | 11.75 [8.50, 15.65] (aligned) | 5.87 [3.51, 8.73] (aligned) | 32.8 [15.7, 46.1] / 80.1 [56.8, 94.1] |
| MixFaceNet-MAD | 1 | webmorph | 12.27 | 12.35 | 35.79 [32.39, 40.20] (aligned) | 18.53 [14.65, 23.68] (aligned) | 40.2 [19.1, 59.3] / 80.1 [56.8, 94.1] |
| MixFaceNet-MAD | 1 | stylegan | 9.20 | 8.99 | 13.21 [9.31, 16.73] (aligned) | 0.00 [0.00, 0.00] (aligned) | 9.3 [3.4, 17.2] / 80.1 [56.8, 94.1] |
| MixFaceNet-MAD | 1 | mad22_FaceMorpher | 4.90 | 4.6 | 13.32 [9.09, 19.11] (aligned) | 8.37 [5.48, 12.78] (aligned) | 86.3 [76.5, 94.1] / 80.1 [56.8, 94.1] |
| MixFaceNet-MAD | 1 | mad22_MIPGAN_I | 16.24 | 16.7 | 21.58 [16.37, 26.39] (aligned) | 0.00 [0.00, 0.00] (aligned) | 8.8 [3.4, 17.6] / 80.1 [56.8, 94.1] |
| MixFaceNet-MAD | 1 | mad22_MIPGAN_II | 20.60 | 20.62 | 26.00 [21.22, 30.26] (aligned) | 0.00 [0.00, 0.00] (aligned) | 8.8 [3.4, 17.6] / 80.1 [56.8, 94.1] |
| MixFaceNet-MAD | 1 | mad22_OpenCV | 8.38 | 8.33 | 11.88 [7.75, 17.03] (aligned) | 0.55 [-0.44, 2.50] (aligned) | 10.3 [3.4, 22.5] / 80.1 [56.8, 94.1] |
| MixFaceNet-MAD | 1 | mad22_Webmorph | 18.17 | 18.2 | 24.11 [18.23, 30.46] (aligned) | 2.53 [0.20, 4.34] (aligned) | 11.3 [3.4, 22.5] / 80.1 [56.8, 94.1] |
| MADation FS ViT-B/16 | 1 | mad22_FaceMorpher | 4.95 | 5.38 | 13.66 [8.92, 19.76] (aligned) | 8.27 [5.15, 12.33] (aligned) | 67.6 [58.3, 82.8] / 75.3 [45.7, 91.8] |
| MADation FS ViT-L/14 | 1 | mordiff | 37.66 | 40.92 | 38.93 [33.42, 45.70] (raw) | 1.27 [0.18, 6.07] | 11.8 [7.8, 17.2] / 19.9 [13.6, 26.3] |
| MADation FS ViT-L/14 | 1 | mad22_FaceMorpher | 17.62 | 22.63 | 21.19 [17.16, 25.98] (aligned) | 1.59 [-1.14, 4.92] (aligned) | 14.7 [10.3, 20.1] / 19.9 [13.6, 26.3] |
| MADation FS ViT-L/14 | 1 | mad22_OpenCV | 23.55 | 30.47 | 26.00 [21.95, 30.39] (aligned) | 0.50 [-1.00, 1.95] (aligned) | 8.3 [5.4, 14.7] / 19.9 [13.6, 26.3] |
| MADation ViT-B/16 (LoRA) | 2 | facemorpher | 0.53 | 1.35 | 2.33 [0.91, 3.95] (aligned) | 1.27 [0.00, 2.60] (aligned) | 38.2 [30.4, 45.6] / 60.3 [51.5, 69.1] |
| MADation ViT-B/16 (LoRA) | 2 | webmorph | 2.45 | 3.42 | 18.12 [13.71, 21.57] (aligned) | 14.64 [10.37, 17.43] (aligned) | 56.4 [48.5, 65.2] / 60.3 [51.5, 69.1] |
| MADation ViT-B/16 (LoRA) | 2 | stylegan | 15.78 | 17.21 | 18.64 [14.72, 22.53] (aligned) | 0.00 [0.00, 0.00] (aligned) | 8.3 [5.4, 12.7] / 60.3 [51.5, 69.1] |
| MADation ViT-B/16 (LoRA) | 2 | mordiff | 0.55 | 1.1 | 12.72 [8.79, 17.17] (raw) | 12.18 [8.26, 16.25] | 67.6 [60.3, 75.5] / 60.3 [51.5, 69.1] |
| MADation ViT-B/16 (LoRA) | 2 | mad22_FaceMorpher | 0.00 | 0.0 | 17.62 [12.83, 22.67] (aligned) | 17.62 [12.83, 22.67] (aligned) | 98.0 [95.1, 100.0] / 60.3 [51.5, 69.1] |
| MADation ViT-B/16 (LoRA) | 2 | mad22_MIPGAN_I | 39.21 | 33.37 | 43.12 [37.73, 47.93] (aligned) | 0.00 [0.00, 0.00] (aligned) | 8.8 [5.4, 13.2] / 60.3 [51.5, 69.1] |
| MADation ViT-B/16 (LoRA) | 2 | mad22_MIPGAN_II | 26.94 | 22.21 | 30.96 [25.57, 36.67] (aligned) | 0.00 [0.00, 0.00] (aligned) | 8.8 [5.4, 13.2] / 60.3 [51.5, 69.1] |
| MADation ViT-B/16 (LoRA) | 2 | mad22_OpenCV | 3.00 | 3.85 | 4.79 [2.46, 8.22] (aligned) | 0.35 [-0.25, 1.87] (aligned) | 11.8 [7.8, 16.2] / 60.3 [51.5, 69.1] |
| MADation ViT-B/16 (LoRA) | 2 | mad22_Webmorph | 9.80 | 10.8 | 13.76 [9.80, 18.52] (aligned) | 1.88 [0.20, 4.75] (aligned) | 12.7 [8.8, 17.2] / 60.3 [51.5, 69.1] |
| MADation ViT-L/14 (LoRA) | 2 | facemorpher | 0.98 | 0.74 | 0.86 [0.07, 1.71] (aligned) | 0.00 [-0.49, 0.54] (aligned) | 2.5 [0.5, 4.9] / 6.4 [2.9, 10.8] |
| MADation ViT-L/14 (LoRA) | 2 | opencv | 2.45 | 0.99 | 1.96 [0.56, 4.03] (aligned) | -0.45 [-1.06, 0.49] (aligned) | 2.5 [0.5, 4.4] / 6.4 [2.9, 10.8] |
| MADation ViT-L/14 (LoRA) | 2 | webmorph | 5.32 | 4.07 | 3.93 [1.92, 5.92] (aligned) | -0.98 [-3.40, 1.41] (aligned) | 2.9 [0.5, 5.9] / 6.4 [2.9, 10.8] |
| MADation ViT-L/14 (LoRA) | 2 | mad22_FaceMorpher | 0.10 | 0.4 | 2.92 [1.03, 4.83] (aligned) | 2.92 [1.03, 4.83] (aligned) | 23.5 [16.2, 30.4] / 6.4 [2.9, 10.8] |
| MADation ViT-L/14 (LoRA) | 2 | mad22_Webmorph | 23.02 | 20.4 | 20.59 [16.65, 25.50] (aligned) | -1.44 [-3.00, 0.25] (aligned) | 3.9 [1.5, 5.4] / 6.4 [2.9, 10.8] |
| MADation FE ViT-L/14 | 2 | mordiff | 22.08 | 22.85 | 27.92 [22.90, 31.92] (raw) | 5.84 [2.80, 8.35] | 7.8 [4.9, 15.2] / 5.4 [2.9, 12.7] |
| MADation FE ViT-L/14 | 2 | mad22_MIPGAN_I | 23.52 | 23.51 | 23.02 [18.12, 26.94] (aligned) | 0.00 [-1.44, 0.25] (aligned) | 4.4 [1.5, 6.9] / 5.4 [2.9, 12.7] |
| MADation FE ViT-L/14 | 2 | mad22_MIPGAN_II | 20.11 | 21.81 | 20.21 [15.27, 24.48] (aligned) | -0.40 [-1.19, 0.25] (aligned) | 4.4 [1.5, 6.9] / 5.4 [2.9, 12.7] |
| MADation FE ViT-L/14 | 2 | mad22_OpenCV | 15.67 | 15.89 | 15.22 [10.76, 19.50] (aligned) | 0.00 [-1.49, 1.22] (aligned) | 3.9 [1.5, 6.9] / 5.4 [2.9, 12.7] |
| MADation FE ViT-L/14 | 2 | mad22_Webmorph | 24.01 | 26.4 | 23.12 [18.23, 28.01] (aligned) | 0.00 [-1.63, 0.91] (aligned) | 4.4 [2.0, 6.9] / 5.4 [2.9, 12.7] |
| MADation FE ViT-B/16 | 2 | mordiff | 18.12 | 17.86 | 44.11 [39.29, 49.04] (raw) | 25.99 [22.10, 30.29] | 52.5 [38.2, 60.3] / 54.9 [41.7, 64.7] |
| MADation FE ViT-B/16 | 2 | mad22_FaceMorpher | 3.47 | 2.89 | 29.46 [24.96, 33.82] (aligned) | 25.00 [20.77, 28.37] (aligned) | 86.8 [76.0, 92.6] / 54.9 [41.7, 64.7] |
| MADation FE ViT-B/16 | 2 | mad22_MIPGAN_I | 27.38 | 26.0 | 31.29 [27.39, 35.34] (aligned) | 0.00 [-0.51, 0.44] (aligned) | 11.3 [5.9, 15.2] / 54.9 [41.7, 64.7] |
| MADation FE ViT-B/16 | 2 | mad22_MIPGAN_II | 35.37 | 34.26 | 43.14 [38.10, 47.03] (aligned) | 0.00 [0.00, 0.00] (aligned) | 11.3 [5.9, 15.2] / 54.9 [41.7, 64.7] |
| MADation FE ViT-B/16 | 2 | mad22_OpenCV | 13.72 | 14.88 | 20.51 [16.40, 24.08] (aligned) | 3.44 [1.39, 6.40] (aligned) | 16.7 [6.9, 23.0] / 54.9 [41.7, 64.7] |
| MADation FE ViT-B/16 | 2 | mad22_Webmorph | 35.25 | 32.8 | 43.61 [37.89, 49.95] (aligned) | 1.98 [0.90, 6.08] (aligned) | 14.7 [7.4, 19.6] / 54.9 [41.7, 64.7] |
| MixFaceNet-MAD | 2 | amsl | 17.15 | 15.18 | 40.69 [36.92, 44.11] (aligned) | 18.62 [14.47, 23.05] (aligned) | 36.3 [28.9, 50.5] / 58.8 [48.0, 73.0] |
| MixFaceNet-MAD | 2 | facemorpher | 2.94 | 3.87 | 6.46 [3.86, 9.82] (aligned) | 2.62 [0.91, 4.46] (aligned) | 27.5 [20.1, 38.2] / 58.8 [48.0, 73.0] |
| MixFaceNet-MAD | 2 | opencv | 4.01 | 4.39 | 13.25 [9.79, 16.32] (aligned) | 7.36 [4.30, 9.47] (aligned) | 31.9 [24.0, 42.6] / 58.8 [48.0, 73.0] |
| MixFaceNet-MAD | 2 | webmorph | 14.68 | 12.35 | 35.79 [32.25, 39.73] (aligned) | 17.18 [13.39, 21.84] (aligned) | 38.2 [29.4, 52.0] / 58.8 [48.0, 73.0] |
| MixFaceNet-MAD | 2 | mordiff | 9.31 | 8.5 | 30.40 [25.88, 35.37] (raw) | 21.09 [17.17, 24.96] | 62.7 [49.5, 76.5] / 58.8 [48.0, 73.0] |
| MixFaceNet-MAD | 2 | mad22_MIPGAN_I | 17.18 | 16.7 | 21.04 [16.63, 25.87] (aligned) | 0.00 [0.00, 0.00] (aligned) | 10.8 [6.9, 15.7] / 58.8 [48.0, 73.0] |
| MixFaceNet-MAD | 2 | mad22_MIPGAN_II | 21.10 | 20.62 | 25.01 [20.66, 29.49] (aligned) | 0.00 [0.00, 0.00] (aligned) | 10.8 [6.9, 15.7] / 58.8 [48.0, 73.0] |
| MixFaceNet-MAD | 2 | mad22_OpenCV | 9.78 | 8.33 | 13.32 [9.10, 18.60] (aligned) | 1.05 [0.00, 2.84] (aligned) | 13.2 [8.3, 19.6] / 58.8 [48.0, 73.0] |
| MixFaceNet-MAD | 2 | mad22_Webmorph | 19.16 | 18.2 | 25.89 [18.63, 30.85] (aligned) | 2.77 [-0.00, 3.91] (aligned) | 12.7 [8.3, 19.1] / 58.8 [48.0, 73.0] |
| MADation FS ViT-L/14 | 2 | mad22_FaceMorpher | 20.05 | 22.63 | 22.52 [18.32, 27.40] (aligned) | 2.43 [-1.15, 5.08] (aligned) | 9.8 [5.4, 13.7] / 11.3 [3.4, 16.7] |
| MADation FS ViT-L/14 | 2 | mad22_MIPGAN_I | 19.11 | 23.8 | 19.50 [15.71, 23.99] (aligned) | 0.00 [-0.05, 0.00] (aligned) | 7.4 [3.4, 11.3] / 11.3 [3.4, 16.7] |
| MADation FS ViT-L/14 | 2 | mad22_MIPGAN_II | 20.70 | 21.81 | 22.04 [17.73, 26.47] (aligned) | 0.00 [0.00, 0.00] (aligned) | 7.4 [3.4, 11.3] / 11.3 [3.4, 16.7] |
| MADation FS ViT-L/14 | 2 | mad22_OpenCV | 24.40 | 30.47 | 26.55 [22.21, 31.80] (aligned) | 0.00 [-2.11, 1.24] (aligned) | 6.9 [2.9, 10.8] / 11.3 [3.4, 16.7] |
| MADation FS ViT-L/14 | 2 | mad22_Webmorph | 26.43 | 33.6 | 31.39 [25.43, 36.43] (aligned) | 0.99 [-1.46, 2.91] (aligned) | 6.4 [2.5, 10.3] / 11.3 [3.4, 16.7] |

## MorDIFF ladder (reproduced MorDIFF rows; A43 control images through the release crop)

| Release, variant | stored-small vs photo | reconstruction D20 vs stored-small | our morph B20 vs D20 | published vs our morph B20 | flagged at 5%-photo threshold: stored-small / D20 / B20 / published |
|---|---|---|---|---|---|
| MADation ViT-B/16, 1 | 0.991 [0.983, 0.997] | 0.503 [0.451, 0.556] | 0.529 [0.438, 0.617] | 0.481 [0.404, 0.556] | 96.2 / 100 / 100 / 100 |
| MADation ViT-B/16, 2 | 0.890 [0.861, 0.917] | 0.941 [0.918, 0.962] | 0.664 [0.562, 0.754] | 0.481 [0.445, 0.509] | 60.3 / 100 / 100 / 100 |
| MADation FE ViT-L/14, 2 | 0.567 [0.544, 0.594] | 0.748 [0.718, 0.781] | 0.572 [0.497, 0.649] | 0.502 [0.477, 0.526] | 5.4 / 27.5 / 30.5 / 30.0 |
| MADation FE ViT-B/16, 2 | 0.882 [0.859, 0.908] | 0.617 [0.582, 0.654] | 0.440 [0.363, 0.516] | 0.497 [0.469, 0.526] | 54.9 / 68.6 / 64.0 / 60.0 |
| MixFaceNet-MAD, 2 | 0.870 [0.834, 0.908] | 0.778 [0.742, 0.819] | 0.489 [0.410, 0.567] | 0.490 [0.458, 0.525] | 58.8 / 85.3 / 87.0 / 86.5 |
| MADation FS ViT-L/14, 1 | 0.572 [0.521, 0.625] | 0.509 [0.466, 0.555] | 0.538 [0.472, 0.609] | 0.458 [0.383, 0.532] | (MorDIFF EER 37.7) |

MorDIFF raw E7 history effect: ViT-B/16 variant 1 0.00 -> 3.93 (+3.9 [1.5, 7.4]), variant 2 0.55 -> 12.72 (+12.2
[8.3, 16.3]); FE ViT-L/14 variant 2 +5.8 [2.8, 8.4]; FE ViT-B/16 variant 2 +26.0 [22.1, 30.3]; MixFaceNet variant 2
+21.1 [17.2, 25.0].

## Release rule (probability of morph > 0.5) and paired logit shifts, variant 1

At the release's own rule, unprocessed raw FRLL photos are flagged at 0.0% (ViT-B/16, ViT-L/14) and 0.5% (MixFaceNet).
ViT-B/16: 50% shrink-and-enlarge 2.0%, raw E7 MorDIFF 3.4%, stored-small 10.8%, FFHQ with DiffAE history 7.1% (orig
0.0%). ViT-L/14: JPEG 50 0.0%, raw E7 0.5%, stored-small 8.1%, FFHQ history 0.3%. MixFaceNet: shrink-and-enlarge
12.3%, raw E7 18.2%, stored-small 26.3%, FFHQ history 7.4%, FEI 7.7 / 10.8%. Paired logit shifts (processed copy minus
its own photo): ViT-B/16 shrink-and-enlarge +1.37 [0.95, 1.86] (99% of photos rise), raw E7 MorDIFF +1.80 [1.30,
2.45] (99.5%), stored-small +10.30 [9.76, 10.80] (100%), FFHQ history +2.01 [1.79, 2.23] (96%); ViT-L/14 JPEG 50
+0.10 (100%), shrink-and-enlarge +0.01, raw E7 +0.09, stored-small +11.12 [10.49, 11.69] (92.5%), FFHQ +0.09;
MixFaceNet shrink-and-enlarge +7.78, raw E7 +11.39, stored-small +12.69, FFHQ +11.58 (99%). Full table:
`rs1_pool_rates.csv` (threshold pool as a column) and `rs1_shifts.csv`.

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

## Findings on the measurement itself

- **JPEG decoder build.** Byte-identical JPEG crops scored on two machines with the same Pillow version number differed
  by up to 5.9 logits (conda Pillow vs PyPI Pillow 10.2.0); after installing the PyPI wheel (libjpeg-turbo 3.0.1)
  identical crops agree within 0.19 logit (ViT-B/16, 13 of 464 images above 0.05; other releases at most 0.08).
- **JPEG re-save of the crop step** (300 files, identical regions, JPEG q95 vs PNG): median |logit difference| 0.003
  to 0.86 by release, up to 16 logits on single images (`rs1_jpeg_storage_check.json`).
- **Detector boxes differ between GPUs** (A100 vs RTX 3090): 47 of 463 (variant 1) and 85 of 464 (variant 2) smoke
  crops differ; their scores differ by up to 9.5 logits. All rows come from one machine.
- **Border.** The release crops of the raw benchmark files contain no black border (mean black fraction 0.000 for
  every raw morph and photo set); our aligned 512 frames carry 5 to 54% black pixels (MorDIFF frames 53 to 54%); the
  release crop of our aligned MorDIFF frames keeps 5 to 8% black pixels (Galn_mordiff, E7aln_mordiff), the other
  aligned genuine frames 0% (`rs1_border.csv`).
- **Unchanged crop script drops images**: 794 of 29,056 (FRLL FaceMorpher 34%).

## Deviations and what could not be verified

- Platform changes (amendments 1 to 6): Athena smoke only; production on one rented RTX 3090; the gate against Athena
  became descriptive. The reused A46 crops and the JPEG-re-encoding corrected crop are not result rows.
- SelfMAD runs: existing WCSS files and a separate DGX run; no SelfMAD row is compared across the two.
- Aligned-frame E7 rows (FRLL landmark families, MAD22, four DiM families) mix our alignment with the history.
- Published numbers from the arXiv HTML; CVF PDFs not opened; published genuine populations and the corrected MAD22's
  equivalence with the published MAD22 not verified.
- Crop files of both variants were on the rented machine only and are gone with it; their sha256 lists are in
  `/mnt/t7/smad_next/RS1/results_rented/prod_v{1,2}_rented/crops_sha256.txt`.
- Compute: Athena smoke jobs 3544220 (0:06:52), 3545836 (0:02:37, cancelled), 3545869 (0:03:34), all 1 GPU, account
  plgrestorearc-gpu-a100; production jobs 3545884, 3545918/3545919, 3545970/3545971, 3545972/3545973 never started
  (0 GPU-hours). Rented RTX 3090 (rs1b) about 2.5 h at 0.44 USD/h, rented and released by the lead; first rented
  machine (137.175.22.196) idle/upload only. DGX: shared GPU, about 2.5 h of scoring and cropping.
