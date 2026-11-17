# Retrain cohorts — per-family EER (%) — S -> H (descriptive, insert-ready)

S = released weights (registered prod scoring, RS1 crops v1 primary / v2 secondary). H = our own retrains (labelled distinctly from released-weights rows), mean over 5 seeds +/- sd; same regen crops for S and H within the same variant. Metric: EER on logit_noTTA (final_metrics pin, as in the FRLL read). No verdict language.

| family (n morph , n genuine) | MADation B: S v1 -> H v1 (mean±sd) | MADation L: S v1 -> H v1 | MixFaceNet X: S v1 -> H v1 | v2 validation (B; L; X) |
|---|---|---|---|---|
| FRLL/amsl (2175, 204) | 3.92 -> 4.93±2.36 (k=5/5) | 7.95 -> 9.65±5.60 (k=5/5) | 15.13 -> 13.95±3.98 (k=5/5) | B 6.69±4.00; L 16.68±5.91; X 15.39±3.84 |
| FRLL/facemorpher (806, 204) | 0.62 -> 2.16±0.67 (k=5/5) | 0.87 -> 0.61±0.21 (k=5/5) | 4.41 -> 2.97±0.64 (k=5/5) | B 1.80±0.47; L 0.46±0.18; X 2.31±0.64 |
| FRLL/opencv (1211, 204) | 1.96 -> 4.90±0.77 (k=5/5) | 2.73 -> 0.82±0.23 (k=5/5) | 4.90 -> 3.91±1.53 (k=5/5) | B 3.53±0.86; L 0.57±0.15; X 3.88±1.34 |
| FRLL/stylegan (1222, 204) | 18.58 -> 14.56±4.19 (k=5/5) | 39.20 -> 12.75±1.94 (k=5/5) | 9.08 -> 11.27±3.28 (k=5/5) | B 14.90±4.03; L 12.69±2.36; X 12.06±3.51 |
| FRLL/webmorph (1221, 204) | 2.21 -> 4.12±2.26 (k=5/5) | 5.32 -> 5.81±3.46 (k=5/5) | 12.25 -> 9.95±3.52 (k=5/5) | B 4.73±3.12; L 8.59±3.60; X 10.90±3.95 |
| MAD22/FaceMorpher (1000, 408) | 0.10 -> 0.88±0.62 (k=5/5) | 0.49 -> 0.59±0.13 (k=5/5) | 5.00 -> 2.98±2.54 (k=5/5) | B 0.60±0.42; L 0.38±0.27; X 5.95±5.91 |
| MAD22/OpenCV (984, 408) | 5.18 -> 7.06±0.60 (k=5/5) | 4.78 -> 0.77±0.18 (k=5/5) | 10.16 -> 7.90±2.15 (k=5/5) | B 6.28±0.56; L 0.58±0.17; X 8.08±2.39 |
| MAD22/Webmorph (500, 408) | 11.52 -> 16.61±0.96 (k=5/5) | 26.72 -> 13.95±2.25 (k=5/5) | 20.00 -> 20.01±2.00 (k=5/5) | B 15.44±1.59; L 10.59±1.01; X 20.74±2.40 |
| MAD22/MIPGAN_I (1000, 408) | 40.69 -> 35.83±13.56 (k=5/5) | 30.80 -> 33.40±10.63 (k=5/5) | 18.50 -> 21.10±6.71 (k=5/5) | B 36.49±12.12; L 28.65±10.33; X 19.18±5.28 |
| MAD22/MIPGAN_II (999, 408) | 28.33 -> 27.40±9.44 (k=5/5) | 15.72 -> 19.94±9.99 (k=5/5) | 23.04 -> 27.41±6.46 (k=5/5) | B 27.05±8.81; L 17.17±9.11; X 24.87±6.55 |
| MAD22/DiM-MvM(dim_a) (500, 408) | 20.60 -> 21.43±8.16 (k=5/5) | 28.68 -> 30.26±5.12 (k=5/5) | 32.60 -> 36.02±3.51 (k=5/5) | B 20.57±8.33; L 31.11±4.02; X 38.13±2.98 |
| MAD22/DiM-MvM(dim_c) (500, 408) | 3.00 -> 5.90±3.92 (k=5/5) | 25.74 -> 19.05±1.01 (k=5/5) | 14.80 -> 14.39±2.24 (k=5/5) | B 5.74±4.27; L 19.41±1.05; X 15.37±1.85 |
| MAD22/DiM-LM2(fast_dim) (500, 408) | 20.10 -> 19.26±7.64 (k=5/5) | 30.15 -> 29.62±5.11 (k=5/5) | 32.40 -> 35.42±1.55 (k=5/5) | B 19.60±7.30; L 32.47±6.45; X 37.51±1.90 |
| MAD22/DiM-LM2-ODE(fast_dim_ode) (499, 408) | 28.26 -> 25.13±7.23 (k=5/5) | 20.59 -> 20.88±5.14 (k=5/5) | 42.65 -> 49.59±3.83 (k=5/5) | B 24.59±7.89; L 23.00±6.14; X 49.98±5.01 |
| MAD22/DiM-MI(greedy_dim) (500, 408) | 35.78 -> 38.97±17.17 (k=5/5) | 17.89 -> 16.22±2.71 (k=5/5) | 22.30 -> 26.42±7.63 (k=5/5) | B 39.11±17.12; L 18.06±4.02; X 27.74±7.86 |
| MAD22/DiM-MI-Semantic(greedy_dim_s) (500, 408) | 14.46 -> 18.97±9.51 (k=5/5) | 23.40 -> 17.50±2.76 (k=5/5) | 10.60 -> 11.44±1.48 (k=5/5) | B 18.85±9.02; L 15.84±2.72; X 11.93±1.18 |
| MAD22/MorDiff (945, 408) | 0.25 -> 0.39±0.34 (k=5/5) | 2.86 -> 1.94±0.52 (k=5/5) | 7.60 -> 13.80±17.92 (k=5/5) | B 1.45±1.34; L 14.31±5.05; X 9.22±1.78 |

