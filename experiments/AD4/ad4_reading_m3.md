# Morph-free networks (AD4), CLIP ViT-B/16 with LoRA (M3): reading, our frames

Status: **final**. All numbers on our frames (our alignment of every benchmark). EER in %, signed AUC (morph positive). 95% intervals: person bootstrap (Amendment 2 (a)), descriptive; the verdicts use point values.

Reproduction gate: pass.

Networks (arm, seed, platform and card):
- morph-free seed 401 (`AD4_m3mf_s401`): WCSS H100 (cluster stack, Amendment 5), NVIDIA H100; sample-order gate pass (200/200)
- morph-free seed 402 (`AD4_m3mf_s402`): WCSS H100 (cluster stack, Amendment 5), NVIDIA H100; sample-order gate pass (200/200)
- morph-free seed 403 (`AD4_m3mf_s403`): WCSS H100 (cluster stack, Amendment 5), NVIDIA H100; sample-order gate pass (200/200)
- morph-free seed 404 (`AD4_m3mf_s404`): WCSS H100 (cluster stack, Amendment 5), NVIDIA H100; sample-order gate pass (200/200)
- morph-free seed 405 (`AD4_m3mf_s405`): WCSS H100 (cluster stack, Amendment 5), NVIDIA H100; sample-order gate pass (200/200)
- label-permuted seed 401 (`AD4_m3perm_s401`): WCSS H100 (cluster stack, Amendment 5), NVIDIA H100; sample-order gate pass (200/200)
- label-permuted seed 402 (`AD4_m3perm_s402`): WCSS H100 (cluster stack, Amendment 5), NVIDIA H100; sample-order gate pass (200/200)
- label-permuted seed 403 (`AD4_m3perm_s403`): WCSS H100 (cluster stack, Amendment 5), NVIDIA H100; sample-order gate pass (200/200)
- label-permuted seed 404 (`AD4_m3perm_s404`): WCSS H100 (cluster stack, Amendment 5), NVIDIA H100; sample-order gate pass (200/200)
- label-permuted seed 405 (`AD4_m3perm_s405`): WCSS H100 (cluster stack, Amendment 5), NVIDIA H100; sample-order gate pass (200/200)
- untrained seed 401 (`AD4_m3zero_s401`): DGX, NVIDIA GB10

## Table 1. EER per cell (%), our frames, CLIP ViT-B/16 with LoRA (M3)

