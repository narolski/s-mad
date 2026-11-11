# Diffusion-autoencoder generation on Athena (DG1): result

Status 11 Nov 2026 19:16 CET: **equivalence gate passed; production running** (Athena array job 3545841). Full record:
`README.md` in this folder.

## Equivalence gate (registered reading: equivalent if every image's mean |difference| ≤ 2 grey levels)

**Equivalent.** 8 images regenerated on an A100 (smoke job 3544800) against the stored DGX A43 files
(`equivalence.json`):

| Image | mean abs diff | max abs diff | glint cosine Athena vs DGX |
|---|---|---|---|
| D20 001_03 / 002_03 / 003_03 / 004_03 (reconstructions, 20 steps) | 0.023 / 0.020 / 0.022 / 0.017 | 1 / 1 / 1 / 1 | 0.99994 / 0.99993 / 0.99989 / 0.99995 |
| B20 draws 0–3 (two-person morphs, 20 steps) | 0.032 / 0.033 / 0.047 / 0.059 | 1 / 2 / 3 / 4 | 0.99992 / 0.99993 / 0.99992 / 0.99990 |

Pooled mean 0.032 grey levels. Image statistics (mean, standard deviation, asymmetry, Laplacian variance) move by at
most 0.01 of their between-image standard deviation, so no detector score is expected to move. For scale: re-running
on the DGX itself differs from the stored file by mean 0.024, max 1. Unregistered cross-check: the 10 `smoke8` files
from Athena against the same jobs on the DGX differ by mean 0.019–0.066, max 4 (`smoke8_athena_vs_dgx.json`).

## Seconds per image on an A100 (40 GB, batch 8–12, fp16 autocast)

3.3–3.4 s per 250-step inversion; 0.33–0.37 s per 20-step render; 100-step render about 4 s for a batch of one (about
1.3 s per image expected at batch 16). For comparison, the shared DGX GB10 took 143 s per inversion today (A43 on an
idle GB10: 13.1 s).

## What was generated (counts per rung)

Production running. Planned: set A 914 files, set B 3,616 files (`prereg.md`).

## Athena jobs and GPU-hours

| Job | Purpose | Result | GPU-hours |
|---|---|---|---|
| 3544197 | smoke | failed at `module load` (Python/3.12.3 needs GCCcore/13.3.0) | 0.001 |
| 3544215 | smoke | failed: venv held numpy 2.5.4 (DiffAE needs < 2) | 0.185 |
| 3544800 | smoke | passed | 0.083 |
| 3545841_0–4 | production: set A, set B shards 0–3 | running | estimate 2.6 (at most 3.5) |

## Validity numbers per rung

Not computed yet (after copy-back).

## What failed

Two smoke jobs (above), fixed. Equivalence and the 8-image checks passed.
