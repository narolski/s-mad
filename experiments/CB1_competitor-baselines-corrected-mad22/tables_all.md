
### Corrected MAD22 (204 genuine + 4,483 morphs): EER (%) per family, seed mean; MEAN5 with two-way person bootstrap 95% CI

| Arm | ckpt | genuine pool | n | FaceMorpher | OpenCV | Webmorph | MIPGAN_I | MIPGAN_II | MEAN5 [95% CI] | published mean | reading (90% seed t-interval of the difference vs M) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A12BR_M1 | es (primary) | e7 | 5 | 39.04 | 4.23 | 14.75 | 18.84 | 24.40 | 20.25 [17.93, 22.75] |  |  |
| A12BR_M1 | es (primary) | native | 5 | 6.01 | 3.79 | 13.50 | 18.84 | 24.40 | 13.31 [11.08, 15.63] | 10.53 | inconclusive; delta +2.78 [-0.23, +5.80], M 3.16 |
| A12BR_M1 | last | e7 | 5 | 43.35 | 4.21 | 13.46 | 23.16 | 30.63 | 22.96 [20.36, 25.53] |  |  |
| A12BR_M1 | last | native | 5 | 11.06 | 4.02 | 12.07 | 23.16 | 30.63 | 16.19 [13.72, 18.65] | 10.53 | inconclusive; delta +5.66 [-0.47, +11.79], M 3.16 |
| A12BR_M2 | es (primary) | e7 | 5 | 74.11 | 12.19 | 19.67 | 42.26 | 43.64 | 38.37 [35.47, 41.17] |  |  |
| A12BR_M2 | es (primary) | native | 5 | 51.55 | 11.87 | 19.39 | 42.26 | 43.64 | 33.74 [30.43, 36.81] | 9.42 | does not reproduce (worse); delta +24.32 [+13.10, +35.54], M 2.83 |
| A12BR_M2 | last | e7 | 5 | 70.50 | 11.30 | 18.40 | 45.34 | 46.15 | 38.34 [35.28, 41.19] |  |  |
| A12BR_M2 | last | native | 5 | 52.37 | 10.87 | 18.26 | 45.34 | 46.15 | 34.60 [31.30, 37.52] | 9.42 | does not reproduce (worse); delta +25.18 [+15.71, +34.65], M 2.83 |
| A12BR_M4 | es (primary) | e7 | 4 | 0.63 | 21.47 | 49.64 | 31.37 | 27.25 | 26.07 [24.41, 27.97] |  |  |
| A12BR_M4 | es (primary) | native | 4 | 99.63 | 22.68 | 51.37 | 31.37 | 27.33 | 46.48 [44.75, 48.38] |  |  |
| A12BR_M5 | es (primary) | e7 | 5 | 17.74 | 9.15 | 22.45 | 36.30 | 37.84 | 24.70 [21.96, 27.97] |  |  |
| A12BR_M5 | es (primary) | native | 5 | 1.06 | 8.82 | 21.67 | 36.30 | 37.84 | 21.14 [19.06, 23.45] |  |  |
| A12BR_M6 | es (primary) | e7 | 5 | 45.28 | 10.39 | 16.98 | 35.40 | 35.03 | 28.61 [26.08, 31.54] |  |  |
| A12BR_M6 | es (primary) | native | 5 | 22.84 | 9.91 | 16.74 | 35.40 | 35.03 | 23.98 [21.30, 27.08] |  |  |
| A12BR_M6 | last | e7 | 5 | 59.10 | 12.81 | 20.09 | 39.28 | 39.32 | 34.12 [31.37, 37.24] |  |  |
| A12BR_M6 | last | native | 5 | 37.08 | 12.43 | 19.60 | 39.28 | 39.32 | 29.54 [26.73, 32.72] |  |  |
| A12BR_M8 | es (primary) | e7 | 5 | 65.12 | 7.35 | 15.27 | 34.15 | 33.26 | 31.03 [28.35, 33.86] |  |  |
| A12BR_M8 | es (primary) | native | 5 | 26.55 | 6.85 | 14.47 | 34.15 | 33.26 | 23.06 [20.23, 26.20] | 13.69 | inconclusive; delta +9.37 [-0.32, +19.05], M 4.11 |
| A12BR_M8 | last | e7 | 5 | 71.06 | 7.10 | 14.10 | 40.74 | 40.12 | 34.62 [31.91, 37.47] |  |  |
| A12BR_M8 | last | native | 5 | 27.87 | 6.72 | 13.70 | 40.74 | 40.12 | 25.83 [23.03, 28.87] | 13.69 | does not reproduce (worse); delta +12.14 [+7.68, +16.61], M 4.11 |
| A12BR_M8O | es (primary) | e7 | 5 | 68.91 | 6.75 | 15.33 | 44.33 | 42.39 | 35.54 [32.72, 38.17] |  |  |
| A12BR_M8O | es (primary) | native | 5 | 30.19 | 6.48 | 14.57 | 44.33 | 42.39 | 27.59 [24.56, 30.32] | 13.69 | does not reproduce (worse); delta +13.90 [+10.38, +17.42], M 4.11 |
| A12BR_M8O | last | e7 | 4 | 69.47 | 9.53 | 18.30 | 51.72 | 50.98 | 40.00 [36.94, 42.75] |  |  |
| A12BR_M8O | last | native | 4 | 43.97 | 9.04 | 17.07 | 51.72 | 50.98 | 34.56 [31.47, 37.58] | 13.69 | does not reproduce (worse); delta +20.87 [+6.08, +35.65], M 4.11 |
| A45_hrnetw18 | es | e7 | 5 | 67.82 | 10.04 | 17.95 | 35.65 | 35.59 | 33.41 [30.38, 36.48] |  |  |
| A45_hrnetw18 | es | native | 5 | 47.25 | 9.79 | 16.91 | 35.65 | 35.59 | 29.04 [25.85, 32.16] | 9.42 | does not reproduce (worse); delta +19.62 [+8.33, +30.91], M 2.83 |
| A45_hrnetw18 | last (primary) | e7 | 5 | 79.23 | 12.21 | 21.33 | 52.64 | 53.42 | 43.77 [40.68, 46.87] |  |  |
| A45_hrnetw18 | last (primary) | native | 5 | 63.82 | 11.47 | 20.31 | 52.64 | 53.42 | 40.33 [37.10, 43.63] | 9.42 | does not reproduce (worse); delta +30.91 [+22.18, +39.64], M 2.83 |
| A45_incepofc | es | e7 | 5 | 76.56 | 7.14 | 15.77 | 24.32 | 28.95 | 30.55 [27.87, 33.29] |  |  |
| A45_incepofc | es | native | 5 | 32.45 | 6.59 | 14.60 | 24.32 | 28.95 | 21.38 [18.34, 24.58] | 10.53 | does not reproduce (worse); delta +10.85 [+8.42, +13.28], M 3.16 |
| A45_incepofc | last (primary) | e7 | 5 | 85.08 | 6.95 | 16.35 | 41.96 | 46.39 | 39.34 [36.64, 42.07] |  |  |
| A45_incepofc | last (primary) | native | 5 | 51.07 | 6.39 | 15.22 | 41.96 | 46.39 | 32.20 [29.12, 35.23] | 10.53 | does not reproduce (worse); delta +21.68 [+15.76, +27.60], M 3.16 |
| FDMAD_f256 | model (primary) | e7 | 3 | 90.48 | 33.52 | 30.10 | 54.29 | 45.09 | 50.69 [48.05, 53.42] |  |  |
| FDMAD_f256 | model (primary) | native | 3 | 100.00 | 41.50 | 39.54 | 54.29 | 45.09 | 56.08 [53.51, 58.77] | 6.12 | no reading (local branch not functional); partial re-implementation, does not reach the published fused number; delta +49.96 [+48.82, +51.10], M 1.84 |
| FDMAD_f512 | model (primary) | e7 | 3 | 50.35 | 39.20 | 58.48 | 20.30 | 30.71 | 39.81 [37.68, 41.71] |  |  |
| FDMAD_f512 | model (primary) | native | 3 | 1.34 | 49.30 | 63.40 | 20.30 | 30.71 | 33.01 [30.80, 35.16] | 6.12 | partial re-implementation, does not reach the published fused number; delta +26.89 [+26.83, +26.94], M 1.84 |
| FDMAD_g256 | model (primary) | e7 | 3 | 95.76 | 33.52 | 30.10 | 54.27 | 45.09 | 51.75 [49.26, 54.34] |  |  |
| FDMAD_g256 | model (primary) | native | 3 | 100.00 | 41.50 | 39.54 | 54.27 | 45.09 | 56.08 [53.51, 58.77] | 6.12 | partial re-implementation, does not reach the published fused number; delta +49.96 [+48.81, +51.11], M 1.84 |
| FDMAD_g512 | model (primary) | e7 | 3 | 52.77 | 35.78 | 60.28 | 21.45 | 21.73 | 38.40 [35.68, 40.88] |  |  |
| FDMAD_g512 | model (primary) | native | 3 | 22.94 | 23.39 | 51.14 | 21.45 | 21.73 | 28.13 [25.55, 30.79] | 6.12 | partial re-implementation, does not reach the published fused number; delta +22.01 [+21.44, +22.58], M 1.84 |

