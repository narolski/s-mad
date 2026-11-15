# Morph-free networks (AD4), CLIP ViT-B/16 with LoRA (M3): reading, our frames

Status: **final**. All numbers on our frames (our alignment of every benchmark). EER in %, signed AUC (morph positive). 95% intervals: person bootstrap (Amendment 2 (a)), descriptive; the verdicts use point values.

**FLAG on every number of this recipe's trained networks: not reproduced on this stack** (reproduction gate, 1 of 11 cells: Fast-DiM-ODE native, morph-free seed mean 4.01% against a bound of 3.0 (per seed 8.72, 1.88, 3.96, 0.10, 5.40)). The registered remedy (the WCSS cluster tasks) decides when it runs; until then this reading is descriptive. No seed is dropped or reweighted.

Networks (arm, seed, platform and card):
- morph-free seed 401 (`AD4_m3mf_s401`): rented machine (Vast), NVIDIA A100-SXM4-40GB; sample-order gate pass (200/200)
- morph-free seed 402 (`AD4_m3mf_s402`): rented machine (Vast), NVIDIA A100-SXM4-40GB; sample-order gate pass (200/200)
- morph-free seed 403 (`AD4_m3mf_s403`): rented machine (Vast), NVIDIA A100-SXM4-40GB; sample-order gate pass (200/200)
- morph-free seed 404 (`AD4_m3mf_s404`): rented machine (Vast), NVIDIA A100-SXM4-40GB; sample-order gate pass (200/200)
- morph-free seed 405 (`AD4_m3mf_s405`): rented machine (Vast), NVIDIA A100-SXM4-40GB; sample-order gate pass (200/200)
- label-permuted seed 401 (`AD4_m3perm_s401`): rented machine (Vast), NVIDIA RTX 6000 Ada Generation; sample-order gate pass (200/200)
- label-permuted seed 402 (`AD4_m3perm_s402`): rented machine (Vast), NVIDIA RTX 6000 Ada Generation; sample-order gate pass (200/200)
- label-permuted seed 403 (`AD4_m3perm_s403`): rented machine (Vast), NVIDIA RTX 6000 Ada Generation; sample-order gate pass (200/200)
- label-permuted seed 404 (`AD4_m3perm_s404`): rented machine (Vast), NVIDIA RTX 6000 Ada Generation; sample-order gate pass (200/200)
- label-permuted seed 405 (`AD4_m3perm_s405`): rented machine (Vast), NVIDIA RTX 6000 Ada Generation; sample-order gate pass (200/200)
- untrained seed 401 (`AD4_m3zero_s401`): DGX, NVIDIA GB10

## Table 1. EER per cell (%), our frames, CLIP ViT-B/16 with LoRA (M3)

Flag: not reproduced on this stack (see top).

