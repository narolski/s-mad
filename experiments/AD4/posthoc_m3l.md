# Morph-free networks (AD4), CLIP ViT-L/14 with LoRA (M3L): post hoc addendum (Amendment 3), our frames

Descriptive readings asked for by the independent review after the numbers were seen; no verdict changes. In our preprocessing. The networks were trained only to flag shrink-and-enlarge copies of synthetic faces (no morph, no blending). 95% intervals: the registered person bootstrap.

## A. Floor logits

| network | training natives: p5 / median / p95 | training copies: p5 / median / p95 | FRLL-5% threshold (p; logit) |
|---|---|---|---|
| `AD4_m3lmf_s401` | -4.06 / -4.06 / -4.05 | 4.01 / 4.02 / 4.02 | 0.0194; -3.92 |
| `AD4_m3lmf_s402` | -4.07 / -4.07 / -4.06 | 4.02 / 4.02 / 4.03 | 0.0188; -3.96 |
| `AD4_m3lperm_s401` | -0.05 / -0.01 / 0.03 | -0.02 / 0.01 / 0.04 | 0.5075; 0.03 |
| `AD4_m3lperm_s402` | -0.04 / -0.00 / 0.04 | -0.03 / 0.01 / 0.05 | 0.5057; 0.02 |
| `AD4_m3lperm_s403` | -0.05 / 0.00 / 0.05 | -0.04 / -0.00 / 0.05 | 0.5072; 0.03 |
| `AD4_m3lperm_s404` | -0.06 / -0.01 / 0.03 | -0.03 / 0.01 / 0.04 | 0.5040; 0.02 |
| `AD4_m3lperm_s405` | -0.04 / 0.01 / 0.06 | -0.05 / -0.01 / 0.03 | 0.5122; 0.05 |
| `AD4_m3lzero_s401` | -0.01 / 0.01 / 0.03 | -0.01 / 0.01 / 0.02 | 0.5073; 0.03 |

Median logits on the evaluation cells, morph-free seeds 401 to 405 (morphs; the cell's genuine photos; the set's unprocessed genuine photos):

