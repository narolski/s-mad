# Diffusion-autoencoder generation on Athena (DG1): full record

Owner record under `DOCUMENTATION.md`. `prereg.md` is the registration, `result.md` the short verdict, this file the
full record. Code: `/home/narolski/smad-next/src/DG1/`. Large outputs: `/mnt/t7/smad_next/DG1/`. Athena project
folder: `/net/pr2/projects/plgrid/plggrestoration/smad-next` (sub-folders `packs/DG1/`, `envs/DG1/`, `results/DG1/`,
`logs/`, `tasks/DG1/`).

## 1. Question and current answer

11 Nov 2026, 18:15 CET. Status: **ready to submit the smoke job; blocked on Athena accepting jobs** (Slurm rejects
both grant accounts for `plgpnarolski`; the lead's watcher reports when an account is accepted; no submission and no
probing until then). Pack, environment script, job files and job lists are on Athena; the 8-image check passed on the DGX.
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
- 11 Nov 17:44–18:10. **DGX 8-image check passed** (`src/DG1/dg1_dgx_test.sh`, log `/mnt/t7/smad_next/DG1/dgx_test.log`,
  outputs `/mnt/t7/smad_next/DG1/dgx_test/gen/smoke8/`, validity `/mnt/t7/smad_next/DG1/dgx_test/validity/`):
  `dg1_gen.py` on `smoke8.csv` with the real command line; 8 encodes in one batch took 1,145 s (143 s per image on
  the shared GB10); renders 17–18 s per 20-step image and 87 s per 100-step image (shared); all finite, min std 0.206;
  genuine writes 2 of 2 pixel-identical to their inputs; repo check: git clean at the pinned commit and 70 of 70
  manifest files equal. The DGX re-render of A43's reconstruction 001_03 (20 steps) differs from the stored A43 D20 file
  by mean 0.024, max 1 grey level (same-machine reproducibility baseline). `dg1_validity.py manifest` ran on the 10
  files (every face found; every two-person image verifies against both contributors at 0.239399; DOSE α 0.1 verifies
  the host only, cosine 0.93 host / 0.18 partner). Contact sheet `/mnt/t7/smad_next/DG1/dgx_test/contact_sheet.png`
  (rows: FRLL REC20, MIR100, CONF20, X100; pool REC20, SAME20, X20, DOSE10): images look as expected; the CONF mix
  shows the known coloured spots of neutral+smiling DiffAE mixes.
- 11 Nov 18:11. Plumbing test of `dg1_run_task.sh` on the DGX with a mock interpreter (fake `DG1_PY` that only makes
  the output folder) and mock `G` / `SCRATCH_LOCAL` under `/mnt/t7/smad_next/DG1/mock_plumbing` (removed after): pack
  sha OK, pack manifest OK, unpack 66 s, both job lists run, result tar + sha written and verified. The packed DiffAE
  repo extracts clean (`git status --porcelain` empty, manifest OK). `bash -n` passes for every shell file.
- 11 Nov 18:12. Fixes before any Athena job: (1) `dg1_run_task.sh` had `( sha256sum -c MANIFEST ) && echo ok`, which
  under `set -e` would not stop on a manifest failure; split into two lines. (2) `dg1_env.sh` now builds the environment
  only when `DG1_ENV_BUILD=1` (set in the smoke job only); production tasks exit 5 if the environment is missing, so
  parallel array tasks can never run `venv --clear` on a shared environment. Re-uploaded the four small scripts (rsync
  exit 0). Current sha256: `dg1_env.sh` 56a1a9a3…, `dg1_run_task.sh` 2e0b1f54…, `dg1_smoke.sbatch` 4f771aba…,
  `dg1_prod.sbatch` d9e40507…. The pack itself is unchanged (`code/dg1_gen.py` in the pack = `src/DG1/dg1_gen.py`,
  sha 21a6ecb7…).

- 11 Nov 18:29. Lead: Athena accepts jobs since 18:25 (account `plgrestorearc-gpu-a100`). Smoke job may go; then
  production as registered up to 150 GPU-hours; check jobs at most every 2 minutes through the lock.
