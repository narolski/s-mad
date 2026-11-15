# Morph-free networks (AD4), CLIP ViT-L/14 with LoRA (M3L): reading, our frames

Status: **final**. All numbers on our frames (our alignment of every benchmark). EER in %, signed AUC (morph positive). 95% intervals: person bootstrap (Amendment 2 (a)), descriptive; the verdicts use point values.

Networks (arm, seed, platform and card):
- morph-free seed 401 (`AD4_m3lmf_s401`): registered (Athena A100 / WCSS H100, Amendment 5), NVIDIA A100-SXM4-40GB; sample-order gate pass (200/200)
- morph-free seed 402 (`AD4_m3lmf_s402`): registered (Athena A100 / WCSS H100, Amendment 5), NVIDIA A100-SXM4-40GB; sample-order gate pass (200/200)
- morph-free seed 403 (`AD4_m3lmf_s403`): registered (Athena A100 / WCSS H100, Amendment 5), NVIDIA H100; sample-order gate pass (200/200)
- morph-free seed 404 (`AD4_m3lmf_s404`): registered (Athena A100 / WCSS H100, Amendment 5), NVIDIA H100; sample-order gate pass (200/200)
- morph-free seed 405 (`AD4_m3lmf_s405`): registered (Athena A100 / WCSS H100, Amendment 5), NVIDIA H100; sample-order gate pass (200/200)
- label-permuted seed 401 (`AD4_m3lperm_s401`): registered (Athena A100 / WCSS H100, Amendment 5), NVIDIA A100-SXM4-40GB; sample-order gate pass (200/200)
- label-permuted seed 402 (`AD4_m3lperm_s402`): registered (Athena A100 / WCSS H100, Amendment 5), NVIDIA A100-SXM4-40GB; sample-order gate pass (200/200)
- label-permuted seed 403 (`AD4_m3lperm_s403`): registered (Athena A100 / WCSS H100, Amendment 5), NVIDIA A100-SXM4-40GB; sample-order gate pass (200/200)
- label-permuted seed 404 (`AD4_m3lperm_s404`): registered (Athena A100 / WCSS H100, Amendment 5), NVIDIA A100-SXM4-40GB; sample-order gate pass (200/200)
- label-permuted seed 405 (`AD4_m3lperm_s405`): registered (Athena A100 / WCSS H100, Amendment 5), NVIDIA A100-SXM4-40GB; sample-order gate pass (200/200)
- untrained seed 401 (`AD4_m3lzero_s401`): DGX, NVIDIA GB10
- morph-trained twin seed 1 (`A12BR_m3l_R_d0_s1`): WCSS H100 (A12BR)
- morph-trained twin seed 2 (`A12BR_m3l_R_d0_s2`): WCSS H100 (A12BR)
- morph-trained twin seed 3 (`A12BR_m3l_R_d0_s3`): WCSS H100 (A12BR)
- morph-trained twin seed 4 (`A12BR_m3l_R_d0_s4`): WCSS H100 (A12BR)
- morph-trained twin seed 5 (`A12BR_m3l_R_d0_s5`): WCSS H100 (A12BR)

## Table 1. EER per cell (%), our frames, CLIP ViT-L/14 with LoRA (M3L)