| cell | seed 401 | seed 402 | untrained |
|---|---|---|---|
| MorDIFF native | 1.31; -3.94; -3.94 | -2.53; -4.00; -4.00 | 0.01; 0.01; 0.01 |
| MorDIFF E7 (history-matched) | 1.31; -2.51; -3.94 | -2.53; -3.46; -4.00 | 0.01; 0.01; 0.01 |
| DiM-A native | -3.61; -3.99; -3.99 | -3.85; -4.01; -4.01 | 0.02; 0.01; 0.01 |
| DiM-A E7 (history-matched) | -3.61; -3.19; -3.99 | -3.85; -3.61; -4.01 | 0.02; 0.01; 0.01 |
| DiM-C native | -3.16; -3.99; -3.99 | -3.76; -4.01; -4.01 | 0.01; 0.01; 0.01 |
| DiM-C E7 (history-matched) | -3.16; -3.21; -3.99 | -3.76; -3.60; -4.01 | 0.01; 0.01; 0.01 |
| Fast-DiM native | -3.64; -3.99; -3.99 | -3.88; -4.01; -4.01 | 0.02; 0.01; 0.01 |
| Fast-DiM E7 (history-matched) | -3.64; -3.20; -3.99 | -3.88; -3.61; -4.01 | 0.02; 0.01; 0.01 |
| Fast-DiM-ODE native | -3.69; -3.99; -3.99 | -3.90; -4.01; -4.01 | 0.02; 0.01; 0.01 |
| Fast-DiM-ODE E7 (history-matched) | -3.69; -3.20; -3.99 | -3.90; -3.62; -4.01 | 0.02; 0.01; 0.01 |
| Greedy-DiM native | -3.74; -3.99; -3.99 | -3.85; -4.01; -4.01 | 0.01; 0.01; 0.01 |
| Greedy-DiM E7 (history-matched) | -3.74; -3.22; -3.99 | -3.85; -3.63; -4.01 | 0.01; 0.01; 0.01 |
| Greedy-DiM-S native | -3.45; -3.99; -3.99 | -3.79; -4.01; -4.01 | 0.02; 0.01; 0.01 |
| Greedy-DiM-S E7 (history-matched) | -3.45; -3.19; -3.99 | -3.79; -3.63; -4.01 | 0.02; 0.01; 0.01 |
| FRLL AMSL native | -3.79; -3.99; -3.99 | -3.90; -4.01; -4.01 | 0.02; 0.01; 0.01 |
| FRLL AMSL E7 (history-matched) | -3.79; -3.92; -3.99 | -3.90; -3.97; -4.01 | 0.02; 0.01; 0.01 |
| FRLL FaceMorpher native | -3.88; -3.99; -3.99 | -3.99; -4.01; -4.01 | 0.02; 0.01; 0.01 |
| FRLL FaceMorpher E7 (history-matched) | -3.88; -3.95; -3.99 | -3.99; -3.99; -4.01 | 0.02; 0.01; 0.01 |
| FRLL OpenCV native | -3.93; -3.99; -3.99 | -4.00; -4.01; -4.01 | 0.02; 0.01; 0.01 |
| FRLL OpenCV E7 (history-matched) | -3.93; -3.95; -3.99 | -4.00; -3.99; -4.01 | 0.02; 0.01; 0.01 |
| FRLL StyleGAN native | -4.00; -3.99; -3.99 | -4.04; -4.01; -4.01 | 0.02; 0.01; 0.01 |
| FRLL StyleGAN E7 (history-matched) | -4.00; -3.99; -3.99 | -4.04; -4.01; -4.01 | 0.02; 0.01; 0.01 |
| FRLL Webmorph native | -3.76; -3.99; -3.99 | -3.89; -4.01; -4.01 | 0.02; 0.01; 0.01 |
| FRLL Webmorph E7 (history-matched) | -3.76; -3.92; -3.99 | -3.89; -3.97; -4.01 | 0.02; 0.01; 0.01 |
| corrected MAD22 FaceMorpher native | -2.88; -3.99; -3.99 | -3.59; -4.01; -4.01 | 0.02; 0.01; 0.01 |
| corrected MAD22 FaceMorpher E7 (history-matched) | -2.88; -3.02; -3.99 | -3.59; -3.55; -4.01 | 0.02; 0.01; 0.01 |
| corrected MAD22 MIPGAN-I native | -4.02; -3.99; -3.99 | -4.05; -4.01; -4.01 | 0.01; 0.01; 0.01 |
| corrected MAD22 MIPGAN-I E7 (history-matched) | -4.02; -3.99; -3.99 | -4.05; -4.01; -4.01 | 0.01; 0.01; 0.01 |
| corrected MAD22 MIPGAN-II native | -4.03; -3.99; -3.99 | -4.05; -4.01; -4.01 | 0.01; 0.01; 0.01 |
| corrected MAD22 MIPGAN-II E7 (history-matched) | -4.03; -3.99; -3.99 | -4.05; -4.01; -4.01 | 0.01; 0.01; 0.01 |
| corrected MAD22 OpenCV native | -3.97; -3.99; -3.99 | -4.01; -4.01; -4.01 | 0.02; 0.01; 0.01 |
| corrected MAD22 OpenCV E7 (history-matched) | -3.97; -3.98; -3.99 | -4.01; -4.00; -4.01 | 0.02; 0.01; 0.01 |
| corrected MAD22 Webmorph native | -3.96; -3.99; -3.99 | -4.00; -4.01; -4.01 | 0.02; 0.01; 0.01 |
| corrected MAD22 Webmorph E7 (history-matched) | -3.96; -3.98; -3.99 | -4.00; -4.00; -4.01 | 0.02; 0.01; 0.01 |

## B. Flag rate of each set's own unprocessed genuine photos at the FRLL-5% threshold, with miss rates, %