## SelfMAD retrains (own preprocessing, own id space; 5/5 seeds — s405 completed 12:02:58Z 16 Nov)

| family (n) | s401 | s402 | s403 | s404 | s405 | mean±sd |
|---|---|---|---|---|---|---|
| FRLL/amsl | 2.45, 4.41, 7.35, 7.63, 7.17 | 5.80±2.28 |
| FRLL/facemorpher | 0.49, 0.98, 2.45, 1.55, 1.96 | 1.49±0.78 |
| FRLL/opencv | 0.16, 0.49, 1.39, 1.47, 1.15 | 0.93±0.58 |
| FRLL/stylegan | 18.99, 20.87, 22.55, 21.57, 22.50 | 21.29±1.47 |
| FRLL/webmorph | 6.86, 14.71, 20.59, 22.06, 24.41 | 17.72±7.05 |
| MAD22/FaceMorpher | n/a, n/a, n/a, n/a, n/a | n/a |
| MAD22/OpenCV | n/a, n/a, n/a, n/a, n/a | n/a |
| MAD22/Webmorph | n/a, n/a, n/a, n/a, n/a | n/a |
| MAD22/MIPGAN_I | n/a, n/a, n/a, n/a, n/a | n/a |
| MAD22/MIPGAN_II | n/a, n/a, n/a, n/a, n/a | n/a |
| MAD22/DiM-MvM(dim_a) | 33.00, 35.30, 37.85, 34.80, 35.80 | 35.35±1.75 |
| MAD22/DiM-MvM(dim_c) | 21.85, 20.60, 23.15, 21.40, 21.30 | 21.66±0.95 |
| MAD22/DiM-LM2(fast_dim) | 44.55, 44.20, 47.00, 44.75, 48.20 | 45.74±1.76 |
| MAD22/DiM-LM2-ODE(fast_dim_ode) | 53.70, 55.05, 56.60, 54.30, 57.31 | 55.39±1.53 |
| MAD22/DiM-MI(greedy_dim) | 52.40, 54.20, 49.30, 46.90, 55.10 | 51.58±3.43 |
| MAD22/DiM-MI-Semantic(greedy_dim_s) | 22.30, 21.20, 22.60, 21.20, 24.20 | 22.30±1.24 |
| MAD22/MorDiff | 28.10, 27.30, 29.90, 26.10, 26.25 | 27.53±1.56 |

## Receipts (SHA256)