| cell | role | morph-free: mean [95% CI] (per seed) | label-permuted: mean (range) | untrained | lowest reference | margin = morph-free mean minus lowest reference [95% CI] | passable without morphs | seeds meeting margin | seeds above 15% | A1 | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MorDIFF native | primary | 0.0 [0.0, 0.0] (0.0, 0.0, 0.0, 0.0, 0.0) | 47.0 (37.3 to 60.8), n=5 | 53.9 | 37.3 | -37.3 [-40.7, -31.9] | yes | 5/5 | 0/5 | not falsified |  |
| MorDIFF E7 (history-matched) | descriptive | 2.9 [1.8, 4.2] (3.3, 0.4, 5.4, 2.0, 3.4) | 48.4 (42.7 to 60.8), n=5 | 48.0 | 42.7 | -39.8 [-44.7, -32.2] | yes | 5/5 | 0/5 | - |  |
| DiM-A native | secondary | 0.8 [0.2, 1.5] (1.4, 1.9, 0.4, 0.0, 0.4) | 45.4 (39.7 to 56.4), n=5 | 50.0 | 39.7 | -38.8 [-42.4, -29.9] | yes | 5/5 | 0/5 | not falsified |  |
| DiM-A E7 (history-matched) | descriptive | 63.4 [58.9, 67.5] (61.9, 63.1, 56.5, 57.7, 78.0) | 46.3 (39.3 to 55.8), n=5 | 45.0 | 39.3 | 24.1 [16.8, 35.2] | no | 0/5 | 5/5 | - |  |
| DiM-C native | secondary | 0.0 [0.0, 0.0] (0.0, 0.0, 0.0, 0.0, 0.0) | 47.0 (37.2 to 61.3), n=5 | 48.0 | 37.2 | -37.2 [-43.5, -30.9] | yes | 5/5 | 0/5 | not falsified |  |
| DiM-C E7 (history-matched) | descriptive | 21.7 [18.2, 25.9] (23.6, 14.7, 24.0, 13.2, 33.3) | 47.6 (35.2 to 60.9), n=5 | 43.2 | 35.2 | -13.5 [-22.0, -6.5] | yes | 4/5 | 3/5 | - | below every label-free reference, not at the published level (above 15% in 3 of 5 seeds) |
| Fast-DiM native | secondary | 1.7 [0.7, 2.5] (2.9, 1.9, 1.0, 0.4, 2.4) | 47.6 (42.2 to 57.4), n=5 | 49.0 | 42.2 | -40.5 [-45.0, -33.4] | yes | 5/5 | 0/5 | not falsified |  |
| Fast-DiM E7 (history-matched) | descriptive | 60.5 [55.0, 64.7] (65.2, 48.0, 58.4, 53.0, 78.0) | 48.3 (40.3 to 56.4), n=5 | 44.2 | 40.3 | 20.2 [10.4, 28.4] | no | 0/5 | 5/5 | - |  |
| Fast-DiM-ODE native | secondary | 4.0 [2.5, 5.6] (8.7, 1.9, 4.0, 0.1, 5.4) | 46.0 (37.3 to 50.9), n=5 | 52.0 | 37.3 | -33.3 [-38.5, -25.7] | yes | 5/5 | 0/5 | not falsified |  |
| Fast-DiM-ODE E7 (history-matched) | descriptive | 75.9 [73.0, 79.1] (80.4, 57.9, 82.4, 65.7, 93.2) | 46.6 (37.3 to 51.5), n=5 | 46.1 | 37.3 | 38.6 [32.5, 47.2] | no | 0/5 | 5/5 | - |  |
| Greedy-DiM native | secondary | 2.4 [1.5, 3.3] (11.2, 0.0, 0.4, 0.0, 0.4) | 50.3 (43.1 to 63.3), n=5 | 55.8 | 43.1 | -40.6 [-43.8, -33.9] | yes | 5/5 | 0/5 | not falsified |  |
| Greedy-DiM E7 (history-matched) | descriptive | 49.9 [47.3, 52.6] (94.6, 4.4, 65.3, 11.3, 74.0) | 51.0 (43.1 to 62.7), n=5 | 50.0 | 43.1 | 6.9 [3.1, 15.2] | no | 2/5 | 3/5 | - |  |
| Greedy-DiM-S native | secondary | 1.0 [0.4, 1.9] (3.0, 0.1, 0.4, 0.1, 1.4) | 48.2 (41.1 to 62.3), n=5 | 53.4 | 41.1 | -40.1 [-43.1, -33.4] | yes | 5/5 | 0/5 | not falsified |  |
| Greedy-DiM-S E7 (history-matched) | descriptive | 46.5 [41.4, 51.6] (59.8, 19.5, 43.2, 36.8, 73.0) | 48.8 (40.6 to 61.8), n=5 | 47.0 | 40.6 | 5.8 [-1.1, 15.6] | no | 1/5 | 5/5 | - |  |
| FRLL AMSL native | descriptive | 1.1 [0.6, 1.8] (3.9, 1.0, 0.5, 0.0, 0.0) | 49.9 (27.4 to 65.7), n=5 | 37.3 | 27.4 | -26.4 [-30.7, -21.9] | yes | 5/5 | 0/5 | - | at least 10 points below every label-free reference (range 27.4 to 65.7%); not 'above chance' |
| FRLL AMSL E7 (history-matched) | descriptive | 8.2 [6.6, 9.8] (23.6, 6.3, 7.4, 0.4, 3.5) | 50.1 (27.0 to 67.6), n=5 | 35.3 | 27.0 | -18.7 [-23.2, -13.9] | yes | 4/5 | 1/5 | - |  |
| FRLL FaceMorpher native | descriptive | 4.1 [2.8, 5.5] (12.3, 3.9, 2.5, 0.5, 1.4) | 48.6 (24.0 to 74.5), n=5 | 33.4 | 24.0 | -19.9 [-24.4, -15.3] | yes | 5/5 | 0/5 | - | at least 10 points below every label-free reference (range 24.0 to 74.5%); not 'above chance' |
| FRLL FaceMorpher E7 (history-matched) | descriptive | 11.1 [8.6, 13.0] (30.8, 7.8, 8.3, 2.0, 6.4) | 48.8 (23.1 to 76.0), n=5 | 32.4 | 23.1 | -12.0 [-17.4, -7.8] | yes | 4/5 | 1/5 | - |  |
| FRLL OpenCV native | descriptive | 19.7 [16.5, 22.9] (40.2, 23.5, 11.7, 7.9, 15.2) | 46.0 (26.5 to 61.2), n=5 | 34.8 | 26.5 | -6.8 [-11.3, -0.8] | no | 3/5 | 3/5 | - | a miss on a landmark cell does not show that the cell needs morphs |
| FRLL OpenCV E7 (history-matched) | descriptive | 36.7 [32.9, 40.3] (67.2, 35.3, 30.5, 18.1, 32.4) | 46.3 (25.5 to 63.2), n=5 | 33.3 | 25.5 | 11.2 [6.1, 17.0] | no | 0/5 | 5/5 | - |  |
| FRLL StyleGAN native | descriptive | 32.9 [28.3, 37.6] (47.5, 33.7, 17.6, 25.0, 40.7) | 51.3 (30.9 to 72.6), n=5 | 46.6 | 30.9 | 2.0 [-3.6, 8.0] | no | 1/5 | 5/5 | - |  |
| FRLL StyleGAN E7 (history-matched) | descriptive | 32.9 [28.3, 37.6] (47.5, 33.7, 17.6, 25.0, 40.7) | 51.3 (30.9 to 72.6), n=5 | 46.6 | 30.9 | 2.0 [-3.6, 8.0] | no | 1/5 | 5/5 | - | E7 not applicable |
| FRLL Webmorph native | descriptive | 1.0 [0.4, 1.5] (2.9, 1.0, 0.9, 0.0, 0.1) | 48.7 (27.4 to 65.2), n=5 | 32.8 | 27.4 | -26.5 [-31.0, -22.2] | yes | 5/5 | 0/5 | - | at least 10 points below every label-free reference (range 27.4 to 65.2%); not 'above chance' |
| FRLL Webmorph E7 (history-matched) | descriptive | 7.8 [6.2, 9.3] (22.0, 4.9, 8.8, 0.0, 3.4) | 48.4 (26.5 to 66.2), n=5 | 30.4 | 26.5 | -18.6 [-23.8, -14.7] | yes | 4/5 | 1/5 | - |  |
| corrected MAD22 FaceMorpher native | descriptive | 0.0 [0.0, 0.0] (0.0, 0.0, 0.0, 0.0, 0.0) | 52.2 (27.5 to 64.7), n=5 | 44.6 | 27.5 | -27.5 [-33.3, -22.6] | yes | 5/5 | 0/5 | - | at least 10 points below every label-free reference (range 27.5 to 64.7%); not 'above chance' |
| corrected MAD22 FaceMorpher E7 (history-matched) | descriptive | 0.1 [0.0, 0.3] (0.0, 0.0, 0.4, 0.0, 0.0) | 52.2 (27.5 to 69.1), n=5 | 39.2 | 27.5 | -27.4 [-32.8, -22.0] | yes | 5/5 | 0/5 | - |  |
| corrected MAD22 MIPGAN-I native | descriptive | 76.4 [74.1, 78.5] (94.2, 61.7, 85.3, 55.4, 85.2) | 52.2 (36.8 to 73.0), n=5 | 56.4 | 36.8 | 39.5 [34.2, 46.5] | no | 0/5 | 5/5 | - |  |
| corrected MAD22 MIPGAN-I E7 (history-matched) | descriptive | 76.4 [74.1, 78.5] (94.2, 61.7, 85.3, 55.4, 85.2) | 52.2 (36.8 to 73.0), n=5 | 56.4 | 36.8 | 39.5 [34.2, 46.5] | no | 0/5 | 5/5 | - | E7 not applicable |
| corrected MAD22 MIPGAN-II native | descriptive | 75.1 [73.0, 77.4] (92.7, 59.8, 81.4, 57.4, 84.3) | 47.5 (33.3 to 68.6), n=5 | 54.4 | 33.3 | 41.8 [36.9, 48.6] | no | 0/5 | 5/5 | - |  |
| corrected MAD22 MIPGAN-II E7 (history-matched) | descriptive | 75.1 [73.0, 77.4] (92.7, 59.8, 81.4, 57.4, 84.3) | 47.5 (33.3 to 68.6), n=5 | 54.4 | 33.3 | 41.8 [36.9, 48.6] | no | 0/5 | 5/5 | - | E7 not applicable |
| corrected MAD22 OpenCV native | descriptive | 34.3 [30.7, 37.6] (30.9, 37.2, 22.0, 47.1, 34.4) | 49.2 (43.1 to 59.3), n=5 | 49.9 | 43.1 | -8.8 [-13.5, -2.6] | no | 2/5 | 5/5 | - | a miss on a landmark cell does not show that the cell needs morphs |
| corrected MAD22 OpenCV E7 (history-matched) | descriptive | 36.6 [33.2, 40.0] (34.3, 38.2, 25.4, 48.1, 36.8) | 49.5 (42.6 to 59.3), n=5 | 49.5 | 42.6 | -6.0 [-11.1, -0.1] | no | 1/5 | 5/5 | - | E7 partial (108/204 identical) |
| corrected MAD22 Webmorph native | descriptive | 27.2 [23.3, 30.4] (26.0, 32.4, 20.5, 33.9, 23.0) | 48.3 (39.2 to 60.7), n=5 | 41.2 | 39.2 | -12.0 [-16.6, -5.1] | yes | 3/5 | 5/5 | - | below every label-free reference, not at the published level (above 15% in 5 of 5 seeds); at least 10 points below every label-free reference (range 39.2 to 60.7%); not 'above chance' |
| corrected MAD22 Webmorph E7 (history-matched) | descriptive | 29.0 [25.4, 33.0] (27.5, 33.4, 24.0, 35.9, 24.5) | 48.4 (39.2 to 60.7), n=5 | 40.7 | 39.2 | -10.2 [-14.3, -2.5] | yes | 3/5 | 5/5 | - | E7 partial (104/204 identical); below every label-free reference, not at the published level (above 15% in 5 of 5 seeds) |