| set | genuine flag rate: mean [95% CI] (per seed) | family: miss rate per seed |
|---|---|---|
| mordiff | 25.5 [22.1, 28.9] (39.2, 11.8) | MorDIFF 0.0, 0.0 |
| dim | 4.9 [2.9, 7.1] (4.9, 4.9) | DiM-A 0.0, 0.4; DiM-C 0.0, 0.4; Fast-DiM 0.0, 7.6; Fast-DiM-ODE 0.0, 6.2; Greedy-DiM 0.0, 0.8; Greedy-DiM-S 0.0, 0.4 |
| frllm | 4.9 [2.9, 7.1] (4.9, 4.9) | FRLL AMSL 0.0, 8.3; FRLL FaceMorpher 5.1, 96.5; FRLL OpenCV 58.9, 96.4; FRLL StyleGAN 99.5, 100.0; FRLL Webmorph 0.0, 4.0 |
| mad22c | 4.9 [2.9, 7.1] (4.9, 4.9) | corrected MAD22 FaceMorpher 0.0, 0.0; corrected MAD22 MIPGAN-I 99.2, 100.0; corrected MAD22 MIPGAN-II 100.0, 100.0; corrected MAD22 OpenCV 88.1, 96.8; corrected MAD22 Webmorph 96.4, 99.2 |

## C. File-size null per cell (score = smaller PNG file is more morph)

| cell | AUC [95% CI] | EER % [95% CI] | median KB morph / genuine | Spearman(network score, smaller file) per seed |
|---|---|---|---|---|
| MorDIFF native | 0.999 [0.997, 1.000] | 2.0 [0.6, 3.1] | 147 / 191 | 0.53, 0.63 |
| MorDIFF E7 (history-matched) | 0.686 [0.612, 0.757] | 36.3 [30.4, 42.1] | 147 / 153 | 0.29, 0.41 |
| DiM-A native | 0.964 [0.941, 0.982] | 10.9 [6.8, 15.5] | 262 / 353 | 0.69, 0.65 |
| DiM-A E7 (history-matched) | 0.441 [0.395, 0.487] | 54.5 [48.5, 58.3] | 262 / 257 | 0.24, 0.17 |
| DiM-C native | 0.992 [0.982, 0.998] | 4.4 [2.2, 7.4] | 246 / 353 | 0.67, 0.69 |
| DiM-C E7 (history-matched) | 0.650 [0.595, 0.708] | 36.8 [32.8, 41.8] | 246 / 258 | 0.13, 0.06 |
| Fast-DiM native | 0.952 [0.925, 0.974] | 12.8 [8.5, 18.0] | 266 / 353 | 0.75, 0.73 |
| Fast-DiM E7 (history-matched) | 0.382 [0.341, 0.419] | 57.8 [54.3, 61.6] | 266 / 258 | 0.40, 0.37 |
| Fast-DiM-ODE native | 0.862 [0.834, 0.891] | 22.6 [17.7, 25.9] | 294 / 353 | 0.59, 0.58 |
| Fast-DiM-ODE E7 (history-matched) | 0.103 [0.067, 0.137] | 83.8 [79.3, 87.7] | 294 / 258 | 0.56, 0.58 |
| Greedy-DiM native | 0.724 [0.687, 0.762] | 31.8 [27.9, 36.0] | 317 / 353 | 0.52, 0.45 |
| Greedy-DiM E7 (history-matched) | 0.037 [0.013, 0.066] | 92.2 [88.6, 95.4] | 317 / 258 | 0.72, 0.62 |
| Greedy-DiM-S native | 0.975 [0.956, 0.990] | 8.8 [4.5, 13.3] | 258 / 353 | 0.72, 0.74 |
| Greedy-DiM-S E7 (history-matched) | 0.478 [0.438, 0.518] | 50.9 [45.1, 54.2] | 258 / 258 | 0.24, 0.27 |
| FRLL AMSL native | 0.979 [0.965, 0.992] | 8.3 [4.4, 12.5] | 252 / 353 | -0.11, 0.03 |
| FRLL AMSL E7 (history-matched) | 0.893 [0.857, 0.927] | 18.6 [13.3, 22.7] | 252 / 304 | -0.18, -0.06 |
| FRLL FaceMorpher native | 0.998 [0.995, 1.000] | 2.5 [0.5, 4.1] | 234 / 353 | 0.45, 0.34 |
| FRLL FaceMorpher E7 (history-matched) | 0.985 [0.972, 0.995] | 6.9 [3.8, 10.0] | 234 / 318 | 0.41, 0.20 |
| FRLL OpenCV native | 0.947 [0.923, 0.969] | 13.3 [8.9, 17.7] | 273 / 353 | 0.37, 0.21 |
| FRLL OpenCV E7 (history-matched) | 0.821 [0.782, 0.861] | 25.5 [22.0, 29.9] | 273 / 313 | 0.22, 0.08 |
| FRLL StyleGAN native | 0.954 [0.931, 0.974] | 12.8 [8.3, 16.0] | 267 / 353 | 0.22, -0.05 |
| FRLL StyleGAN E7 (history-matched) | 0.954 [0.931, 0.974] | 12.8 [8.3, 16.0] | 267 / 353 | 0.22, -0.05 |
| FRLL Webmorph native | 0.955 [0.931, 0.978] | 12.8 [7.4, 17.6] | 267 / 353 | 0.13, 0.30 |
| FRLL Webmorph E7 (history-matched) | 0.803 [0.755, 0.853] | 27.0 [22.5, 30.9] | 267 / 303 | -0.01, 0.16 |
| corrected MAD22 FaceMorpher native | 1.000 [0.999, 1.000] | 0.5 [0.0, 1.5] | 212 / 353 | 0.39, 0.43 |
| corrected MAD22 FaceMorpher E7 (history-matched) | 0.930 [0.893, 0.961] | 12.7 [8.3, 18.0] | 212 / 254 | 0.05, -0.03 |
| corrected MAD22 MIPGAN-I native | 0.554 [0.525, 0.584] | 42.6 [39.5, 46.5] | 343 / 353 | 0.41, 0.24 |
| corrected MAD22 MIPGAN-I E7 (history-matched) | 0.554 [0.525, 0.584] | 42.6 [39.5, 46.5] | 343 / 353 | 0.41, 0.24 |
| corrected MAD22 MIPGAN-II native | 0.623 [0.591, 0.653] | 39.7 [35.8, 43.6] | 331 / 353 | 0.34, 0.17 |
| corrected MAD22 MIPGAN-II E7 (history-matched) | 0.623 [0.591, 0.653] | 39.7 [35.8, 43.6] | 331 / 353 | 0.34, 0.17 |
| corrected MAD22 OpenCV native | 0.700 [0.669, 0.728] | 36.8 [34.2, 39.6] | 321 / 353 | 0.39, 0.29 |
| corrected MAD22 OpenCV E7 (history-matched) | 0.658 [0.620, 0.692] | 37.3 [34.9, 40.7] | 321 / 344 | 0.38, 0.28 |
| corrected MAD22 Webmorph native | 0.768 [0.720, 0.814] | 30.8 [26.2, 35.3] | 303 / 353 | 0.42, 0.23 |
| corrected MAD22 Webmorph E7 (history-matched) | 0.728 [0.674, 0.777] | 32.4 [27.7, 36.8] | 303 / 343 | 0.38, 0.20 |

