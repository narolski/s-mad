# AD6 Hsbr (matched-recipe retrains) — per-family EER (%) — 2026-11-17

Hsbr rows = AD6 matched-recipe retrains trained on the WCSS ad6w arrays (v3 wheel set), scored through the SAME
Athena-registered path as AD5 (ad5_score_athena.py, frozen RS1 regen crops, score_v1/score_v2 manifests, pins
56bb1244/42806acb asserted), tags h_<name>__ad6v1/ad6v2. v1 primary, v2 validation. Metric: EER on logit_noTTA
(final_metrics pin; ties-halved, no threshold fitting). Id space: prod athena_manifest.csv (missing_ids 0

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
| FRLL/amsl (?, ?) | n/a, n/a, n/a, n/a, n/a | n/a | n/a |
| FRLL/facemorpher (?, ?) | n/a, n/a, n/a, n/a, n/a | n/a | n/a |
| FRLL/opencv (?, ?) | n/a, n/a, n/a, n/a, n/a | n/a | n/a |
| FRLL/stylegan (?, ?) | n/a, n/a, n/a, n/a, n/a | n/a | n/a |
| FRLL/webmorph (?, ?) | n/a, n/a, n/a, n/a, n/a | n/a | n/a |
| MAD22/FaceMorpher (?, ?) | n/a, n/a, n/a, n/a, n/a | n/a | n/a |
| MAD22/OpenCV (?, ?) | n/a, n/a, n/a, n/a, n/a | n/a | n/a |
| MAD22/Webmorph (?, ?) | n/a, n/a, n/a, n/a, n/a | n/a | n/a |
| MAD22/MIPGAN_I (?, ?) | n/a, n/a, n/a, n/a, n/a | n/a | n/a |
| MAD22/MIPGAN_II (?, ?) | n/a, n/a, n/a, n/a, n/a | n/a | n/a |
| MAD22/DiM-MvM(dim_a) (?, ?) | n/a, n/a, n/a, n/a, n/a | n/a | n/a |
| MAD22/DiM-MvM(dim_c) (?, ?) | n/a, n/a, n/a, n/a, n/a | n/a | n/a |
| MAD22/DiM-LM2(fast_dim) (?, ?) | n/a, n/a, n/a, n/a, n/a | n/a | n/a |
| MAD22/DiM-LM2-ODE(fast_dim_ode) (?, ?) | n/a, n/a, n/a, n/a, n/a | n/a | n/a |
| MAD22/DiM-MI(greedy_dim) (?, ?) | n/a, n/a, n/a, n/a, n/a | n/a | n/a |
| MAD22/DiM-MI-Semantic(greedy_dim_s) (?, ?) | n/a, n/a, n/a, n/a, n/a | n/a | n/a |
| MAD22/MorDiff (?, ?) | n/a, n/a, n/a, n/a, n/a | n/a | n/a |

## Receipts (SHA256, scores npz; feat npz in scores_h_sbr/RECEIPTS_sha256.csv)

```
HsbrB v1: seeds scored 5/5 shas d078f09d30984e1b..da0a05ea42575d04 missing_ids_total 0
HsbrB v2: seeds scored 5/5 shas 0c71447ee6e3a949..92b605a7863464fb missing_ids_total 0
HsbrX v1: seeds scored 5/5 shas 7927fd92b14e9fa5..9c43f72f8c48245b missing_ids_total 0
HsbrX v2: seeds scored 5/5 shas 93697263af918bae..9a5d29dea360ffad missing_ids_total 0
receipts_csv /home/narolski/ad6_stage/scores_h_sbr/RECEIPTS_sha256.csv: lines 20
```

Adaptation notes vs AD5 aggregate (c745230): source npz scores_h_<scriptname>__ad6<v>.npz in
/home/narolski/ad6_stage/scores_h_sbr/ (script names; WCSS tars madation_B_v3sbr_s40N.tar renamed at pull stage
after sha256 verification — scoring path unchanged); madation_L block pending (H2 lands ~02:30-03:30Z 17 Nov).
Space policy: /mnt/t7 full -> outputs under experiments/. Pulled tars + converted weights deleted by the scoring
script per seed after receipts (sha256 preserved in RECEIPTS_sha256.csv).
