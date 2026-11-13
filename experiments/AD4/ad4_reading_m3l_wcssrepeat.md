# Morph-free networks (AD4), CLIP ViT-L/14 with LoRA (M3L): reading, our frames

Status: **final**. All numbers on our frames (our alignment of every benchmark). EER in %, signed AUC (morph positive). 95% intervals: person bootstrap (Amendment 2 (a)), descriptive; the verdicts use point values.

Networks (arm, seed, platform and card):
- morph-free seed 401 (`AD4_m3lmf_s401`): WCSS H100 (cross-platform repeat, not registered), NVIDIA H100; sample-order gate pass (200/200)
- morph-free seed 402 (`AD4_m3lmf_s402`): WCSS H100 (cross-platform repeat, not registered), NVIDIA H100; sample-order gate pass (200/200)
- morph-free seed 403 (`AD4_m3lmf_s403`): WCSS H100 (cross-platform repeat, not registered), NVIDIA H100; sample-order gate pass (200/200)
- morph-free seed 404 (`AD4_m3lmf_s404`): WCSS H100 (cross-platform repeat, not registered), NVIDIA H100; sample-order gate pass (200/200)
- morph-free seed 405 (`AD4_m3lmf_s405`): WCSS H100 (cross-platform repeat, not registered), NVIDIA H100; sample-order gate pass (200/200)
- label-permuted seed 401 (`AD4_m3lperm_s401`): WCSS H100 (cross-platform repeat, not registered), NVIDIA H100; sample-order gate pass (200/200)
- label-permuted seed 402 (`AD4_m3lperm_s402`): WCSS H100 (cross-platform repeat, not registered), NVIDIA H100; sample-order gate pass (200/200)
- label-permuted seed 403 (`AD4_m3lperm_s403`): WCSS H100 (cross-platform repeat, not registered), NVIDIA H100; sample-order gate pass (200/200)
- label-permuted seed 404 (`AD4_m3lperm_s404`): WCSS H100 (cross-platform repeat, not registered), NVIDIA H100; sample-order gate pass (200/200)
- label-permuted seed 405 (`AD4_m3lperm_s405`): WCSS H100 (cross-platform repeat, not registered), NVIDIA H100; sample-order gate pass (200/200)
- untrained seed 401 (`AD4_m3lzero_s401`): DGX, NVIDIA GB10
- morph-trained twin seed 1 (`A12BR_m3l_R_d0_s1`): WCSS H100 (A12BR)
- morph-trained twin seed 2 (`A12BR_m3l_R_d0_s2`): WCSS H100 (A12BR)
- morph-trained twin seed 3 (`A12BR_m3l_R_d0_s3`): WCSS H100 (A12BR)
- morph-trained twin seed 4 (`A12BR_m3l_R_d0_s4`): WCSS H100 (A12BR)
- morph-trained twin seed 5 (`A12BR_m3l_R_d0_s5`): WCSS H100 (A12BR)

## Table 1. EER per cell (%), our frames, CLIP ViT-L/14 with LoRA (M3L)