| cell | role | morph-free: mean [95% CI] (per seed) | label-permuted: mean (range) | untrained | lowest reference | margin = morph-free mean minus lowest reference [95% CI] | passable without morphs | seeds meeting margin | seeds above 15% | A1 | morph-trained twin: mean (range) | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MorDIFF native | primary | 0.0 [0.0, 0.0] (0.0, 0.0, 0.0, 0.0, 0.0) | 46.1 (41.2 to 52.0), n=5 | 50.0 | 41.2 | -41.2 [-43.7, -35.8] | yes | 5/5 | 0/5 | not falsified | 48.7 (34.8 to 56.9) |  |
| MorDIFF E7 (history-matched) | descriptive | 4.0 [2.4, 5.5] (2.0, 8.9, 5.5, 2.8, 1.0) | 47.5 (45.1 to 50.6), n=5 | 42.2 | 42.2 | -38.1 [-42.0, -33.2] | yes | 5/5 | 0/5 | - | 53.7 (41.7 to 60.3) |  |
| DiM-A native | secondary | 3.6 [2.6, 4.7] (0.0, 2.4, 11.8, 2.4, 1.4) | 45.3 (20.6 to 65.2), n=5 | 39.3 | 20.6 | -17.0 [-22.5, -12.1] | yes | 4/5 | 0/5 | not falsified | 10.2 (7.8 to 12.8) |  |
| DiM-A E7 (history-matched) | descriptive | 83.7 [80.6, 86.7] (80.3, 86.8, 91.2, 68.6, 91.6) | 46.3 (22.5 to 65.2), n=5 | 37.2 | 22.5 | 61.2 [56.2, 67.1] | no | 0/5 | 5/5 | - | 7.1 (4.4 to 10.2) |  |
| DiM-C native | secondary | 1.6 [0.9, 2.5] (0.0, 1.1, 6.4, 0.4, 0.1) | 43.2 (21.6 to 65.2), n=5 | 41.2 | 21.6 | -20.0 [-25.1, -15.0] | yes | 5/5 | 0/5 | not falsified | 22.4 (16.2 to 28.4) |  |
| DiM-C E7 (history-matched) | descriptive | 60.2 [55.2, 65.3] (47.5, 68.6, 80.3, 39.7, 64.8) | 43.7 (23.1 to 65.2), n=5 | 40.2 | 23.1 | 37.0 [30.4, 44.0] | no | 0/5 | 5/5 | - | 17.6 (10.2 to 23.6) |  |
| Fast-DiM native | secondary | 9.1 [7.1, 11.0] (0.1, 6.9, 24.6, 6.8, 6.9) | 44.5 (22.6 to 64.8), n=5 | 42.1 | 22.6 | -13.5 [-18.9, -8.1] | yes | 4/5 | 1/5 | not falsified | 29.7 (24.1 to 38.8) |  |
| Fast-DiM E7 (history-matched) | descriptive | 86.5 [83.5, 89.4] (79.4, 88.3, 95.1, 74.6, 95.0) | 45.1 (24.6 to 64.8), n=5 | 40.6 | 24.6 | 61.9 [56.6, 68.8] | no | 0/5 | 5/5 | - | 25.1 (15.6 to 32.4) |  |
| Fast-DiM-ODE native | secondary | 11.8 [9.5, 14.3] (0.4, 5.9, 18.6, 17.6, 16.2) | 42.7 (18.2 to 59.8), n=5 | 32.4 | 18.2 | -6.4 [-12.3, -1.5] | no | 2/5 | 3/5 | falsified | 13.7 (9.3 to 22.6) | does not reach 15%; the morph-trained recipe reaches 13.7% |
| Fast-DiM-ODE E7 (history-matched) | descriptive | 92.7 [90.2, 94.9] (87.3, 92.6, 97.0, 88.8, 97.6) | 42.6 (19.1 to 58.3), n=5 | 31.4 | 19.1 | 73.6 [68.0, 78.2] | no | 0/5 | 5/5 | - | 8.4 (5.9 to 11.2) |  |
| Greedy-DiM native | secondary | 9.5 [7.5, 11.5] (0.0, 2.0, 15.6, 11.2, 18.7) | 42.3 (24.9 to 57.8), n=5 | 59.8 | 24.9 | -15.4 [-20.2, -8.1] | yes | 3/5 | 2/5 | not falsified | 18.4 (8.9 to 32.4) |  |
| Greedy-DiM E7 (history-matched) | descriptive | 91.2 [87.9, 93.8] (91.2, 85.2, 95.6, 86.8, 97.0) | 42.7 (24.0 to 56.9), n=5 | 57.9 | 24.0 | 67.2 [59.8, 75.3] | no | 0/5 | 5/5 | - | 13.0 (7.7 to 20.6) |  |
| Greedy-DiM-S native | secondary | 4.4 [3.2, 5.8] (0.0, 1.4, 13.2, 5.4, 2.0) | 41.5 (17.6 to 63.8), n=5 | 33.4 | 17.6 | -13.2 [-18.1, -7.8] | yes | 4/5 | 0/5 | not falsified | 27.0 (21.0 to 37.7) |  |
| Greedy-DiM-S E7 (history-matched) | descriptive | 76.7 [72.8, 80.9] (65.6, 73.5, 86.8, 67.6, 90.2) | 41.1 (17.6 to 62.2), n=5 | 31.4 | 17.6 | 59.1 [52.1, 65.6] | no | 0/5 | 5/5 | - | 23.0 (14.7 to 30.8) |  |
| FRLL AMSL native | descriptive | 3.4 [2.4, 4.4] (0.0, 7.3, 4.0, 0.9, 4.9) | 44.7 (29.5 to 54.9), n=5 | 37.7 | 29.5 | -26.1 [-33.0, -20.3] | yes | 5/5 | 0/5 | - | 1.1 (0.5 to 2.0) | at least 10 points below every label-free reference (range 29.5 to 54.9%); not 'above chance' |
| FRLL AMSL E7 (history-matched) | descriptive | 15.6 [13.0, 18.2] (8.3, 17.6, 14.2, 1.5, 36.3) | 44.6 (31.4 to 55.0), n=5 | 35.9 | 31.4 | -15.8 [-22.1, -8.5] | yes | 4/5 | 2/5 | - | 0.3 (0.0 to 0.5) |  |
| FRLL FaceMorpher native | descriptive | 20.6 [18.2, 23.1] (5.0, 35.8, 27.9, 10.4, 24.0) | 40.2 (22.6 to 48.5), n=5 | 22.1 | 22.1 | -1.5 [-4.8, 4.2] | no | 2/5 | 3/5 | - | 0.1 (0.0 to 0.4) | a miss on a landmark cell does not show that the cell needs morphs |
| FRLL FaceMorpher E7 (history-matched) | descriptive | 33.4 [30.3, 36.5] (13.6, 50.0, 41.1, 13.1, 49.1) | 40.5 (23.5 to 49.0), n=5 | 22.1 | 22.1 | 11.3 [7.3, 17.2] | no | 0/5 | 3/5 | - | 0.0 (0.0 to 0.1) |  |
| FRLL OpenCV native | descriptive | 34.3 [31.3, 37.6] (18.6, 45.6, 36.4, 42.1, 28.9) | 38.3 (19.7 to 54.4), n=5 | 27.4 | 19.7 | 14.6 [8.8, 20.5] | no | 0/5 | 5/5 | - | 0.5 (0.4 to 0.5) | a miss on a landmark cell does not show that the cell needs morphs |
| FRLL OpenCV E7 (history-matched) | descriptive | 53.6 [49.8, 57.3] (37.3, 62.7, 54.8, 55.4, 57.8) | 38.0 (19.7 to 52.4), n=5 | 27.0 | 19.7 | 33.9 [27.0, 39.3] | no | 0/5 | 5/5 | - | 0.3 (0.0 to 0.5) |  |
| FRLL StyleGAN native | descriptive | 76.6 [74.2, 79.4] (57.3, 85.8, 80.4, 74.5, 85.2) | 40.5 (17.7 to 65.2), n=5 | 40.7 | 17.7 | 59.0 [54.2, 64.8] | no | 0/5 | 5/5 | - | 37.4 (31.8 to 40.7) |  |
| FRLL StyleGAN E7 (history-matched) | descriptive | 76.6 [74.2, 79.4] (57.3, 85.8, 80.4, 74.5, 85.2) | 40.5 (17.7 to 65.2), n=5 | 40.7 | 17.7 | 59.0 [54.2, 64.8] | no | 0/5 | 5/5 | - | 37.4 (31.8 to 40.7) | E7 not applicable |
| FRLL Webmorph native | descriptive | 1.6 [1.0, 2.3] (0.0, 4.0, 2.4, 0.0, 1.5) | 44.0 (26.5 to 55.8), n=5 | 35.3 | 26.5 | -24.9 [-30.7, -20.0] | yes | 5/5 | 0/5 | - | 0.1 (0.0 to 0.5) | at least 10 points below every label-free reference (range 26.5 to 55.8%); not 'above chance' |
| FRLL Webmorph E7 (history-matched) | descriptive | 11.1 [8.5, 13.7] (6.5, 14.2, 10.8, 0.1, 24.0) | 44.1 (27.9 to 54.9), n=5 | 33.8 | 27.9 | -16.8 [-23.3, -10.5] | yes | 4/5 | 1/5 | - | 0.1 (0.0 to 0.4) |  |
| corrected MAD22 FaceMorpher native | descriptive | 0.0 [0.0, 0.0] (0.0, 0.0, 0.0, 0.0, 0.0) | 43.2 (18.1 to 55.4), n=5 | 25.0 | 18.1 | -18.1 [-22.6, -13.5] | yes | 5/5 | 0/5 | - | no twin | at least 10 points below every label-free reference (range 18.1 to 55.4%); not 'above chance'; no twin |
| corrected MAD22 FaceMorpher E7 (history-matched) | descriptive | 37.7 [33.7, 41.7] (44.6, 55.4, 45.5, 2.0, 41.2) | 43.0 (18.2 to 53.9), n=5 | 22.5 | 18.2 | 19.5 [13.2, 24.8] | no | 1/5 | 4/5 | - | no twin | no twin |
| corrected MAD22 MIPGAN-I native | descriptive | 87.2 [83.2, 90.5] (72.0, 88.2, 94.1, 90.7, 91.1) | 44.6 (19.1 to 83.3), n=5 | 54.9 | 19.1 | 68.1 [61.4, 73.8] | no | 0/5 | 5/5 | - | no twin | no twin |
| corrected MAD22 MIPGAN-I E7 (history-matched) | descriptive | 87.2 [83.2, 90.5] (72.0, 88.2, 94.1, 90.7, 91.1) | 44.6 (19.1 to 83.3), n=5 | 54.9 | 19.1 | 68.1 [61.4, 73.8] | no | 0/5 | 5/5 | - | no twin | E7 not applicable; no twin |
| corrected MAD22 MIPGAN-II native | descriptive | 92.8 [90.7, 94.8] (80.4, 96.2, 97.9, 92.3, 97.1) | 42.6 (19.6 to 76.5), n=5 | 44.1 | 19.6 | 73.2 [68.0, 78.5] | no | 0/5 | 5/5 | - | no twin | no twin |
| corrected MAD22 MIPGAN-II E7 (history-matched) | descriptive | 92.8 [90.7, 94.8] (80.4, 96.2, 97.9, 92.3, 97.1) | 42.6 (19.6 to 76.5), n=5 | 44.1 | 19.6 | 73.2 [68.0, 78.5] | no | 0/5 | 5/5 | - | no twin | E7 not applicable; no twin |
| corrected MAD22 OpenCV native | descriptive | 46.6 [43.6, 49.7] (40.2, 51.5, 48.1, 53.4, 39.7) | 39.2 (22.6 to 63.2), n=5 | 38.7 | 22.6 | 24.0 [18.9, 28.8] | no | 0/5 | 5/5 | - | no twin | a miss on a landmark cell does not show that the cell needs morphs; no twin |
| corrected MAD22 OpenCV E7 (history-matched) | descriptive | 49.8 [46.6, 52.9] (42.7, 53.9, 51.0, 56.8, 44.6) | 39.3 (23.1 to 62.7), n=5 | 38.2 | 23.1 | 26.7 [21.7, 31.8] | no | 0/5 | 5/5 | - | no twin | E7 partial (108/204 identical); no twin |
| corrected MAD22 Webmorph native | descriptive | 36.5 [33.6, 39.8] (33.4, 42.1, 38.2, 29.4, 39.2) | 37.5 (22.6 to 50.4), n=5 | 33.8 | 22.6 | 13.9 [9.4, 19.7] | no | 0/5 | 5/5 | - | no twin | a miss on a landmark cell does not show that the cell needs morphs; no twin |
| corrected MAD22 Webmorph E7 (history-matched) | descriptive | 39.9 [36.8, 43.5] (36.2, 44.2, 43.2, 32.4, 43.7) | 37.4 (22.6 to 50.4), n=5 | 33.8 | 22.6 | 17.4 [12.3, 23.1] | no | 0/5 | 5/5 | - | no twin | E7 partial (104/204 identical); no twin |

