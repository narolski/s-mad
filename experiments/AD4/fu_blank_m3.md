**H-new-3 (post hoc follow-up): incomplete (2 of 5).** Blanked MorDIFF history-matched, morph-free seed mean EER 8.1% over 2 networks that passed the unblanked-score gate (per seed 2.9, 13.2); rule: above 15% supported, at most 5% falsified. Flag on the networks: not reproduced on this stack. The 'passable' and 'A1' columns apply the AD4 rule to blanked images descriptively; they are not the registered AD4 verdicts.

# Morph-free networks (AD4), CLIP ViT-B/16 with LoRA (M3): border-blanked re-score (H-new-3, post hoc follow-up), our frames with everything outside the fixed face ellipse set to grey

Status: **incomplete (2 of 5 morph-free networks): descriptive rows only**. All numbers on our frames (our alignment of every benchmark). EER in %, signed AUC (morph positive). 95% intervals: person bootstrap (Amendment 2 (a)), descriptive; the verdicts use point values.

Networks (arm, seed, platform and card):
- morph-free seed 402 (`AD4_m3mf_s402`): DGX, NVIDIA GB10, blanked (Amendment 4b)
- morph-free seed 403 (`AD4_m3mf_s403`): DGX, NVIDIA GB10, blanked (Amendment 4b)
- label-permuted seed 401 (`AD4_m3perm_s401`): DGX, NVIDIA GB10, blanked (Amendment 4b)
- label-permuted seed 402 (`AD4_m3perm_s402`): DGX, NVIDIA GB10, blanked (Amendment 4b)
- label-permuted seed 403 (`AD4_m3perm_s403`): DGX, NVIDIA GB10, blanked (Amendment 4b)
- label-permuted seed 404 (`AD4_m3perm_s404`): DGX, NVIDIA GB10, blanked (Amendment 4b)
- label-permuted seed 405 (`AD4_m3perm_s405`): DGX, NVIDIA GB10, blanked (Amendment 4b)
- untrained seed 401 (`AD4_m3zero_s401`): DGX, NVIDIA GB10, blanked (Amendment 4b)
- morph-free: seeds 401, 404, 405 not present

## Table 1. EER per cell (%), our frames, CLIP ViT-B/16 with LoRA (M3)