| cell | role | morph-free: mean [95% CI] (per seed) | label-permuted: mean (range) | untrained | lowest reference | margin = morph-free mean minus lowest reference [95% CI] | passable without morphs | seeds meeting margin | seeds above 15% | A1 | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MorDIFF native | primary | 0.0 [0.0, 0.0] (0.0, 0.0, 0.0, 0.0, 0.0) | 47.0 (37.3 to 60.8), n=5 | 53.9 | 37.3 | -37.3 [-41.1, -32.2] | yes | 5/5 | 0/5 | not falsified |  |
| MorDIFF E7 (history-matched) | descriptive | 2.4 [1.5, 3.6] (0.9, 0.1, 5.5, 1.9, 3.5) | 48.4 (43.1 to 60.8), n=5 | 48.0 | 43.1 | -40.7 [-45.1, -33.0] | yes | 5/5 | 0/5 | - |  |
| DiM-A native | secondary | 1.0 [0.3, 1.5] (0.4, 3.4, 0.1, 0.0, 0.9) | 45.7 (39.7 to 56.4), n=5 | 50.0 | 39.7 | -38.7 [-42.5, -29.9] | yes | 5/5 | 0/5 | not falsified |  |
| DiM-A E7 (history-matched) | descriptive | 59.7 [55.5, 63.8] (47.0, 62.8, 52.4, 58.4, 78.0) | 46.2 (39.3 to 55.4), n=5 | 45.0 | 39.3 | 20.4 [13.7, 31.4] | no | 0/5 | 5/5 | - |  |
| DiM-C native | secondary | 0.0 [0.0, 0.0] (0.0, 0.0, 0.0, 0.0, 0.0) | 47.1 (37.8 to 61.3), n=5 | 48.0 | 37.8 | -37.8 [-43.6, -30.9] | yes | 5/5 | 0/5 | not falsified |  |
| DiM-C E7 (history-matched) | descriptive | 19.4 [15.8, 23.0] (17.6, 13.8, 17.1, 14.7, 33.8) | 47.7 (35.9 to 60.9), n=5 | 43.2 | 35.9 | -16.5 [-24.4, -9.5] | yes | 4/5 | 3/5 | - | below every label-free reference, not at the published level (above 15% in 3 of 5 seeds) |
| Fast-DiM native | secondary | 1.9 [0.8, 2.7] (1.9, 3.9, 0.4, 0.0, 3.4) | 47.6 (42.2 to 56.8), n=5 | 49.0 | 42.2 | -40.3 [-45.0, -33.5] | yes | 5/5 | 0/5 | not falsified |  |
| Fast-DiM E7 (history-matched) | descriptive | 56.4 [51.5, 61.5] (54.5, 47.6, 50.4, 52.0, 77.4) | 48.3 (40.3 to 56.4), n=5 | 44.2 | 40.3 | 16.1 [6.7, 25.0] | no | 0/5 | 5/5 | - |  |
| Fast-DiM-ODE native | secondary | 2.7 [1.4, 3.7] (2.0, 4.0, 2.0, 0.0, 5.5) | 46.0 (37.3 to 50.9), n=5 | 52.0 | 37.3 | -34.6 [-39.8, -27.3] | yes | 5/5 | 0/5 | not falsified |  |
| Fast-DiM-ODE E7 (history-matched) | descriptive | 71.6 [68.6, 74.9] (66.3, 54.5, 77.1, 67.7, 92.7) | 46.7 (37.2 to 51.5), n=5 | 46.1 | 37.2 | 34.5 [28.4, 43.0] | no | 0/5 | 5/5 | - |  |
| Greedy-DiM native | secondary | 0.2 [0.0, 0.6] (0.5, 0.0, 0.1, 0.0, 0.4) | 50.1 (42.7 to 63.8), n=5 | 55.8 | 42.7 | -42.5 [-45.7, -36.1] | yes | 5/5 | 0/5 | not falsified |  |
| Greedy-DiM E7 (history-matched) | descriptive | 43.1 [40.3, 45.9] (84.4, 3.0, 44.2, 10.9, 73.0) | 50.8 (42.7 to 62.2), n=5 | 50.0 | 42.7 | 0.4 [-3.9, 8.5] | no | 2/5 | 3/5 | - |  |
| Greedy-DiM-S native | secondary | 0.8 [0.2, 1.5] (2.0, 0.4, 0.0, 0.1, 1.4) | 48.4 (41.2 to 62.6), n=5 | 53.4 | 41.2 | -40.4 [-43.6, -33.7] | yes | 5/5 | 0/5 | not falsified |  |
| Greedy-DiM-S E7 (history-matched) | descriptive | 43.9 [39.2, 49.1] (53.0, 17.2, 41.6, 35.9, 72.0) | 48.9 (40.3 to 61.8), n=5 | 47.0 | 40.3 | 3.6 [-3.3, 13.0] | no | 1/5 | 5/5 | - |  |
| FRLL AMSL native | descriptive | 0.6 [0.2, 1.0] (0.5, 2.0, 0.4, 0.0, 0.0) | 49.8 (27.0 to 65.7), n=5 | 37.3 | 27.0 | -26.4 [-31.2, -22.4] | yes | 5/5 | 0/5 | - | at least 10 points below every label-free reference (range 27.0 to 65.7%); not 'above chance' |
| FRLL AMSL E7 (history-matched) | descriptive | 4.8 [3.4, 6.2] (9.3, 5.9, 4.4, 0.5, 3.9) | 50.2 (27.0 to 68.1), n=5 | 35.3 | 27.0 | -22.1 [-26.5, -17.4] | yes | 5/5 | 0/5 | - |  |
| FRLL FaceMorpher native | descriptive | 2.5 [1.5, 3.6] (5.9, 3.9, 0.5, 0.5, 1.5) | 48.7 (24.5 to 74.9), n=5 | 33.4 | 24.5 | -22.0 [-26.1, -17.0] | yes | 5/5 | 0/5 | - | at least 10 points below every label-free reference (range 24.5 to 74.9%); not 'above chance' |
| FRLL FaceMorpher E7 (history-matched) | descriptive | 7.0 [5.1, 8.6] (17.7, 6.3, 3.4, 1.5, 6.3) | 48.7 (23.5 to 76.0), n=5 | 32.4 | 23.5 | -16.5 [-21.2, -12.0] | yes | 4/5 | 1/5 | - |  |
| FRLL OpenCV native | descriptive | 17.7 [14.4, 20.9] (34.2, 25.5, 6.9, 6.3, 15.7) | 45.9 (26.5 to 60.9), n=5 | 34.8 | 26.5 | -8.7 [-13.2, -2.9] | no | 3/5 | 3/5 | - | a miss on a landmark cell does not show that the cell needs morphs |
| FRLL OpenCV E7 (history-matched) | descriptive | 30.9 [27.2, 34.5] (54.9, 33.3, 18.1, 15.7, 32.3) | 46.3 (25.6 to 63.6), n=5 | 33.3 | 25.6 | 5.3 [0.2, 11.0] | no | 0/5 | 5/5 | - |  |
| FRLL StyleGAN native | descriptive | 33.1 [28.5, 38.6] (40.7, 38.2, 25.0, 21.2, 40.7) | 51.3 (30.9 to 72.6), n=5 | 46.6 | 30.9 | 2.3 [-3.1, 8.8] | no | 0/5 | 5/5 | - |  |
| FRLL StyleGAN E7 (history-matched) | descriptive | 33.1 [28.5, 38.6] (40.7, 38.2, 25.0, 21.2, 40.7) | 51.3 (30.9 to 72.6), n=5 | 46.6 | 30.9 | 2.3 [-3.1, 8.8] | no | 0/5 | 5/5 | - | E7 not applicable |
| FRLL Webmorph native | descriptive | 0.7 [0.2, 1.0] (0.9, 2.0, 0.5, 0.0, 0.1) | 48.7 (27.4 to 65.2), n=5 | 32.8 | 27.4 | -26.7 [-31.3, -22.5] | yes | 5/5 | 0/5 | - | at least 10 points below every label-free reference (range 27.4 to 65.2%); not 'above chance' |
| FRLL Webmorph E7 (history-matched) | descriptive | 4.5 [3.2, 5.7] (9.3, 5.0, 4.9, 0.4, 2.9) | 48.4 (26.5 to 66.2), n=5 | 30.4 | 26.5 | -22.0 [-27.0, -18.1] | yes | 5/5 | 0/5 | - |  |
| corrected MAD22 FaceMorpher native | descriptive | 0.0 [0.0, 0.0] (0.0, 0.0, 0.0, 0.0, 0.0) | 52.3 (27.5 to 64.8), n=5 | 44.6 | 27.5 | -27.5 [-33.3, -22.6] | yes | 5/5 | 0/5 | - | at least 10 points below every label-free reference (range 27.5 to 64.8%); not 'above chance' |
| corrected MAD22 FaceMorpher E7 (history-matched) | descriptive | 0.0 [0.0, 0.0] (0.0, 0.0, 0.0, 0.0, 0.0) | 52.5 (27.5 to 69.2), n=5 | 39.2 | 27.5 | -27.5 [-32.8, -22.0] | yes | 5/5 | 0/5 | - |  |
| corrected MAD22 MIPGAN-I native | descriptive | 72.5 [69.9, 75.0] (84.9, 59.3, 80.9, 52.8, 84.8) | 52.3 (36.8 to 73.5), n=5 | 56.4 | 36.8 | 35.8 [30.4, 42.4] | no | 0/5 | 5/5 | - |  |
| corrected MAD22 MIPGAN-I E7 (history-matched) | descriptive | 72.5 [69.9, 75.0] (84.9, 59.3, 80.9, 52.8, 84.8) | 52.3 (36.8 to 73.5), n=5 | 56.4 | 36.8 | 35.8 [30.4, 42.4] | no | 0/5 | 5/5 | - | E7 not applicable |
| corrected MAD22 MIPGAN-II native | descriptive | 72.5 [70.3, 74.8] (82.4, 58.8, 82.4, 55.4, 83.4) | 47.8 (33.4 to 69.1), n=5 | 54.4 | 33.4 | 39.1 [34.2, 45.9] | no | 0/5 | 5/5 | - |  |
| corrected MAD22 MIPGAN-II E7 (history-matched) | descriptive | 72.5 [70.3, 74.8] (82.4, 58.8, 82.4, 55.4, 83.4) | 47.8 (33.4 to 69.1), n=5 | 54.4 | 33.4 | 39.1 [34.2, 45.9] | no | 0/5 | 5/5 | - | E7 not applicable |
| corrected MAD22 OpenCV native | descriptive | 37.0 [33.6, 40.7] (38.2, 44.6, 23.6, 43.7, 34.9) | 49.2 (42.7 to 59.8), n=5 | 49.9 | 42.7 | -5.7 [-10.4, 0.7] | no | 1/5 | 5/5 | - | a miss on a landmark cell does not show that the cell needs morphs |
| corrected MAD22 OpenCV E7 (history-matched) | descriptive | 39.6 [36.2, 42.8] (40.8, 46.6, 26.9, 46.6, 37.3) | 49.6 (42.6 to 59.8), n=5 | 49.5 | 42.6 | -3.0 [-8.0, 2.9] | no | 1/5 | 5/5 | - | E7 partial (108/204 identical) |
| corrected MAD22 Webmorph native | descriptive | 26.7 [23.3, 30.0] (24.9, 32.4, 20.0, 32.8, 23.1) | 48.1 (39.7 to 60.2), n=5 | 41.2 | 39.7 | -13.0 [-16.7, -5.4] | yes | 3/5 | 5/5 | - | below every label-free reference, not at the published level (above 15% in 5 of 5 seeds); at least 10 points below every label-free reference (range 39.7 to 60.2%); not 'above chance' |
| corrected MAD22 Webmorph E7 (history-matched) | descriptive | 28.9 [25.5, 32.5] (28.3, 33.8, 23.6, 33.9, 25.0) | 48.5 (39.7 to 60.8), n=5 | 40.7 | 39.7 | -10.7 [-14.4, -2.9] | yes | 3/5 | 5/5 | - | E7 partial (104/204 identical); below every label-free reference, not at the published level (above 15% in 5 of 5 seeds) |