| cell | role | morph-free: mean [95% CI] (per seed) | label-permuted: mean (range) | untrained | lowest reference | margin = morph-free mean minus lowest reference [95% CI] | passable without morphs | seeds meeting margin | seeds above 15% | A1 | morph-trained twin: mean (range) | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MorDIFF native | primary | 0.0 [0.0, 0.0] (0.0, 0.0, 0.0, 0.0, 0.0) | 46.0 (40.7 to 52.0), n=5 | 50.0 | 40.7 | -40.7 [-43.6, -35.7] | yes | 5/5 | 0/5 | not falsified | 48.7 (34.8 to 56.9) |  |
| MorDIFF E7 (history-matched) | descriptive | 4.2 [2.5, 5.7] (2.0, 9.8, 5.5, 2.8, 1.0) | 47.5 (45.1 to 50.5), n=5 | 42.2 | 42.2 | -38.0 [-41.8, -33.1] | yes | 5/5 | 0/5 | - | 53.7 (41.7 to 60.3) |  |
| DiM-A native | secondary | 3.2 [2.4, 4.3] (0.0, 0.4, 11.8, 2.4, 1.4) | 45.3 (20.6 to 65.2), n=5 | 39.3 | 20.6 | -17.4 [-22.9, -12.6] | yes | 4/5 | 0/5 | not falsified | 10.2 (7.8 to 12.8) |  |
| DiM-A E7 (history-matched) | descriptive | 83.6 [80.5, 86.7] (80.0, 86.8, 91.2, 68.6, 91.6) | 46.1 (22.0 to 64.8), n=5 | 37.2 | 22.0 | 61.6 [56.1, 67.1] | no | 0/5 | 5/5 | - | 7.1 (4.4 to 10.2) |  |
| DiM-C native | secondary | 1.5 [0.9, 2.2] (0.0, 0.4, 6.4, 0.4, 0.1) | 43.1 (21.5 to 64.8), n=5 | 41.2 | 21.5 | -20.0 [-25.5, -15.2] | yes | 5/5 | 0/5 | not falsified | 22.4 (16.2 to 28.4) |  |
| DiM-C E7 (history-matched) | descriptive | 60.2 [55.2, 65.2] (48.0, 68.2, 80.3, 39.7, 64.8) | 43.6 (23.5 to 64.8), n=5 | 40.2 | 23.5 | 36.7 [30.4, 43.9] | no | 0/5 | 5/5 | - | 17.6 (10.2 to 23.6) |  |
| Fast-DiM native | secondary | 8.5 [6.7, 10.3] (0.4, 4.0, 24.6, 6.8, 6.9) | 44.6 (23.0 to 64.8), n=5 | 42.1 | 23.0 | -14.5 [-19.4, -8.6] | yes | 4/5 | 1/5 | not falsified | 29.7 (24.1 to 38.8) |  |
| Fast-DiM E7 (history-matched) | descriptive | 86.3 [83.2, 89.3] (79.4, 87.2, 95.1, 74.6, 95.0) | 45.1 (24.6 to 64.7), n=5 | 40.6 | 24.6 | 61.7 [56.3, 68.7] | no | 0/5 | 5/5 | - | 25.1 (15.6 to 32.4) |  |
| Fast-DiM-ODE native | secondary | 11.5 [9.3, 14.0] (0.4, 4.4, 18.6, 17.6, 16.2) | 42.7 (18.2 to 59.4), n=5 | 32.4 | 18.2 | -6.7 [-12.6, -1.9] | no | 2/5 | 3/5 | falsified | 13.7 (9.3 to 22.6) | does not reach 15%; the morph-trained recipe reaches 13.7% |
| Fast-DiM-ODE E7 (history-matched) | descriptive | 92.8 [90.4, 95.0] (87.9, 92.7, 97.0, 88.8, 97.6) | 42.6 (19.1 to 58.3), n=5 | 31.4 | 19.1 | 73.7 [68.1, 78.3] | no | 0/5 | 5/5 | - | 8.4 (5.9 to 11.2) |  |
| Greedy-DiM native | secondary | 9.2 [7.3, 11.2] (0.0, 0.4, 15.6, 11.2, 18.7) | 42.2 (25.0 to 57.4), n=5 | 59.8 | 25.0 | -15.8 [-20.4, -8.5] | yes | 3/5 | 2/5 | not falsified | 18.4 (8.9 to 32.4) |  |
| Greedy-DiM E7 (history-matched) | descriptive | 91.0 [87.7, 93.6] (91.2, 84.3, 95.6, 86.8, 97.0) | 42.5 (23.9 to 56.8), n=5 | 57.9 | 23.9 | 67.1 [59.6, 75.0] | no | 0/5 | 5/5 | - | 13.0 (7.7 to 20.6) |  |
| Greedy-DiM-S native | secondary | 4.2 [3.1, 5.6] (0.0, 0.4, 13.2, 5.4, 2.0) | 41.2 (17.6 to 63.8), n=5 | 33.4 | 17.6 | -13.4 [-18.2, -8.0] | yes | 4/5 | 0/5 | not falsified | 27.0 (21.0 to 37.7) |  |
| Greedy-DiM-S E7 (history-matched) | descriptive | 77.0 [73.0, 81.0] (65.7, 74.6, 86.8, 67.6, 90.2) | 41.3 (17.6 to 62.2), n=5 | 31.4 | 17.6 | 59.4 [52.3, 65.9] | no | 0/5 | 5/5 | - | 23.0 (14.7 to 30.8) |  |
| FRLL AMSL native | descriptive | 3.1 [2.2, 4.0] (0.0, 5.8, 4.0, 0.9, 4.9) | 44.5 (29.5 to 54.4), n=5 | 37.7 | 29.5 | -26.4 [-33.4, -20.7] | yes | 5/5 | 0/5 | - | 1.1 (0.5 to 2.0) | at least 10 points below every label-free reference (range 29.5 to 54.4%); not 'above chance' |
| FRLL AMSL E7 (history-matched) | descriptive | 16.0 [13.3, 18.8] (8.8, 19.1, 14.2, 1.5, 36.3) | 44.7 (31.4 to 55.4), n=5 | 35.9 | 31.4 | -15.4 [-21.7, -8.0] | yes | 4/5 | 2/5 | - | 0.3 (0.0 to 0.5) |  |
| FRLL FaceMorpher native | descriptive | 20.3 [17.8, 22.7] (6.3, 32.8, 27.9, 10.4, 24.0) | 40.2 (22.6 to 48.7), n=5 | 22.1 | 22.1 | -1.8 [-5.2, 3.8] | no | 2/5 | 3/5 | - | 0.1 (0.0 to 0.4) | a miss on a landmark cell does not show that the cell needs morphs |
| FRLL FaceMorpher E7 (history-matched) | descriptive | 34.2 [30.9, 37.2] (14.2, 53.4, 41.1, 13.1, 49.1) | 40.3 (23.1 to 48.5), n=5 | 22.1 | 22.1 | 12.1 [8.0, 17.9] | no | 0/5 | 3/5 | - | 0.0 (0.0 to 0.1) |  |
| FRLL OpenCV native | descriptive | 33.2 [30.1, 36.5] (19.1, 39.3, 36.4, 42.1, 28.9) | 38.2 (19.7 to 53.9), n=5 | 27.4 | 19.7 | 13.4 [7.7, 19.3] | no | 0/5 | 5/5 | - | 0.5 (0.4 to 0.5) | a miss on a landmark cell does not show that the cell needs morphs |
| FRLL OpenCV E7 (history-matched) | descriptive | 53.2 [49.2, 56.7] (38.2, 59.8, 54.8, 55.4, 57.8) | 38.0 (19.7 to 52.4), n=5 | 27.0 | 19.7 | 33.5 [26.2, 38.9] | no | 0/5 | 5/5 | - | 0.3 (0.0 to 0.5) |  |
| FRLL StyleGAN native | descriptive | 76.2 [73.8, 79.1] (56.9, 83.8, 80.4, 74.5, 85.2) | 40.4 (17.7 to 65.2), n=5 | 40.7 | 17.7 | 58.5 [53.9, 64.5] | no | 0/5 | 5/5 | - | 37.4 (31.8 to 40.7) |  |
| FRLL StyleGAN E7 (history-matched) | descriptive | 76.2 [73.8, 79.1] (56.9, 83.8, 80.4, 74.5, 85.2) | 40.4 (17.7 to 65.2), n=5 | 40.7 | 17.7 | 58.5 [53.9, 64.5] | no | 0/5 | 5/5 | - | 37.4 (31.8 to 40.7) | E7 not applicable |
| FRLL Webmorph native | descriptive | 1.6 [0.9, 2.1] (0.0, 3.8, 2.4, 0.0, 1.5) | 44.0 (26.5 to 55.4), n=5 | 35.3 | 26.5 | -24.9 [-30.9, -20.1] | yes | 5/5 | 0/5 | - | 0.1 (0.0 to 0.5) | at least 10 points below every label-free reference (range 26.5 to 55.4%); not 'above chance' |
| FRLL Webmorph E7 (history-matched) | descriptive | 11.7 [8.9, 14.3] (7.4, 16.2, 10.8, 0.1, 24.0) | 44.0 (27.9 to 54.9), n=5 | 33.8 | 27.9 | -16.2 [-22.9, -10.0] | yes | 4/5 | 2/5 | - | 0.1 (0.0 to 0.4) |  |
| corrected MAD22 FaceMorpher native | descriptive | 0.0 [0.0, 0.0] (0.0, 0.0, 0.0, 0.0, 0.0) | 43.1 (18.1 to 55.4), n=5 | 25.0 | 18.1 | -18.1 [-22.6, -13.6] | yes | 5/5 | 0/5 | - | no twin | at least 10 points below every label-free reference (range 18.1 to 55.4%); not 'above chance'; no twin |
| corrected MAD22 FaceMorpher E7 (history-matched) | descriptive | 37.6 [33.6, 41.6] (44.6, 54.9, 45.5, 2.0, 41.2) | 43.0 (18.5 to 53.9), n=5 | 22.5 | 18.5 | 19.1 [13.0, 24.8] | no | 1/5 | 4/5 | - | no twin | no twin |
| corrected MAD22 MIPGAN-I native | descriptive | 87.3 [83.0, 90.4] (72.1, 88.3, 94.1, 90.7, 91.1) | 44.5 (19.1 to 83.3), n=5 | 54.9 | 19.1 | 68.2 [61.4, 73.8] | no | 0/5 | 5/5 | - | no twin | no twin |
| corrected MAD22 MIPGAN-I E7 (history-matched) | descriptive | 87.3 [83.0, 90.4] (72.1, 88.3, 94.1, 90.7, 91.1) | 44.5 (19.1 to 83.3), n=5 | 54.9 | 19.1 | 68.2 [61.4, 73.8] | no | 0/5 | 5/5 | - | no twin | E7 not applicable; no twin |
| corrected MAD22 MIPGAN-II native | descriptive | 92.6 [90.5, 94.7] (79.9, 96.1, 97.9, 92.3, 97.1) | 42.7 (19.6 to 76.5), n=5 | 44.1 | 19.6 | 73.0 [67.9, 78.4] | no | 0/5 | 5/5 | - | no twin | no twin |
| corrected MAD22 MIPGAN-II E7 (history-matched) | descriptive | 92.6 [90.5, 94.7] (79.9, 96.1, 97.9, 92.3, 97.1) | 42.7 (19.6 to 76.5), n=5 | 44.1 | 19.6 | 73.0 [67.9, 78.4] | no | 0/5 | 5/5 | - | no twin | E7 not applicable; no twin |
| corrected MAD22 OpenCV native | descriptive | 45.6 [42.4, 48.8] (39.8, 47.1, 48.1, 53.4, 39.7) | 39.3 (23.1 to 63.1), n=5 | 38.7 | 23.1 | 22.5 [17.6, 27.8] | no | 0/5 | 5/5 | - | no twin | a miss on a landmark cell does not show that the cell needs morphs; no twin |
| corrected MAD22 OpenCV E7 (history-matched) | descriptive | 48.6 [45.4, 51.8] (42.8, 48.1, 51.0, 56.8, 44.6) | 39.4 (23.6 to 62.7), n=5 | 38.2 | 23.6 | 25.1 [20.4, 30.7] | no | 0/5 | 5/5 | - | no twin | E7 partial (108/204 identical); no twin |
| corrected MAD22 Webmorph native | descriptive | 36.4 [33.6, 39.7] (33.4, 41.6, 38.2, 29.4, 39.2) | 37.3 (22.6 to 50.1), n=5 | 33.8 | 22.6 | 13.8 [9.2, 19.5] | no | 0/5 | 5/5 | - | no twin | a miss on a landmark cell does not show that the cell needs morphs; no twin |
| corrected MAD22 Webmorph E7 (history-matched) | descriptive | 40.2 [36.9, 43.7] (36.8, 45.0, 43.2, 32.4, 43.7) | 37.5 (23.0 to 50.1), n=5 | 33.8 | 23.0 | 17.2 [12.4, 23.1] | no | 0/5 | 5/5 | - | no twin | E7 partial (104/204 identical); no twin |