### Corrected MAD22 (204 genuine + 4,483 morphs): BPCER (%) at APCER 1 / 5 / 10 / 20 %, native genuine pool, primary checkpoint, seed mean

| Arm | family | BPCER@1 | BPCER@5 | BPCER@10 | BPCER@20 |
|---|---|---|---|---|---|
| A12BR_M1 | FaceMorpher | 69.71 | 14.41 | 1.57 | 0.20 |
| A12BR_M1 | OpenCV | 11.47 | 3.04 | 0.88 | 0.20 |
| A12BR_M1 | Webmorph | 42.16 | 25.39 | 16.47 | 8.24 |
| A12BR_M1 | MIPGAN_I | 53.14 | 35.49 | 26.57 | 18.14 |
| A12BR_M1 | MIPGAN_II | 60.39 | 45.39 | 38.73 | 28.24 |
| A12BR_M2 | FaceMorpher | 100.00 | 98.73 | 89.41 | 71.08 |
| A12BR_M2 | OpenCV | 42.75 | 24.31 | 14.90 | 5.98 |
| A12BR_M2 | Webmorph | 65.69 | 45.39 | 32.75 | 18.14 |
| A12BR_M2 | MIPGAN_I | 95.29 | 78.92 | 68.33 | 56.76 |
| A12BR_M2 | MIPGAN_II | 95.49 | 81.67 | 70.00 | 58.43 |
| A12BR_M5 | FaceMorpher | 16.27 | 0.59 | 0.10 | 0.00 |
| A12BR_M5 | OpenCV | 83.33 | 31.37 | 13.92 | 0.49 |
| A12BR_M5 | Webmorph | 88.14 | 67.84 | 50.98 | 28.14 |
| A12BR_M5 | MIPGAN_I | 95.00 | 85.10 | 74.31 | 58.73 |
| A12BR_M5 | MIPGAN_II | 92.35 | 82.25 | 73.63 | 57.35 |
| A12BR_M6 | FaceMorpher | 98.14 | 76.76 | 47.65 | 26.86 |
| A12BR_M6 | OpenCV | 41.57 | 15.20 | 10.10 | 4.02 |
| A12BR_M6 | Webmorph | 61.86 | 37.55 | 25.00 | 14.51 |
| A12BR_M6 | MIPGAN_I | 100.00 | 94.31 | 83.82 | 61.96 |
| A12BR_M6 | MIPGAN_II | 100.00 | 95.59 | 82.45 | 60.78 |
| A12BR_M8 | FaceMorpher | 85.29 | 62.06 | 40.88 | 27.94 |
| A12BR_M8 | OpenCV | 27.25 | 8.63 | 4.12 | 0.59 |
| A12BR_M8 | Webmorph | 55.69 | 33.82 | 22.06 | 9.80 |
| A12BR_M8 | MIPGAN_I | 89.12 | 73.53 | 64.12 | 50.49 |
| A12BR_M8 | MIPGAN_II | 87.35 | 74.61 | 62.65 | 47.75 |
| A12BR_M8O | FaceMorpher | 98.43 | 80.00 | 57.45 | 38.24 |
| A12BR_M8O | OpenCV | 24.90 | 8.14 | 3.73 | 1.08 |
| A12BR_M8O | Webmorph | 51.18 | 31.86 | 21.96 | 9.12 |
| A12BR_M8O | MIPGAN_I | 95.98 | 85.69 | 77.84 | 67.55 |
| A12BR_M8O | MIPGAN_II | 94.80 | 85.69 | 75.69 | 64.31 |
| A12BR_M4 | FaceMorpher | 100.00 | 100.00 | 100.00 | 100.00 |
| A12BR_M4 | OpenCV | 54.90 | 41.91 | 34.68 | 24.75 |
| A12BR_M4 | Webmorph | 94.85 | 84.56 | 79.41 | 70.83 |
| A12BR_M4 | MIPGAN_I | 69.85 | 54.17 | 47.92 | 39.09 |
| A12BR_M4 | MIPGAN_II | 66.18 | 48.90 | 41.67 | 31.50 |
| A45_incepofc | FaceMorpher | 91.67 | 75.49 | 69.12 | 62.65 |
| A45_incepofc | OpenCV | 28.24 | 10.29 | 4.31 | 1.37 |
| A45_incepofc | Webmorph | 57.55 | 34.71 | 23.04 | 11.18 |
| A45_incepofc | MIPGAN_I | 87.25 | 79.61 | 74.90 | 67.35 |
| A45_incepofc | MIPGAN_II | 90.49 | 83.24 | 79.51 | 72.84 |
| A45_hrnetw18 | FaceMorpher | 98.53 | 96.76 | 90.39 | 86.08 |
| A45_hrnetw18 | OpenCV | 48.43 | 24.02 | 14.12 | 5.29 |
| A45_hrnetw18 | Webmorph | 72.55 | 46.27 | 33.92 | 20.49 |
| A45_hrnetw18 | MIPGAN_I | 98.82 | 95.10 | 89.41 | 82.06 |
| A45_hrnetw18 | MIPGAN_II | 98.73 | 95.39 | 89.41 | 81.96 |
| FDMAD_g256 | FaceMorpher | 100.00 | 100.00 | 100.00 | 100.00 |
| FDMAD_g256 | OpenCV | 96.41 | 89.54 | 83.33 | 69.12 |
| FDMAD_g256 | Webmorph | 87.58 | 76.31 | 67.97 | 57.68 |
| FDMAD_g256 | MIPGAN_I | 100.00 | 99.67 | 96.57 | 88.56 |
| FDMAD_g256 | MIPGAN_II | 99.67 | 95.10 | 87.09 | 79.90 |
| FDMAD_g512 | FaceMorpher | 100.00 | 100.00 | 100.00 | 100.00 |
| FDMAD_g512 | OpenCV | 66.67 | 50.33 | 39.87 | 26.63 |
| FDMAD_g512 | Webmorph | 97.39 | 95.42 | 90.52 | 81.37 |
| FDMAD_g512 | MIPGAN_I | 96.08 | 70.92 | 49.02 | 22.39 |
| FDMAD_g512 | MIPGAN_II | 98.04 | 66.34 | 44.61 | 23.86 |
| FDMAD_f256 | FaceMorpher | 100.00 | 100.00 | 100.00 | 100.00 |
| FDMAD_f256 | OpenCV | 96.41 | 89.54 | 83.33 | 69.12 |
| FDMAD_f256 | Webmorph | 87.58 | 76.31 | 67.97 | 57.68 |
| FDMAD_f256 | MIPGAN_I | 100.00 | 99.67 | 96.57 | 88.56 |
| FDMAD_f256 | MIPGAN_II | 99.51 | 95.10 | 87.09 | 79.90 |
| FDMAD_f512 | FaceMorpher | 1.63 | 0.33 | 0.00 | 0.00 |
| FDMAD_f512 | OpenCV | 86.76 | 77.29 | 70.10 | 60.78 |
| FDMAD_f512 | Webmorph | 96.41 | 91.99 | 89.05 | 83.66 |
| FDMAD_f512 | MIPGAN_I | 51.96 | 39.38 | 29.74 | 20.42 |
| FDMAD_f512 | MIPGAN_II | 70.42 | 53.92 | 48.04 | 38.40 |