## Table 2. Signed AUC per cell, our frames, CLIP ViT-B/16 with LoRA (M3)

Flag: not reproduced on this stack (see top).

| cell | morph-free: mean [95% CI] (per seed) | label-permuted: mean (range) | untrained | folded reference AUC, max |
|---|---|---|---|---|
| MorDIFF native | 1.000 [1.000, 1.000] (1.000, 1.000, 1.000, 1.000, 1.000) | 0.543 (0.365 to 0.688) | 0.436 | 0.688 |
| MorDIFF E7 (history-matched) | 0.996 [0.993, 0.998] (0.996, 1.000, 0.990, 0.998, 0.995) | 0.524 (0.359 to 0.606) | 0.551 | 0.641 |
| DiM-A native | 1.000 [0.999, 1.000] (1.000, 0.999, 1.000, 1.000, 1.000) | 0.568 (0.413 to 0.683) | 0.493 | 0.683 |
| DiM-A E7 (history-matched) | 0.331 [0.280, 0.385] (0.342, 0.329, 0.416, 0.409, 0.159) | 0.565 (0.426 to 0.690) | 0.569 | 0.690 |
| DiM-C native | 1.000 [1.000, 1.000] (1.000, 1.000, 1.000, 1.000, 1.000) | 0.541 (0.350 to 0.659) | 0.518 | 0.659 |
| DiM-C E7 (history-matched) | 0.852 [0.811, 0.889] (0.837, 0.928, 0.846, 0.924, 0.724) | 0.538 (0.362 to 0.672) | 0.595 | 0.672 |
| Fast-DiM native | 0.999 [0.997, 1.000] (0.998, 0.999, 1.000, 1.000, 0.997) | 0.536 (0.392 to 0.594) | 0.508 | 0.608 |
| Fast-DiM E7 (history-matched) | 0.366 [0.310, 0.426] (0.277, 0.519, 0.404, 0.492, 0.139) | 0.532 (0.406 to 0.605) | 0.583 | 0.605 |
| Fast-DiM-ODE native | 0.991 [0.985, 0.996] (0.975, 0.999, 0.995, 1.000, 0.989) | 0.563 (0.476 to 0.731) | 0.462 | 0.731 |
| Fast-DiM-ODE E7 (history-matched) | 0.178 [0.149, 0.205] (0.104, 0.381, 0.086, 0.301, 0.017) | 0.560 (0.507 to 0.738) | 0.537 | 0.738 |
| Greedy-DiM native | 0.992 [0.988, 0.996] (0.961, 1.000, 1.000, 1.000, 1.000) | 0.510 (0.330 to 0.639) | 0.406 | 0.670 |
| Greedy-DiM E7 (history-matched) | 0.482 [0.458, 0.508] (0.014, 0.987, 0.294, 0.949, 0.168) | 0.507 (0.342 to 0.648) | 0.484 | 0.658 |
| Greedy-DiM-S native | 0.999 [0.997, 1.000] (0.995, 1.000, 1.000, 1.000, 0.999) | 0.527 (0.320 to 0.666) | 0.446 | 0.680 |
| Greedy-DiM-S E7 (history-matched) | 0.537 [0.477, 0.598] (0.345, 0.877, 0.594, 0.684, 0.185) | 0.524 (0.334 to 0.676) | 0.523 | 0.676 |
| FRLL AMSL native | 0.998 [0.997, 0.999] (0.993, 0.999, 1.000, 1.000, 1.000) | 0.508 (0.304 to 0.792) | 0.656 | 0.792 |
| FRLL AMSL E7 (history-matched) | 0.963 [0.952, 0.973] (0.855, 0.989, 0.976, 1.000, 0.993) | 0.507 (0.278 to 0.802) | 0.685 | 0.802 |
| FRLL FaceMorpher native | 0.989 [0.983, 0.994] (0.955, 0.993, 0.997, 1.000, 0.999) | 0.522 (0.174 to 0.831) | 0.708 | 0.831 |
| FRLL FaceMorpher E7 (history-matched) | 0.946 [0.931, 0.961] (0.788, 0.982, 0.976, 0.999, 0.987) | 0.522 (0.161 to 0.835) | 0.725 | 0.839 |
| FRLL OpenCV native | 0.877 [0.848, 0.904] (0.649, 0.866, 0.952, 0.978, 0.940) | 0.563 (0.365 to 0.814) | 0.680 | 0.814 |
| FRLL OpenCV E7 (history-matched) | 0.690 [0.650, 0.729] (0.285, 0.717, 0.781, 0.910, 0.757) | 0.562 (0.346 to 0.820) | 0.700 | 0.820 |
| FRLL StyleGAN native | 0.737 [0.688, 0.784] (0.549, 0.746, 0.900, 0.833, 0.659) | 0.498 (0.201 to 0.776) | 0.553 | 0.799 |
| FRLL StyleGAN E7 (history-matched) | 0.737 [0.688, 0.784] (0.549, 0.746, 0.900, 0.833, 0.659) | 0.498 (0.201 to 0.776) | 0.553 | 0.799 |
| FRLL Webmorph native | 0.999 [0.998, 1.000] (0.995, 1.000, 1.000, 1.000, 1.000) | 0.523 (0.321 to 0.785) | 0.722 | 0.785 |
| FRLL Webmorph E7 (history-matched) | 0.967 [0.956, 0.976] (0.874, 0.993, 0.970, 1.000, 0.996) | 0.522 (0.296 to 0.793) | 0.748 | 0.793 |
| corrected MAD22 FaceMorpher native | 1.000 [1.000, 1.000] (1.000, 1.000, 1.000, 1.000, 1.000) | 0.469 (0.307 to 0.782) | 0.579 | 0.782 |
| corrected MAD22 FaceMorpher E7 (history-matched) | 1.000 [1.000, 1.000] (1.000, 1.000, 1.000, 1.000, 1.000) | 0.468 (0.237 to 0.793) | 0.659 | 0.793 |
| corrected MAD22 MIPGAN-I native | 0.182 [0.159, 0.205] (0.017, 0.326, 0.069, 0.438, 0.062) | 0.487 (0.204 to 0.736) | 0.400 | 0.796 |
| corrected MAD22 MIPGAN-I E7 (history-matched) | 0.182 [0.159, 0.205] (0.017, 0.326, 0.069, 0.438, 0.062) | 0.487 (0.204 to 0.736) | 0.400 | 0.796 |
| corrected MAD22 MIPGAN-II native | 0.194 [0.173, 0.216] (0.021, 0.375, 0.090, 0.410, 0.074) | 0.541 (0.253 to 0.776) | 0.442 | 0.776 |
| corrected MAD22 MIPGAN-II E7 (history-matched) | 0.194 [0.173, 0.216] (0.021, 0.375, 0.090, 0.410, 0.074) | 0.541 (0.253 to 0.776) | 0.442 | 0.776 |
| corrected MAD22 OpenCV native | 0.723 [0.681, 0.764] (0.781, 0.697, 0.855, 0.560, 0.723) | 0.513 (0.361 to 0.620) | 0.492 | 0.639 |
| corrected MAD22 OpenCV E7 (history-matched) | 0.692 [0.647, 0.735] (0.737, 0.673, 0.827, 0.532, 0.691) | 0.512 (0.360 to 0.621) | 0.495 | 0.640 |
| corrected MAD22 Webmorph native | 0.818 [0.784, 0.849] (0.828, 0.763, 0.871, 0.749, 0.878) | 0.536 (0.378 to 0.649) | 0.620 | 0.649 |
| corrected MAD22 Webmorph E7 (history-matched) | 0.787 [0.751, 0.822] (0.786, 0.738, 0.840, 0.722, 0.849) | 0.536 (0.374 to 0.649) | 0.624 | 0.649 |