| cell | role | morph-free: mean [95% CI] (per seed) | label-permuted: mean (range) | untrained | lowest reference | margin = morph-free mean minus lowest reference [95% CI] | passable without morphs | seeds meeting margin | seeds above 15% | A1 | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MorDIFF native | primary | 0.0 [0.0, 0.0] (0.0, 0.0) | 45.8 (35.7 to 53.9), n=5 | 44.6 | 35.7 | -35.7 [-38.7, -30.8] | incomplete (2 of 5) | 2/2 | 0/2 | incomplete (2 of 5) |  |
| MorDIFF E7 (history-matched) | descriptive | 8.1 [5.3, 10.8] (2.9, 13.2) | 45.9 (34.9 to 51.4), n=5 | 35.3 | 34.9 | -26.8 [-32.0, -20.9] | incomplete (2 of 5) | 2/2 | 0/2 | incomplete (2 of 5) |  |
| DiM-A native | secondary | 2.5 [0.9, 4.2] (2.0, 3.0) | 46.1 (32.9 to 54.0), n=5 | 49.6 | 32.9 | -30.4 [-36.0, -24.5] | incomplete (2 of 5) | 2/2 | 0/2 | incomplete (2 of 5) |  |
| DiM-A E7 (history-matched) | descriptive | 52.3 [47.5, 56.6] (52.4, 52.1) | 45.5 (40.2 to 52.9), n=5 | 41.6 | 40.2 | 12.1 [7.4, 20.0] | incomplete (2 of 5) | 0/2 | 2/2 | incomplete (2 of 5) |  |
| DiM-C native | secondary | 0.5 [0.0, 1.1] (0.1, 0.9) | 46.6 (36.3 to 54.5), n=5 | 44.5 | 36.3 | -35.8 [-39.0, -29.6] | incomplete (2 of 5) | 2/2 | 0/2 | incomplete (2 of 5) |  |
| DiM-C E7 (history-matched) | descriptive | 12.2 [8.6, 16.3] (9.3, 15.2) | 45.8 (34.4 to 51.5), n=5 | 36.8 | 34.4 | -22.1 [-28.0, -16.4] | incomplete (2 of 5) | 2/2 | 1/2 | incomplete (2 of 5) |  |
| Fast-DiM native | secondary | 2.2 [0.9, 4.4] (1.4, 3.0) | 45.9 (32.8 to 54.4), n=5 | 45.7 | 32.8 | -30.6 [-35.8, -24.6] | incomplete (2 of 5) | 2/2 | 0/2 | incomplete (2 of 5) |  |
| Fast-DiM E7 (history-matched) | descriptive | 38.9 [33.3, 43.3] (33.3, 44.6) | 45.8 (39.1 to 54.4), n=5 | 37.8 | 37.8 | 1.2 [-4.8, 7.8] | incomplete (2 of 5) | 0/2 | 2/2 | incomplete (2 of 5) |  |
| Fast-DiM-ODE native | secondary | 5.9 [3.7, 9.1] (2.1, 9.8) | 44.4 (31.9 to 53.5), n=5 | 50.5 | 31.9 | -25.9 [-31.4, -19.8] | incomplete (2 of 5) | 2/2 | 0/2 | incomplete (2 of 5) |  |
| Fast-DiM-ODE E7 (history-matched) | descriptive | 48.5 [44.4, 52.3] (37.7, 59.3) | 43.7 (37.2 to 51.9), n=5 | 40.7 | 37.2 | 11.3 [6.6, 18.0] | incomplete (2 of 5) | 0/2 | 2/2 | incomplete (2 of 5) |  |
| Greedy-DiM native | secondary | 1.0 [0.0, 2.0] (0.0, 2.0) | 47.0 (32.8 to 55.9), n=5 | 54.0 | 32.8 | -31.8 [-36.9, -26.8] | incomplete (2 of 5) | 2/2 | 0/2 | incomplete (2 of 5) |  |
| Greedy-DiM E7 (history-matched) | descriptive | 21.3 [18.0, 24.9] (2.4, 40.2) | 46.8 (36.2 to 55.4), n=5 | 44.7 | 36.2 | -14.9 [-20.6, -8.0] | incomplete (2 of 5) | 1/2 | 1/2 | incomplete (2 of 5) |  |
| Greedy-DiM-S native | secondary | 0.9 [0.0, 2.1] (0.4, 1.4) | 46.7 (35.8 to 55.8), n=5 | 52.0 | 35.8 | -34.9 [-39.3, -29.3] | incomplete (2 of 5) | 2/2 | 0/2 | incomplete (2 of 5) |  |
| Greedy-DiM-S E7 (history-matched) | descriptive | 17.4 [13.9, 21.4] (10.8, 24.0) | 45.7 (37.8 to 56.3), n=5 | 42.6 | 37.8 | -20.4 [-26.2, -14.4] | incomplete (2 of 5) | 2/2 | 1/2 | incomplete (2 of 5) |  |
| FRLL AMSL native | descriptive | 3.2 [1.6, 5.2] (2.0, 4.4) | 46.1 (32.4 to 55.4), n=5 | 45.6 | 32.4 | -29.2 [-35.0, -24.8] | incomplete (2 of 5) | 2/2 | 0/2 | incomplete (2 of 5) |  |
| FRLL AMSL E7 (history-matched) | descriptive | 13.0 [8.8, 16.4] (10.3, 15.6) | 46.1 (31.4 to 55.9), n=5 | 42.1 | 31.4 | -18.4 [-25.3, -12.7] | incomplete (2 of 5) | 2/2 | 1/2 | incomplete (2 of 5) |  |
| FRLL FaceMorpher native | descriptive | 6.1 [3.6, 9.6] (6.8, 5.4) | 46.9 (31.8 to 55.4), n=5 | 42.6 | 31.8 | -25.7 [-31.5, -20.5] | incomplete (2 of 5) | 2/2 | 0/2 | incomplete (2 of 5) |  |
| FRLL FaceMorpher E7 (history-matched) | descriptive | 12.3 [8.1, 16.6] (14.2, 10.3) | 47.0 (30.9 to 55.9), n=5 | 40.2 | 30.9 | -18.6 [-25.5, -12.5] | incomplete (2 of 5) | 2/2 | 0/2 | incomplete (2 of 5) |  |
| FRLL OpenCV native | descriptive | 11.2 [6.8, 15.2] (15.7, 6.7) | 47.3 (31.9 to 53.9), n=5 | 41.7 | 31.9 | -20.6 [-27.9, -14.9] | incomplete (2 of 5) | 2/2 | 1/2 | incomplete (2 of 5) |  |
| FRLL OpenCV E7 (history-matched) | descriptive | 20.2 [14.4, 26.3] (25.6, 14.7) | 47.6 (30.9 to 54.4), n=5 | 39.1 | 30.9 | -10.7 [-18.8, -2.9] | incomplete (2 of 5) | 1/2 | 1/2 | incomplete (2 of 5) |  |
| FRLL StyleGAN native | descriptive | 16.2 [10.8, 21.4] (18.2, 14.2) | 50.3 (30.5 to 68.6), n=5 | 45.6 | 30.5 | -14.3 [-20.9, -7.1] | incomplete (2 of 5) | 2/2 | 1/2 | incomplete (2 of 5) |  |
| FRLL StyleGAN E7 (history-matched) | descriptive | 16.2 [10.8, 21.4] (18.2, 14.2) | 50.3 (30.5 to 68.6), n=5 | 45.6 | 30.5 | -14.3 [-20.9, -7.1] | incomplete (2 of 5) | 2/2 | 1/2 | incomplete (2 of 5) | E7 not applicable |
| FRLL Webmorph native | descriptive | 8.3 [5.3, 11.4] (4.9, 11.7) | 45.7 (35.8 to 51.6), n=5 | 43.6 | 35.8 | -27.5 [-33.0, -21.6] | incomplete (2 of 5) | 2/2 | 0/2 | incomplete (2 of 5) |  |
| FRLL Webmorph E7 (history-matched) | descriptive | 22.8 [18.1, 26.9] (17.6, 28.0) | 45.7 (33.8 to 52.5), n=5 | 40.2 | 33.8 | -11.0 [-18.1, -4.7] | incomplete (2 of 5) | 1/2 | 2/2 | incomplete (2 of 5) |  |
| corrected MAD22 FaceMorpher native | descriptive | 0.0 [0.0, 0.0] (0.0, 0.0) | 53.4 (50.0 to 55.9), n=5 | 66.1 | 50.0 | -50.0 [-52.0, -44.3] | incomplete (2 of 5) | 2/2 | 0/2 | incomplete (2 of 5) |  |
| corrected MAD22 FaceMorpher E7 (history-matched) | descriptive | 3.2 [1.5, 5.4] (0.5, 5.9) | 53.0 (44.6 to 58.3), n=5 | 60.3 | 44.6 | -41.4 [-47.8, -35.6] | incomplete (2 of 5) | 2/2 | 0/2 | incomplete (2 of 5) |  |
| corrected MAD22 MIPGAN-I native | descriptive | 43.3 [39.1, 48.0] (45.0, 41.7) | 45.9 (36.8 to 60.9), n=5 | 43.1 | 36.8 | 6.6 [2.6, 14.3] | incomplete (2 of 5) | 0/2 | 2/2 | incomplete (2 of 5) |  |
| corrected MAD22 MIPGAN-I E7 (history-matched) | descriptive | 43.3 [39.1, 48.0] (45.0, 41.7) | 45.9 (36.8 to 60.9), n=5 | 43.1 | 36.8 | 6.6 [2.6, 14.3] | incomplete (2 of 5) | 0/2 | 2/2 | incomplete (2 of 5) | E7 not applicable |
| corrected MAD22 MIPGAN-II native | descriptive | 39.7 [35.6, 43.4] (40.7, 38.7) | 46.8 (34.7 to 63.2), n=5 | 43.2 | 34.7 | 5.0 [-0.7, 11.2] | incomplete (2 of 5) | 0/2 | 2/2 | incomplete (2 of 5) |  |
| corrected MAD22 MIPGAN-II E7 (history-matched) | descriptive | 39.7 [35.6, 43.4] (40.7, 38.7) | 46.8 (34.7 to 63.2), n=5 | 43.2 | 34.7 | 5.0 [-0.7, 11.2] | incomplete (2 of 5) | 0/2 | 2/2 | incomplete (2 of 5) | E7 not applicable |
| corrected MAD22 OpenCV native | descriptive | 23.2 [16.4, 28.0] (29.3, 17.2) | 49.9 (44.6 to 53.9), n=5 | 46.6 | 44.6 | -21.4 [-28.0, -14.9] | incomplete (2 of 5) | 2/2 | 2/2 | incomplete (2 of 5) |  |
| corrected MAD22 OpenCV E7 (history-matched) | descriptive | 24.3 [18.3, 30.2] (29.9, 18.6) | 50.0 (44.5 to 53.9), n=5 | 46.6 | 44.5 | -20.3 [-26.1, -12.5] | incomplete (2 of 5) | 2/2 | 2/2 | incomplete (2 of 5) | E7 partial (108/204 identical) |
| corrected MAD22 Webmorph native | descriptive | 28.1 [22.6, 34.3] (32.7, 23.5) | 48.9 (41.7 to 55.3), n=5 | 43.7 | 41.7 | -13.6 [-19.4, -4.9] | incomplete (2 of 5) | 1/2 | 2/2 | incomplete (2 of 5) |  |
| corrected MAD22 Webmorph E7 (history-matched) | descriptive | 29.9 [24.3, 36.8] (35.2, 24.6) | 48.6 (41.1 to 55.4), n=5 | 43.6 | 41.1 | -11.2 [-17.3, -2.4] | incomplete (2 of 5) | 1/2 | 2/2 | incomplete (2 of 5) | E7 partial (104/204 identical) |