- 11 Nov 18:31. **Smoke job submitted: Athena job 3544197** (`sbatch --parsable packs/DG1/dg1_smoke.sbatch` from
  `/net/pr2/projects/plgrid/plggrestoration/smad-next`, one connection under the lock). Log
  `/net/pr2/projects/plgrid/plggrestoration/smad-next/logs/DG1-smoke-3544197.out`; result tar
  `.../results/DG1/DG1_smoke_3544197.tar`. If it fails: read the log, fix, re-upload the changed script, resubmit
  (the environment folder `envs/DG1/venv` may need removal by the owner if the build broke half-way).

- 11 Nov 18:31–18:39. **Smoke job 3544197 FAILED after 4 s** (node t0016, exit 1:0, 0.001 GPU-hours): `module load
  Python/3.12.3` is refused on Athena unless its prerequisite `GCCcore/13.3.0` is loaded first (`module spider
  Python/3.12.3`). Nothing else ran. A first status check at 18:35 returned nothing because `flock -w 120` on the
  single shared lock timed out (another owner's long upload); a flock timeout is a local wait, not a refused login.
- 11 Nov 18:38. Lead: (1) `-C localfs` gives only 4.0 GB of `$SCRATCH_LOCAL` on Athena (the lead's first smoke died
  with 'No space left on device'); use `-C memfs` and `$MEMFS` (RAM disk, counts toward `--mem`, at most 120G per
  GPU to stay billed as one GPU). Our task would also have failed there: it copied the 2.9 GB tar and then extracted
  it (5.8 GB peak). (2) Two locks from now on: short commands take `/tmp/smadnext-athena-cmd.lock` (`-w 300`),
  transfers take `/tmp/smadnext-athena.lock` (`-w 1800`).
- 11 Nov 18:41. Fixes: both job files load `GCCcore/13.3.0 Python/3.12.3`, use `#SBATCH -C memfs`, `TMPDIR=$MEMFS/tmp`,
  `--mem=64G` (data in the RAM disk about 3 GB for the extracted pack + up to a few GB of pip temporary files; process
  about 10 GB). `dg1_run_task.sh` now checks the pack's sha256 on the project store and extracts it straight into
  `$MEMFS` (no copy of the tar). Upload of the four small scripts queued on the transfer lock, then resubmission.

- 11 Nov 18:47. Scripts uploaded (transfer lock, rsync exit 0; sha256 `dg1_run_task.sh` 476d1939…, `dg1_smoke.sbatch`
  de19e077…, `dg1_prod.sbatch` ad59138c…, `dg1_env.sh` unchanged 56a1a9a3…). **Smoke job resubmitted: Athena job
  3544215** (log `.../smad-next/logs/DG1-smoke-3544215.out`, result `.../results/DG1/DG1_smoke_3544215.tar`).

- 11 Nov 18:47–18:59. **Smoke job 3544215 FAILED after 11 min 6 s** (node t0016, driver 595.91.07, so the cu130 torch
  build, as on the DGX; 0.185 GPU-hours). The environment built (torch 2.12.1+cu130, torchvision 0.27.1+cu130, every pin
  installed, about 10 min on the project store), the pack checked and unpacked into `$MEMFS` in 7 s, then `dg1_gen.py`
  stopped at `from numpy.lib.function_base import flip` (DiffAE `experiment.py`): the venv held **numpy 2.5.4**,
  although `numpy==1.26.4` had installed as the first pin (no deviation was recorded). Some later install upgraded
  it; none of the pinned packages declares numpy >= 2 in its metadata (checked on the DGX copies), so the cause is not
  identified. The environment check did not test versions, which let this through.
- 11 Nov 19:02. Fix in `dg1_env.sh` (sha256 fb137945…): numpy 1.26.4 and pillow 12.2.0 join torch and torchvision in
  the constraints file; the other pins install in one pip call under the constraints (one by one only if that
  fails); `pip check` is logged; the environment check now asserts numpy 1.26.4, pillow 12.2.0, torch 2.12.1,
  torchvision 0.27.1 and imports `numpy.lib.function_base`; an existing venv whose torch is already pinned is
  repaired instead of rebuilt (saves the 10-minute torch install).
- 11 Nov 19:03. **Smoke job resubmitted: Athena job 3544800** (log `.../smad-next/logs/DG1-smoke-3544800.out`).

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

Produced so far (DGX):

| Item | Path | Items | Hash |
|---|---|---|---|
| Pool photos, byte-identical copies (aligner input) | `/mnt/t7/smad_next/DG1/pool_in/` | 1,072 | per-file sha checked against `AR1/src` |
| Pool photos, DiffAE-aligned (256 px) | `/mnt/t7/smad_next/DG1/pool_a256/` | 1,072 (0 dropped) | list `/mnt/t7/smad_next/DG1/pool_a256.sha256` 77fc3fe8… |
| DiffAE repo file manifest | `/mnt/t7/smad_next/DG1/repo_manifest.sha256` | 70 tracked files | fb5d24d3… |
| Job lists | `/mnt/t7/smad_next/DG1/jobs/` (`eq`, `smoke8`, `setA`, `setB_s0..3`, `lists_summary.json`) | 8 / 10 / 914 / 908+904+896+908 jobs | see timeline 17:43 |
| Athena pack | `/mnt/t7/smad_next/DG1/packs/dg1_pack.tar` (+ `.sha256`); copy on Athena `.../smad-next/packs/DG1/dg1_pack.tar` | 2,880,163,840 bytes | 670b55f19770811505ca00c2be1ea3681440f8190c4e79b4e1c2a68f211336c5 |
| DGX 8-image check | `/mnt/t7/smad_next/DG1/dgx_test/` | 10 files + validity | `gen/smoke8/gen_rows.csv` |

Planned sets: set A 914 files (102 genuine writes + 812 renders); set B 3,616 files (1,072 genuine writes + 2,544
renders: REC / MIR / SAME / X 536 each at 20 steps, DOSE 4 × 100). An earlier line of this README said 4,688 for set B;
that was an arithmetic slip, corrected at 18:16.

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

Done:
- DGX 8-image check of the real command line (timeline 17:44–18:10): finite images, genuine writes lossless, repo and
  checkpoint pinned, validity script runs end to end.
- Same-machine reproducibility baseline: the DGX re-render of A43's D20 001_03 equals the stored file within mean 0.024,
  max 1 grey level (A43's own gate g0: mean 0.014–0.021, max 1).
- Pool alignment: 400 of 400 files shared with AD1b's alignment are byte-identical.
- Plumbing test of the Athena task script with a mock interpreter; packed repo extracts clean.
- A43 reference speeds on the unshared GB10: 13.07 s per 250-step inversion, 1.03 / 5.13 s per 20 / 100-step render
  (`/mnt/t7/smad_heldout/a43/gen/gen_log.json`).

Planned: the equivalence gate on Athena (`prereg.md`); sha256 of every result tar on copy-back.

Not verified: that `module load Python/3.12.3` and the pinned wheels install on an Athena compute node (first seen in the
smoke job); that compute nodes reach download.pytorch.org and PyPI; that `git` exists on compute nodes (the per-file
manifest check runs regardless).

## 7. Dead ends and failures

- 17:31: `pkill -f "run_align_unchanged.py.*DG1/pool_in"` also matched the shell running it (its own command line
  contains the pattern) and killed that shell (exit 144). It still stopped the one slow aligner process. Lesson: write
  multi-step process control into a script file or use patterns that cannot match themselves.
- 18:12: two shell-logic faults found by reading before any Athena job ran (manifest check that `set -e` would not stop
  on; environment rebuild possible from parallel tasks). Fixed (timeline 18:12).

## 8. Observations and ideas

- In A43's pair list the 100 neutral pairs cover only 86 of the 102 FRLL persons; 16 persons have no two-person morph
  in set A (they still have every one-person rung).
- The DGX GPU was at 96% use with about 20 processes and 5 GB of free host memory at 17:19 (swap full); the AD1b full
  run (PID 1953728) holds 13 GB.

## 9. Open items and next steps

1. Wait for the lead's message that an Athena account is accepted (no submission, no probing before).
2. Submit the smoke job: `flock -w 120 /tmp/smadnext-athena.lock ssh -o BatchMode=yes plgpnarolski@athena.cyfronet.pl
   'cd /net/pr2/projects/plgrid/plggrestoration/smad-next && sbatch --parsable packs/DG1/dg1_smoke.sbatch'`.
3. Fetch its tar (`bash src/DG1/dg1_fetch.sh smoke_<jobid>`), run the equivalence gate
   (`.venv-spark/bin/python -I src/DG1/dg1_validity.py equiv --gen /mnt/t7/smad_next/DG1/gen/smoke_<jobid>/out_smoke_<jobid>/eq
   --ref /mnt/t7/smad_heldout/a43/gen --out experiments/DG1_diffusion-generation-athena/equivalence.json`), read the A100
   speeds from `gen_log.json`, write the estimate into `result.md`.
4. Submit production (`dg1_prod.sbatch`, array 0–4, `--time` from the estimate, at most 4 h), tell the lead when set A
   exists, fetch, run `dg1_validity.py manifest` on set A, then on set B.

## 10. Handover state

19:03: Athena smoke job 3544800 submitted (3544197 failed at module load, 3544215 at the numpy version; see timeline). Before that: no Athena job. Files staged on Athena:
`/net/pr2/projects/plgrid/plggrestoration/smad-next/packs/DG1/{dg1_pack.tar,dg1_pack.tar.sha256,dg1_env.sh,dg1_run_task.sh,dg1_smoke.sbatch,dg1_prod.sbatch}`.
Compute spent: 0 Athena GPU-hours; DGX GB10 about 0.45 GPU-hours (8-image check, shared) plus CPU alignment.

## 11. Reproduce from scratch

```
S=/home/narolski/smad-next/src/DG1; PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
python3 -I $S/dg1_lists.py poolin --pool /home/narolski/smad-next/experiments/AR1/pool.csv --out /mnt/t7/smad_next/DG1/pool_in
mkdir -p /mnt/t7/smad_next/DG1/align_run/temp   # + shape_predictor_68_face_landmarks.dat(.bz2) from /mnt/t7/smad_heldout/a41_diffae/work/align_run/temp
bash $S/dg1_align_parts.sh 4                    # wait until the 4 aligner processes end; expect 1,072 files in pool_a256
$PY -I $S/dg1_lists.py lists --pool /home/narolski/smad-next/experiments/AR1/pool.csv --pool-a256 /mnt/t7/smad_next/DG1/pool_a256 \
  --frll-a256 /mnt/t7/smad_heldout/a41_diffae/data/a41diffae/a256/png256 \
  --a43-pairs /home/narolski/mambamorph-code-a43/smadcvpr/plans/A43/A43_pairs.csv \
  --self-pairs /mnt/t7/smad_heldout/a41_diffae/data/provenance/self_pairs.csv --out /mnt/t7/smad_next/DG1/jobs
bash $S/dg1_dgx_test.sh                         # 8-image check on the DGX
bash $S/dg1_pack.sh                             # /mnt/t7/smad_next/DG1/packs/dg1_pack.tar
# upload pack + dg1_env.sh dg1_run_task.sh dg1_smoke.sbatch dg1_prod.sbatch to Athena packs/DG1 (rsync under the lock)
# Athena: sbatch packs/DG1/dg1_smoke.sbatch ; then sbatch --time=<est> packs/DG1/dg1_prod.sbatch
bash $S/dg1_fetch.sh <TAG...>                   # copy back + sha256 + unpack into /mnt/t7/smad_next/DG1/gen/<TAG>
$PY -I $S/dg1_validity.py equiv --gen <.../eq> --ref /mnt/t7/smad_heldout/a43/gen --out <json>
$PY -I $S/dg1_validity.py manifest --gen-root /mnt/t7/smad_next/DG1/gen/<TAG> --pool /home/narolski/smad-next/experiments/AR1/pool.csv --out-dir <dir>
```
