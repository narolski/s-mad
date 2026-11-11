# Retrains of released methods with the authors' code (AD5): result

Status 11 Nov 2026, 20:15 CET: training running on Athena; no score of a retrain exists. Full record: `README.md`.

## Athena jobs (accounts: plgrestorearc-gpu-a100 for the smoke jobs; plgmultivision-gpu-a100 for the production arrays, moved there by the lead at 19:48 or submitted there)

| Job | Purpose | GPUs | GPU-hours | State |
|---|---|---|---|---|
| 3544190 | smoke A, first try (env build; failed: 4 GB localfs full) | 1 | 0.065 | FAILED |
| 3544192 | smoke B, first try | 2 | 0 | cancelled before start |
| 3544216 | smoke A: SMDD crop with the authors' script (39,723 of 40,000 kept) | 1 | 0.20 | COMPLETED |
| 3544217 | smoke B: MADation ViT-L/14 and ViT-B/16 DDP, MixFaceNet-MAD speed | 2 | 0.2 | COMPLETED |
| 3544218 | SelfMAD smoke: environment, face labels (missing package; failed after the labels) | 1 | 0.59 | FAILED |
| 3545815_[401-405] | MixFaceNet-MAD retrains, first submission (cancelled after the pre-run review) | 1 | 0.19 | CANCELLED |
| 3545870_[401-405] | MixFaceNet-MAD retrains v2 (per-epoch weights) | 1 per seed | about 34 planned | submitted |
| 3545882 | SelfMAD smoke v3: 1.45 it/s, 30 GPU-h per seed estimated | 1 | 0.57 | COMPLETED |
| 3545933_[401-404] | SelfMAD retrains | 1 per seed | about 120 planned | submitted |
| 3545936 (task 405) | SelfMAD retrain seed 405 | 1 | about 30 planned | submitted |
| 3545813_[401-405] | MADation ViT-L/14 retrains | 8 per seed | about 62 planned | submitted |
| 3545814_[401-405] | MADation ViT-B/16 retrains | 8 per seed | about 16 planned | submitted |

## Results

None yet.