## Table 2. Signed AUC per cell, our frames, CLIP ViT-B/16 with LoRA (M3)

| cell | morph-free: mean [95% CI] (per seed) | label-permuted: mean (range) | untrained | folded reference AUC, max |
|---|---|---|---|---|
| MorDIFF native | 1.000 [1.000, 1.000] (1.000, 1.000, 1.000, 1.000, 1.000) | 0.543 (0.364 to 0.686) | 0.436 | 0.686 |
| MorDIFF E7 (history-matched) | 0.997 [0.994, 0.999] (1.000, 1.000, 0.991, 0.998, 0.995) | 0.524 (0.359 to 0.605) | 0.551 | 0.641 |
| DiM-A native | 0.999 [0.999, 1.000] (1.000, 0.997, 1.000, 1.000, 1.000) | 0.567 (0.413 to 0.684) | 0.493 | 0.684 |
| DiM-A E7 (history-matched) | 0.377 [0.325, 0.432] (0.546, 0.347, 0.460, 0.376, 0.156) | 0.564 (0.426 to 0.691) | 0.569 | 0.691 |
| DiM-C native | 1.000 [1.000, 1.000] (1.000, 1.000, 1.000, 1.000, 1.000) | 0.540 (0.351 to 0.658) | 0.518 | 0.658 |
| DiM-C E7 (history-matched) | 0.878 [0.843, 0.910] (0.907, 0.932, 0.917, 0.918, 0.715) | 0.538 (0.362 to 0.672) | 0.595 | 0.672 |
| Fast-DiM native | 0.998 [0.996, 0.999] (0.999, 0.996, 1.000, 1.000, 0.995) | 0.535 (0.392 to 0.594) | 0.508 | 0.608 |
| Fast-DiM E7 (history-matched) | 0.407 [0.347, 0.469] (0.416, 0.533, 0.464, 0.484, 0.137) | 0.532 (0.406 to 0.604) | 0.583 | 0.604 |
| Fast-DiM-ODE native | 0.996 [0.993, 0.998] (0.999, 0.996, 0.999, 1.000, 0.988) | 0.563 (0.476 to 0.732) | 0.462 | 0.732 |
| Fast-DiM-ODE E7 (history-matched) | 0.225 [0.191, 0.258] (0.259, 0.431, 0.144, 0.274, 0.019) | 0.560 (0.507 to 0.739) | 0.537 | 0.739 |
| Greedy-DiM native | 1.000 [1.000, 1.000] (1.000, 1.000, 1.000, 1.000, 1.000) | 0.510 (0.330 to 0.640) | 0.406 | 0.670 |
| Greedy-DiM E7 (history-matched) | 0.558 [0.531, 0.587] (0.101, 0.993, 0.562, 0.954, 0.181) | 0.507 (0.341 to 0.650) | 0.484 | 0.659 |
| Greedy-DiM-S native | 0.999 [0.998, 1.000] (0.999, 1.000, 1.000, 1.000, 0.998) | 0.525 (0.319 to 0.666) | 0.446 | 0.681 |
| Greedy-DiM-S E7 (history-matched) | 0.565 [0.504, 0.626] (0.426, 0.894, 0.623, 0.695, 0.186) | 0.523 (0.332 to 0.676) | 0.523 | 0.676 |
| FRLL AMSL native | 1.000 [0.999, 1.000] (1.000, 0.998, 1.000, 1.000, 1.000) | 0.507 (0.301 to 0.793) | 0.656 | 0.793 |
| FRLL AMSL E7 (history-matched) | 0.989 [0.982, 0.994] (0.970, 0.990, 0.992, 1.000, 0.993) | 0.507 (0.276 to 0.803) | 0.685 | 0.803 |
| FRLL FaceMorpher native | 0.995 [0.992, 0.998] (0.984, 0.992, 1.000, 1.000, 0.999) | 0.520 (0.172 to 0.830) | 0.708 | 0.830 |
| FRLL FaceMorpher E7 (history-matched) | 0.977 [0.967, 0.985] (0.916, 0.986, 0.995, 0.999, 0.987) | 0.520 (0.158 to 0.835) | 0.725 | 0.842 |
| FRLL OpenCV native | 0.895 [0.869, 0.919] (0.736, 0.835, 0.982, 0.985, 0.939) | 0.562 (0.364 to 0.814) | 0.680 | 0.814 |
| FRLL OpenCV E7 (history-matched) | 0.754 [0.715, 0.791] (0.453, 0.728, 0.897, 0.928, 0.764) | 0.561 (0.343 to 0.820) | 0.700 | 0.820 |
| FRLL StyleGAN native | 0.738 [0.685, 0.790] (0.646, 0.687, 0.835, 0.869, 0.654) | 0.498 (0.202 to 0.777) | 0.553 | 0.798 |
| FRLL StyleGAN E7 (history-matched) | 0.738 [0.685, 0.790] (0.646, 0.687, 0.835, 0.869, 0.654) | 0.498 (0.202 to 0.777) | 0.553 | 0.798 |
| FRLL Webmorph native | 1.000 [0.999, 1.000] (1.000, 0.999, 1.000, 1.000, 1.000) | 0.523 (0.318 to 0.785) | 0.722 | 0.785 |
| FRLL Webmorph E7 (history-matched) | 0.990 [0.984, 0.995] (0.970, 0.992, 0.991, 1.000, 0.996) | 0.522 (0.294 to 0.793) | 0.748 | 0.793 |
| corrected MAD22 FaceMorpher native | 1.000 [1.000, 1.000] (1.000, 1.000, 1.000, 1.000, 1.000) | 0.467 (0.303 to 0.783) | 0.579 | 0.783 |
| corrected MAD22 FaceMorpher E7 (history-matched) | 1.000 [1.000, 1.000] (1.000, 1.000, 1.000, 1.000, 1.000) | 0.466 (0.235 to 0.794) | 0.659 | 0.794 |
| corrected MAD22 MIPGAN-I native | 0.215 [0.189, 0.242] (0.079, 0.359, 0.096, 0.475, 0.064) | 0.486 (0.200 to 0.738) | 0.400 | 0.800 |
| corrected MAD22 MIPGAN-I E7 (history-matched) | 0.215 [0.189, 0.242] (0.079, 0.359, 0.096, 0.475, 0.064) | 0.486 (0.200 to 0.738) | 0.400 | 0.800 |
| corrected MAD22 MIPGAN-II native | 0.217 [0.194, 0.240] (0.089, 0.387, 0.086, 0.442, 0.080) | 0.539 (0.247 to 0.777) | 0.442 | 0.777 |
| corrected MAD22 MIPGAN-II E7 (history-matched) | 0.217 [0.194, 0.240] (0.089, 0.387, 0.086, 0.442, 0.080) | 0.539 (0.247 to 0.777) | 0.442 | 0.777 |
| corrected MAD22 OpenCV native | 0.691 [0.647, 0.734] (0.676, 0.605, 0.846, 0.612, 0.716) | 0.513 (0.361 to 0.621) | 0.492 | 0.639 |
| corrected MAD22 OpenCV E7 (history-matched) | 0.663 [0.617, 0.707] (0.640, 0.585, 0.820, 0.583, 0.685) | 0.512 (0.360 to 0.622) | 0.495 | 0.640 |
| corrected MAD22 Webmorph native | 0.817 [0.785, 0.847] (0.820, 0.739, 0.883, 0.767, 0.877) | 0.537 (0.379 to 0.648) | 0.620 | 0.648 |
| corrected MAD22 Webmorph E7 (history-matched) | 0.791 [0.756, 0.824] (0.789, 0.724, 0.852, 0.740, 0.848) | 0.536 (0.376 to 0.648) | 0.624 | 0.648 |