## Table 2. Signed AUC per cell, our frames, CLIP ViT-L/14 with LoRA (M3L)

| cell | morph-free: mean [95% CI] (per seed) | label-permuted: mean (range) | untrained | folded reference AUC, max | morph-trained twin: mean |
|---|---|---|---|---|---|
| MorDIFF native | 1.000 [1.000, 1.000] (1.000, 1.000, 1.000, 1.000, 1.000) | 0.552 (0.439 to 0.630) | 0.523 | 0.630 | 0.550 |
| MorDIFF E7 (history-matched) | 0.992 [0.986, 0.996] (0.998, 0.973, 0.989, 0.998, 1.000) | 0.528 (0.451 to 0.569) | 0.607 | 0.607 | 0.469 |
| DiM-A native | 0.990 [0.985, 0.994] (1.000, 0.998, 0.955, 0.997, 0.998) | 0.547 (0.262 to 0.875) | 0.668 | 0.875 | 0.962 |
| DiM-A E7 (history-matched) | 0.095 [0.070, 0.124] (0.124, 0.063, 0.020, 0.236, 0.031) | 0.544 (0.271 to 0.863) | 0.693 | 0.863 | 0.981 |
| DiM-C native | 0.997 [0.995, 0.999] (1.000, 0.999, 0.987, 1.000, 1.000) | 0.578 (0.264 to 0.859) | 0.628 | 0.859 | 0.883 |
| DiM-C E7 (history-matched) | 0.356 [0.300, 0.417] (0.516, 0.233, 0.118, 0.624, 0.291) | 0.576 (0.273 to 0.846) | 0.653 | 0.846 | 0.916 |
| Fast-DiM native | 0.962 [0.951, 0.972] (1.000, 0.985, 0.852, 0.986, 0.984) | 0.553 (0.258 to 0.848) | 0.619 | 0.848 | 0.806 |
| Fast-DiM E7 (history-matched) | 0.070 [0.050, 0.092] (0.122, 0.050, 0.007, 0.157, 0.013) | 0.551 (0.265 to 0.836) | 0.643 | 0.836 | 0.846 |
| Fast-DiM-ODE native | 0.941 [0.923, 0.957] (1.000, 0.987, 0.889, 0.915, 0.915) | 0.581 (0.330 to 0.888) | 0.743 | 0.888 | 0.937 |
| Fast-DiM-ODE E7 (history-matched) | 0.026 [0.014, 0.042] (0.053, 0.023, 0.005, 0.047, 0.003) | 0.579 (0.342 to 0.879) | 0.766 | 0.879 | 0.973 |
| Greedy-DiM native | 0.958 [0.943, 0.971] (1.000, 0.999, 0.925, 0.962, 0.903) | 0.590 (0.355 to 0.822) | 0.358 | 0.822 | 0.880 |
| Greedy-DiM E7 (history-matched) | 0.034 [0.018, 0.058] (0.029, 0.073, 0.011, 0.055, 0.005) | 0.585 (0.367 to 0.832) | 0.373 | 0.832 | 0.932 |
| Greedy-DiM-S native | 0.987 [0.981, 0.992] (1.000, 0.999, 0.947, 0.991, 0.997) | 0.604 (0.283 to 0.912) | 0.732 | 0.912 | 0.852 |
| Greedy-DiM-S E7 (history-matched) | 0.164 [0.126, 0.206] (0.273, 0.192, 0.053, 0.265, 0.037) | 0.601 (0.294 to 0.903) | 0.755 | 0.903 | 0.877 |
| FRLL AMSL native | 0.994 [0.991, 0.996] (1.000, 0.986, 0.994, 1.000, 0.989) | 0.565 (0.417 to 0.760) | 0.680 | 0.760 | 1.000 |
| FRLL AMSL E7 (history-matched) | 0.899 [0.874, 0.922] (0.959, 0.901, 0.934, 0.999, 0.701) | 0.566 (0.404 to 0.751) | 0.692 | 0.751 | 1.000 |
| FRLL FaceMorpher native | 0.858 [0.836, 0.880] (0.988, 0.688, 0.800, 0.965, 0.851) | 0.625 (0.505 to 0.846) | 0.854 | 0.854 | 1.000 |
| FRLL FaceMorpher E7 (history-matched) | 0.702 [0.667, 0.737] (0.936, 0.482, 0.613, 0.948, 0.532) | 0.626 (0.515 to 0.839) | 0.860 | 0.860 | 1.000 |
| FRLL OpenCV native | 0.719 [0.684, 0.754] (0.897, 0.571, 0.708, 0.626, 0.794) | 0.651 (0.446 to 0.869) | 0.808 | 0.869 | 1.000 |
| FRLL OpenCV E7 (history-matched) | 0.462 [0.414, 0.510] (0.680, 0.318, 0.470, 0.446, 0.395) | 0.651 (0.455 to 0.863) | 0.814 | 0.863 | 1.000 |
| FRLL StyleGAN native | 0.158 [0.133, 0.184] (0.386, 0.056, 0.109, 0.167, 0.070) | 0.617 (0.269 to 0.903) | 0.643 | 0.903 | 0.681 |
| FRLL StyleGAN E7 (history-matched) | 0.158 [0.133, 0.184] (0.386, 0.056, 0.109, 0.167, 0.070) | 0.617 (0.269 to 0.903) | 0.643 | 0.903 | 0.681 |
| FRLL Webmorph native | 0.998 [0.996, 0.999] (1.000, 0.994, 0.998, 1.000, 0.998) | 0.576 (0.408 to 0.798) | 0.707 | 0.798 | 1.000 |
| FRLL Webmorph E7 (history-matched) | 0.948 [0.927, 0.965] (0.981, 0.934, 0.962, 1.000, 0.861) | 0.576 (0.419 to 0.788) | 0.718 | 0.788 | 1.000 |
| corrected MAD22 FaceMorpher native | 1.000 [1.000, 1.000] (1.000, 1.000, 1.000, 1.000, 1.000) | 0.582 (0.420 to 0.901) | 0.843 | 0.901 | no twin |
| corrected MAD22 FaceMorpher E7 (history-matched) | 0.657 [0.607, 0.705] (0.623, 0.440, 0.568, 0.999, 0.657) | 0.581 (0.436 to 0.891) | 0.865 | 0.891 | no twin |
| corrected MAD22 MIPGAN-I native | 0.060 [0.041, 0.086] (0.185, 0.042, 0.009, 0.030, 0.034) | 0.572 (0.089 to 0.881) | 0.424 | 0.911 | no twin |
| corrected MAD22 MIPGAN-I E7 (history-matched) | 0.060 [0.041, 0.086] (0.185, 0.042, 0.009, 0.030, 0.034) | 0.572 (0.089 to 0.881) | 0.424 | 0.911 | no twin |
| corrected MAD22 MIPGAN-II native | 0.026 [0.017, 0.037] (0.097, 0.008, 0.002, 0.016, 0.006) | 0.591 (0.163 to 0.880) | 0.576 | 0.880 | no twin |
| corrected MAD22 MIPGAN-II E7 (history-matched) | 0.026 [0.017, 0.037] (0.097, 0.008, 0.002, 0.016, 0.006) | 0.591 (0.163 to 0.880) | 0.576 | 0.880 | no twin |
| corrected MAD22 OpenCV native | 0.566 [0.529, 0.603] (0.674, 0.492, 0.560, 0.444, 0.662) | 0.637 (0.305 to 0.838) | 0.676 | 0.838 | no twin |
| corrected MAD22 OpenCV E7 (history-matched) | 0.527 [0.486, 0.565] (0.636, 0.457, 0.530, 0.412, 0.598) | 0.636 (0.306 to 0.836) | 0.677 | 0.836 | no twin |
| corrected MAD22 Webmorph native | 0.682 [0.650, 0.713] (0.724, 0.607, 0.660, 0.755, 0.662) | 0.665 (0.480 to 0.849) | 0.727 | 0.849 | no twin |
| corrected MAD22 Webmorph E7 (history-matched) | 0.640 [0.603, 0.677] (0.683, 0.570, 0.624, 0.735, 0.590) | 0.665 (0.482 to 0.847) | 0.729 | 0.847 | no twin |