### FRLL-Morphs: EER (%) per family, seed mean; MEAN5 with two-way person bootstrap 95% CI

| Arm | ckpt | genuine pool | n | amsl | facemorpher | opencv | stylegan | webmorph | MEAN5 [95% CI] | published mean | reading (90% seed t-interval of the difference vs M) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A12BR_M1 | es (primary) | e7 | 5 | 45.88 | 70.48 | 72.37 | 15.31 | 41.83 | 49.17 [46.23, 52.23] |  |  |
| A12BR_M1 | es (primary) | native | 5 | 27.66 | 51.19 | 53.03 | 15.31 | 25.10 | 34.46 [31.72, 37.30] | 8.11 | does not reproduce (worse); delta +26.34 [+16.54, +36.14], M 2.43 |
| A12BR_M1 | last | e7 | 5 | 50.27 | 72.65 | 77.27 | 17.37 | 48.16 | 53.14 [49.50, 56.82] |  |  |
| A12BR_M1 | last | native | 5 | 33.06 | 58.63 | 62.85 | 17.37 | 30.59 | 40.50 [36.92, 44.03] | 8.11 | does not reproduce (worse); delta +32.38 [+26.65, +38.12], M 2.43 |
| A12BR_M2 | es (primary) | e7 | 5 | 79.54 | 93.03 | 89.88 | 39.32 | 73.33 | 75.02 [71.80, 78.11] |  |  |
| A12BR_M2 | es (primary) | native | 5 | 72.94 | 91.07 | 87.02 | 39.32 | 67.06 | 71.48 [68.13, 74.85] |  |  |
| A12BR_M2 | last | e7 | 5 | 76.66 | 89.53 | 84.54 | 43.13 | 70.20 | 72.81 [69.69, 75.89] |  |  |
| A12BR_M2 | last | native | 5 | 71.19 | 87.24 | 80.48 | 43.13 | 65.00 | 69.41 [66.17, 72.55] |  |  |
| A12BR_M4 | es (primary) | e7 | 4 | 99.98 | 81.62 | 24.50 | 47.77 | 100.00 | 70.77 [69.38, 72.44] |  |  |
| A12BR_M4 | es (primary) | native | 4 | 100.00 | 90.29 | 40.56 | 47.77 | 100.00 | 75.72 [74.02, 77.53] |  |  |
| A12BR_M5 | es (primary) | e7 | 5 | 24.73 | 28.06 | 30.61 | 39.35 | 13.36 | 27.22 [23.04, 30.81] |  |  |
| A12BR_M5 | es (primary) | native | 5 | 8.92 | 17.39 | 17.58 | 39.35 | 3.82 | 17.41 [13.85, 21.02] | 10.62 | inconclusive; delta +6.79 [-1.55, +15.14], M 3.19 |
| A12BR_M6 | es (primary) | e7 | 5 | 74.43 | 66.48 | 84.73 | 35.80 | 68.92 | 66.07 [63.45, 69.00] |  |  |
| A12BR_M6 | es (primary) | native | 5 | 67.93 | 60.70 | 80.68 | 35.80 | 61.22 | 61.26 [58.36, 64.02] | 6.6 | does not reproduce (worse); delta +54.67 [+49.11, +60.22], M 1.98 |
| A12BR_M6 | last | e7 | 5 | 80.31 | 77.25 | 93.55 | 37.65 | 74.30 | 72.61 [69.96, 75.44] |  |  |
| A12BR_M6 | last | native | 5 | 74.31 | 72.67 | 91.34 | 37.65 | 67.98 | 68.79 [65.95, 71.87] | 6.6 | does not reproduce (worse); delta +62.19 [+56.97, +67.42], M 1.98 |
| A12BR_M8 | es (primary) | e7 | 5 | 62.43 | 75.00 | 69.82 | 23.14 | 60.97 | 58.27 [54.99, 61.61] |  |  |
| A12BR_M8 | es (primary) | native | 5 | 46.58 | 66.38 | 58.07 | 23.14 | 44.83 | 47.80 [44.91, 50.99] | 8.96 | does not reproduce (worse); delta +38.84 [+30.05, +47.64], M 2.69 |
| A12BR_M8 | last | e7 | 5 | 60.11 | 62.58 | 64.90 | 27.15 | 58.51 | 54.65 [50.88, 58.50] |  |  |
| A12BR_M8 | last | native | 5 | 44.06 | 50.85 | 50.69 | 27.15 | 41.49 | 42.85 [39.31, 46.43] | 8.96 | does not reproduce (worse); delta +33.89 [+29.09, +38.69], M 2.69 |
| A12BR_M8O | es (primary) | e7 | 5 | 66.96 | 88.06 | 85.01 | 32.80 | 65.20 | 67.61 [64.36, 70.88] |  |  |
| A12BR_M8O | es (primary) | native | 5 | 56.38 | 85.21 | 78.90 | 32.80 | 54.99 | 61.66 [58.36, 64.94] | 8.96 | does not reproduce (worse); delta +52.70 [+44.42, +60.98], M 2.69 |
| A12BR_M8O | last | e7 | 4 | 64.45 | 75.11 | 70.72 | 38.55 | 62.95 | 62.36 [58.31, 66.32] |  |  |
| A12BR_M8O | last | native | 4 | 53.65 | 68.48 | 62.49 | 38.55 | 50.99 | 54.83 [50.91, 58.83] | 8.96 | does not reproduce (worse); delta +45.88 [+38.35, +53.41], M 2.69 |
| A45_hrnetw18 | es | e7 | 5 | 67.83 | 81.46 | 78.91 | 33.31 | 60.95 | 64.49 [61.01, 67.75] |  |  |
| A45_hrnetw18 | es | native | 5 | 58.54 | 76.68 | 73.33 | 33.31 | 51.08 | 58.59 [55.16, 62.04] |  |  |
| A45_hrnetw18 | last (primary) | e7 | 5 | 68.62 | 85.29 | 79.48 | 46.05 | 63.03 | 68.49 [64.98, 71.83] |  |  |
| A45_hrnetw18 | last (primary) | native | 5 | 60.81 | 82.15 | 75.47 | 46.05 | 54.87 | 63.87 [60.30, 67.28] |  |  |
| A45_incepofc | es | e7 | 5 | 38.05 | 81.55 | 71.05 | 22.40 | 27.92 | 48.19 [45.39, 50.98] |  |  |
| A45_incepofc | es | native | 5 | 24.67 | 75.93 | 60.20 | 22.40 | 16.70 | 39.98 [37.31, 42.88] | 8.11 | does not reproduce (worse); delta +31.87 [+26.40, +37.33], M 2.43 |
| A45_incepofc | last (primary) | e7 | 5 | 42.51 | 81.28 | 77.37 | 31.19 | 31.93 | 52.86 [49.66, 55.97] |  |  |
| A45_incepofc | last (primary) | native | 5 | 29.35 | 74.33 | 66.70 | 31.19 | 20.93 | 44.50 [41.45, 47.64] | 8.11 | does not reproduce (worse); delta +36.38 [+27.87, +44.90], M 2.43 |
| FDMAD_f256 | model (primary) | e7 | 3 | 89.12 | 72.74 | 25.96 | 41.33 | 89.53 | 63.74 [61.16, 65.82] |  |  |
| FDMAD_f256 | model (primary) | native | 3 | 97.68 | 97.03 | 81.88 | 41.33 | 97.21 | 83.02 [81.09, 84.93] | 1.85 | no reading (local branch not functional); partial re-implementation, does not reach the published fused number; delta +81.17 [+80.58, +81.77], M 1.50 |
| FDMAD_f512 | model (primary) | e7 | 3 | 4.41 | 5.23 | 45.86 | 25.32 | 4.04 | 16.97 [15.28, 18.86] |  |  |
| FDMAD_f512 | model (primary) | native | 3 | 1.86 | 16.00 | 49.99 | 25.32 | 2.02 | 19.04 [17.09, 21.47] | 1.85 | partial re-implementation, does not reach the published fused number; delta +17.19 [+16.61, +17.77], M 1.50 |
| FDMAD_g256 | model (primary) | e7 | 3 | 89.09 | 72.74 | 25.96 | 41.33 | 89.53 | 63.73 [61.12, 65.81] |  |  |
| FDMAD_g256 | model (primary) | native | 3 | 97.68 | 97.03 | 81.88 | 41.33 | 97.21 | 83.02 [81.08, 84.92] | 1.85 | partial re-implementation, does not reach the published fused number; delta +81.17 [+80.58, +81.77], M 1.50 |
| FDMAD_g512 | model (primary) | e7 | 3 | 22.61 | 16.52 | 79.28 | 58.64 | 11.64 | 37.74 [35.43, 39.97] |  |  |
| FDMAD_g512 | model (primary) | native | 3 | 0.02 | 0.98 | 14.83 | 58.64 | 0.00 | 14.90 [13.25, 16.59] | 1.85 | partial re-implementation, does not reach the published fused number; delta +13.05 [+12.56, +13.53], M 1.50 |