## Table 3a. Fixed threshold "0.5 rule": flag rate (genuine photos flagged) and miss rate (morphs not flagged), %, our frames, CLIP ViT-B/16 with LoRA (M3)

Threshold pool: none (score at least 0.5). Arm means; per-seed miss rates in brackets.

Flag: not reproduced on this stack (see top).

| cell | morph-free flag / miss (per-seed miss) | label-permuted flag / miss | untrained flag / miss |
|---|---|---|---|
| MorDIFF native | 0.0 / 64.5 (4.1, 82.7, 60.8, 76.7, 98.4) | 57.4 / 43.4 | 67.6 / 39.3 |
| MorDIFF E7 (history-matched) | 0.5 / 64.5 (4.1, 82.7, 60.8, 76.7, 98.4) | 60.8 / 43.4 | 54.4 / 39.3 |
| DiM-A native | 0.0 / 97.9 (89.8, 100.0, 99.8, 100.0, 100.0) | 48.6 / 46.4 | 46.1 / 55.8 |
| DiM-A E7 (history-matched) | 3.6 / 97.9 (89.8, 100.0, 99.8, 100.0, 100.0) | 48.4 / 46.4 | 33.8 / 55.8 |
| DiM-C native | 0.0 / 86.4 (33.6, 100.0, 98.4, 100.0, 100.0) | 48.6 / 47.6 | 46.1 / 52.0 |
| DiM-C E7 (history-matched) | 3.7 / 86.4 (33.6, 100.0, 98.4, 100.0, 100.0) | 48.1 / 47.6 | 33.3 / 52.0 |
| Fast-DiM native | 0.0 / 98.8 (94.2, 100.0, 100.0, 100.0, 100.0) | 48.6 / 48.7 | 46.1 / 54.8 |
| Fast-DiM E7 (history-matched) | 3.6 / 98.8 (94.2, 100.0, 100.0, 100.0, 100.0) | 47.8 / 48.7 | 33.3 / 54.8 |
| Fast-DiM-ODE native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.6 / 46.2 | 46.1 / 60.3 |
| Fast-DiM-ODE E7 (history-matched) | 3.9 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.1 / 46.2 | 33.3 / 60.3 |
| Greedy-DiM native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.6 / 50.2 | 46.1 / 69.4 |
| Greedy-DiM E7 (history-matched) | 3.2 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.3 / 50.2 | 33.8 / 69.4 |
| Greedy-DiM-S native | 0.0 / 97.7 (89.6, 100.0, 99.2, 99.6, 100.0) | 48.6 / 48.4 | 46.1 / 63.4 |
| Greedy-DiM-S E7 (history-matched) | 3.3 / 97.7 (89.6, 100.0, 99.2, 99.6, 100.0) | 48.5 / 48.4 | 34.3 / 63.4 |
| FRLL AMSL native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.6 / 50.2 | 46.1 / 31.9 |
| FRLL AMSL E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.8 / 50.2 | 41.2 / 31.9 |
| FRLL FaceMorpher native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.6 / 46.0 | 46.1 / 24.1 |
| FRLL FaceMorpher E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 49.1 / 46.0 | 42.2 / 24.1 |
| FRLL OpenCV native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.6 / 45.1 | 46.1 / 27.2 |
| FRLL OpenCV E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 49.0 / 45.1 | 41.7 / 27.2 |
| FRLL StyleGAN native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.6 / 45.6 | 46.1 / 48.0 |
| FRLL StyleGAN E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.6 / 45.6 | 46.1 / 48.0 |
| FRLL Webmorph native | 0.0 / 100.0 (99.9, 100.0, 100.0, 100.0, 100.0) | 48.6 / 49.2 | 46.1 / 22.9 |
| FRLL Webmorph E7 (history-matched) | 0.0 / 100.0 (99.9, 100.0, 100.0, 100.0, 100.0) | 49.2 / 49.2 | 41.7 / 22.9 |
| corrected MAD22 FaceMorpher native | 0.0 / 4.3 (0.0, 3.3, 3.3, 1.6, 13.1) | 48.6 / 54.9 | 46.1 / 43.5 |
| corrected MAD22 FaceMorpher E7 (history-matched) | 5.5 / 4.3 (0.0, 3.3, 3.3, 1.6, 13.1) | 48.3 / 54.9 | 32.4 / 43.5 |
| corrected MAD22 MIPGAN-I native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.6 / 50.7 | 46.1 / 71.0 |
| corrected MAD22 MIPGAN-I E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.6 / 50.7 | 46.1 / 71.0 |
| corrected MAD22 MIPGAN-II native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.6 / 46.2 | 46.1 / 67.9 |
| corrected MAD22 MIPGAN-II E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.6 / 46.2 | 46.1 / 67.9 |
| corrected MAD22 OpenCV native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.6 / 51.3 | 46.1 / 55.9 |
| corrected MAD22 OpenCV E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.8 / 51.3 | 45.6 / 55.9 |
| corrected MAD22 Webmorph native | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 48.6 / 50.3 | 46.1 / 38.0 |
| corrected MAD22 Webmorph E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0, 100.0, 100.0, 100.0) | 49.0 / 50.3 | 45.6 / 38.0 |