## Table 3a. Fixed threshold "0.5 rule": flag rate (genuine photos flagged) and miss rate (morphs not flagged), %, our frames, CLIP ViT-B/16 with LoRA (M3)

Threshold pool: none (score at least 0.5). Arm means; per-seed miss rates in brackets.

| cell | morph-free flag / miss (per-seed miss) | label-permuted flag / miss | untrained flag / miss |
|---|---|---|---|
| MorDIFF native | 0.0 / 71.1 (5.0, 92.6, 85.7, 73.6, 98.7) | 57.4 / 43.2 | 67.6 / 39.3 |
| MorDIFF E7 (history-matched) | 0.0 / 71.1 (5.0, 92.6, 85.7, 73.6, 98.7) | 60.9 / 43.2 | 54.4 / 39.3 |
| DiM-A native | 0.0 / 98.7 (93.4, 100.0, 100.0, 100.0, 100.0) | 48.8 / 46.4 | 46.1 / 55.8 |
| DiM-A E7 (history-matched) | 0.5 / 98.7 (93.4, 100.0, 100.0, 100.0, 100.0) | 48.7 / 46.4 | 33.8 / 55.8 |
| DiM-C native | 0.0 / 90.3 (51.4, 100.0, 100.0, 100.0, 100.0) | 48.8 / 47.6 | 46.1 / 52.0 |
| DiM-C E7 (history-matched) | 0.4 / 90.3 (51.4, 100.0, 100.0, 100.0, 100.0) | 48.5 / 47.6 | 33.3 / 52.0 |
| Fast-DiM native | 0.0 / 99.5 (97.6, 100.0, 100.0, 100.0, 100.0) | 48.8 / 48.7 | 46.1 / 54.8 |
| Fast-DiM E7 (history-matched) | 0.6 / 99.5 (97.6, 100.0, 100.0, 100.0, 100.0) | 48.2 / 48.7 | 33.3 / 54.8 |
| Fast-DiM-ODE native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.8 / 46.1 | 46.1 / 60.3 |
| Fast-DiM-ODE E7 (history-matched) | 0.5 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.5 / 46.1 | 33.3 / 60.3 |
| Greedy-DiM native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.8 / 50.0 | 46.1 / 69.4 |
| Greedy-DiM E7 (history-matched) | 0.5 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.9 / 50.0 | 33.8 / 69.4 |
| Greedy-DiM-S native | 0.0 / 99.0 (95.6, 100.0, 100.0, 99.6, 100.0) | 48.8 / 48.2 | 46.1 / 63.4 |
| Greedy-DiM-S E7 (history-matched) | 0.5 / 99.0 (95.6, 100.0, 100.0, 99.6, 100.0) | 48.9 / 48.2 | 34.3 / 63.4 |
| FRLL AMSL native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.8 / 50.1 | 46.1 / 31.9 |
| FRLL AMSL E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.9 / 50.1 | 41.2 / 31.9 |
| FRLL FaceMorpher native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.8 / 45.9 | 46.1 / 24.1 |
| FRLL FaceMorpher E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 49.2 / 45.9 | 42.2 / 24.1 |
| FRLL OpenCV native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.8 / 44.9 | 46.1 / 27.2 |
| FRLL OpenCV E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 49.1 / 44.9 | 41.7 / 27.2 |
| FRLL StyleGAN native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.8 / 45.4 | 46.1 / 48.0 |
| FRLL StyleGAN E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.8 / 45.4 | 46.1 / 48.0 |
| FRLL Webmorph native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.8 / 49.1 | 46.1 / 22.9 |
| FRLL Webmorph E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 49.4 / 49.1 | 41.7 / 22.9 |
| corrected MAD22 FaceMorpher native | 0.0 / 7.2 (0.0, 12.6, 8.9, 1.1, 13.6) | 48.8 / 54.9 | 46.1 / 43.5 |
| corrected MAD22 FaceMorpher E7 (history-matched) | 1.3 / 7.2 (0.0, 12.6, 8.9, 1.1, 13.6) | 48.6 / 54.9 | 32.4 / 43.5 |
| corrected MAD22 MIPGAN-I native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.8 / 50.7 | 46.1 / 71.0 |
| corrected MAD22 MIPGAN-I E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.8 / 50.7 | 46.1 / 71.0 |
| corrected MAD22 MIPGAN-II native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.8 / 46.1 | 46.1 / 67.9 |
| corrected MAD22 MIPGAN-II E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.8 / 46.1 | 46.1 / 67.9 |
| corrected MAD22 OpenCV native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.8 / 51.2 | 46.1 / 55.9 |
| corrected MAD22 OpenCV E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.9 / 51.2 | 45.6 / 55.9 |
| corrected MAD22 Webmorph native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.8 / 50.2 | 46.1 / 38.0 |
| corrected MAD22 Webmorph E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 49.1 / 50.2 | 45.6 / 38.0 |