## D. Seed spread of the morph-free networks (no seed mean for reversed or split cells)

| cell | EER % per seed | AUC per seed | EER range | kind | EER mean |
|---|---|---|---|---|---|
| MorDIFF native | 0.0, 0.0 | 1.000, 1.000 | 0.0 | - | 0.0 |
| MorDIFF E7 (history-matched) | 2.0, 8.9 | 0.998, 0.973 | 6.9 | - | 5.4 |
| DiM-A native | 0.0, 2.4 | 1.000, 0.998 | 2.4 | - | 1.2 |
| DiM-A E7 (history-matched) | 80.3, 86.8 | 0.124, 0.063 | 6.5 | reversed | not printed |
| DiM-C native | 0.0, 1.1 | 1.000, 0.999 | 1.1 | - | 0.5 |
| DiM-C E7 (history-matched) | 47.5, 68.6 | 0.516, 0.233 | 21.1 | - | 58.0 |
| Fast-DiM native | 0.1, 6.9 | 1.000, 0.985 | 6.8 | - | 3.5 |
| Fast-DiM E7 (history-matched) | 79.4, 88.3 | 0.122, 0.050 | 8.9 | reversed | not printed |
| Fast-DiM-ODE native | 0.4, 5.9 | 1.000, 0.987 | 5.5 | - | 3.2 |
| Fast-DiM-ODE E7 (history-matched) | 87.3, 92.6 | 0.053, 0.023 | 5.3 | reversed | not printed |
| Greedy-DiM native | 0.0, 2.0 | 1.000, 0.999 | 2.0 | - | 1.0 |
| Greedy-DiM E7 (history-matched) | 91.2, 85.2 | 0.029, 0.073 | 5.9 | reversed | not printed |
| Greedy-DiM-S native | 0.0, 1.4 | 1.000, 0.999 | 1.4 | - | 0.7 |
| Greedy-DiM-S E7 (history-matched) | 65.6, 73.5 | 0.273, 0.192 | 7.8 | reversed | not printed |
| FRLL AMSL native | 0.0, 7.3 | 1.000, 0.986 | 7.3 | - | 3.7 |
| FRLL AMSL E7 (history-matched) | 8.3, 17.6 | 0.959, 0.901 | 9.3 | - | 13.0 |
| FRLL FaceMorpher native | 5.0, 35.8 | 0.988, 0.688 | 30.8 | wide | 20.4 |
| FRLL FaceMorpher E7 (history-matched) | 13.6, 50.0 | 0.936, 0.482 | 36.4 | wide | 31.8 |
| FRLL OpenCV native | 18.6, 45.6 | 0.897, 0.571 | 27.0 | - | 32.1 |
| FRLL OpenCV E7 (history-matched) | 37.3, 62.7 | 0.680, 0.318 | 25.5 | split | not printed |
| FRLL StyleGAN native | 57.3, 85.8 | 0.386, 0.056 | 28.5 | reversed | not printed |
| FRLL StyleGAN E7 (history-matched) | 57.3, 85.8 | 0.386, 0.056 | 28.5 | reversed | not printed |
| FRLL Webmorph native | 0.0, 4.0 | 1.000, 0.994 | 4.0 | - | 2.0 |
| FRLL Webmorph E7 (history-matched) | 6.5, 14.2 | 0.981, 0.934 | 7.8 | - | 10.3 |
| corrected MAD22 FaceMorpher native | 0.0, 0.0 | 1.000, 1.000 | 0.0 | - | 0.0 |
| corrected MAD22 FaceMorpher E7 (history-matched) | 44.6, 55.4 | 0.623, 0.440 | 10.8 | - | 50.0 |
| corrected MAD22 MIPGAN-I native | 72.0, 88.2 | 0.185, 0.042 | 16.2 | reversed | not printed |
| corrected MAD22 MIPGAN-I E7 (history-matched) | 72.0, 88.2 | 0.185, 0.042 | 16.2 | reversed | not printed |
| corrected MAD22 MIPGAN-II native | 80.4, 96.2 | 0.097, 0.008 | 15.8 | reversed | not printed |
| corrected MAD22 MIPGAN-II E7 (history-matched) | 80.4, 96.2 | 0.097, 0.008 | 15.8 | reversed | not printed |
| corrected MAD22 OpenCV native | 40.2, 51.5 | 0.674, 0.492 | 11.3 | - | 45.8 |
| corrected MAD22 OpenCV E7 (history-matched) | 42.7, 53.9 | 0.636, 0.457 | 11.3 | - | 48.3 |
| corrected MAD22 Webmorph native | 33.4, 42.1 | 0.724, 0.607 | 8.7 | - | 37.7 |
| corrected MAD22 Webmorph E7 (history-matched) | 36.2, 44.2 | 0.683, 0.570 | 7.9 | - | 40.2 |

## E. Label-permuted networks, training set (threshold 0.5, no TTA)

| network | own labels: accuracy / AUC | true labels: accuracy / AUC |
|---|---|---|
| `AD4_m3lperm_s401` | 0.516 / 0.525 | 0.683 / 0.742 |
| `AD4_m3lperm_s402` | 0.519 / 0.527 | 0.550 / 0.578 |
| `AD4_m3lperm_s403` | 0.518 / 0.526 | 0.471 / 0.471 |
| `AD4_m3lperm_s404` | 0.514 / 0.524 | 0.680 / 0.734 |
| `AD4_m3lperm_s405` | 0.518 / 0.524 | 0.357 / 0.306 |
