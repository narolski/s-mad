# Diffusion-autoencoder generation on Athena (DG1): result

Status 11 Nov 2026 20:10 CET: **equivalence gate passed; set A done; set B 2 of 4 shards done; add-on queued.** Full record:
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

Set A (FRLL, `/mnt/t7/smad_next/DG1/gen/setA/out_setA/setA/`): genuine same-storage 102; reconstruction 102 + 102 (20 /
100 steps); mirror mix 102 + 102; two-person morph 100 + 100 (A43 neutral pairs); neutral+smiling mix (confounded)
102 + 102. Total 914, all finite, genuine writes 102 of 102 lossless.
Set B (FRGC / colorFERET): shards 1 and 3 done (904 + 908 files); shards 0 and 2 running (array 3545877). Planned
3,616: genuine 1,072; REC / MIR / SAME / X 536 each; dose 4 × 100.
Add-on (amendment 2, array 3545907): queued.

## Athena jobs and GPU-hours

| Job | Account | Purpose | Result | GPU-hours |
|---|---|---|---|---|
| 3544197 | plgrestorearc | smoke | failed at `module load` (Python/3.12.3 needs GCCcore/13.3.0) | 0.001 |
| 3544215 | plgrestorearc | smoke | failed: venv held numpy 2.5.4 (DiffAE needs < 2) | 0.185 |
| 3544800 | plgrestorearc | smoke | passed | 0.083 |
| 3545841_0 (3545857) | plgrestorearc | set A | done, 1,705 s | 0.47 |
| 3545841_1, _3 | plgrestorearc | set B shards 0, 2 | cancelled at about 10 min on slow node t0010 (18.8 s per inversion) | about 0.33 |
| 3545841_2 (3545865) | plgrestorearc | set B shard 1 | done, 1,454 s | 0.40 |
| 3545841_4 (3545841) | plgrestorearc | set B shard 3 | done, 1,577 s | 0.44 |
| 3545877_1, _3 | plgmultivision (moved by the lead) | set B shards 0, 2 (resubmitted, t0010 excluded) | queued | — |
| 3545907_0–7 | plgmultivision | add-on (amendment 2) | queued (start estimate 12 Nov 06:37) | estimate 3.3 |

## Validity numbers per rung

Set A (`validity/setA_validity.csv`; glint cosine to the raw photos, median; verification at FMR 1e-3; asymmetry and
Laplacian variance in the face box, median): genuine 0.984, asym 14.1, lapvar 289; REC20 0.964 / 12.8 / 158; REC100
0.980 / 13.6 / 214; MIR20 0.902 / 4.1 / 224; MIR100 0.896 / 6.0 / 529; X20 host 0.534, partner 0.535, both verify 99 of
100, asym 11.8, lapvar 198; X100 0.541 / 0.541, both 99 of 100, 13.2 / 497; CONF20 0.895 / 0.885, 14.3 / 269; CONF100
0.885 / 0.874, 16.0 / 570. Every one-person image verifies against its host. Set B: after all shards are in.

## What failed

Two smoke jobs (above), fixed. Equivalence and the 8-image checks passed.