## Table 2. Signed AUC per cell, our frames, CLIP ViT-L/14 with LoRA (M3L)

| cell | morph-free: mean [95% CI] (per seed) | label-permuted: mean (range) | untrained | folded reference AUC, max | morph-trained twin: mean |
|---|---|---|---|---|---|
| MorDIFF native | 1.000 [1.000, 1.000] (1.000, 1.000, 1.000, 1.000, 1.000) | 0.553 (0.438 to 0.631) | 0.523 | 0.631 | 0.550 |
| MorDIFF E7 (history-matched) | 0.991 [0.985, 0.996] (0.998, 0.971, 0.989, 0.998, 1.000) | 0.528 (0.451 to 0.570) | 0.607 | 0.607 | 0.469 |
| DiM-A native | 0.990 [0.986, 0.994] (1.000, 1.000, 0.955, 0.997, 0.998) | 0.547 (0.265 to 0.874) | 0.668 | 0.874 | 0.962 |
| DiM-A E7 (history-matched) | 0.095 [0.070, 0.123] (0.122, 0.063, 0.020, 0.236, 0.031) | 0.544 (0.274 to 0.863) | 0.693 | 0.863 | 0.981 |
| DiM-C native | 0.997 [0.995, 0.999] (1.000, 1.000, 0.987, 1.000, 1.000) | 0.578 (0.267 to 0.859) | 0.628 | 0.859 | 0.883 |
| DiM-C E7 (history-matched) | 0.358 [0.301, 0.418] (0.513, 0.242, 0.118, 0.624, 0.291) | 0.576 (0.277 to 0.845) | 0.653 | 0.845 | 0.916 |
| Fast-DiM native | 0.963 [0.953, 0.973] (1.000, 0.995, 0.852, 0.986, 0.984) | 0.554 (0.261 to 0.848) | 0.619 | 0.848 | 0.806 |
| Fast-DiM E7 (history-matched) | 0.071 [0.051, 0.094] (0.122, 0.058, 0.007, 0.157, 0.013) | 0.551 (0.269 to 0.835) | 0.643 | 0.835 | 0.846 |
| Fast-DiM-ODE native | 0.943 [0.925, 0.958] (1.000, 0.993, 0.889, 0.915, 0.915) | 0.581 (0.333 to 0.888) | 0.743 | 0.888 | 0.937 |
| Fast-DiM-ODE E7 (history-matched) | 0.025 [0.014, 0.041] (0.052, 0.020, 0.005, 0.047, 0.003) | 0.580 (0.345 to 0.879) | 0.766 | 0.879 | 0.973 |
| Greedy-DiM native | 0.958 [0.943, 0.971] (1.000, 1.000, 0.925, 0.962, 0.903) | 0.590 (0.358 to 0.821) | 0.358 | 0.821 | 0.880 |
| Greedy-DiM E7 (history-matched) | 0.036 [0.019, 0.059] (0.026, 0.082, 0.011, 0.055, 0.005) | 0.586 (0.371 to 0.831) | 0.373 | 0.831 | 0.932 |
| Greedy-DiM-S native | 0.987 [0.981, 0.992] (1.000, 1.000, 0.947, 0.991, 0.997) | 0.604 (0.285 to 0.912) | 0.732 | 0.912 | 0.852 |
| Greedy-DiM-S E7 (history-matched) | 0.161 [0.123, 0.203] (0.268, 0.181, 0.053, 0.265, 0.037) | 0.602 (0.296 to 0.902) | 0.755 | 0.902 | 0.877 |
| FRLL AMSL native | 0.995 [0.992, 0.997] (1.000, 0.991, 0.994, 1.000, 0.989) | 0.565 (0.416 to 0.759) | 0.680 | 0.759 | 1.000 |
| FRLL AMSL E7 (history-matched) | 0.894 [0.868, 0.918] (0.955, 0.880, 0.934, 0.999, 0.701) | 0.566 (0.403 to 0.750) | 0.692 | 0.750 | 1.000 |
| FRLL FaceMorpher native | 0.866 [0.843, 0.889] (0.987, 0.730, 0.800, 0.965, 0.851) | 0.625 (0.509 to 0.845) | 0.854 | 0.854 | 1.000 |
| FRLL FaceMorpher E7 (history-matched) | 0.702 [0.665, 0.738] (0.929, 0.486, 0.613, 0.948, 0.532) | 0.627 (0.520 to 0.839) | 0.860 | 0.860 | 1.000 |
| FRLL OpenCV native | 0.734 [0.697, 0.769] (0.897, 0.644, 0.708, 0.626, 0.794) | 0.651 (0.450 to 0.869) | 0.808 | 0.869 | 1.000 |
| FRLL OpenCV E7 (history-matched) | 0.471 [0.422, 0.521] (0.677, 0.368, 0.470, 0.446, 0.395) | 0.651 (0.460 to 0.863) | 0.814 | 0.863 | 1.000 |
| FRLL StyleGAN native | 0.162 [0.136, 0.189] (0.388, 0.074, 0.109, 0.167, 0.070) | 0.618 (0.273 to 0.903) | 0.643 | 0.903 | 0.681 |
| FRLL StyleGAN E7 (history-matched) | 0.162 [0.136, 0.189] (0.388, 0.074, 0.109, 0.167, 0.070) | 0.618 (0.273 to 0.903) | 0.643 | 0.903 | 0.681 |
| FRLL Webmorph native | 0.998 [0.997, 0.999] (1.000, 0.996, 0.998, 1.000, 0.998) | 0.577 (0.412 to 0.798) | 0.707 | 0.798 | 1.000 |
| FRLL Webmorph E7 (history-matched) | 0.944 [0.923, 0.962] (0.978, 0.918, 0.962, 1.000, 0.861) | 0.577 (0.423 to 0.788) | 0.718 | 0.788 | 1.000 |
| corrected MAD22 FaceMorpher native | 1.000 [1.000, 1.000] (1.000, 1.000, 1.000, 1.000, 1.000) | 0.583 (0.422 to 0.901) | 0.843 | 0.901 | no twin |
| corrected MAD22 FaceMorpher E7 (history-matched) | 0.659 [0.608, 0.707] (0.615, 0.456, 0.568, 0.999, 0.657) | 0.581 (0.437 to 0.890) | 0.865 | 0.890 | no twin |
| corrected MAD22 MIPGAN-I native | 0.061 [0.041, 0.087] (0.185, 0.045, 0.009, 0.030, 0.034) | 0.572 (0.091 to 0.880) | 0.424 | 0.909 | no twin |
| corrected MAD22 MIPGAN-I E7 (history-matched) | 0.061 [0.041, 0.087] (0.185, 0.045, 0.009, 0.030, 0.034) | 0.572 (0.091 to 0.880) | 0.424 | 0.909 | no twin |
| corrected MAD22 MIPGAN-II native | 0.026 [0.017, 0.038] (0.098, 0.009, 0.002, 0.016, 0.006) | 0.592 (0.166 to 0.880) | 0.576 | 0.880 | no twin |
| corrected MAD22 MIPGAN-II E7 (history-matched) | 0.026 [0.017, 0.038] (0.098, 0.009, 0.002, 0.016, 0.006) | 0.592 (0.166 to 0.880) | 0.576 | 0.880 | no twin |
| corrected MAD22 OpenCV native | 0.580 [0.542, 0.617] (0.677, 0.559, 0.560, 0.444, 0.662) | 0.637 (0.308 to 0.838) | 0.676 | 0.838 | no twin |
| corrected MAD22 OpenCV E7 (history-matched) | 0.540 [0.498, 0.579] (0.638, 0.522, 0.530, 0.412, 0.598) | 0.636 (0.309 to 0.836) | 0.677 | 0.836 | no twin |
| corrected MAD22 Webmorph native | 0.683 [0.650, 0.715] (0.722, 0.614, 0.660, 0.755, 0.662) | 0.665 (0.484 to 0.849) | 0.727 | 0.849 | no twin |
| corrected MAD22 Webmorph E7 (history-matched) | 0.639 [0.601, 0.677] (0.678, 0.570, 0.624, 0.735, 0.590) | 0.665 (0.487 to 0.847) | 0.729 | 0.847 | no twin |