```
RWS madation_vitb16 v1: scores_rel_madation_vitb16__v1.npz sha256 a0c3cf427e2115506439de91c6946b31819258bdf4c8af918adaa7d747e397b0 missing_ids 0
RWS madation_vitl14 v1: scores_rel_madation_vitl14__v1.npz sha256 0716fa31f3d8219489e6532be3a8a371ef42a1c12bbe6e2166c5783cd4d193e7 missing_ids 0
RWS mixfacenet_mad_smdd v1: scores_rel_mixfacenet_mad_smdd__v1.npz sha256 e0d7f49edb7a2510cdc86d4fcd9993417e271cfe7146c20b88b17002c0ebfc2d missing_ids 0
RWS madation_vitb16 v2: scores_rel_madation_vitb16__v2.npz sha256 9dd197a5d8b57350225ff7e4ced5c8bf001c8c4ea21c93f117941afc5de061d7 missing_ids 0
RWS madation_vitl14 v2: scores_rel_madation_vitl14__v2.npz sha256 cd959b5e01029a61af78800759fc1552cf3ffb2dfbaa0356feb1be0387dd115e missing_ids 0
RWS mixfacenet_mad_smdd v2: scores_rel_mixfacenet_mad_smdd__v2.npz sha256 3e64e394405aaec4689b87fb6e74a2659e08ac1399b80cb845037f98c718c41b missing_ids 0
RSX madation_vitb16 v1: scores_rel_madation_vitb16__ad5v1.npz sha256 e76d3f360be0338bf21a28b8e0b42fa815c7500cc7ee204b5f3368a4f3b9c2f5 missing_ids 0
RSX madation_vitb16 v2: scores_rel_madation_vitb16__ad5v2.npz sha256 9205fe7c1b128eda6e0a55e0eabdf7f210667200395defd5bd5490015c9b30ee missing_ids 0
RSX madation_vitl14 v1: scores_rel_madation_vitl14__ad5v1.npz sha256 c12c85f860ad6bae37fc54dfb238d314a1f88be5ea3a937a8eafec7b21535d0d missing_ids 0
RSX madation_vitl14 v2: scores_rel_madation_vitl14__ad5v2.npz sha256 32c9cb23348b882fcdd081a8614a6961186dec7d141c18e765e2f993cc8e11fa missing_ids 0
RSX mixfacenet_mad_smdd v1: scores_rel_mixfacenet_mad_smdd__ad5v1.npz sha256 4a895f4da4c182c8668dd15e8e2996eb632eb03cf6f1147fbfdc0fcd24d4c121 missing_ids 0
RSX mixfacenet_mad_smdd v2: scores_rel_mixfacenet_mad_smdd__ad5v2.npz sha256 b01ef171b57104c8d5251c7055c6eab1e07a68e26e73e0a48f233fd6ed3cbbf2 missing_ids 0
H madation_B v1: seeds 5 shas 6c72ad67584531c8..21cbfbcba35bb0d4
H madation_B v2: seeds 5 shas 19310a3dba5cf6b9..118af21c0207d8ea
H madation_L v1: seeds 5 shas cb01d57f3eb68e62..7c8274106752183c
H madation_L v2: seeds 5 shas c3c36c4e810bb46b..4f6f5f6a5296a85c
H mixfacenet_X v1: seeds 5 shas dbf5c35662deba02..ab2ee2031c57cb82
H mixfacenet_X v2: seeds 5 shas 05127c72d09564ba..5ddea16ecb1ca582
Hselfmad s401: scores_own_selfmad_S_s401__ad5.npz sha256 d3a53c52d3c83d4c0b6050c638fdd68c582e850a2a28ccdc34a6a3dd301dfc0c missing_ids 0
Hselfmad s402: scores_own_selfmad_S_s402__ad5.npz sha256 9099f6748ebb018baa76b4e44687a1631a7c4413d5b05e908f557c1c703e2a4f missing_ids 0
Hselfmad s403: scores_own_selfmad_S_s403__ad5.npz sha256 03a812c13de71551700e8bdc3db0feee8e630471315901835f36616a09cdb24d missing_ids 0
Hselfmad s404: scores_own_selfmad_S_s404__ad5.npz sha256 1fe532a7fc725f1affc42d661363afc942c173878519696bc5cd94b0e682e2e7 missing_ids 0
Hselfmad s405: scores_own_selfmad_S_s405__ad5.npz sha256 aa68a5e069bd40225250bda93cf39b208f3946ff650d12a3fead6da08c51f21c missing_ids 0
```