## Table 3b. Fixed threshold "FRLL-5%": flag rate (genuine photos flagged) and miss rate (morphs not flagged), %, our frames, CLIP ViT-B/16 with LoRA (M3)

Threshold pool: 204 unprocessed FRLL genuine photos, at most 10 flagged. Arm means; per-seed miss rates in brackets.

| cell | morph-free flag / miss (per-seed miss) | label-permuted flag / miss | untrained flag / miss |
|---|---|---|---|
| MorDIFF native | 60.9 / 0.0 (0.0, 0.0, 0.0, 0.0, 0.0) | 9.3 / 86.9 | 11.8 / 96.6 |
| MorDIFF E7 (history-matched) | 100.0 / 0.0 (0.0, 0.0, 0.0, 0.0, 0.0) | 8.6 / 86.9 | 3.4 / 96.6 |
| DiM-A native | 4.9 / 0.3 (0.0, 1.6, 0.0, 0.0, 0.0) | 4.9 / 88.9 | 4.9 / 100.0 |
| DiM-A E7 (history-matched) | 99.9 / 0.3 (0.0, 1.6, 0.0, 0.0, 0.0) | 4.3 / 88.9 | 1.0 / 100.0 |
| DiM-C native | 4.9 / 0.0 (0.0, 0.0, 0.0, 0.0, 0.0) | 4.9 / 91.8 | 4.9 / 100.0 |
| DiM-C E7 (history-matched) | 99.9 / 0.0 (0.0, 0.0, 0.0, 0.0, 0.0) | 4.0 / 91.8 | 1.0 / 100.0 |
| Fast-DiM native | 4.9 / 0.8 (0.0, 1.6, 0.0, 0.0, 2.4) | 4.9 / 91.6 | 4.9 / 99.8 |
| Fast-DiM E7 (history-matched) | 99.9 / 0.8 (0.0, 1.6, 0.0, 0.0, 2.4) | 4.2 / 91.6 | 1.0 / 99.8 |
| Fast-DiM-ODE native | 4.9 / 1.8 (0.4, 2.2, 0.0, 0.0, 6.4) | 4.9 / 89.4 | 4.9 / 99.8 |
| Fast-DiM-ODE E7 (history-matched) | 99.9 / 1.8 (0.4, 2.2, 0.0, 0.0, 6.4) | 4.0 / 89.4 | 1.0 / 99.8 |
| Greedy-DiM native | 4.9 / 0.0 (0.0, 0.0, 0.0, 0.0, 0.0) | 4.9 / 94.3 | 4.9 / 100.0 |
| Greedy-DiM E7 (history-matched) | 100.0 / 0.0 (0.0, 0.0, 0.0, 0.0, 0.0) | 3.9 / 94.3 | 1.0 / 100.0 |
| Greedy-DiM-S native | 4.9 / 0.4 (1.0, 0.0, 0.0, 0.0, 0.8) | 4.9 / 93.3 | 4.9 / 100.0 |
| Greedy-DiM-S E7 (history-matched) | 100.0 / 0.4 (1.0, 0.0, 0.0, 0.0, 0.8) | 4.1 / 93.3 | 1.0 / 100.0 |
| FRLL AMSL native | 4.9 / 0.0 (0.0, 0.0, 0.0, 0.0, 0.0) | 4.9 / 91.9 | 4.9 / 92.8 |
| FRLL AMSL E7 (history-matched) | 39.7 / 0.0 (0.0, 0.0, 0.0, 0.0, 0.0) | 4.2 / 91.9 | 2.5 / 92.8 |
| FRLL FaceMorpher native | 4.9 / 2.0 (6.3, 3.4, 0.0, 0.0, 0.2) | 4.9 / 90.2 | 4.9 / 90.3 |
| FRLL FaceMorpher E7 (history-matched) | 22.4 / 2.0 (6.3, 3.4, 0.0, 0.0, 0.2) | 4.7 / 90.2 | 3.4 / 90.3 |
| FRLL OpenCV native | 4.9 / 41.3 (86.3, 72.1, 8.4, 7.5, 32.1) | 4.9 / 88.4 | 4.9 / 93.5 |
| FRLL OpenCV E7 (history-matched) | 26.9 / 41.3 (86.3, 72.1, 8.4, 7.5, 32.1) | 4.5 / 88.4 | 2.9 / 93.5 |
| FRLL StyleGAN native | 4.9 / 72.1 (86.4, 80.8, 49.1, 57.4, 86.7) | 4.9 / 90.8 | 4.9 / 100.0 |
| FRLL StyleGAN E7 (history-matched) | 4.9 / 72.1 (86.4, 80.8, 49.1, 57.4, 86.7) | 4.9 / 90.8 | 4.9 / 100.0 |
| FRLL Webmorph native | 4.9 / 0.0 (0.0, 0.1, 0.0, 0.0, 0.0) | 4.9 / 92.3 | 4.9 / 85.8 |
| FRLL Webmorph E7 (history-matched) | 40.1 / 0.0 (0.0, 0.1, 0.0, 0.0, 0.0) | 4.4 / 92.3 | 2.9 / 85.8 |
| corrected MAD22 FaceMorpher native | 5.2 / 0.0 (0.0, 0.0, 0.0, 0.0, 0.0) | 5.0 / 92.9 | 4.9 / 97.8 |
| corrected MAD22 FaceMorpher E7 (history-matched) | 100.0 / 0.0 (0.0, 0.0, 0.0, 0.0, 0.0) | 4.3 / 92.9 | 1.0 / 97.8 |
| corrected MAD22 MIPGAN-I native | 5.2 / 99.7 (100.0, 99.0, 99.8, 99.7, 100.0) | 5.0 / 92.1 | 4.9 / 100.0 |
| corrected MAD22 MIPGAN-I E7 (history-matched) | 5.2 / 99.7 (100.0, 99.0, 99.8, 99.7, 100.0) | 5.0 / 92.1 | 4.9 / 100.0 |
| corrected MAD22 MIPGAN-II native | 5.2 / 99.8 (100.0, 99.2, 99.8, 99.9, 100.0) | 5.0 / 91.8 | 4.9 / 100.0 |
| corrected MAD22 MIPGAN-II E7 (history-matched) | 5.2 / 99.8 (100.0, 99.2, 99.8, 99.9, 100.0) | 5.0 / 91.8 | 4.9 / 100.0 |
| corrected MAD22 OpenCV native | 5.2 / 79.9 (82.2, 94.4, 51.7, 93.8, 77.1) | 5.0 / 94.6 | 4.9 / 98.5 |
| corrected MAD22 OpenCV E7 (history-matched) | 7.1 / 79.9 (82.2, 94.4, 51.7, 93.8, 77.1) | 4.7 / 94.6 | 4.9 / 98.5 |
| corrected MAD22 Webmorph native | 5.2 / 70.0 (68.0, 95.6, 47.8, 87.2, 51.2) | 5.0 / 91.2 | 4.9 / 93.2 |
| corrected MAD22 Webmorph E7 (history-matched) | 8.0 / 70.0 (68.0, 95.6, 47.8, 87.2, 51.2) | 4.5 / 91.2 | 4.9 / 93.2 |