## Table 3a. Fixed threshold "0.5 rule": flag rate (genuine photos flagged) and miss rate (morphs not flagged), %, our frames, CLIP ViT-L/14 with LoRA (M3L)

Threshold pool: none (score at least 0.5). Arm means; per-seed miss rates in brackets.

| cell | morph-free flag / miss (per-seed miss) | label-permuted flag / miss | untrained flag / miss | morph-trained twin flag / miss |
|---|---|---|---|---|
| MorDIFF native | 0.0 / 63.0 (12.3, 98.8, 100.0, 95.7, 8.4) | 53.0 / 39.2 | 86.3 / 4.6 | 0.0 / 99.7 |
| MorDIFF E7 (history-matched) | 0.0 / 63.0 (12.3, 98.8, 100.0, 95.7, 8.4) | 56.0 / 39.2 | 78.9 / 4.6 | 0.0 / 99.7 |
| DiM-A native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.7 / 49.1 | 85.8 / 3.2 | 0.0 / 99.5 |
| DiM-A E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 46.0 / 49.1 | 84.3 / 3.2 | 0.0 / 99.5 |
| DiM-C native | 0.0 / 100.0 (99.8, 100.0, 100.0, 100.0, 100.0) | 45.7 / 44.6 | 85.8 / 2.2 | 0.0 / 96.1 |
| DiM-C E7 (history-matched) | 0.0 / 100.0 (99.8, 100.0, 100.0, 100.0, 100.0) | 46.4 / 44.6 | 83.3 / 2.2 | 0.0 / 96.1 |
| Fast-DiM native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.7 / 47.3 | 85.8 / 6.0 | 0.0 / 99.9 |
| Fast-DiM E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 46.0 / 47.3 | 84.3 / 6.0 | 0.0 / 99.9 |
| Fast-DiM-ODE native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.7 / 42.6 | 85.8 / 2.4 | 0.0 / 98.3 |
| Fast-DiM-ODE E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 46.2 / 42.6 | 83.3 / 2.4 | 0.0 / 98.3 |
| Greedy-DiM native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.7 / 38.8 | 85.8 / 23.6 | 0.0 / 100.0 |
| Greedy-DiM E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 46.6 / 38.8 | 84.3 / 23.6 | 0.0 / 100.0 |
| Greedy-DiM-S native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.7 / 40.3 | 85.8 / 1.4 | 0.0 / 78.8 |
| Greedy-DiM-S E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 46.7 / 40.3 | 84.3 / 1.4 | 0.0 / 78.8 |
| FRLL AMSL native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.7 / 44.7 | 85.8 / 2.8 | 0.0 / 100.0 |
| FRLL AMSL E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.5 / 44.7 | 83.8 / 2.8 | 0.0 / 100.0 |
| FRLL FaceMorpher native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.7 / 34.6 | 85.8 / 0.0 | 0.0 / 5.5 |
| FRLL FaceMorpher E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.2 / 34.6 | 84.3 / 0.0 | 0.0 / 5.5 |
| FRLL OpenCV native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.7 / 29.6 | 85.8 / 0.2 | 0.0 / 3.3 |
| FRLL OpenCV E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.5 / 29.6 | 82.8 / 0.2 | 0.0 / 3.3 |
| FRLL StyleGAN native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.7 / 38.7 | 85.8 / 1.9 | 0.0 / 99.9 |
| FRLL StyleGAN E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.7 / 38.7 | 85.8 / 1.9 | 0.0 / 99.9 |
| FRLL Webmorph native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.7 / 44.1 | 85.8 / 2.3 | 0.0 / 67.6 |
| FRLL Webmorph E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.2 / 44.1 | 83.8 / 2.3 | 0.0 / 67.6 |
| corrected MAD22 FaceMorpher native | 0.0 / 98.1 (95.4, 99.9, 100.0, 99.7, 95.6) | 45.7 / 42.0 | 85.8 / 0.3 | no twin |
| corrected MAD22 FaceMorpher E7 (history-matched) | 0.0 / 98.1 (95.4, 99.9, 100.0, 99.7, 95.6) | 46.2 / 42.0 | 83.8 / 0.3 | no twin |
| corrected MAD22 MIPGAN-I native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.7 / 44.2 | 85.8 / 15.8 | no twin |
| corrected MAD22 MIPGAN-I E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.7 / 44.2 | 85.8 / 15.8 | no twin |
| corrected MAD22 MIPGAN-II native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.7 / 40.3 | 85.8 / 4.9 | no twin |
| corrected MAD22 MIPGAN-II E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.7 / 40.3 | 85.8 / 4.9 | no twin |
| corrected MAD22 OpenCV native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.7 / 35.4 | 85.8 / 2.9 | no twin |
| corrected MAD22 OpenCV E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.5 / 35.4 | 85.8 / 2.9 | no twin |
| corrected MAD22 Webmorph native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.7 / 29.5 | 85.8 / 1.4 | no twin |
| corrected MAD22 Webmorph E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 45.5 / 29.5 | 86.8 / 1.4 | no twin |

