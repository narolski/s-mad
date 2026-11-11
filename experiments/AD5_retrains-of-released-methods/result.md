# Retrains of released methods with the authors' code (AD5): result

Status 11 Nov 2026, 19:10 CET: training running on Athena; no score of a retrain exists. Full record: `README.md`.

## Athena jobs (account plgrestorearc-gpu-a100)

| Job | Purpose | GPUs | GPU-hours | State |
|---|---|---|---|---|
| 3544190 | smoke A, first try (env build; failed: 4 GB localfs full) | 1 | 0.065 | FAILED |
| 3544192 | smoke B, first try | 2 | 0 | cancelled before start |
| 3544216 | smoke A: SMDD crop with the authors' script (39,723 of 40,000 kept) | 1 | 0.20 | COMPLETED |
| 3544217 | smoke B: MADation ViT-L/14 and ViT-B/16 DDP, MixFaceNet-MAD speed | 2 | 0.2 | COMPLETED |
| 3544218 | SelfMAD smoke: environment, face labels, 1-epoch speed | 1 | running | |
| 3545813_[401-405] | MADation ViT-L/14 retrains | 8 per seed | about 62 planned | submitted |
| 3545814_[401-405] | MADation ViT-B/16 retrains | 8 per seed | about 16 planned | submitted |
| 3545815_[401-405] | MixFaceNet-MAD retrains | 1 per seed | about 33 planned | submitted |

## Results

None yet.