## Table 3a. Fixed threshold "0.5 rule": flag rate (genuine photos flagged) and miss rate (morphs not flagged), %, our frames, CLIP ViT-L/14 with LoRA (M3L)

Threshold pool: none (score at least 0.5). Arm means; per-seed miss rates in brackets.

| cell | morph-free flag / miss (per-seed miss) | label-permuted flag / miss | untrained flag / miss | morph-trained twin flag / miss |
|---|---|---|---|---|
| MorDIFF native | 0.0 / 63.1 (12.7, 98.9, 100.0, 95.7, 8.4) | 53.0 / 39.3 | 86.3 / 4.6 | 0.0 / 99.7 |
| MorDIFF E7 (history-matched) | 0.1 / 63.1 (12.7, 98.9, 100.0, 95.7, 8.4) | 55.7 / 39.3 | 78.9 / 4.6 | 0.0 / 99.7 |
| DiM-A native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.6 / 49.2 | 85.8 / 3.2 | 0.0 / 99.5 |
| DiM-A E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 46.1 / 49.2 | 84.3 / 3.2 | 0.0 / 99.5 |
| DiM-C native | 0.0 / 100.0 (99.8, 100.0, 100.0, 100.0, 100.0) | 45.6 / 44.6 | 85.8 / 2.2 | 0.0 / 96.1 |
| DiM-C E7 (history-matched) | 0.0 / 100.0 (99.8, 100.0, 100.0, 100.0, 100.0) | 46.3 / 44.6 | 83.3 / 2.2 | 0.0 / 96.1 |
| Fast-DiM native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.6 / 47.4 | 85.8 / 6.0 | 0.0 / 99.9 |
| Fast-DiM E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 46.3 / 47.4 | 84.3 / 6.0 | 0.0 / 99.9 |
| Fast-DiM-ODE native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.6 / 42.7 | 85.8 / 2.4 | 0.0 / 98.3 |
| Fast-DiM-ODE E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 46.1 / 42.7 | 83.3 / 2.4 | 0.0 / 98.3 |
| Greedy-DiM native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.6 / 38.9 | 85.8 / 23.6 | 0.0 / 100.0 |
| Greedy-DiM E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 46.8 / 38.9 | 84.3 / 23.6 | 0.0 / 100.0 |
| Greedy-DiM-S native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.6 / 40.5 | 85.8 / 1.4 | 0.0 / 78.8 |
| Greedy-DiM-S E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 46.3 / 40.5 | 84.3 / 1.4 | 0.0 / 78.8 |
| FRLL AMSL native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.6 / 44.9 | 85.8 / 2.8 | 0.0 / 100.0 |
| FRLL AMSL E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.2 / 44.9 | 83.8 / 2.8 | 0.0 / 100.0 |
| FRLL FaceMorpher native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.6 / 34.7 | 85.8 / 0.0 | 0.0 / 5.5 |
| FRLL FaceMorpher E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.1 / 34.7 | 84.3 / 0.0 | 0.0 / 5.5 |
| FRLL OpenCV native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.6 / 29.7 | 85.8 / 0.2 | 0.0 / 3.3 |
| FRLL OpenCV E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.2 / 29.7 | 82.8 / 0.2 | 0.0 / 3.3 |
| FRLL StyleGAN native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.6 / 38.9 | 85.8 / 1.9 | 0.0 / 99.9 |
| FRLL StyleGAN E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.6 / 38.9 | 85.8 / 1.9 | 0.0 / 99.9 |
| FRLL Webmorph native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.6 / 44.2 | 85.8 / 2.3 | 0.0 / 67.6 |
| FRLL Webmorph E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.4 / 44.2 | 83.8 / 2.3 | 0.0 / 67.6 |
| corrected MAD22 FaceMorpher native | 0.0 / 98.1 (95.2, 100.0, 100.0, 99.7, 95.6) | 45.7 / 42.0 | 85.8 / 0.3 | no twin |
| corrected MAD22 FaceMorpher E7 (history-matched) | 0.0 / 98.1 (95.2, 100.0, 100.0, 99.7, 95.6) | 46.1 / 42.0 | 83.8 / 0.3 | no twin |
| corrected MAD22 MIPGAN-I native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.7 / 44.1 | 85.8 / 15.8 | no twin |
| corrected MAD22 MIPGAN-I E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.7 / 44.1 | 85.8 / 15.8 | no twin |
| corrected MAD22 MIPGAN-II native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.7 / 40.2 | 85.8 / 4.9 | no twin |
| corrected MAD22 MIPGAN-II E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.7 / 40.2 | 85.8 / 4.9 | no twin |
| corrected MAD22 OpenCV native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.7 / 35.4 | 85.8 / 2.9 | no twin |
| corrected MAD22 OpenCV E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.6 / 35.4 | 85.8 / 2.9 | no twin |
| corrected MAD22 Webmorph native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.7 / 29.6 | 85.8 / 1.4 | no twin |
| corrected MAD22 Webmorph E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.9 / 29.6 | 86.8 / 1.4 | no twin |