## Table 3b. Fixed threshold "FRLL-5%": flag rate (genuine photos flagged) and miss rate (morphs not flagged), %, our frames, CLIP ViT-B/16 with LoRA (M3)

Threshold pool: 204 unprocessed FRLL genuine photos, at most 10 flagged. Arm means; per-seed miss rates in brackets.

Flag: not reproduced on this stack (see top).

| cell | morph-free flag / miss (per-seed miss) | label-permuted flag / miss | untrained flag / miss |
|---|---|---|---|
| MorDIFF native | 50.7 / 0.0 (0.0, 0.0, 0.0, 0.0, 0.0) | 9.4 / 86.7 | 11.8 / 96.6 |
| MorDIFF E7 (history-matched) | 100.0 / 0.0 (0.0, 0.0, 0.0, 0.0, 0.0) | 8.7 / 86.7 | 3.4 / 96.6 |
| DiM-A native | 4.9 / 0.1 (0.2, 0.2, 0.0, 0.0, 0.0) | 4.9 / 88.9 | 4.9 / 100.0 |
| DiM-A E7 (history-matched) | 100.0 / 0.1 (0.2, 0.2, 0.0, 0.0, 0.0) | 4.3 / 88.9 | 1.0 / 100.0 |
| DiM-C native | 4.9 / 0.0 (0.0, 0.0, 0.0, 0.0, 0.0) | 4.9 / 91.8 | 4.9 / 100.0 |
| DiM-C E7 (history-matched) | 100.0 / 0.0 (0.0, 0.0, 0.0, 0.0, 0.0) | 4.0 / 91.8 | 1.0 / 100.0 |
| Fast-DiM native | 4.9 / 0.5 (0.4, 0.8, 0.0, 0.0, 1.4) | 4.9 / 91.5 | 4.9 / 99.8 |
| Fast-DiM E7 (history-matched) | 100.0 / 0.5 (0.4, 0.8, 0.0, 0.0, 1.4) | 4.2 / 91.5 | 1.0 / 99.8 |
| Fast-DiM-ODE native | 4.9 / 3.9 (10.8, 0.4, 3.0, 0.0, 5.4) | 4.9 / 89.4 | 4.9 / 99.8 |
| Fast-DiM-ODE E7 (history-matched) | 100.0 / 3.9 (10.8, 0.4, 3.0, 0.0, 5.4) | 3.9 / 89.4 | 1.0 / 99.8 |
| Greedy-DiM native | 4.9 / 4.1 (20.4, 0.0, 0.0, 0.0, 0.0) | 4.9 / 94.3 | 4.9 / 100.0 |
| Greedy-DiM E7 (history-matched) | 100.0 / 4.1 (20.4, 0.0, 0.0, 0.0, 0.0) | 3.9 / 94.3 | 1.0 / 100.0 |
| Greedy-DiM-S native | 4.9 / 0.4 (2.0, 0.0, 0.0, 0.0, 0.2) | 4.9 / 93.2 | 4.9 / 100.0 |
| Greedy-DiM-S E7 (history-matched) | 100.0 / 0.4 (2.0, 0.0, 0.0, 0.0, 0.2) | 4.2 / 93.2 | 1.0 / 100.0 |
| FRLL AMSL native | 4.9 / 0.6 (2.8, 0.0, 0.0, 0.0, 0.0) | 4.9 / 91.8 | 4.9 / 92.8 |
| FRLL AMSL E7 (history-matched) | 45.2 / 0.6 (2.8, 0.0, 0.0, 0.0, 0.0) | 4.3 / 91.8 | 2.5 / 92.8 |
| FRLL FaceMorpher native | 4.9 / 5.1 (21.5, 2.8, 0.8, 0.0, 0.2) | 4.9 / 90.0 | 4.9 / 90.3 |
| FRLL FaceMorpher E7 (history-matched) | 26.0 / 5.1 (21.5, 2.8, 0.8, 0.0, 0.2) | 4.5 / 90.0 | 3.4 / 90.3 |
| FRLL OpenCV native | 4.9 / 43.4 (88.0, 58.5, 28.5, 11.3, 30.5) | 4.9 / 88.2 | 4.9 / 93.5 |
| FRLL OpenCV E7 (history-matched) | 29.7 / 43.4 (88.0, 58.5, 28.5, 11.3, 30.5) | 4.6 / 88.2 | 2.9 / 93.5 |
| FRLL StyleGAN native | 4.9 / 69.6 (87.2, 68.8, 38.5, 68.5, 84.8) | 4.9 / 90.7 | 4.9 / 100.0 |
| FRLL StyleGAN E7 (history-matched) | 4.9 / 69.6 (87.2, 68.8, 38.5, 68.5, 84.8) | 4.9 / 90.7 | 4.9 / 100.0 |
| FRLL Webmorph native | 4.9 / 0.3 (1.3, 0.0, 0.0, 0.0, 0.0) | 4.9 / 92.2 | 4.9 / 85.8 |
| FRLL Webmorph E7 (history-matched) | 45.1 / 0.3 (1.3, 0.0, 0.0, 0.0, 0.0) | 4.5 / 92.2 | 2.9 / 85.8 |
| corrected MAD22 FaceMorpher native | 5.1 / 0.0 (0.0, 0.0, 0.0, 0.0, 0.0) | 4.9 / 92.9 | 4.9 / 97.8 |
| corrected MAD22 FaceMorpher E7 (history-matched) | 100.0 / 0.0 (0.0, 0.0, 0.0, 0.0, 0.0) | 4.3 / 92.9 | 1.0 / 97.8 |
| corrected MAD22 MIPGAN-I native | 5.1 / 99.7 (100.0, 98.8, 99.9, 99.9, 100.0) | 4.9 / 92.1 | 4.9 / 100.0 |
| corrected MAD22 MIPGAN-I E7 (history-matched) | 5.1 / 99.7 (100.0, 98.8, 99.9, 99.9, 100.0) | 4.9 / 92.1 | 4.9 / 100.0 |
| corrected MAD22 MIPGAN-II native | 5.1 / 99.7 (100.0, 98.8, 99.9, 100.0, 100.0) | 4.9 / 91.8 | 4.9 / 100.0 |
| corrected MAD22 MIPGAN-II E7 (history-matched) | 5.1 / 99.7 (100.0, 98.8, 99.9, 100.0, 100.0) | 4.9 / 91.8 | 4.9 / 100.0 |
| corrected MAD22 OpenCV native | 5.1 / 74.9 (64.2, 85.0, 53.9, 97.0, 74.7) | 4.9 / 94.6 | 4.9 / 98.5 |
| corrected MAD22 OpenCV E7 (history-matched) | 8.2 / 74.9 (64.2, 85.0, 53.9, 97.0, 74.7) | 4.7 / 94.6 | 4.9 / 98.5 |
| corrected MAD22 Webmorph native | 5.1 / 67.4 (52.6, 90.0, 54.8, 89.8, 50.0) | 4.9 / 91.2 | 4.9 / 93.2 |
| corrected MAD22 Webmorph E7 (history-matched) | 8.4 / 67.4 (52.6, 90.0, 54.8, 89.8, 50.0) | 4.6 / 91.2 | 4.9 / 93.2 |