### FRLL-Morphs: BPCER (%) at APCER 1 / 5 / 10 / 20 %, native genuine pool, primary checkpoint, seed mean

| Arm | family | BPCER@1 | BPCER@5 | BPCER@10 | BPCER@20 |
|---|---|---|---|---|---|
| A12BR_M1 | amsl | 86.96 | 70.20 | 55.39 | 39.22 |
| A12BR_M1 | facemorpher | 90.20 | 81.18 | 74.31 | 66.96 |
| A12BR_M1 | opencv | 86.27 | 75.49 | 69.71 | 64.02 |
| A12BR_M1 | stylegan | 56.08 | 33.04 | 22.45 | 11.08 |
| A12BR_M1 | webmorph | 92.55 | 65.88 | 50.69 | 34.22 |
| A12BR_M2 | amsl | 100.00 | 99.71 | 98.43 | 94.61 |
| A12BR_M2 | facemorpher | 100.00 | 100.00 | 100.00 | 100.00 |
| A12BR_M2 | opencv | 100.00 | 100.00 | 99.71 | 99.12 |
| A12BR_M2 | stylegan | 87.55 | 76.08 | 67.06 | 56.18 |
| A12BR_M2 | webmorph | 100.00 | 99.80 | 96.27 | 92.84 |
| A12BR_M5 | amsl | 53.92 | 23.73 | 20.69 | 11.96 |
| A12BR_M5 | facemorpher | 79.61 | 42.16 | 29.90 | 22.06 |
| A12BR_M5 | opencv | 84.61 | 42.94 | 27.84 | 21.96 |
| A12BR_M5 | stylegan | 96.47 | 90.98 | 84.41 | 70.69 |
| A12BR_M5 | webmorph | 46.37 | 4.31 | 0.29 | 0.10 |
| A12BR_M6 | amsl | 99.80 | 98.04 | 96.67 | 94.12 |
| A12BR_M6 | facemorpher | 99.90 | 95.78 | 92.75 | 86.96 |
| A12BR_M6 | opencv | 100.00 | 98.33 | 96.67 | 94.71 |
| A12BR_M6 | stylegan | 95.39 | 81.67 | 72.16 | 54.80 |
| A12BR_M6 | webmorph | 99.90 | 96.37 | 93.82 | 88.63 |
| A12BR_M8 | amsl | 93.82 | 84.31 | 77.75 | 67.45 |
| A12BR_M8 | facemorpher | 95.78 | 91.86 | 88.73 | 83.92 |
| A12BR_M8 | opencv | 91.96 | 82.84 | 78.92 | 72.94 |
| A12BR_M8 | stylegan | 72.94 | 53.53 | 41.57 | 27.84 |
| A12BR_M8 | webmorph | 96.86 | 84.51 | 75.39 | 65.49 |
| A12BR_M8O | amsl | 98.73 | 96.67 | 93.53 | 87.65 |
| A12BR_M8O | facemorpher | 99.71 | 99.31 | 98.92 | 98.24 |
| A12BR_M8O | opencv | 99.51 | 98.33 | 97.16 | 94.61 |
| A12BR_M8O | stylegan | 85.78 | 72.84 | 63.63 | 49.80 |
| A12BR_M8O | webmorph | 99.61 | 95.00 | 90.78 | 85.69 |
| A12BR_M4 | amsl | 100.00 | 100.00 | 100.00 | 100.00 |
| A12BR_M4 | facemorpher | 100.00 | 100.00 | 99.88 | 99.63 |
| A12BR_M4 | opencv | 78.80 | 67.52 | 59.56 | 50.49 |
| A12BR_M4 | stylegan | 97.67 | 86.89 | 78.31 | 67.52 |
| A12BR_M4 | webmorph | 100.00 | 100.00 | 100.00 | 100.00 |
| A45_incepofc | amsl | 90.98 | 73.63 | 59.90 | 44.51 |
| A45_incepofc | facemorpher | 99.12 | 96.86 | 95.29 | 92.16 |
| A45_incepofc | opencv | 95.00 | 90.59 | 85.69 | 81.57 |
| A45_incepofc | stylegan | 83.53 | 73.14 | 64.12 | 48.04 |
| A45_incepofc | webmorph | 95.78 | 57.16 | 43.73 | 27.45 |
| A45_hrnetw18 | amsl | 99.41 | 97.16 | 94.51 | 88.73 |
| A45_hrnetw18 | facemorpher | 99.61 | 98.53 | 97.16 | 96.18 |
| A45_hrnetw18 | opencv | 98.24 | 96.27 | 94.90 | 91.27 |
| A45_hrnetw18 | stylegan | 95.39 | 90.78 | 84.31 | 72.65 |
| A45_hrnetw18 | webmorph | 99.80 | 95.88 | 91.96 | 82.94 |
| FDMAD_g256 | amsl | 100.00 | 100.00 | 100.00 | 100.00 |
| FDMAD_g256 | facemorpher | 100.00 | 100.00 | 100.00 | 100.00 |
| FDMAD_g256 | opencv | 100.00 | 99.35 | 97.55 | 96.41 |
| FDMAD_g256 | stylegan | 97.22 | 88.89 | 79.74 | 68.79 |
| FDMAD_g256 | webmorph | 100.00 | 100.00 | 100.00 | 100.00 |
| FDMAD_g512 | amsl | 0.00 | 0.00 | 0.00 | 0.00 |
| FDMAD_g512 | facemorpher | 0.98 | 0.33 | 0.00 | 0.00 |
| FDMAD_g512 | opencv | 45.92 | 27.12 | 20.59 | 12.91 |
| FDMAD_g512 | stylegan | 100.00 | 100.00 | 99.18 | 95.42 |
| FDMAD_g512 | webmorph | 0.00 | 0.00 | 0.00 | 0.00 |
| FDMAD_f256 | amsl | 100.00 | 100.00 | 100.00 | 100.00 |
| FDMAD_f256 | facemorpher | 100.00 | 100.00 | 100.00 | 100.00 |
| FDMAD_f256 | opencv | 100.00 | 99.35 | 97.55 | 96.41 |
| FDMAD_f256 | stylegan | 97.22 | 88.89 | 79.74 | 68.79 |
| FDMAD_f256 | webmorph | 100.00 | 100.00 | 100.00 | 100.00 |
| FDMAD_f512 | amsl | 5.23 | 0.00 | 0.00 | 0.00 |
| FDMAD_f512 | facemorpher | 40.36 | 27.12 | 18.63 | 13.73 |
| FDMAD_f512 | opencv | 87.25 | 75.16 | 67.97 | 60.13 |
| FDMAD_f512 | stylegan | 51.31 | 41.99 | 36.93 | 27.78 |
| FDMAD_f512 | webmorph | 8.66 | 0.00 | 0.00 | 0.00 |

### Networks excluded by the scorer gate C1

- A12BR_M5 es: C1_EXCLUDED: C1 missing or failed for ['A12BR_M5_s1_es', 'A12BR_M5_s2_es', 'A12BR_M5_s6_es']
- A12BR_M4 es: C1_EXCLUDED: C1 missing or failed for ['A12BR_M4_s3_es']
- A12BR_M5 last: C1_EXCLUDED: C1 missing or failed for ['A12BR_M5_s1_last', 'A12BR_M5_s3_last', 'A12BR_M5_s4_last', 'A12BR_M5_s5_last', 'A12BR_M5_s6_last', 'A12BR_M5_s7_last']
- A12BR_M5 last: WITHHELD: no reading: fewer than 3 networks pass C1
- A12BR_M8O last: C1_EXCLUDED: C1 missing or failed for ['A12BR_M8O_s3_last']