## Table 3b. Fixed threshold "FRLL-5%": flag rate (genuine photos flagged) and miss rate (morphs not flagged), %, our frames, CLIP ViT-L/14 with LoRA (M3L)

Threshold pool: 204 unprocessed FRLL genuine photos, at most 10 flagged. Arm means; per-seed miss rates in brackets.

| cell | morph-free flag / miss (per-seed miss) | label-permuted flag / miss | untrained flag / miss | morph-trained twin flag / miss |
|---|---|---|---|---|
| MorDIFF native | 21.0 / 0.0 (0.0, 0.0, 0.0, 0.0, 0.0) | 9.7 / 90.3 | 3.4 / 99.0 | 71.6 / 21.1 |
| MorDIFF E7 (history-matched) | 100.0 / 0.0 (0.0, 0.0, 0.0, 0.0, 0.0) | 10.9 / 90.3 | 0.5 / 99.0 | 84.6 / 21.1 |
| DiM-A native | 4.9 / 7.4 (0.0, 0.4, 34.8, 1.6, 0.2) | 4.9 / 85.7 | 4.9 / 88.6 | 4.9 / 21.5 |
| DiM-A E7 (history-matched) | 100.0 / 7.4 (0.0, 0.4, 34.8, 1.6, 0.2) | 5.0 / 85.7 | 2.0 / 88.6 | 2.4 / 21.5 |
| DiM-C native | 4.9 / 2.0 (0.0, 0.4, 9.6, 0.2, 0.0) | 4.9 / 86.6 | 4.9 / 92.6 | 4.9 / 48.2 |
| DiM-C E7 (history-matched) | 100.0 / 2.0 (0.0, 0.4, 9.6, 0.2, 0.0) | 5.0 / 86.6 | 2.5 / 92.6 | 2.4 / 48.2 |
| Fast-DiM native | 4.9 / 18.3 (0.0, 7.6, 65.8, 8.6, 9.6) | 4.9 / 86.9 | 4.9 / 94.0 | 4.9 / 69.0 |
| Fast-DiM E7 (history-matched) | 100.0 / 18.3 (0.0, 7.6, 65.8, 8.6, 9.6) | 5.0 / 86.9 | 2.0 / 94.0 | 2.3 / 69.0 |
| Fast-DiM-ODE native | 4.9 / 29.8 (0.0, 6.2, 67.3, 44.3, 31.1) | 4.9 / 85.7 | 4.9 / 82.6 | 4.9 / 37.5 |
| Fast-DiM-ODE E7 (history-matched) | 100.0 / 29.8 (0.0, 6.2, 67.3, 44.3, 31.1) | 4.8 / 85.7 | 2.0 / 82.6 | 2.3 / 37.5 |
| Greedy-DiM native | 4.9 / 22.5 (0.0, 0.8, 53.8, 24.8, 33.2) | 4.9 / 86.0 | 4.9 / 99.6 | 4.9 / 60.6 |
| Greedy-DiM E7 (history-matched) | 100.0 / 22.5 (0.0, 0.8, 53.8, 24.8, 33.2) | 4.8 / 86.0 | 2.5 / 99.6 | 2.5 / 60.6 |
| Greedy-DiM-S native | 4.9 / 7.4 (0.0, 0.4, 29.2, 6.2, 1.0) | 4.9 / 83.7 | 4.9 / 82.8 | 4.9 / 50.2 |
| Greedy-DiM-S E7 (history-matched) | 100.0 / 7.4 (0.0, 0.4, 29.2, 6.2, 1.0) | 4.8 / 83.7 | 2.5 / 82.8 | 2.5 / 50.2 |
| FRLL AMSL native | 4.9 / 3.3 (0.0, 8.3, 3.6, 0.0, 4.7) | 4.9 / 93.0 | 4.9 / 93.2 | 4.9 / 0.1 |
| FRLL AMSL E7 (history-matched) | 38.3 / 3.3 (0.0, 8.3, 3.6, 0.0, 4.7) | 5.2 / 93.0 | 3.9 / 93.2 | 2.9 / 0.1 |
| FRLL FaceMorpher native | 4.9 / 56.0 (5.1, 96.5, 89.0, 24.9, 64.6) | 4.9 / 90.9 | 4.9 / 73.2 | 4.9 / 0.0 |
| FRLL FaceMorpher E7 (history-matched) | 17.2 / 56.0 (5.1, 96.5, 89.0, 24.9, 64.6) | 5.2 / 90.9 | 3.9 / 73.2 | 3.6 / 0.0 |
| FRLL OpenCV native | 4.9 / 83.5 (58.9, 96.4, 88.9, 99.8, 73.4) | 4.9 / 88.9 | 4.9 / 80.1 | 4.9 / 0.2 |
| FRLL OpenCV E7 (history-matched) | 21.1 / 83.5 (58.9, 96.4, 88.9, 99.8, 73.4) | 5.4 / 88.9 | 3.4 / 80.1 | 3.6 / 0.2 |
| FRLL StyleGAN native | 4.9 / 99.9 (99.5, 100.0, 100.0, 100.0, 100.0) | 4.9 / 86.7 | 4.9 / 95.6 | 4.9 / 94.7 |
| FRLL StyleGAN E7 (history-matched) | 4.9 / 99.9 (99.5, 100.0, 100.0, 100.0, 100.0) | 4.9 / 86.7 | 4.9 / 95.6 | 4.9 / 94.7 |
| FRLL Webmorph native | 4.9 / 1.0 (0.0, 4.0, 0.7, 0.0, 0.4) | 4.9 / 91.8 | 4.9 / 89.5 | 4.9 / 0.0 |
| FRLL Webmorph E7 (history-matched) | 39.6 / 1.0 (0.0, 4.0, 0.7, 0.0, 0.4) | 5.2 / 91.8 | 2.9 / 89.5 | 3.3 / 0.0 |
| corrected MAD22 FaceMorpher native | 5.1 / 0.0 (0.0, 0.0, 0.0, 0.0, 0.0) | 5.0 / 87.1 | 4.4 / 70.0 | no twin |
| corrected MAD22 FaceMorpher E7 (history-matched) | 100.0 / 0.0 (0.0, 0.0, 0.0, 0.0, 0.0) | 4.7 / 87.1 | 2.5 / 70.0 | no twin |
| corrected MAD22 MIPGAN-I native | 5.1 / 99.8 (99.2, 100.0, 100.0, 100.0, 99.9) | 5.0 / 90.4 | 4.4 / 99.6 | no twin |
| corrected MAD22 MIPGAN-I E7 (history-matched) | 5.1 / 99.8 (99.2, 100.0, 100.0, 100.0, 99.9) | 5.0 / 90.4 | 4.4 / 99.6 | no twin |
| corrected MAD22 MIPGAN-II native | 5.1 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 5.0 / 91.3 | 4.4 / 96.6 | no twin |
| corrected MAD22 MIPGAN-II E7 (history-matched) | 5.1 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 5.0 / 91.3 | 4.4 / 96.6 | no twin |
| corrected MAD22 OpenCV native | 5.1 / 92.5 (88.1, 96.8, 92.4, 100.0, 85.4) | 5.0 / 83.4 | 4.4 / 89.4 | no twin |
| corrected MAD22 OpenCV E7 (history-matched) | 6.4 / 92.5 (88.1, 96.8, 92.4, 100.0, 85.4) | 5.3 / 83.4 | 4.9 / 89.4 | no twin |
| corrected MAD22 Webmorph native | 5.1 / 95.6 (96.4, 99.2, 97.6, 94.8, 89.8) | 5.0 / 84.4 | 4.4 / 85.2 | no twin |
| corrected MAD22 Webmorph E7 (history-matched) | 6.7 / 95.6 (96.4, 99.2, 97.6, 94.8, 89.8) | 5.4 / 84.4 | 4.4 / 85.2 | no twin |