## Table 4. Training accuracy (threshold 0.5, no TTA), CLIP ViT-B/16 with LoRA (M3)

Flag: not reproduced on this stack (see top).

| network | arm | own training labels: accuracy / AUC | true labels: accuracy / AUC | share of labels permuted | train hours |
|---|---|---|---|---|---|
| `AD4_m3mf_s401` | morph-free | 1.0 / 1.0 | 1.0 / 1.0 | 0.0 | 0.8719861990875668 |
| `AD4_m3mf_s402` | morph-free | 1.0 / 1.0 | 1.0 / 1.0 | 0.0 | 0.8721523830625746 |
| `AD4_m3mf_s403` | morph-free | 1.0 / 1.0 | 1.0 / 1.0 | 0.0 | 0.8679078467686971 |
| `AD4_m3mf_s404` | morph-free | 1.0 / 1.0 | 1.0 / 1.0 | 0.0 | 0.8676792309019301 |
| `AD4_m3mf_s405` | morph-free | 1.0 / 1.0 | 1.0 / 1.0 | 0.0 | 0.8696686667866177 |
| `AD4_m3perm_s401` | label-permuted | 0.5196 / 0.5236 | 0.6086 / 0.6439 | 0.4986 | 1.2499128421147665 |
| `AD4_m3perm_s402` | label-permuted | 0.5154 / 0.5219 | 0.6185 / 0.6648 | 0.4988 | 1.264921070403523 |
| `AD4_m3perm_s403` | label-permuted | 0.5142 / 0.521 | 0.6859 / 0.7466 | 0.4984 | 1.2374028712511063 |
| `AD4_m3perm_s404` | label-permuted | 0.5167 / 0.5229 | 0.6321 / 0.6626 | 0.4978 | 1.249528352684445 |
| `AD4_m3perm_s405` | label-permuted | 0.5117 / 0.5179 | 0.3991 / 0.3659 | 0.5016 | 1.2391860406266317 |
| `AD4_m3zero_s401` | untrained | 0.2953 / 0.227 | 0.2953 / 0.227 | 0.0 | None |