## Table 2. Signed AUC per cell, our frames, CLIP ViT-B/16 with LoRA (M3)

| cell | morph-free: mean [95% CI] (per seed) | label-permuted: mean (range) | untrained | folded reference AUC, max |
|---|---|---|---|---|
| MorDIFF native | 1.000 [1.000, 1.000] (1.000, 1.000) | 0.547 (0.439 to 0.711) | 0.580 | 0.711 |
| MorDIFF E7 (history-matched) | 0.967 [0.950, 0.982] (0.994, 0.941) | 0.556 (0.484 to 0.682) | 0.684 | 0.684 |
| DiM-A native | 0.997 [0.993, 0.999] (0.999, 0.995) | 0.559 (0.455 to 0.754) | 0.493 | 0.754 |
| DiM-A E7 (history-matched) | 0.499 [0.447, 0.552] (0.482, 0.517) | 0.571 (0.462 to 0.655) | 0.603 | 0.655 |
| DiM-C native | 1.000 [1.000, 1.000] (1.000, 1.000) | 0.545 (0.438 to 0.713) | 0.556 | 0.713 |
| DiM-C E7 (history-matched) | 0.936 [0.905, 0.963] (0.955, 0.918) | 0.556 (0.487 to 0.683) | 0.665 | 0.683 |
| Fast-DiM native | 0.996 [0.991, 0.999] (0.999, 0.993) | 0.558 (0.453 to 0.748) | 0.535 | 0.748 |
| Fast-DiM E7 (history-matched) | 0.671 [0.615, 0.725] (0.731, 0.612) | 0.570 (0.457 to 0.648) | 0.641 | 0.648 |
| Fast-DiM-ODE native | 0.980 [0.966, 0.991] (0.998, 0.961) | 0.576 (0.455 to 0.759) | 0.495 | 0.759 |
| Fast-DiM-ODE E7 (history-matched) | 0.518 [0.469, 0.563] (0.664, 0.371) | 0.588 (0.459 to 0.666) | 0.605 | 0.666 |
| Greedy-DiM native | 0.999 [0.998, 1.000] (1.000, 0.999) | 0.537 (0.420 to 0.740) | 0.452 | 0.740 |
| Greedy-DiM E7 (history-matched) | 0.816 [0.784, 0.850] (0.993, 0.640) | 0.548 (0.427 to 0.658) | 0.566 | 0.658 |
| Greedy-DiM-S native | 1.000 [0.999, 1.000] (1.000, 0.999) | 0.547 (0.418 to 0.725) | 0.480 | 0.725 |
| Greedy-DiM-S E7 (history-matched) | 0.886 [0.849, 0.919] (0.942, 0.830) | 0.559 (0.423 to 0.631) | 0.592 | 0.631 |
| FRLL AMSL native | 0.994 [0.988, 0.998] (0.998, 0.990) | 0.563 (0.429 to 0.707) | 0.541 | 0.707 |
| FRLL AMSL E7 (history-matched) | 0.949 [0.923, 0.971] (0.969, 0.930) | 0.562 (0.425 to 0.731) | 0.588 | 0.731 |
| FRLL FaceMorpher native | 0.984 [0.972, 0.993] (0.985, 0.984) | 0.549 (0.424 to 0.725) | 0.583 | 0.725 |
| FRLL FaceMorpher E7 (history-matched) | 0.950 [0.922, 0.973] (0.944, 0.955) | 0.548 (0.422 to 0.741) | 0.614 | 0.741 |
| FRLL OpenCV native | 0.959 [0.934, 0.979] (0.936, 0.982) | 0.541 (0.453 to 0.725) | 0.598 | 0.725 |
| FRLL OpenCV E7 (history-matched) | 0.878 [0.830, 0.924] (0.824, 0.932) | 0.540 (0.450 to 0.743) | 0.631 | 0.743 |
| FRLL StyleGAN native | 0.920 [0.880, 0.956] (0.906, 0.935) | 0.509 (0.248 to 0.764) | 0.547 | 0.764 |
| FRLL StyleGAN E7 (history-matched) | 0.920 [0.880, 0.956] (0.906, 0.935) | 0.509 (0.248 to 0.764) | 0.547 | 0.764 |
| FRLL Webmorph native | 0.969 [0.950, 0.984] (0.992, 0.946) | 0.570 (0.484 to 0.674) | 0.560 | 0.674 |
| FRLL Webmorph E7 (history-matched) | 0.853 [0.811, 0.893] (0.914, 0.792) | 0.569 (0.480 to 0.699) | 0.607 | 0.699 |
| corrected MAD22 FaceMorpher native | 1.000 [1.000, 1.000] (1.000, 1.000) | 0.456 (0.403 to 0.518) | 0.257 | 0.743 |
| corrected MAD22 FaceMorpher E7 (history-matched) | 0.993 [0.986, 0.998] (1.000, 0.986) | 0.466 (0.398 to 0.569) | 0.369 | 0.631 |
| corrected MAD22 MIPGAN-I native | 0.596 [0.540, 0.648] (0.568, 0.623) | 0.567 (0.338 to 0.699) | 0.590 | 0.699 |
| corrected MAD22 MIPGAN-I E7 (history-matched) | 0.596 [0.540, 0.648] (0.568, 0.623) | 0.567 (0.338 to 0.699) | 0.590 | 0.699 |
| corrected MAD22 MIPGAN-II native | 0.643 [0.595, 0.691] (0.627, 0.659) | 0.558 (0.302 to 0.697) | 0.588 | 0.698 |
| corrected MAD22 MIPGAN-II E7 (history-matched) | 0.643 [0.595, 0.691] (0.627, 0.659) | 0.558 (0.302 to 0.697) | 0.588 | 0.698 |
| corrected MAD22 OpenCV native | 0.859 [0.801, 0.910] (0.801, 0.917) | 0.509 (0.449 to 0.567) | 0.527 | 0.567 |
| corrected MAD22 OpenCV E7 (history-matched) | 0.838 [0.778, 0.891] (0.774, 0.902) | 0.509 (0.452 to 0.569) | 0.533 | 0.569 |
| corrected MAD22 Webmorph native | 0.796 [0.736, 0.853] (0.730, 0.863) | 0.524 (0.430 to 0.601) | 0.559 | 0.601 |
| corrected MAD22 Webmorph E7 (history-matched) | 0.767 [0.706, 0.826] (0.695, 0.839) | 0.524 (0.431 to 0.604) | 0.565 | 0.604 |