## Table 3b. Fixed threshold "FRLL-5%": flag rate (genuine photos flagged) and miss rate (morphs not flagged), %, our frames, CLIP ViT-L/14 with LoRA (M3L)

Threshold pool: 204 unprocessed FRLL genuine photos, at most 10 flagged. Arm means; per-seed miss rates in brackets.

| cell | morph-free flag / miss (per-seed miss) | label-permuted flag / miss | untrained flag / miss | morph-trained twin flag / miss |
|---|---|---|---|---|
| MorDIFF native | 20.5 / 0.0 (0.0, 0.0, 0.0, 0.0, 0.0) | 9.6 / 90.5 | 3.4 / 99.0 | 71.6 / 21.1 |
| MorDIFF E7 (history-matched) | 100.0 / 0.0 (0.0, 0.0, 0.0, 0.0, 0.0) | 10.9 / 90.5 | 0.5 / 99.0 | 84.6 / 21.1 |
| DiM-A native | 4.9 / 7.4 (0.0, 0.2, 34.8, 1.6, 0.2) | 4.9 / 85.8 | 4.9 / 88.6 | 4.9 / 21.5 |
| DiM-A E7 (history-matched) | 100.0 / 7.4 (0.0, 0.2, 34.8, 1.6, 0.2) | 5.0 / 85.8 | 2.0 / 88.6 | 2.4 / 21.5 |
| DiM-C native | 4.9 / 2.0 (0.0, 0.0, 9.6, 0.2, 0.0) | 4.9 / 86.7 | 4.9 / 92.6 | 4.9 / 48.2 |
| DiM-C E7 (history-matched) | 100.0 / 2.0 (0.0, 0.0, 9.6, 0.2, 0.0) | 4.8 / 86.7 | 2.5 / 92.6 | 2.4 / 48.2 |
| Fast-DiM native | 4.9 / 17.4 (0.0, 3.2, 65.8, 8.6, 9.6) | 4.9 / 86.8 | 4.9 / 94.0 | 4.9 / 69.0 |
| Fast-DiM E7 (history-matched) | 100.0 / 17.4 (0.0, 3.2, 65.8, 8.6, 9.6) | 5.1 / 86.8 | 2.0 / 94.0 | 2.3 / 69.0 |
| Fast-DiM-ODE native | 4.9 / 29.4 (0.0, 4.4, 67.3, 44.3, 31.1) | 4.9 / 85.9 | 4.9 / 82.6 | 4.9 / 37.5 |
| Fast-DiM-ODE E7 (history-matched) | 100.0 / 29.4 (0.0, 4.4, 67.3, 44.3, 31.1) | 4.8 / 85.9 | 2.0 / 82.6 | 2.3 / 37.5 |
| Greedy-DiM native | 4.9 / 22.4 (0.0, 0.0, 53.8, 24.8, 33.2) | 4.9 / 85.9 | 4.9 / 99.6 | 4.9 / 60.6 |
| Greedy-DiM E7 (history-matched) | 100.0 / 22.4 (0.0, 0.0, 53.8, 24.8, 33.2) | 4.8 / 85.9 | 2.5 / 99.6 | 2.5 / 60.6 |
| Greedy-DiM-S native | 4.9 / 7.3 (0.0, 0.0, 29.2, 6.2, 1.0) | 4.9 / 83.8 | 4.9 / 82.8 | 4.9 / 50.2 |
| Greedy-DiM-S E7 (history-matched) | 100.0 / 7.3 (0.0, 0.0, 29.2, 6.2, 1.0) | 5.0 / 83.8 | 2.5 / 82.8 | 2.5 / 50.2 |
| FRLL AMSL native | 4.9 / 2.9 (0.0, 6.0, 3.6, 0.0, 4.7) | 4.9 / 93.1 | 4.9 / 93.2 | 4.9 / 0.1 |
| FRLL AMSL E7 (history-matched) | 40.6 / 2.9 (0.0, 6.0, 3.6, 0.0, 4.7) | 5.2 / 93.1 | 3.9 / 93.2 | 2.9 / 0.1 |
| FRLL FaceMorpher native | 4.9 / 55.1 (6.6, 90.5, 89.0, 24.9, 64.6) | 4.9 / 91.1 | 4.9 / 73.2 | 4.9 / 0.0 |
| FRLL FaceMorpher E7 (history-matched) | 17.9 / 55.1 (6.6, 90.5, 89.0, 24.9, 64.6) | 5.4 / 91.1 | 3.9 / 73.2 | 3.6 / 0.0 |
| FRLL OpenCV native | 4.9 / 82.4 (60.4, 89.7, 88.9, 99.8, 73.4) | 4.9 / 89.1 | 4.9 / 80.1 | 4.9 / 0.2 |
| FRLL OpenCV E7 (history-matched) | 22.0 / 82.4 (60.4, 89.7, 88.9, 99.8, 73.4) | 5.2 / 89.1 | 3.4 / 80.1 | 3.6 / 0.2 |
| FRLL StyleGAN native | 4.9 / 99.9 (99.5, 100.0, 100.0, 100.0, 100.0) | 4.9 / 86.7 | 4.9 / 95.6 | 4.9 / 94.7 |
| FRLL StyleGAN E7 (history-matched) | 4.9 / 99.9 (99.5, 100.0, 100.0, 100.0, 100.0) | 4.9 / 86.7 | 4.9 / 95.6 | 4.9 / 94.7 |
| FRLL Webmorph native | 4.9 / 0.6 (0.0, 2.0, 0.7, 0.0, 0.4) | 4.9 / 91.9 | 4.9 / 89.5 | 4.9 / 0.0 |
| FRLL Webmorph E7 (history-matched) | 41.1 / 0.6 (0.0, 2.0, 0.7, 0.0, 0.4) | 5.1 / 91.9 | 2.9 / 89.5 | 3.3 / 0.0 |
| corrected MAD22 FaceMorpher native | 5.2 / 0.0 (0.0, 0.0, 0.0, 0.0, 0.0) | 5.0 / 87.2 | 4.4 / 70.0 | no twin |
| corrected MAD22 FaceMorpher E7 (history-matched) | 100.0 / 0.0 (0.0, 0.0, 0.0, 0.0, 0.0) | 4.7 / 87.2 | 2.5 / 70.0 | no twin |
| corrected MAD22 MIPGAN-I native | 5.2 / 99.8 (99.2, 100.0, 100.0, 100.0, 99.9) | 5.0 / 90.6 | 4.4 / 99.6 | no twin |
| corrected MAD22 MIPGAN-I E7 (history-matched) | 5.2 / 99.8 (99.2, 100.0, 100.0, 100.0, 99.9) | 5.0 / 90.6 | 4.4 / 99.6 | no twin |
| corrected MAD22 MIPGAN-II native | 5.2 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 5.0 / 91.4 | 4.4 / 96.6 | no twin |
| corrected MAD22 MIPGAN-II E7 (history-matched) | 5.2 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 5.0 / 91.4 | 4.4 / 96.6 | no twin |
| corrected MAD22 OpenCV native | 5.2 / 91.5 (88.0, 91.9, 92.4, 100.0, 85.4) | 5.0 / 83.7 | 4.4 / 89.4 | no twin |
| corrected MAD22 OpenCV E7 (history-matched) | 6.5 / 91.5 (88.0, 91.9, 92.4, 100.0, 85.4) | 5.3 / 83.7 | 4.9 / 89.4 | no twin |
| corrected MAD22 Webmorph native | 5.2 / 95.3 (96.8, 97.6, 97.6, 94.8, 89.8) | 5.0 / 84.5 | 4.4 / 85.2 | no twin |
| corrected MAD22 Webmorph E7 (history-matched) | 6.8 / 95.3 (96.8, 97.6, 97.6, 94.8, 89.8) | 5.3 / 84.5 | 4.4 / 85.2 | no twin |