Qualifiers: (1) H rows = our OWN retrained versions of the released methods (distinct from "
                 "released-weights rows); (2) scoring runs on GB10-regenerated RS1 crops (per-file byte-identity vs "
                 "prod crops: v1 80.2% (22,664/28,253), v2 74.4% (21,619/29,049)); (3) FRLL FaceMorpher v1 cell uses only the morph rows with a v1 crop (RS1 amendment 7); "
                 "(4) SelfMAD block = 5/5 seeds, own-mode preprocessing (s405 scored 16 Nov on GB10, npz sha256 aa68a5e0...); (5) EER ties-halved, no threshold fitting; "
                 "(6) release sanity: released B/L AND MixFaceNet weights re-scored on regen crops, per-family EER delta vs "
                 "prod-S v1/v2 mean|d| 0.099-0.257 pp, max 1.40 pp (17 families each; MixFaceNet v1 mean|d| 0.257 pp max 0.980 pp, v2 mean|d| 0.245 pp max 0.490 pp; "
                 "independent check 2026-11-16T06:20Z, /tmp/rsx_delta_20261116.py, n=17/17 families, missing_scored_ids 0). "


## AD6 Hsbr madation_B (ViT-B/16) retrains (matched-recipe, WCSS ad6w v3; own crops, prod id space) — 5/5 seeds

| family (n morph, n genuine) | s401 | s402 | s403 | s404 | s405 | mean±sd (v1) | mean±sd (v2) |
|---|---|---|---|---|---|---|---|
| FRLL/amsl (2175, 204) | 13.73, 9.24, 6.86, 9.80, 7.86 | 9.50±2.63 (k=5/5) | 7.81±2.32 (k=5/5) |
| FRLL/facemorpher (802, 204) | 2.74, 2.00, 2.45, 2.94, 2.37 | 2.50±0.36 (k=5/5) | 2.09±1.31 (k=5/5) |
| FRLL/opencv (1211, 204) | 1.96, 1.40, 1.96, 1.82, 1.40 | 1.71±0.28 (k=5/5) | 1.00±0.20 (k=5/5) |
| FRLL/stylegan (1222, 204) | 12.25, 8.33, 13.42, 18.74, 9.90 | 12.53±4.00 (k=5/5) | 11.57±4.73 (k=5/5) |
| FRLL/webmorph (1221, 204) | 17.16, 13.24, 8.35, 13.02, 11.76 | 12.71±3.16 (k=5/5) | 10.27±2.85 (k=5/5) |
| MAD22/FaceMorpher (1000, 408) | 3.20, 2.45, 1.47, 0.60, 1.72 | 1.89±0.99 (k=5/5) | 1.15±0.59 (k=5/5) |
| MAD22/OpenCV (984, 408) | 5.64, 3.86, 4.90, 4.90, 4.90 | 4.84±0.63 (k=5/5) | 2.75±0.52 (k=5/5) |
| MAD22/Webmorph (500, 408) | 13.20, 11.00, 9.20, 12.25, 11.76 | 11.48±1.51 (k=5/5) | 9.03±1.01 (k=5/5) |
| MAD22/MIPGAN_I (1000, 408) | 34.30, 11.70, 16.20, 7.00, 16.67 | 17.17±10.34 (k=5/5) | 14.00±7.38 (k=5/5) |
| MAD22/MIPGAN_II (999, 408) | 13.97, 5.31, 4.66, 2.45, 6.01 | 6.48±4.40 (k=5/5) | 4.71±2.54 (k=5/5) |
| MAD22/DiM-MvM(dim_a) (500, 408) | 31.86, 13.20, 16.60, 5.40, 9.40 | 15.29±10.16 (k=5/5) | 12.52±8.67 (k=5/5) |
| MAD22/DiM-MvM(dim_c) (500, 408) | 16.80, 3.19, 4.90, 2.21, 1.47 | 5.71±6.33 (k=5/5) | 4.46±4.68 (k=5/5) |
| MAD22/DiM-LM2(fast_dim) (500, 408) | 30.39, 9.60, 18.38, 5.00, 9.20 | 14.51±10.12 (k=5/5) | 11.48±7.83 (k=5/5) |
| MAD22/DiM-LM2-ODE(fast_dim_ode) (499, 408) | 20.04, 10.54, 12.83, 7.60, 13.43 | 12.89±4.61 (k=5/5) | 10.49±3.55 (k=5/5) |
| MAD22/DiM-MI(greedy_dim) (500, 408) | 8.58, 9.80, 7.20, 8.00, 12.50 | 9.22±2.07 (k=5/5) | 7.41±2.41 (k=5/5) |
| MAD22/DiM-MI-Semantic(greedy_dim_s) (500, 408) | 20.20, 5.64, 9.07, 3.80, 5.39 | 8.82±6.65 (k=5/5) | 6.29±4.43 (k=5/5) |
| MAD22/MorDiff (944, 408) | 1.80, 3.19, 1.06, 0.49, 2.94 | 1.90±1.17 (k=5/5) | 3.39±3.12 (k=5/5) |

## AD6 Hsbr mixfacenet_X retrains (matched-recipe, WCSS ad6w v3; own crops, prod id space) — 5/5 seeds

| family (n morph, n genuine) | s401 | s402 | s403 | s404 | s405 | mean±sd (v1) | mean±sd (v2) |
|---|---|---|---|---|---|---|---|
| FRLL/amsl (2175, 204) | 21.08, 19.12, 23.53, 17.16, 12.60 | 18.70±4.15 (k=5/5) | 18.37±2.93 (k=5/5) |
| FRLL/facemorpher (802, 204) | 14.09, 10.10, 11.72, 7.86, 7.84 | 10.32±2.67 (k=5/5) | 10.49±3.09 (k=5/5) |
| FRLL/opencv (1211, 204) | 15.44, 12.25, 13.29, 11.27, 8.67 | 12.19±2.50 (k=5/5) | 10.66±2.41 (k=5/5) |
| FRLL/stylegan (1222, 204) | 33.39, 24.30, 25.86, 21.28, 22.06 | 25.38±4.83 (k=5/5) | 23.89±3.48 (k=5/5) |
| FRLL/webmorph (1221, 204) | 31.86, 25.98, 30.38, 29.40, 25.80 | 28.69±2.70 (k=5/5) | 27.11±1.33 (k=5/5) |
| MAD22/FaceMorpher (1000, 408) | 5.00, 6.40, 8.70, 6.13, 5.40 | 6.33±1.44 (k=5/5) | 11.09±2.63 (k=5/5) |
| MAD22/OpenCV (984, 408) | 18.38, 17.38, 18.50, 15.93, 13.24 | 16.68±2.19 (k=5/5) | 14.98±2.14 (k=5/5) |
| MAD22/Webmorph (500, 408) | 22.30, 22.79, 26.96, 22.55, 19.60 | 22.84±2.64 (k=5/5) | 20.49±0.96 (k=5/5) |
| MAD22/MIPGAN_I (1000, 408) | 37.50, 30.60, 25.10, 25.49, 27.94 | 29.33±5.07 (k=5/5) | 26.47±5.21 (k=5/5) |
| MAD22/MIPGAN_II (999, 408) | 33.82, 31.86, 29.93, 25.74, 23.62 | 29.00±4.24 (k=5/5) | 25.71±4.44 (k=5/5) |
| MAD22/DiM-MvM(dim_a) (500, 408) | 41.91, 42.60, 35.60, 35.60, 45.80 | 40.30±4.54 (k=5/5) | 40.61±5.02 (k=5/5) |
| MAD22/DiM-MvM(dim_c) (500, 408) | 28.43, 21.57, 23.28, 18.40, 22.80 | 22.90±3.63 (k=5/5) | 23.33±2.72 (k=5/5) |
| MAD22/DiM-LM2(fast_dim) (500, 408) | 48.60, 45.60, 43.14, 44.36, 51.60 | 46.66±3.43 (k=5/5) | 46.31±2.82 (k=5/5) |
| MAD22/DiM-LM2-ODE(fast_dim_ode) (499, 408) | 51.23, 49.51, 47.29, 47.70, 57.35 | 50.62±4.08 (k=5/5) | 50.00±3.87 (k=5/5) |
| MAD22/DiM-MI(greedy_dim) (500, 408) | 35.60, 34.00, 32.40, 26.96, 32.40 | 32.27±3.25 (k=5/5) | 32.85±3.50 (k=5/5) |
| MAD22/DiM-MI-Semantic(greedy_dim_s) (500, 408) | 22.80, 20.10, 19.85, 15.40, 17.20 | 19.07±2.85 (k=5/5) | 18.69±3.26 (k=5/5) |
| MAD22/MorDiff (944, 408) | 14.62, 23.41, 21.81, 15.93, 12.25 | 17.61±4.79 (k=5/5) | 24.89±2.30 (k=5/5) |


## AD6 Hsbr madation_L (ViT-L/14) retrains (matched-recipe, WCSS ad6w v3; own crops, prod id space) — L rows appended when 5/5

| family (n morph, n genuine) | s401 | s402 | s403 | s404 | s405 | mean±sd (v1) | mean±sd (v2) |
|---|---|---|---|---|---|---|---|
| FRLL/amsl (2175, 204) | 24.09, 22.06, 21.01, 18.14, 11.26 | 19.31±4.99 (k=5/5) | 25.90±6.10 (k=5/5) |
| FRLL/facemorpher (802, 204) | 1.87, 1.96, 1.50, 1.37, 0.75 | 1.49±0.48 (k=5/5) | 1.29±0.43 (k=5/5) |
| FRLL/opencv (1211, 204) | 1.57, 1.96, 1.16, 1.24, 0.91 | 1.37±0.41 (k=5/5) | 1.14±0.30 (k=5/5) |
| FRLL/stylegan (1222, 204) | 15.69, 17.35, 11.87, 11.95, 12.25 | 13.82±2.54 (k=5/5) | 15.98±3.95 (k=5/5) |
| FRLL/webmorph (1221, 204) | 33.33, 25.98, 32.84, 30.14, 21.57 | 28.77±4.97 (k=5/5) | 31.30±3.96 (k=5/5) |
| MAD22/FaceMorpher (1000, 408) | 6.86, 8.00, 6.00, 6.86, 3.50 | 6.25±1.69 (k=5/5) | 4.96±2.08 (k=5/5) |
| MAD22/OpenCV (984, 408) | 3.66, 6.62, 5.59, 4.67, 2.85 | 4.68±1.50 (k=5/5) | 3.72±1.20 (k=5/5) |
| MAD22/Webmorph (500, 408) | 10.78, 14.20, 14.20, 12.01, 9.40 | 12.12±2.11 (k=5/5) | 10.27±2.50 (k=5/5) |
| MAD22/MIPGAN_I (1000, 408) | 18.63, 21.20, 10.20, 26.70, 15.40 | 18.43±6.19 (k=5/5) | 15.83±4.97 (k=5/5) |
| MAD22/MIPGAN_II (999, 408) | 15.02, 13.48, 5.71, 13.73, 9.56 | 11.50±3.83 (k=5/5) | 10.01±3.22 (k=5/5) |
| MAD22/DiM-MvM(dim_a) (500, 408) | 37.50, 29.66, 33.09, 29.20, 34.80 | 32.85±3.50 (k=5/5) | 30.67±2.68 (k=5/5) |
| MAD22/DiM-MvM(dim_c) (500, 408) | 35.29, 30.15, 27.00, 28.92, 32.00 | 30.67±3.16 (k=5/5) | 29.02±2.05 (k=5/5) |
| MAD22/DiM-LM2(fast_dim) (500, 408) | 36.76, 36.60, 32.40, 35.29, 47.79 | 37.77±5.87 (k=5/5) | 36.03±4.59 (k=5/5) |
| MAD22/DiM-LM2-ODE(fast_dim_ode) (499, 408) | 30.06, 22.55, 18.38, 21.08, 26.85 | 23.78±4.66 (k=5/5) | 21.47±5.42 (k=5/5) |
| MAD22/DiM-MI(greedy_dim) (500, 408) | 48.20, 43.14, 35.29, 44.61, 32.00 | 40.65±6.75 (k=5/5) | 42.41±7.61 (k=5/5) |
| MAD22/DiM-MI-Semantic(greedy_dim_s) (500, 408) | 22.30, 27.94, 18.60, 24.02, 26.40 | 23.85±3.65 (k=5/5) | 22.24±3.51 (k=5/5) |
| MAD22/MorDiff (944, 408) | 5.88, 4.45, 3.60, 4.24, 3.50 | 4.33±0.96 (k=5/5) | 34.02±6.96 (k=5/5) |