## Table 3a. Fixed threshold "0.5 rule": flag rate (genuine photos flagged) and miss rate (morphs not flagged), %, our frames, CLIP ViT-B/16 with LoRA (M3)

Threshold pool: none (score at least 0.5). Arm means; per-seed miss rates in brackets.

| cell | morph-free flag / miss (per-seed miss) | label-permuted flag / miss | untrained flag / miss |
|---|---|---|---|
| MorDIFF native | 0.0 / 99.2 (99.9, 98.4) | 56.6 / 42.5 | 48.0 / 36.9 |
| MorDIFF E7 (history-matched) | 0.0 / 99.2 (99.9, 98.4) | 55.5 / 42.5 | 34.8 / 36.9 |
| DiM-A native | 0.0 / 99.9 (100.0, 99.8) | 55.1 / 42.0 | 46.6 / 51.8 |
| DiM-A E7 (history-matched) | 0.0 / 99.9 (100.0, 99.8) | 54.7 / 42.0 | 31.9 / 51.8 |
| DiM-C native | 0.0 / 99.2 (99.8, 98.6) | 55.1 / 43.3 | 46.6 / 42.8 |
| DiM-C E7 (history-matched) | 0.0 / 99.2 (99.8, 98.6) | 54.2 / 43.3 | 32.4 / 42.8 |
| Fast-DiM native | 0.0 / 100.0 (100.0, 100.0) | 55.1 / 42.1 | 46.6 / 45.2 |
| Fast-DiM E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0) | 54.2 / 42.1 | 32.4 / 45.2 |
| Fast-DiM-ODE native | 0.0 / 100.0 (100.0, 100.0) | 55.1 / 40.9 | 46.6 / 52.9 |
| Fast-DiM-ODE E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0) | 54.4 / 40.9 | 32.8 / 52.9 |
| Greedy-DiM native | 0.0 / 100.0 (100.0, 100.0) | 55.1 / 41.2 | 46.6 / 58.8 |
| Greedy-DiM E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0) | 54.5 / 41.2 | 32.4 / 58.8 |
| Greedy-DiM-S native | 0.0 / 99.7 (100.0, 99.4) | 55.1 / 41.9 | 46.6 / 55.0 |
| Greedy-DiM-S E7 (history-matched) | 0.0 / 99.7 (100.0, 99.4) | 54.5 / 41.9 | 31.9 / 55.0 |
| FRLL AMSL native | 0.0 / 100.0 (100.0, 100.0) | 55.1 / 41.2 | 46.6 / 45.3 |
| FRLL AMSL E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0) | 55.5 / 41.2 | 38.2 / 45.3 |
| FRLL FaceMorpher native | 0.0 / 100.0 (100.0, 100.0) | 55.1 / 42.6 | 46.6 / 39.2 |
| FRLL FaceMorpher E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0) | 55.6 / 42.6 | 41.7 / 39.2 |
| FRLL OpenCV native | 0.0 / 100.0 (100.0, 100.0) | 55.1 / 43.6 | 46.6 / 36.7 |
| FRLL OpenCV E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0) | 55.7 / 43.6 | 41.2 / 36.7 |
| FRLL StyleGAN native | 0.0 / 100.0 (100.0, 100.0) | 55.1 / 40.7 | 46.6 / 45.2 |
| FRLL StyleGAN E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0) | 55.1 / 40.7 | 46.6 / 45.2 |
| FRLL Webmorph native | 0.0 / 100.0 (100.0, 100.0) | 55.1 / 39.9 | 46.6 / 42.0 |
| FRLL Webmorph E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0) | 55.4 / 39.9 | 38.7 / 42.0 |
| corrected MAD22 FaceMorpher native | 0.0 / 32.1 (31.5, 32.8) | 55.1 / 50.5 | 46.6 / 87.6 |
| corrected MAD22 FaceMorpher E7 (history-matched) | 0.0 / 32.1 (31.5, 32.8) | 54.7 / 50.5 | 30.9 / 87.6 |
| corrected MAD22 MIPGAN-I native | 0.0 / 100.0 (100.0, 100.0) | 55.1 / 39.2 | 46.6 / 40.0 |
| corrected MAD22 MIPGAN-I E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0) | 55.1 / 39.2 | 46.6 / 40.0 |
| corrected MAD22 MIPGAN-II native | 0.0 / 100.0 (100.0, 100.0) | 55.1 / 40.2 | 46.6 / 40.2 |
| corrected MAD22 MIPGAN-II E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0) | 55.1 / 40.2 | 46.6 / 40.2 |
| corrected MAD22 OpenCV native | 0.0 / 100.0 (100.0, 100.0) | 55.1 / 43.7 | 46.6 / 47.6 |
| corrected MAD22 OpenCV E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0) | 55.2 / 43.7 | 45.6 / 47.6 |
| corrected MAD22 Webmorph native | 0.0 / 100.0 (100.0, 100.0) | 55.1 / 44.8 | 46.6 / 42.0 |
| corrected MAD22 Webmorph E7 (history-matched) | 0.0 / 100.0 (100.0, 100.0) | 55.2 / 44.8 | 46.1 / 42.0 |