## Table 4. Training accuracy (threshold 0.5, no TTA), CLIP ViT-L/14 with LoRA (M3L)

| network | arm | own training labels: accuracy / AUC | true labels: accuracy / AUC | share of labels permuted | train hours |
|---|---|---|---|---|---|
| `AD4_m3lmf_s401` | morph-free | 1.0 / 1.0 | 1.0 / 1.0 | 0.0 | 1.9442100709676742 |
| `AD4_m3lmf_s402` | morph-free | 1.0 / 1.0 | 1.0 / 1.0 | 0.0 | 1.93708522995313 |
| `AD4_m3lmf_s403` | morph-free | 1.0 / 1.0 | 1.0 / 1.0 | 0.0 | 1.937295011613104 |
| `AD4_m3lmf_s404` | morph-free | 1.0 / 1.0 | 1.0 / 1.0 | 0.0 | 1.9427971332603031 |
| `AD4_m3lmf_s405` | morph-free | 1.0 / 1.0 | 1.0 / 1.0 | 0.0 | 1.9379563901821772 |
| `AD4_m3lperm_s401` | label-permuted | 0.5164 / 0.5256 | 0.6824 / 0.7415 | 0.4986 | 1.9460736260811489 |
| `AD4_m3lperm_s402` | label-permuted | 0.5192 / 0.5275 | 0.5507 / 0.5784 | 0.4988 | 1.9416250224908194 |
| `AD4_m3lperm_s403` | label-permuted | 0.5185 / 0.5263 | 0.4713 / 0.4707 | 0.4984 | 1.9385096278455523 |
| `AD4_m3lperm_s404` | label-permuted | 0.5142 / 0.524 | 0.6798 / 0.7347 | 0.4978 | 1.9371222535769144 |
| `AD4_m3lperm_s405` | label-permuted | 0.5175 / 0.5243 | 0.3575 / 0.3071 | 0.5016 | 1.9358602574798796 |
| `AD4_m3lzero_s401` | untrained | 0.4923 / 0.4351 | 0.4923 / 0.4351 | 0.0 | None |