## Table 4. Training accuracy (threshold 0.5, no TTA), CLIP ViT-B/16 with LoRA (M3)

| network | arm | own training labels: accuracy / AUC | true labels: accuracy / AUC | share of labels permuted | train hours |
|---|---|---|---|---|---|
| `AD4_m3mf_s401` | morph-free | 1.0 / 1.0 | 1.0 / 1.0 | 0.0 | 0.5206088322401047 |
| `AD4_m3mf_s402` | morph-free | 1.0 / 1.0 | 1.0 / 1.0 | 0.0 | 0.5188676049311955 |
| `AD4_m3mf_s403` | morph-free | 1.0 / 1.0 | 1.0 / 1.0 | 0.0 | 0.5196988765398661 |
| `AD4_m3mf_s404` | morph-free | 1.0 / 1.0 | 1.0 / 1.0 | 0.0 | 0.5194040908416112 |
| `AD4_m3mf_s405` | morph-free | 1.0 / 1.0 | 1.0 / 1.0 | 0.0 | 0.5195104009575314 |
| `AD4_m3perm_s401` | label-permuted | 0.5194 / 0.5236 | 0.6093 / 0.6449 | 0.4986 | 0.5192203282647663 |
| `AD4_m3perm_s402` | label-permuted | 0.5153 / 0.5218 | 0.6165 / 0.6629 | 0.4988 | 0.5186984881427553 |
| `AD4_m3perm_s403` | label-permuted | 0.514 / 0.5211 | 0.6854 / 0.7463 | 0.4984 | 0.5192206018500858 |
| `AD4_m3perm_s404` | label-permuted | 0.5166 / 0.5228 | 0.6311 / 0.6608 | 0.4978 | 0.5188637433449427 |
| `AD4_m3perm_s405` | label-permuted | 0.5119 / 0.5179 | 0.3988 / 0.3654 | 0.5016 | 0.5197417490349876 |
| `AD4_m3zero_s401` | untrained | 0.2953 / 0.227 | 0.2953 / 0.227 | 0.0 | None |
