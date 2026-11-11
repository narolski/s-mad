# Diffusion-autoencoder generation on Athena (DG1): full record

Owner record under `DOCUMENTATION.md`. `prereg.md` is the registration, `result.md` the short verdict, this file the
full record. Code: `/home/narolski/smad-next/src/DG1/`. Large outputs: `/mnt/t7/smad_next/DG1/`. Athena project
folder: `/net/pr2/projects/plgrid/plggrestoration/smad-next` (sub-folders `packs/DG1/`, `envs/DG1/`, `results/DG1/`,
`logs/`, `tasks/DG1/`).

## 1. Question and current answer

11 Nov 2026, 17:35 CET. Status: **preparing; blocked on Athena accepting jobs** (Slurm rejects both grant accounts for
`plgpnarolski`; the lead's watcher will report when an account is accepted; no submission and no probing until then).
DiffAE (diffusion autoencoder) generation on the shared DGX runs at about 157 s per inversion while other jobs share the
GPU, so the diffusion controls are incomplete: the identical-and-mirrored-inputs check (AD1b) covered 32 of 102
persons, FRLL has no expression-matched one-person controls, and no diffusion twin set outside FRLL exists. This
experiment ports the exact generator of the earlier MorDIFF-controls study (A43) to Athena (A100, x86), checks that
Athena reproduces stored DGX images (equivalence gate), then builds set A (FRLL, benchmark-linked, neutral only, 20 and
100 decoding steps) and set B (FRGC and colorFERET, 536 hosts, 20 steps, with a dose series). No detector is scored
here. No answer yet.

## 2. Timeline

- 11 Nov 17:10–17:20. Read `OWNER_BRIEF.md`, `ATHENA.md`, `11_AUDIT_PLAN.md`, `14_CLASS_DEFINITIONS.md`, the MorDIFF
  ladder re-read (AD1) result, the identical-and-mirrored-inputs check (AD1b) prereg and result, the review of the
  expression cue use study (C1b), the A43 ledger README
  (`/home/narolski/mambamorph-code/experiments/A43_mordiff-two-by-two/README.md`), the A43 generator
  `/home/narolski/mambamorph-code-a44/smadcvpr/a43_gen.py` (sha256 fc862ec674dcaee420fc1d88b45b77fea21bcae953aa62cae54032e13a1a8d1e,
  confirmed) and its wrapper `.../A43_mordiff-two-by-two/raw/a43_run_gen.sh`, the AD1b script `src/AD1b/ad1b_gen.py`,
  DiffAE's `align.py` and the X3 runner `run_align_unchanged.py`.
- 11 Nov 17:20. One Athena login (lock `/tmp/smadnext-athena.lock`, read-only listing): project folder exists (13 GB
  used, `envs/` empty, no `logs/versions.txt`, so the shared environment has not been built yet); Lmod has
  `Python/3.12.3` (the DGX Python version) besides 3.10.4; `git` at `/usr/bin/git`; no apptainer; no jobs of ours queued.
- 11 Nov 17:24. `prereg.md` written (before any code ran or any image was made).
- 11 Nov 17:26. `src/DG1/dg1_gen.py` written (job-list driven A43 generator; see section 4).
- 11 Nov 17:27. Lead: Athena does not accept jobs yet; account for job files is `plgrestorearc-gpu-a100`; prepare
  everything else. This README started.
- 11 Nov 17:29. Pool inputs: `python3 -I src/DG1/dg1_lists.py poolin --pool /home/narolski/smad-next/experiments/AR1/pool.csv
  --out /mnt/t7/smad_next/DG1/pool_in` → 1,072 byte-identical copies (sha checked per file; pool.csv sha256
  861019781e79159fe7904eb60e8cda6a57e978023722615dd46023db2f299352). dlib model copied to
  `/mnt/t7/smad_next/DG1/align_run/temp/` (sha fbdc2cb8…, bz2 7d6637b8…).
- 11 Nov 17:29. Aligner started as one process (`run_align_unchanged.py`, cwd `align_run`). It ran at about 3 s per
  photo (DGX load average 114 on 20 cores). Killed at 26 photos to restart in parallel; my `pkill -f` pattern also
  matched and killed its own shell (exit 144), harmless. The 26 written PNGs were checked to open fully at 256 × 256.
- 11 Nov 17:31. `bash src/DG1/dg1_align_parts.sh 4`: the 1,046 remaining photos as 4 symlink parts
  (`/mnt/t7/smad_next/DG1/pool_in_parts/p0..p3`), 4 aligner processes into `/mnt/t7/smad_next/DG1/pool_a256`, logs
  `/mnt/t7/smad_next/DG1/pool_align_p<k>.log` (about 1 photo per second together). Each aligner process also starts 8
  idle multiprocessing workers (align.py creates `Pool(8)` but its parallel code is commented out).
- 11 Nov 17:33. Written: `src/DG1/dg1_env.sh`, `dg1_run_task.sh`, `dg1_smoke.sbatch`, `dg1_prod.sbatch`,
  `dg1_pack.sh`, `dg1_validity.py`, `dg1_dgx_test.sh` (section 4).
- 11 Nov 17:42. Alignment finished: 1,072 of 1,072 photos aligned (every photo had a face; none dropped), all open as
  256 × 256 RGB. The 400 files that AD1b also aligned (`/mnt/t7/smad_next/AD1b/pool_a256`) are byte-identical to
  ours. Hash list `/mnt/t7/smad_next/DG1/pool_a256.sha256` (sha256 77fc3fe8e241a06b00e8f96cce14e1125f56e9f16c7ae47653ced0a4d73b75f0).
  Symlink parts removed.
- 11 Nov 17:43. Job lists: `.venv-spark/bin/python -I src/DG1/dg1_lists.py lists --pool .../AR1/pool.csv --pool-a256
  /mnt/t7/smad_next/DG1/pool_a256 --frll-a256 /mnt/t7/smad_heldout/a41_diffae/data/a41diffae/a256/png256 --a43-pairs
  /home/narolski/mambamorph-code-a43/smadcvpr/plans/A43/A43_pairs.csv --self-pairs
  /mnt/t7/smad_heldout/a41_diffae/data/provenance/self_pairs.csv --out /mnt/t7/smad_next/DG1/jobs` → `eq.csv` (8 jobs,
  sha 3dfe6828…), `smoke8.csv` (10 jobs, c8ba541a…), `setA.csv` (914 jobs, 8491b41a…), `setB_s0..3.csv` (908 / 904 /
  896 / 908 jobs; 403 / 404 / 404 / 403 encodes; 640 / 636 / 628 / 640 renders), summary
  `/mnt/t7/smad_next/DG1/jobs/lists_summary.json`. Set B counts: G 1,072, REC / MIR / SAME / X 536 each, DOSE 100 per
  fraction.
- 11 Nov 17:43. DGX 8-image check started: `nohup bash src/DG1/dg1_dgx_test.sh > /mnt/t7/smad_next/DG1/dgx_test.log`
  (GPU had about 33 GB in use by other processes, 38 GB host memory available).
- 11 Nov 17:44. Pack built: `bash src/DG1/dg1_pack.sh` → `/mnt/t7/smad_next/DG1/packs/dg1_pack.tar`, 2,880,163,840 bytes,
  sha256 670b55f19770811505ca00c2be1ea3681440f8190c4e79b4e1c2a68f211336c5, 1,276 input photos. Upload to
  `/net/pr2/projects/plgrid/plggrestoration/smad-next/packs/DG1/` started with the Athena lock (rsync), together with
  `dg1_env.sh`, `dg1_run_task.sh`, `dg1_smoke.sbatch`, `dg1_prod.sbatch` (copies in `/mnt/t7/smad_next/DG1/packs/`).
- 11 Nov 17:44–17:46. Upload done: `flock -w 600 /tmp/smadnext-athena.lock rsync -a --partial -e "ssh -o BatchMode=yes"
  <the six files> plgpnarolski@athena.cyfronet.pl:/net/pr2/projects/plgrid/plggrestoration/smad-next/packs/DG1/`, exit
  0, 2,880,875,330 bytes in 82 s (35 MB/s). The pack's sha256 is checked again inside every job (`dg1_run_task.sh`),
  not on the login node.

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
- `src/DG1/dg1_lists.py poolin` — byte-identical copies of the pool photos (H and S of each host) as
  `<db>_<subject>_H.png` / `_S.png` (the aligner's input folder). `dg1_lists.py lists` — job lists `eq.csv`
  (equivalence gate), `smoke8.csv` (8 generated images of both sets at 20 and 100 steps + 2 genuine writes),
  `setA.csv`, `setB_s0..3.csv` (hosts cut into 4 shards along the partner cycles, so a partner's photo is mostly encoded in
  the same shard), `lists_summary.json`. Drops hosts whose H photo has no face after alignment; drops a SAME job when
  the host's S photo is missing and an X / DOSE job when the partner's S photo is missing.
- `src/DG1/dg1_align_parts.sh N` — the unchanged DiffAE aligner (`run_align_unchanged.py` + `align.py` sha 7d7cf0d0…,
  cwd `/mnt/t7/smad_next/DG1/align_run` with the dlib model in `temp/`) on N symlink parts of the photos not yet aligned.
- `src/DG1/dg1_pack.sh` — builds `/mnt/t7/smad_next/DG1/packs/dg1_pack.tar` (+ `.sha256`): `dg1pack/repo` (DiffAE with
  `.git`), `repo_manifest.sha256`, `ckpt/last.ckpt`, `inputs/a256` (FRLL X3 a256 + aligned pool), `jobs/*.csv`,
  `code/dg1_gen.py`, `MANIFEST.sha256`.
- `src/DG1/dg1_env.sh` — sourced inside an Athena job after `module load Python/3.12.3`: builds once (or verifies)
  `$G/envs/DG1/venv`, torch 2.12.1 / torchvision 0.27.1 from download.pytorch.org (cu130 if driver ≥ 580, else cu128,
  then cu126), then the other DGX pins one by one under a constraints file holding torch; a pin that fails is replaced
  by the newest that installs and recorded in `$G/envs/DG1/versions.txt` (with `pip freeze`).
- `src/DG1/dg1_run_task.sh TAG LIST...` — one task in `$SCRATCH_LOCAL`: copies and sha-checks the pack, checks its
  manifest, runs `dg1_gen.py` per job list, logs GPU memory every 10 s, writes `$G/results/DG1/DG1_<TAG>.tar` + `.sha256`;
  refuses an existing result tar.
- `src/DG1/dg1_smoke.sbatch` — smoke job (50 min limit, 1 A100, `-c 8 --mem=64G -C localfs`, account
  `plgrestorearc-gpu-a100`): env, then `eq` and `smoke8`. `src/DG1/dg1_prod.sbatch` — array 0–4: `setA`,
  `setB_s0..3`; `--time` set at submission from the measured speed (at most 4 h).
- `src/DG1/dg1_validity.py equiv` — equivalence gate numbers (pixel differences, glint cosine between the Athena and
  DGX file, image statistics against the between-image spread of the 204 / 200 stored A43 files).
  `dg1_validity.py manifest` — manifest (image, set, rung, host, partner, steps, alpha, seed, generation run, hashes,
  cosines, statistics) and per-rung validity numbers (`manifest.csv`, `validity.json`, `validity.csv`).
- `src/DG1/dg1_dgx_test.sh` — the 8-image check on the DGX (inputs as a symlink folder, the A43 DiffAE venv, then
  `dg1_validity.py manifest`), outputs `/mnt/t7/smad_next/DG1/dgx_test/`.
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