## Table 3b. Fixed threshold "FRLL-5%": flag rate (genuine photos flagged) and miss rate (morphs not flagged), %, our frames, CLIP ViT-B/16 with LoRA (M3)

Threshold pool: 204 unprocessed FRLL genuine photos, at most 10 flagged. Arm means; per-seed miss rates in brackets.

| cell | morph-free flag / miss (per-seed miss) | label-permuted flag / miss | untrained flag / miss |
|---|---|---|---|
| MorDIFF native | 5.6 / 0.0 (0.0, 0.0) | 5.2 / 93.0 | 4.9 / 94.9 |
| MorDIFF E7 (history-matched) | 92.9 / 0.0 (0.0, 0.0) | 4.1 / 93.0 | 1.5 / 94.9 |
| DiM-A native | 4.9 / 1.0 (0.6, 1.4) | 4.9 / 92.6 | 4.9 / 98.4 |
| DiM-A E7 (history-matched) | 97.1 / 1.0 (0.6, 1.4) | 4.4 / 92.6 | 0.5 / 98.4 |
| DiM-C native | 4.9 / 0.0 (0.0, 0.0) | 4.9 / 94.1 | 4.9 / 97.8 |
| DiM-C E7 (history-matched) | 97.5 / 0.0 (0.0, 0.0) | 4.6 / 94.1 | 0.5 / 97.8 |
| Fast-DiM native | 4.9 / 1.5 (1.0, 2.0) | 4.9 / 93.6 | 4.9 / 97.2 |
| Fast-DiM E7 (history-matched) | 96.6 / 1.5 (1.0, 2.0) | 4.5 / 93.6 | 0.5 / 97.2 |
| Fast-DiM-ODE native | 4.9 / 7.9 (1.4, 14.4) | 4.9 / 93.4 | 4.9 / 98.6 |
| Fast-DiM-ODE E7 (history-matched) | 97.1 / 7.9 (1.4, 14.4) | 4.7 / 93.4 | 0.5 / 98.6 |
| Greedy-DiM native | 4.9 / 0.0 (0.0, 0.0) | 4.9 / 95.0 | 4.9 / 100.0 |
| Greedy-DiM E7 (history-matched) | 96.6 / 0.0 (0.0, 0.0) | 4.5 / 95.0 | 1.0 / 100.0 |
| Greedy-DiM-S native | 4.9 / 0.1 (0.0, 0.2) | 4.9 / 94.7 | 4.9 / 98.0 |
| Greedy-DiM-S E7 (history-matched) | 96.8 / 0.1 (0.0, 0.2) | 4.5 / 94.7 | 1.0 / 98.0 |
| FRLL AMSL native | 4.9 / 2.4 (0.9, 4.0) | 4.9 / 93.5 | 4.9 / 97.2 |
| FRLL AMSL E7 (history-matched) | 35.3 / 2.4 (0.9, 4.0) | 4.5 / 93.5 | 3.9 / 97.2 |
| FRLL FaceMorpher native | 4.9 / 8.4 (11.3, 5.6) | 4.9 / 93.8 | 4.9 / 96.7 |
| FRLL FaceMorpher E7 (history-matched) | 20.1 / 8.4 (11.3, 5.6) | 4.8 / 93.8 | 4.4 / 96.7 |
| FRLL OpenCV native | 4.9 / 18.8 (30.3, 7.4) | 4.9 / 94.2 | 4.9 / 95.2 |
| FRLL OpenCV E7 (history-matched) | 23.0 / 18.8 (30.3, 7.4) | 4.6 / 94.2 | 3.4 / 95.2 |
| FRLL StyleGAN native | 4.9 / 29.9 (36.3, 23.4) | 4.9 / 94.3 | 4.9 / 99.3 |
| FRLL StyleGAN E7 (history-matched) | 4.9 / 29.9 (36.3, 23.4) | 4.9 / 94.3 | 4.9 / 99.3 |
| FRLL Webmorph native | 4.9 / 12.6 (4.8, 20.4) | 4.9 / 93.7 | 4.9 / 98.2 |
| FRLL Webmorph E7 (history-matched) | 35.8 / 12.6 (4.8, 20.4) | 4.7 / 93.7 | 3.4 / 98.2 |
| corrected MAD22 FaceMorpher native | 5.1 / 0.0 (0.0, 0.0) | 4.9 / 98.2 | 4.9 / 100.0 |
| corrected MAD22 FaceMorpher E7 (history-matched) | 98.0 / 0.0 (0.0, 0.0) | 4.3 / 98.2 | 0.5 / 100.0 |
| corrected MAD22 MIPGAN-I native | 5.1 / 90.6 (92.3, 88.9) | 4.9 / 91.5 | 4.9 / 97.8 |
| corrected MAD22 MIPGAN-I E7 (history-matched) | 5.1 / 90.6 (92.3, 88.9) | 4.9 / 91.5 | 4.9 / 97.8 |
| corrected MAD22 MIPGAN-II native | 5.1 / 87.8 (88.7, 86.9) | 4.9 / 89.8 | 4.9 / 98.3 |
| corrected MAD22 MIPGAN-II E7 (history-matched) | 5.1 / 87.8 (88.7, 86.9) | 4.9 / 89.8 | 4.9 / 98.3 |
| corrected MAD22 OpenCV native | 5.1 / 41.2 (52.1, 30.2) | 4.9 / 94.5 | 4.9 / 97.0 |
| corrected MAD22 OpenCV E7 (history-matched) | 7.6 / 41.2 (52.1, 30.2) | 4.7 / 94.5 | 4.4 / 97.0 |
| corrected MAD22 Webmorph native | 5.1 / 60.1 (73.6, 46.6) | 4.9 / 93.7 | 4.9 / 96.8 |
| corrected MAD22 Webmorph E7 (history-matched) | 8.1 / 60.1 (73.6, 46.6) | 4.7 / 93.7 | 4.4 / 96.8 |

## Table 4. Training accuracy (threshold 0.5, no TTA), CLIP ViT-B/16 with LoRA (M3)

| network | arm | own training labels: accuracy / AUC | true labels: accuracy / AUC | share of labels permuted | train hours |
|---|---|---|---|---|---|
