# Diffusion-autoencoder generation on Athena (DG1): full record

Owner record under `DOCUMENTATION.md`. `prereg.md` is the registration, `result.md` the short verdict, this file the
full record. Code: `/home/narolski/smad-next/src/DG1/`. Large outputs: `/mnt/t7/smad_next/DG1/`. Athena project
folder: `/net/pr2/projects/plgrid/plggrestoration/smad-next` (sub-folders `packs/DG1/`, `envs/DG1/`, `results/DG1/`,
`logs/`, `tasks/DG1/`).

## 1. Question and current answer

11 Nov 2026, 17:40 CET. Status: **preparing; blocked on Athena accepting jobs** (Slurm rejects both grant accounts for
`plgpnarolski`; the lead's watcher will report when an account is accepted; no submission and no probing until then).
DiffAE (diffusion autoencoder) generation on the shared DGX runs at about 157 s per inversion while other jobs share the
GPU, so the diffusion controls are incomplete: the identical-and-mirrored-inputs check (AD1b) covered 32 of 102
persons, FRLL has no expression-matched one-person controls, and no diffusion twin set outside FRLL exists. This
experiment ports the exact generator of the earlier MorDIFF-controls study (A43) to Athena (A100, x86), checks that
Athena reproduces stored DGX images (equivalence gate), then builds set A (FRLL, benchmark-linked, neutral only, 20 and
100 decoding steps) and set B (FRGC and colorFERET, 536 hosts, 20 steps, with a dose series). No detector is scored
here. No answer yet.

## 2. Timeline

- 11 Nov 17:15–17:35. Read `OWNER_BRIEF.md`, `ATHENA.md`, `11_AUDIT_PLAN.md`, `14_CLASS_DEFINITIONS.md`, the MorDIFF
  ladder re-read (AD1) result, the identical-and-mirrored-inputs check (AD1b) prereg and result, the review of the
  expression cue use study (C1b), the A43 ledger README
  (`/home/narolski/mambamorph-code/experiments/A43_mordiff-two-by-two/README.md`), the A43 generator
  `/home/narolski/mambamorph-code-a44/smadcvpr/a43_gen.py` (sha256 fc862ec674dcaee420fc1d88b45b77fea21bcae953aa62cae54032e13a1a8d1e,
  confirmed) and its wrapper `.../A43_mordiff-two-by-two/raw/a43_run_gen.sh`, the AD1b script `src/AD1b/ad1b_gen.py`,
  DiffAE's `align.py` and the X3 runner `run_align_unchanged.py`.
- 11 Nov 17:20. One Athena login (lock `/tmp/smadnext-athena.lock`, read-only listing): project folder exists (13 GB
  used, `envs/` empty, no `logs/versions.txt`, so the shared environment has not been built yet); Lmod has
  `Python/3.12.3` (the DGX Python version) besides 3.10.4; `git` at `/usr/bin/git`; no apptainer; no jobs of ours queued.
- 11 Nov 17:30. `prereg.md` written (before any code ran or any image was made).
- 11 Nov 17:35. `src/DG1/dg1_gen.py` written (job-list driven A43 generator; see section 4).
- 11 Nov 17:40. Lead: Athena does not accept jobs yet; account for job files is `plgrestorearc-gpu-a100`; prepare
  everything else. This README started.

## 3. Data

Inputs (all read-only, nothing moved):

| Input | Path | Items | Hash / pin |
|---|---|---|---|
| FRLL DiffAE-aligned photos (X3 a256) | `/mnt/t7/smad_heldout/a41_diffae/data/a41diffae/a256/png256/` | 204 (102 persons × `_03` neutral, `_08` smiling) | X3 data root `SHA256SUMS` c2c06f4a1de9bbc125ef5a2f21271f14e122af20b4a5c42db28ac64fb07d99ff |
| A43 pair list | `/home/narolski/mambamorph-code-a43/smadcvpr/plans/A43/A43_pairs.csv` | 200 draws (100 neutral `03`, 100 smiling); the 100 neutral pairs cover 86 persons | 5cce5fcbf9eacb1eae2c4c5e0021c9d00d9f4b345c18bdb9537b4ff2d1d4ea77 |
| X3 same-person list | `/mnt/t7/smad_heldout/a41_diffae/data/provenance/self_pairs.csv` | 102 (`p_03`, `p_08`) | 4366459d35ea27940fc471d72cee21dfb8075e5efb4e156119d9d89dfd711650 |
| A43 stored DGX images (equivalence references) | `/mnt/t7/smad_heldout/a43/gen/{D20,B20}/png256/` | 204 / 200 | per-file sha in `/mnt/t7/smad_heldout/a43/gen/gen_log.rows.csv` (fb8783da…) |
| Raw FRLL photos (face-recognition references) | `/mnt/t7/Datasety/downloads/frll_base/extracted/{neutral_front,smiling_front}/<stem>.jpg` | 204 used | X3 `provenance/raw_frll.sha256` 142a4151… |
| FRGC / colorFERET pool (landmark ladder AR1) | `/home/narolski/smad-next/experiments/AR1/pool.csv`, frames under `/mnt/t7/smad_next/AR1/src/` | 536 hosts (FRGC 427, FERET 109); 1,072 unique photos (H and S of every host); partner photo B = the partner's S for 536 of 536; partner always from the same database; partner map is a permutation with 88 cycles (largest 163) | — |
| DiffAE checkout | `/mnt/t7/thirdparty/diffae_00c57d3f626f28bf9ed8aff58d90baab25de3af4/repo` | HEAD 00c57d3f626f28bf9ed8aff58d90baab25de3af4, clean | `align.py` 7d7cf0d0… |
| DiffAE checkpoint | `.../checkpoints_download/ffhq256_autoenc/last.ckpt` | 2,722,085,968 bytes | 9bd2ba9e4c22afde8f18958026a4e8e625ef67d2c3ee76bb3aa72f3e67d3b9ca |
| dlib landmark model (aligner) | `/mnt/t7/smad_heldout/a41_diffae/work/align_run/temp/shape_predictor_68_face_landmarks.dat` | — | fbdc2cb80eb9aa7a758672cbfdda32ba6300efe9b6e6c7a299ff7e736b11b92f |

Sets to be produced: see `prereg.md` (set A: 1,016 files; set B: 4,688 files planned). None exists yet.

## 4. Code

- `src/DG1/dg1_gen.py` — the A43 generator driven by a job list (columns `set,pool,rung,name,src_a,src_b,alpha,steps,host,partner`).
  Unchanged image path (pinned repo and checkpoint, `encode`, `encode_stochastic` T = 250, `render` T = 20 or 100, the A43
  `interp()` verbatim with α as an argument, fp16 autocast, batch 16, `save_image`). Sources named `<stem>__flip` are
  the loaded tensor flipped left-right (`torch.flip`, lossless, as AD1b). Empty `src_b` = reconstruction
  `render(x_T(A), z(A))` (the limit of the identical-input mix; A43's slerp is 0/0 there, AD1b). `steps = 0` = genuine
  photo written back through the same `save_image` call, checked pixel-identical to its input. Checks: `python -I`,
  checkpoint sha256, repo commit via git (and a per-file manifest if given), unique output names, finite codes and
  images; refuses an existing output folder.
- Planned: `dg1_lists.py` (job lists and pool alignment inputs), `dg1_validity.py` (manifest and validity numbers on
  the DGX), `dg1_smoke.sbatch`, `dg1_prod.sbatch` (Athena).
- DGX environment used by A43 (and to be reproduced on Athena): `/mnt/t7/thirdparty/diffae_venv` (Python 3.12.3; its own
  site-packages hold pytorch_lightning 2.5.5, torchmetrics 1.8.2, lightning_utilities 0.15.2, lmdb 1.7.3, pandas 2.2.3,
  pytorch_fid 0.3.0, pytz 2025.2, tzdata 2025.2; a `.pth` adds `/home/narolski/mambamorph-code/.venv-spark` with
  torch 2.12.1+cu130, torchvision 0.27.1+cu130, numpy 1.26.4, pillow 12.2.0, scipy 1.17.1, lpips 0.1.4, tqdm 4.68.3,
  PyYAML 6.0.3). DiffAE needs numpy < 2 (`from numpy.lib.function_base import flip` in `experiment.py`).
- Seeds: `LitModel` calls `pl.seed_everything(conf.seed)` with seed 0; DDIM sampling and inversion use η = 0
  (`diffusion/base.py`: the drawn noise is multiplied by σ = 0), so no random number affects a pixel.

## 5. Results

None yet.

## 6. Checks

Planned: the 8-image run of the real command line on the DGX; the equivalence gate on Athena (`prereg.md`); per-image
finite and lossless checks in `dg1_gen.py`; sha256 of every result tar on copy-back.

Facts checked so far: A43 measured on the GB10 13.07 s per image for the 250-step inversion and 1.03 / 5.13 s per
image for 20 / 100-step renders when the GPU was not shared (`/mnt/t7/smad_heldout/a43/gen/gen_log.json`); repeated
runs of this path on the same GB10 differ by at most 1 grey level (A43 gate g0: mean 0.014–0.021).

## 7. Dead ends and failures

None yet.

## 8. Observations and ideas

- In A43's pair list the 100 neutral pairs cover only 86 of the 102 FRLL persons; 16 persons have no two-person morph
  in set A (they still have every one-person rung).
- The DGX GPU was at 96% use with about 20 processes and 5 GB of free host memory at 17:19 (swap full); the AD1b full
  run (PID 1953728) holds 13 GB.

## 9. Open items and next steps

1. Write `dg1_lists.py`; align the 1,072 FRGC/colorFERET photos on the DGX CPU with the unchanged aligner.
2. Run `dg1_gen.py` on 8 images on the DGX with its real command line.
3. Build the pack (code, checkpoint, inputs, job lists) and upload it to `packs/DG1/` with the Athena lock.
4. Write the Athena smoke and production job files with account `plgrestorearc-gpu-a100`.
5. When the lead says an account is accepted: smoke job (≤ 1 GPU-hour), equivalence gate, estimate, production.

## 10. Handover state

No process of this experiment is running. No Athena job submitted. Compute spent: 0 GPU-hours.

## 11. Reproduce from scratch

To be filled as the commands are fixed.