## Table 4. Training accuracy (threshold 0.5, no TTA), CLIP ViT-L/14 with LoRA (M3L)

| network | arm | own training labels: accuracy / AUC | true labels: accuracy / AUC | share of labels permuted | train hours |
|---|---|---|---|---|---|
| `AD4_m3lmf_s401` | morph-free | 1.0 / 1.0 | 1.0 / 1.0 | 0.0 | 4.074969368245867 |
| `AD4_m3lmf_s402` | morph-free | 1.0 / 1.0 | 1.0 / 1.0 | 0.0 | 3.58144524315993 |
| `AD4_m3lmf_s403` | morph-free | 1.0 / 1.0 | 1.0 / 1.0 | 0.0 | 1.937295011613104 |
| `AD4_m3lmf_s404` | morph-free | 1.0 / 1.0 | 1.0 / 1.0 | 0.0 | 1.9427971332603031 |
| `AD4_m3lmf_s405` | morph-free | 1.0 / 1.0 | 1.0 / 1.0 | 0.0 | 1.9379563901821772 |
| `AD4_m3lperm_s401` | label-permuted | 0.5165 / 0.5255 | 0.6833 / 0.7421 | 0.4986 | 3.5329683905177647 |
| `AD4_m3lperm_s402` | label-permuted | 0.5187 / 0.5274 | 0.5503 / 0.578 | 0.4988 | 3.8718582776519987 |
| `AD4_m3lperm_s403` | label-permuted | 0.5178 / 0.5263 | 0.471 / 0.4711 | 0.4984 | 3.8754484607776005 |
| `AD4_m3lperm_s404` | label-permuted | 0.5144 / 0.5239 | 0.6797 / 0.7344 | 0.4978 | 3.5599983872969947 |
| `AD4_m3lperm_s405` | label-permuted | 0.5179 / 0.5243 | 0.3567 / 0.306 | 0.5016 | 3.531470794412825 |
| `AD4_m3lzero_s401` | untrained | 0.4923 / 0.4351 | 0.4923 / 0.4351 | 0.0 | None |
