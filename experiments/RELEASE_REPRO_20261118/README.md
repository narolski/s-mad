# Release reproduction run (2026-11-18)

Goal: show that the published release repository (`narolski/dont-cut-corners`) reproduces the frozen networks when run
from a clean clone. No benchmark image or benchmark score was opened; comparisons use weights and the development /
training score sets stored in the frozen archives (`PN1_Sb_s40x.tar`, `AD4_m3*_s401.tar` scores_train only).

Launch files: `src/public_release/repro/` (`make_pool.py`, `compare.py`, `sb_train.sbatch` (WCSS), `sb_train_athena.sbatch`,
`mf_train.sbatch`). Local work dir: `/mnt/t7/smad_next/release_repro/` (temporary).

## Commits tested
- release `446ba8e` (start), `5737486` (after fix 1; the archive shipped to the clusters is `git archive` of a fresh
  clone of the pushed commit).

## Release-code bugs found and fixed
1. `5737486` `training/score.py` ran without TF32, while training and the internal scorer of the stored scores enable
   TF32 matmul/cuDNN. Fixed (two lines). Unit tests OK; reproduce_table1 (largest diff 0.005 EER points), reproduce_supplement
   (1,556 cells, 0 mismatches), reproduce_morph_free (52 values, 0 mismatches) re-run after the fix.

## Run 1: local, no cluster (DGX Spark GB10; torch 2.12.1+cu130, timm 1.0.27, numpy 2.5.5, pillow 12.2.0)
- Release `build_lists.py` on the pool rebuilt from the internal manifests (`make_pool.py`, 5,535 images): all seven arms
  identical to the internal lists row for row; `train_Sb.csv` (path, label) identical in order to the pack's list the
  frozen s403 was trained on (8,386 rows).
- Release `train.py`, fresh clone, seed 403, 100 updates on the local GPU: batch label composition of all 100 batches
  identical to the frozen meta.json; loss at update 100 = 0.6928, frozen log 0.6928. (The frozen train.log has no
  per-update loss before step 100, so the first-20-update comparison is done on batch composition.)
- Release `score.py` on the frozen s403, local stack, train images (5,535): logit max |diff| 0.083 (no TF32) / 0.079
  (TF32), median 9.6e-5 against the stored scores: the local stack (different torch/pillow/GPU) is not the reference
  stack; cluster runs use torch 2.2.1.
- Morph-free: release `morph_free/build_data.py` on the pack's 25,000 SMDD natives: list (50,000 rows) and all five
  permuted lists identical to the internal manifests; all 25,000 80-px copies pixel-identical.

## Runs 2-4 (clusters)
See the log below.

## Log
- 16:09 WCSS smoke submitted: job 6355185 (lem-gpu-short, 1 H100, release 5737486, Sb seed 403, 200 updates, container
  smad_torch221_cu121_v1.sif = the original Sb stack, pack unpacked on $TMPDIR). Pending (Priority); Slurm forecast
  moved between 19 Nov 04:40 and 20 Nov 22:11.
- 17:15 not started after an hour: Athena fallback smoke submitted, job 3558886 (plgrid-gpu-a100, A100-SXM4, project
  torch 2.2.1 venv, memfs). Pending (Priority) at 18:28. Note the frozen Sb nets were trained on an A100-PCIE-40GB, so
  neither cluster has the identical GPU model; bit identity is not guaranteed on either.
- 18:28 handed back with both smokes queued; production (step 3) and step 4 not launched (smoke has not passed).
  Inputs staged: WCSS `release_repro/inputs/` (sif, pn1_pack_fs.tar, mf_data.tar, clip_weights.tar, release_5737486.tar,
  repro_lists*.tar); Athena `smad-next/release_repro/inputs/` (Sb inputs only).

## Next commands (after a smoke passes: compare.py on its tar against the frozen s403 loss trace, steps 100/200)
- WCSS production: `sbatch --export=ALL,REL=5737486,SEED=403,SCORE=1 repo/sb_train.sbatch`
- then seeds 404-407 the same; morph-free: `sbatch --export=ALL,REL=5737486,SEED=401,BACKBONE=vitb16 repo/mf_train.sbatch`
  (vitl14: same with BACKBONE=vitl14, ~4-8 h; copy mf_train.sbatch to repo/ first).
- compare: `python -I src/public_release/repro/compare.py FROZEN_DIR RESULT_DIR sb|mf`
