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

## SelfMAD retrains (own preprocessing, own id space; 4/5 seeds — s405 still training)

| family (n) | s401 | s402 | s403 | s404 | mean±sd |
|---|---|---|---|---|---|
| FRLL/amsl | 2.45, 4.41, 7.35, 7.63 | 5.46±2.48 |
| FRLL/facemorpher | 0.49, 0.98, 2.45, 1.55 | 1.37±0.84 |
| FRLL/opencv | 0.16, 0.49, 1.39, 1.47 | 0.88±0.65 |
| FRLL/stylegan | 18.99, 20.87, 22.55, 21.57 | 20.99±1.51 |
| FRLL/webmorph | 6.86, 14.71, 20.59, 22.06 | 16.05±6.90 |
| MAD22/FaceMorpher | n/a, n/a, n/a, n/a | n/a |
| MAD22/OpenCV | n/a, n/a, n/a, n/a | n/a |
| MAD22/Webmorph | n/a, n/a, n/a, n/a | n/a |
| MAD22/MIPGAN_I | n/a, n/a, n/a, n/a | n/a |
| MAD22/MIPGAN_II | n/a, n/a, n/a, n/a | n/a |
| MAD22/DiM-MvM(dim_a) | 33.00, 35.30, 37.85, 34.80 | 35.24±2.00 |
| MAD22/DiM-MvM(dim_c) | 21.85, 20.60, 23.15, 21.40 | 21.75±1.07 |
| MAD22/DiM-LM2(fast_dim) | 44.55, 44.20, 47.00, 44.75 | 45.12±1.27 |
| MAD22/DiM-LM2-ODE(fast_dim_ode) | 53.70, 55.05, 56.60, 54.30 | 54.91±1.25 |
| MAD22/DiM-MI(greedy_dim) | 52.40, 54.20, 49.30, 46.90 | 50.70±3.24 |
| MAD22/DiM-MI-Semantic(greedy_dim_s) | 22.30, 21.20, 22.60, 21.20 | 21.82±0.73 |
| MAD22/MorDiff | 28.10, 27.30, 29.90, 26.10 | 27.85±1.59 |

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
```

Qualifiers: (1) H rows = our OWN retrained versions of the released methods (distinct from released-weights rows); (2) scoring runs on GB10-regenerated RS1 crops (per-file byte-identity vs prod crops: v1 80.2% (22,664/28,253), v2 74.4% (21,619/29,049)); (3) FRLL FaceMorpher v1 cell uses only the morph rows with a v1 crop (RS1 amendment 7); (4) SelfMAD block = 4/5 seeds, own-mode preprocessing; (5) EER ties-halved, no threshold fitting; (6) release sanity: released B/L AND MixFaceNet weights re-scored on regen crops, per-family EER delta vs prod-S v1/v2 mean|d| 0.099-0.257 pp, max 1.40 pp (17 families each; MixFaceNet v1 mean|d| 0.257 pp max 0.980 pp, v2 mean|d| 0.245 pp max 0.490 pp; independent check 2026-11-16T06:20Z, /tmp/rsx_delta_20261116.py, n=17/17 families, missing_scored_ids 0).
