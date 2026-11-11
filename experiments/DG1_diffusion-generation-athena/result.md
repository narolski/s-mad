# Diffusion-autoencoder generation on Athena (DG1): result

Status 11 Nov 2026 21:15 CET: **equivalence gate passed; production done (set A 914 files, set B 3,616 files, all
finite, copied back with hash checks); validity numbers computed; add-on (amendment 2): 2 of 8 tasks done and fetched (images only), 6 pending.**
Full record: `README.md` in this folder. Reading rules for anyone who scores these images: `prereg.md` amendment 1.

## Equivalence gate (registered reading: equivalent if every image's mean |difference| ≤ 2 grey levels)

**Equivalent.** 8 images regenerated on an A100 (smoke job 3544800) against the stored DGX A43 files
(`equivalence.json`):

| Image | mean abs diff | max abs diff | glint cosine Athena vs DGX |
|---|---|---|---|
| D20 001_03 / 002_03 / 003_03 / 004_03 (reconstructions, 20 steps) | 0.023 / 0.020 / 0.022 / 0.017 | 1 / 1 / 1 / 1 | 0.99994 / 0.99993 / 0.99989 / 0.99995 |
| B20 draws 0–3 (two-person morphs, 20 steps) | 0.032 / 0.033 / 0.047 / 0.059 | 1 / 2 / 3 / 4 | 0.99992 / 0.99993 / 0.99992 / 0.99990 |

Pooled 0.032 grey levels; image statistics move by at most 0.01 between-image SD (no detector score expected to move).
Same-machine baseline: a DGX re-render differs from the stored file by mean 0.024, max 1. Even so, DGX and Athena images
are never combined inside one contrast (amendment 1; morphs differ more across machines than reconstructions).

## Seconds per image on an A100 (40 GB, batch 16, fp16 autocast)

Inversion (250 steps) 3.01–3.20 s; render 0.24–0.27 s at 20 steps and 1.24–1.42 s at 100 steps. Shared DGX GB10 today:
143 s per inversion. One node (t0010) ran at 18.8 s per inversion; its two tasks were cancelled and rerun elsewhere.

## What was generated (counts per rung)

- **Set A (FRLL, 102 persons, neutral)**, `/mnt/t7/smad_next/DG1/gen/setA/out_setA/setA/`: genuine photo same storage
  102; reconstruction 102 + 102 (20 / 100 steps); mirror mix 102 + 102; two-person morph 100 + 100 (A43 neutral
  pairs); neutral+smiling mix, confounded 102 + 102. Total 914.
- **Set B (FRGC 427 + colorFERET 109 hosts)**, `/mnt/t7/smad_next/DG1/gen/setB_s{0..3}/out_setB_s*/setB_s*/`: genuine
  H and S 1,072; reconstruction 536; mirror mix 536; same-person mix 536; two-person morph 536; dose α 0.1 / 0.2 / 0.3 /
  0.4: 100 each. Total 3,616. 20 steps.
- Every image finite; every genuine write pixel-identical to its input (1,174 of 1,174); every file re-hashed after
  copy-back. Manifests (image, set, rung, host, partner, steps, α, seed, generation run, hashes, cosines, statistics,
  person-use and flag columns): `validity/setA_manifest.csv`, `validity/setB_manifest.csv`.

## Athena jobs and GPU-hours

| Job | Account | Purpose | Result | GPU-hours |
|---|---|---|---|---|
| 3544197 | plgrestorearc | smoke | failed at `module load` (Python/3.12.3 needs GCCcore/13.3.0) | 0.001 |
| 3544215 | plgrestorearc | smoke | failed: venv held numpy 2.5.4 (DiffAE needs < 2) | 0.185 |
| 3544800 | plgrestorearc | smoke | passed | 0.083 |
| 3545841_0 (3545857) | plgrestorearc | set A | done | 0.486 |
| 3545841_1, _3 | plgrestorearc | set B shards 0, 2 | cancelled on slow node t0010 | 0.309 |
| 3545841_2 (3545865), _4 (3545841) | plgrestorearc | set B shards 1, 3 | done | 0.859 |
| 3545877_1 (3545939), _3 (3545877) | plgmultivision (moved by the lead) | set B shards 0, 2 | done | 1.059 |
| 3545907_0 (3545986), _1 (3545988) | plgmultivision | add-on shards 0, 1 | done; re-renders match production (max 3 grey levels) | 0.789 |
| **Total so far** | | | | **3.77** |
| 3545907_2–7 | plgmultivision | add-on shards 2–7 | pending (ReqNodeNotAvail) | estimate 2.4 |

## Validity numbers per rung (glint cosine and verification at FMR 1e-3, the A43 route; medians)

| Rung | Set A 20 / 100 steps: cos host; both verify | Set B (20 steps): cos host / partner; verify both (indep. refs) |
|---|---|---|
| genuine, same storage | 0.984 | 0.989 |
| reconstruction | 0.964 / 0.980 | 0.959 |
| mirror mix | 0.902 / 0.896 | 0.891 |
| same-person mix | (neutral+smiling, confounded) 0.895 / 0.885 | 0.885 / 0.885; 1.000 |
| two-person morph | 0.534 / 0.541; 99 of 100 at both step counts | 0.566 / 0.569; 527 of 536 = 0.983 (0.959) |
| dose α 0.1 / 0.2 / 0.3 / 0.4 | — | host 0.936 / 0.866 / 0.774 / 0.676; both 0.73 / 0.90 / 0.96 / 0.99 |

Left-right asymmetry (face box, median): genuine 13.4–14.1, reconstruction 12.4–13.6, two-person morph 10.9–13.2,
mirror mix 3.3–6.0. Laplacian variance (face box, median): set B genuine 171, REC 87, MIR 109, SAME 128, X 96; set A
100-step renders 2.5–3.4 times their 20-step versions (e.g. X 497 vs 198). Flags in set B: 55 photos with a black
wedge, 7 greyscale photos, 4 probable-twin morphs, 16 morphs with a shared capture date (72 of 536 morphs flagged).
Full tables: `README.md` section 5, `validity/*_summary.csv`.

## What failed

- Smoke jobs 3544197 (module prerequisite) and 3544215 (numpy 2.5.4 in the environment, cause of the upgrade not
  identified; fixed by constraining numpy and pillow and asserting versions).
- Node t0010: 6× slower; two tasks cancelled and rerun (0.31 GPU-hours lost).
- First add-on check on the DGX died with CUDA out-of-memory (shared GPU); the retry passed.
- `/mnt/t7` filled at about 20:40 (not caused by this experiment's writes, which total 3.7 GB); all copy-backs re-verified.
