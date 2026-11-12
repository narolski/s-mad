# Diffusion-autoencoder generation on Athena (DG1): full record

Owner record under `DOCUMENTATION.md`. `prereg.md` is the registration, `result.md` the short verdict, this file the
full record. Code: `/home/narolski/smad-next/src/DG1/`. Large outputs: `/mnt/t7/smad_next/DG1/`. Athena project
folder: `/net/pr2/projects/plgrid/plggrestoration/smad-next` (sub-folders `packs/DG1/`, `envs/DG1/`, `results/DG1/`,
`logs/`, `tasks/DG1/`).

## 1. Question and current answer

11 Nov 2026, 21:20 CET. Status: **production finished; add-on running (2 of 8 tasks done, 6 pending on Athena).**
The equivalence gate passed (Athena reproduces stored DGX A43 images within mean 0.02–0.06 grey levels). Set A (FRLL, 914
files) and set B (FRGC/colorFERET, 3,616 files) exist on T7 with manifests and validity numbers; 3.77 Athena GPU-hours
used so far. DiffAE (diffusion autoencoder) generation on the shared DGX runs at about 157 s per inversion while other jobs share the
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

- 11 Nov 19:06–19:11. **Smoke job 3544800 COMPLETED** (node t0012, 4 min 57 s = 0.083 GPU-hours, exit 0:0). Environment
  repaired (numpy 1.26.4, pillow 12.2.0, torch 2.12.1+cu130, torchvision 0.27.1+cu130, pytorch-lightning 2.5.5; record
  `/net/pr2/projects/plgrid/plggrestoration/smad-next/envs/DG1/versions.txt`, copy in the result tar). Pack sha OK,
  unpack 11 s, `eq` (12 encodes in 41 s = 3.38 s per image; 8 renders at 20 steps, 0.33–0.37 s per image in batches
  of 4) and `smoke8` (8 encodes in 26 s = 3.28 s per image; 100-step renders about 4 s for a batch of one), all finite,
  genuine writes 2 of 2 lossless, repo git-clean and 70 of 70 manifest files equal, GPU peak 10,249 MiB. Result
  `.../results/DG1/DG1_smoke_3544800.tar`, fetched with `bash src/DG1/dg1_fetch.sh smoke_3544800` (sha OK) into
  `/mnt/t7/smad_next/DG1/gen/smoke_3544800/`.
- 11 Nov 19:13. **Equivalence gate: equivalent.** `.venv-spark/bin/python -I src/DG1/dg1_validity.py equiv --gen
  /mnt/t7/smad_next/DG1/gen/smoke_3544800/out_smoke_3544800/eq --ref /mnt/t7/smad_heldout/a43/gen --out
  experiments/DG1_diffusion-generation-athena/equivalence.json`: per-image mean |difference| 0.017–0.059 grey levels
  (pooled 0.032), max 4, 5–15% of pixels differ (by 1–4 levels), glint cosine Athena vs DGX ≥ 0.99989; the largest
  change of any image statistic is 0.01 of the between-image standard deviation of that rung (Laplacian variance).
  Cross-check beside it (not registered): the 10 `smoke8` files from Athena vs the same 10 jobs on the DGX:
  mean 0.019–0.066, max 4, genuine writes identical (`smoke8_athena_vs_dgx.json`). Reading: Athena images may be
  combined with DGX images of this generator; every manifest row still carries `gen_run`. **[Withdrawn 19:45 by
  amendment 1 and review finding 7: DGX and Athena images are never combined inside one contrast.]**
- 11 Nov 19:14. Estimate (upper bound with margin: 3.4 s per encode, 0.4 s per 20-step render, 2.0 s per 100-step
  render, 2 min overhead per task): set A (306 encodes, 406 + 406 renders) about 36 min; each set B shard (about 404
  encodes, about 636 renders) about 30 min; total about 2.6 GPU-hours, at most 3.5. Timing sent to the lead.
- 11 Nov 19:15. **Production submitted: Athena array job 3545841** (`sbatch --parsable --time=01:30:00
  packs/DG1/dg1_prod.sbatch`; tasks 0 = setA, 1–4 = setB_s0..s3; logs `.../smad-next/logs/DG1-prod-3545841_<k>.out`;
  results `.../results/DG1/DG1_<list>.tar`). If a task fails: read its log; the result tar name is refused if it
  exists, so a rerun of a failed task needs no cleanup unless its tar was written.

- 11 Nov 19:25. Production tasks started: 3545841_0 (set A, node t0013, 19:24:40), _1 (setB_s0, t0010, Slurm id
  3545862, 19:25:40), _2 (t0019), _3 (t0010), _4 (t0013, 19:31). Set A encoding at batch 16: 3.04 s per image.
- 11 Nov 19:28. Lead: independent pre-run review in (`experiments/reviews/PRERUN_DG1_20261111.md`, GO WITH FIXES;
  production stays). Reviewer's CPU checks copied to `/mnt/t7/smad_next/DG1/review_checks/` (`pair_input_stats.json`,
  `inputs_vs_renders.png`, `find_twoface.py`). Instructions: (1) reading registration before the validity table on
  production images; (2) add-on array approved (about 4 A100-hours), register first; (3) manifest columns for person
  use and cue flags; (4) record corrections; (5) container image for new jobs where packages allow.
- 11 Nov 19:45. `prereg.md` amendment 1 (reading registration), amendment 2 (add-on) and a deviations section written
  (no production image read yet).
- 11 Nov 19:30–19:31. Add-on code: `src/DG1/dg1_addon.py` (modes rec / mix / noise / sem / fresh; codes and fresh draws
  saved; θ checked before rendering; outputs always written), `src/DG1/dg1_addon_lists.py`, `dg1_addon_task.sh` (tar
  always written, then the generator's exit code), `dg1_addon.sbatch` (array 0–7, `-C memfs`, 64G, existing DG1
  environment), `dg1_addon_pack.sh`. Lists: `.venv-spark/bin/python -I src/DG1/dg1_addon_lists.py --pool
  .../AR1/pool.csv --pn1-split .../PN1_protocol-network-first-tests/split/ladder_split.csv --prod-jobs
  /mnt/t7/smad_next/DG1/jobs --pool-a256 /mnt/t7/smad_next/DG1/pool_a256 --out /mnt/t7/smad_next/DG1/addon_jobs`:
  8 shards of 67 hosts, 1,106–1,226 jobs and 201–203 encodes each; 536 per host pool, 255 dose hosts (191 test-read
  ∪ 100 production dose hosts, 36 in both) × 8 dose renders; totals 7,400 renders at 20 steps, 2,144 at 100 steps,
  about 1,616 encodes; summary `/mnt/t7/smad_next/DG1/addon_jobs/addon_lists_summary.json`.
- 11 Nov 19:31. DGX 8-image check of the add-on: first attempt died with CUDA out-of-memory at model load (shared
  GB10, about 40 GB in use by 19 processes; log `/mnt/t7/smad_next/DG1/dgx_test/addon_test8_attempt0_oom.log`);
  restarted with up to 6 attempts 60 s apart (`src/DG1/dg1_addon_dgx_test.sh`).

- 11 Nov 19:33–19:36. **Slow node:** production tasks 3545841_1 (setB_s0) and _3 (setB_s2) both landed on node t0010 and
  encoded at 18.8 and 18.4 s per image (first batch of 16: 300 s and 294 s), against 3.0–3.1 s on t0013 and t0019; at
  that speed they would exceed the 1:30 limit. Both cancelled at about 10 min (my own jobs) and resubmitted as
  **array 3545877** (`sbatch --parsable --array=1,3 --exclude=t0010 --time=01:30:00 packs/DG1/dg1_prod.sbatch`;
  logs `DG1-prod-3545877_1.out`, `_3.out`). t0010 had 124 of 128 CPUs allocated; cause of the slowness not
  identified (cgroup gives our job its 8 cores). Future DG1 jobs exclude t0010.

- 11 Nov 19:34–19:54. **DGX 8-image check of the add-on passed** (attempt 1 of `src/DG1/dg1_addon_dgx_test.sh`; log
  `/mnt/t7/smad_next/DG1/dgx_test/addon_test8_attempt1.log`; outputs `/mnt/t7/smad_next/DG1/dgx_test/addon_test8/`):
  4 encodes (H, flip H, S, partner S) in 986 s on the shared GB10, 9 renders (rec, mix, mirror mix, two fresh draws,
  noise-only, semantic-only, 100-step mix, same-person dose 0.1), all finite, θ finite (1.536–1.555), `codes.npz`
  (4 × z 512 and x_T 3 × 256 × 256, float32) and `fresh.npz` (2 draws, seeds 462287824053858823 and
  195321709206190538, std 1.0) written. Contact sheet `/mnt/t7/smad_next/DG1/dgx_test/addon_contact_sheet.png`.
- 11 Nov 19:55. Mock plumbing test of `dg1_addon_task.sh` with a fake interpreter that exits 3: both packs
  sha-checked and unpacked, result tar written and verified, task exit code 3 propagated. Add-on pack
  `/mnt/t7/smad_next/DG1/packs/dg1_addon_pack.tar` (sha256 ee3c589068b9a449e36203b95fec6a3fed7f8348d37b037566d28ae6345db8df;
  `code/dg1_addon.py` sha 6a0c9711…, 8 shard lists + test list), `dg1_addon_task.sh` cfbda68d…, `dg1_addon.sbatch`
  85a7b941… (account `plgmultivision-gpu-a100` as the lead asked at 19:48, `--exclude=t0010`, 2:00 limit, `-C memfs`).
- 11 Nov 19:55. **Add-on array submitted: Athena job 3545907** (tasks 0–7 = `addon_s0..7`, account
  `plgmultivision-gpu-a100`; logs `.../smad-next/logs/DG1-addon-3545907_<k>.out`; results
  `.../results/DG1/DG1_addon_s<k>.tar`). Estimate per shard: about 202 encodes × 3.1 s + about 925 renders at 20 steps
  × 0.3 s + 268 at 100 steps × 1.5 s ≈ 25 min; 8 shards ≈ 3.3 GPU-hours.
- 11 Nov 19:48. Lead moved our pending jobs (the production tasks 3545877_1 and _3) in place to account
  `plgmultivision-gpu-a100` (higher priority tonight); smoke jobs and production tasks 3545841_0, _2, _4 ran on
  `plgrestorearc-gpu-a100`.

- 11 Nov 19:53. **Set A finished** (task 3545841_0 = Slurm id 3545857, node t0013, 1,705 s task / 1,646 s generator,
  0.47 GPU-hours): 914 files, all finite, min std 0.172, genuine writes 102 of 102 lossless, GPU peak 13,251 MiB;
  306 encodes at 3.16 s; renders 0.24–0.27 s (20 steps) and 1.24–1.42 s (100 steps) per image. Set B shard 1
  (task 3545841_2, node t0019) finished at 19:51 (1,454 s). Both fetched: `bash src/DG1/dg1_fetch.sh setA setB_s1`
  (sha OK; `DG1_setA.tar` sha256 053ca8f2f98ebdebeadfb777de18d6d72782852298383b39bd7f6191bc7e9399) into
  `/mnt/t7/smad_next/DG1/gen/setA/out_setA/setA/` and `/mnt/t7/smad_next/DG1/gen/setB_s1/out_setB_s1/setB_s1/`.
  Lead told that set A exists (19:56).
- 11 Nov 19:56. Set A manifest and validity started on the DGX (after amendment 1): `.venv-spark/bin/python -I
  src/DG1/dg1_validity.py manifest --gen-root /mnt/t7/smad_next/DG1/gen/setA --pool .../AR1/pool.csv --out-dir
  /mnt/t7/smad_next/DG1/validity/setA --gen-run athena_DG1` (log `/mnt/t7/smad_next/DG1/validity_setA.log`); about
  1,118 embeddings at about 1.4 per second on the shared GB10.
- 11 Nov 19:58. `src/DG1/dg1_manifest_extra.py` written (review findings 5, 6, 8): PNG bytes, verification against the
  independent reference, database, partner cycle id, PN1 role / test-read / validation-reserved host and partner,
  PD1-training person, wedge / greyscale / twin-pair / shared-date flags, pair disagreement; per-pool summaries for
  all, unflagged and per database.

- 11 Nov 20:03. Set B shard 3 finished (task 3545841_4, node t0013, 1,577 s, 0.44 GPU-h) and fetched (`DG1_setB_s3.tar`
  sha256 1c3f3678…; shard 1 tar 8b917ce3…). Both: all finite, genuine writes 268 of 268 lossless, 3.01 / 3.19 s per
  inversion, GPU peak 13,249 MiB.
- 11 Nov 20:07. Set A validity done (`/mnt/t7/smad_next/DG1/validity/setA/`: `manifest.csv`, `validity.csv`,
  `validity.json`; then `dg1_manifest_extra.py` → `manifest_full.csv`, `validity_full.json`; copies of the two summaries
  in `experiments/DG1_diffusion-generation-athena/validity/`). Table in section 5.
- 11 Nov 20:08. Athena start estimates: production shards 0 and 2 (3545877) 20:19; add-on (3545907) 12 Nov 06:37.
- 11 Nov 20:09. Set B validity started per shard (shards 1 and 3 now, sequentially; logs
  `/mnt/t7/smad_next/DG1/validity_setB_s<k>.log`, outputs `/mnt/t7/smad_next/DG1/validity/setB_s<k>/`);
  `src/DG1/dg1_merge_manifests.py` merges the shard manifests (paths relative to `/mnt/t7/smad_next/DG1/gen`) before
  `dg1_manifest_extra.py` adds the person-use and flag columns.

- 11 Nov 20:17–20:28. Task 3545877_1 (set B shard 0, account plgmultivision) started on node t0016: about 9 min from
  start to the first encode (environment check and import from the project store), then 6.1 s per inversion (16 in
  97 s), about twice t0013/t0019 but within the 1:30 limit; left running. Task 3545877_3 and the add-on wait with
  'ReqNodeNotAvail' (Slurm lists t0001–t0031, t0034–t0036, t0038–t0047 as unavailable).
- 11 Nov 20:31. Validity of set B shards 1 and 3 done (`/mnt/t7/smad_next/DG1/validity/setB_s1/`, `setB_s3/`).
- Note: `versions.txt` says 'torch index ' (blank) because the repair run of job 3544800 read
  `envs/DG1/torch_index.txt`, which the first build (3544215) had not written; the torch build is cu130
  (`torch 2.12.1+cu130` in the same file and in every `gen_log.json`).

- 11 Nov 20:43. Lead: /mnt/t7 hit 100% at about 20:40 (writes failed); new rule: check `df -h /mnt/t7` before any write
  over 1 GB, keep 50 GB free, leave the add-on's saved codes and noise maps on Athena, no second local copies of
  packs. Checked at 20:44: 57 GB free; the three fetched tars re-verified (`sha256sum -c`: setA, setB_s1, setB_s3 OK)
  and every extracted image re-hashed against its generation row (setA 914, setB_s1 904, setB_s3 908, smoke 18:
  0 mismatches); the validity manifests of setA / setB_s1 / setB_s3 were written before 20:40 and are complete (914 /
  904 / 908 rows). Our files on T7: 3.7 GB, of which 2.7 GB is the base pack `/mnt/t7/smad_next/DG1/packs/dg1_pack.tar`
  (on Athena too; whether to delete the local copy is asked of the lead, not done).
- 11 Nov 20:44. `dg1_addon_task.sh` (sha256 c9325c50…, uploaded while the add-on was still pending, so all 8 tasks use
  it): codes and fresh draws now go into a separate `DG1_addon_s<k>_codes.tar` (+ .sha256) that stays on Athena; the
  image tar records their sha256 in `codes_sha256.txt`. Mock-tested (fake interpreter exiting 3: both tars written and
  verified, exit code kept). The mock unpacked the 2.9 GB pack on T7 for about a minute (free space dipped to about
  54 GB); removed after.

- 11 Nov 20:52. Set B shard 0 finished (task 3545877_1 = Slurm id 3545939, node t0016, account plgmultivision,
  1,704 s, 0.47 GPU-h; 3.20 s per inversion on average; all finite; genuine 268 of 268 lossless); fetched (tar sha256
  3a176569…), validity started (`/mnt/t7/smad_next/DG1/validity/setB_s0/`). Add-on tasks 3545907_0 and _1 started on
  t0016 at 20:50 and 20:51 (their generator log goes to `out_addon_s<k>/addon_s<k>.log` inside the tar, so the Slurm
  log shows progress only at the end).

- 11 Nov 21:05. **Set B finished**: shard 2 (task 3545877_3 = Slurm id 3545877, node t0016, plgmultivision, 1,634 s;
  3.12 s per inversion; all finite; genuine 268 of 268 lossless) fetched (tar sha256 62637f1c…); validity started.
  Set B totals: 908 + 904 + 896 + 908 = 3,616 files = genuine 1,072, REC / MIR / SAME / X 536 each, DOSE 4 × 100;
  every image finite; per-file hashes checked against the generation rows by `dg1_validity.py`.
- 11 Nov 21:06. Accounting (`sacct`, billing 1 GPU per job, elapsed time): smoke 3544197 4 s, 3544215 666 s, 3544800
  297 s; production 3545841_0 1,749 s (set A), _1 616 s and _3 496 s (cancelled on t0010), _2 1,489 s, _4 1,605 s;
  3545877_1 2,023 s, _3 1,789 s. **Total 10,734 s = 2.98 GPU-hours** (smoke 0.27, set A 0.49, set B 1.92, lost on
  t0010 0.31). Add-on 3545907: tasks 0, 1 running on t0016 since 20:50, tasks 2–7 pending (ReqNodeNotAvail).

- 11 Nov 21:09–21:12. Set B manifest: `src/DG1/dg1_merge_manifests.py --out /mnt/t7/smad_next/DG1/validity/setB/manifest.csv
  <validity/setB_s0..3>:<setB_s0..3>` (3,616 rows), then `dg1_manifest_extra.py` (`manifest_full.csv` sha256
  263478b8…, `validity_full.json`). First run counted 0 greyscale photos because the test was exact R = G = B; the
  reviewer's 7 grey colorFERET photos carry 1–2 grey levels of channel noise after alignment, so the rule is now channel
  spread ≤ 2 at every pixel (7 found, matching the review). Checks against the review's counts: test-read hosts 191,
  validation-reserved hosts 8, PN1 roles test 200 / train 156 / dev 100 / excluded 80, PD1-training hosts 152,
  partner cycles 88, two-person morphs with a validation-reserved partner 8. Set A: `manifest_full.csv` sha256
  95f3f8b3…. Copies (under 2 MB): `experiments/DG1_diffusion-generation-athena/validity/{setA,setB}_manifest.csv`,
  `{setA,setB}_summary.csv`, `*_validity_full.json`.

- 11 Nov 21:13–21:15. **Add-on tasks 0 and 1 finished** (3545907_0 = Slurm id 3545986, 1,403 s; _1 = 3545988, 1,438 s;
  node t0016, account plgmultivision; exit 0). Shard 0: 202 encodes at 3.10 s, 1,218 renders (0.245–0.251 s at 20
  steps, 1.22–1.31 s at 100), all finite, nothing skipped, 134 fresh draws; shard 1: 203 encodes, 1,130 renders, all
  finite. Image tars fetched (`bash src/DG1/dg1_fetch.sh addon_s0`, `addon_s1`; sha256 d693f23e… and 93b08c1c…) into
  `/mnt/t7/smad_next/DG1/gen/addon_s<k>/out_addon_s<k>/addon_s<k>/`. Codes tars stay on Athena:
  `.../results/DG1/DG1_addon_s0_codes.tar` (264,693,760 bytes, sha256 b118e25b…; inside: codes.npz 1561b37b…,
  fresh.npz 85b661d6…), `DG1_addon_s1_codes.tar` (265,482,240 bytes, sha256 2a52b4af…).
- 11 Nov 21:16. **Run-to-run check** (add-on re-renders vs production images of the same 67 hosts of shard 0,
  `addon_s0_rerun_check.json`): REC20 / SAME20 / X20 / MIR20 median per-image mean |difference| 0.0 (most files
  pixel-identical), largest per-image mean 0.018 / 0.033 / 0.037 / 0.026, max 1 / 2 / 3 / 1 grey levels.
- 11 Nov 21:18. `dg1_validity.py` extended for the add-on rungs (partner references for NOISEX / SEMX / DOSEX = partner's
  S, for NOISES / SEMS / DOSES = host's S; `mode` and `fresh_seed` columns); manifest runs for add-on shards 0 and 1
  started (`/mnt/t7/smad_next/DG1/validity/addon_s<k>/`, gen run `athena_DG1_addon`). Add-on tasks 2–7 still
  pending ('ReqNodeNotAvail', start time N/A).

- 11 Nov 21:40. Lead: add-on tasks 2–7 forecast after 02:30; prepare a rented-machine route (author approved), started
  by the lead. Registered as `prereg.md` amendment 3 (one platform per shard; gate = the registered 8-image equivalence
  reading; Athena task cancelled once the rented shard is verified; shards 0–1 stay Athena). Written:
  `src/DG1/rented/remote_run.sh` (on the machine: setup with uv-managed Python 3.12.3 and the DG1 pins, `eq`, `shard K`;
  sha256 5182c56c…) and `src/DG1/rented/drive.sh HOST PORT LEASE_FOLDER` (DGX side: upload 2.88 GB with retries, sha
  check, setup, gate read with `dg1_validity.py equiv` → `equivalence_rented.json`, then per shard: skip if the Athena
  task already runs or finished, else run, fetch to `/mnt/t7/smad_next/DG1/rented_results/`, verify, unpack to
  `gen/addon_sK/` with `PLATFORM.txt`, `scancel 3545907_K`; codes tars copied only while T7 has > 56 GB free; RELEASE in
  the lease folder at the end and on any failure exit; log `LEASE_FOLDER/dg1_drive.log`). The Athena-state parser was
  tested live (task 1 COMPLETED, task 2 PENDING from the range line). Not started by me (uploads from owner sessions are
  refused tonight); the command went to the lead.

- 11 Nov 22:51–22:57. First rented run (lead; RTX 3090 24 GB, driver 615.71, about 0.15 USD; logs
  `/mnt/t7/smad_next/vast/dg1/dg1_drive.log`, `drive_main.log`): upload and setup passed (torch 2.12.1+cu130, all pins,
  SETUP_OK in about 1.5 min); the equivalence run stopped after 2 s before any image: `DiffAE repo is not the clean
  pinned commit (HEAD '')`. Script fault, not the card: tar run as root keeps the owner uid 1000, and git refuses a repo
  owned by another user ('dubious ownership'), so `rev-parse` returned nothing. Fix in `remote_run.sh` (sha256
  0eabf19e…): `tar --no-same-owner`, `git config --global --add safe.directory <repo>`, and a repo check right after
  unpacking in setup (fails setup instead of the gate). The unpack + check tested on the DGX. The gate itself was not
  reached; no rented image exists.

- 11 Nov 23:14–23:20. Second rented run (RTX 3090, 79.112.108.70:39744): setup failed at the pack manifest check,
  `./repo/.git/index: FAILED`. Script fault introduced by the first fix: the new `git status` repo check ran BEFORE the
  manifest check, and `git status` rewrites `.git/index`, which is listed in the pack manifest. Fixes: `remote_run.sh`
  (sha256 bf1f33f6…) checks the pack manifests first, then git, then the per-file repo manifest; `drive.sh` (sha256
  13b2fbe6…) copies `/root/dg1/*.log` and `out_*/*.log` to `LEASE_FOLDER/remote_logs/` before any RELEASE, and on a setup
  failure writes no RELEASE (machine kept for a fix; the guard stops it at the cap).
- 11 Nov 23:35. Rehearsal of the whole remote setup on the DGX in a clean folder (`DG1_ROOT=<scratch> DG1_REHEARSE=1`,
  fresh venv as python3, fresh HOME): pack sha OK, unpack with `--no-same-owner`, pack manifests OK, git HEAD and clean
  status OK, repo file manifest OK, `pip install uv`, `uv python install 3.12.3` OK; x86_64 resolution with `uv pip
  compile --python-platform x86_64-manylinux_2_28`: torch 2.12.1+cu130 / torchvision 0.27.1+cu130 resolve (cu128 has no
  torch 2.12.1, so a driver < 580 would fail at setup), and the full pin set resolves with numpy 1.26.4, pillow 12.2.0,
  scipy 1.17.1, pandas 2.2.3, pytorch-lightning 2.5.5. Not rehearsable here: the x86 install itself and the GPU run
  (the first rented run did install and import everything). Scratch folder removed.

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
| Smoke / equivalence images (Athena) | `/mnt/t7/smad_next/DG1/gen/smoke_3544800/` | 8 + 10 | tar 1,402,880 bytes, sha in `athena_results/` |
| **Set A** (Athena) | `/mnt/t7/smad_next/DG1/gen/setA/out_setA/setA/` (pools `A_*`) | 914 | tar sha256 053ca8f2… |
| **Set B** shards 0–3 (Athena) | `/mnt/t7/smad_next/DG1/gen/setB_s{0,1,2,3}/out_setB_s*/setB_s*/` (pools `B_*`) | 908 + 904 + 896 + 908 | tars 3a176569…, 8b917ce3…, 62637f1c…, 1c3f3678… |
| Add-on shards 0–1 (Athena; images only) | `/mnt/t7/smad_next/DG1/gen/addon_s{0,1}/out_addon_s*/addon_s*/` (pools `AO_*`) | 1,218 + 1,130 | tars d693f23e…, 93b08c1c… |
| Add-on codes and fresh draws | Athena only: `.../smad-next/results/DG1/DG1_addon_s<k>_codes.tar` | per shard about 265 MB | s0 b118e25b…, s1 2a52b4af… |
| Result tars as fetched | `/mnt/t7/smad_next/DG1/athena_results/` | one per task, with `.sha256` | — |
| Manifests and validity | `/mnt/t7/smad_next/DG1/validity/{setA,setB,setB_s0..3,addon_s*}/`; copies in `experiments/DG1_diffusion-generation-athena/validity/` | set A 914 rows, set B 3,616 rows | setA `manifest_full.csv` 95f3f8b3…, setB 263478b8… |

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
- `src/DG1/dg1_fetch.sh TAG...` — copy result tars back under the transfer lock, `sha256sum -c`, unpack into
  `/mnt/t7/smad_next/DG1/gen/<TAG>/` (refuses an existing folder). For the add-on it fetches only the image tar.
- `src/DG1/dg1_merge_manifests.py` — merge per-shard manifests into one (paths relative to `/mnt/t7/smad_next/DG1/gen`).
- `src/DG1/dg1_manifest_extra.py` — person-use and cue columns (PNG bytes, verification against the independent
  reference, database, partner cycle, PN1 role / test-read / validation-reserved host and partner, PD1-training person,
  wedge / greyscale / twin-pair / shared-date flags, pair disagreement) and per-pool summaries (all, unflagged, per
  database) → `manifest_full.csv`, `validity_full.json`.
- Add-on (amendment 2): `src/DG1/dg1_addon.py` (generator: modes rec / mix / noise / sem / fresh, codes and fresh draws
  saved, θ checked before rendering, outputs always written), `dg1_addon_lists.py` (8 shard lists + test list),
  `dg1_addon_task.sh` (both packs checked, image tar and separate codes tar always written, generator exit code kept),
  `dg1_addon.sbatch` (array 0–7, plgmultivision, `--exclude=t0010`), `dg1_addon_pack.sh`, `dg1_addon_dgx_test.sh`
  (DGX 8-image check with retries on CUDA out-of-memory).
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

### Equivalence gate (smoke job 3544800; `equivalence.json`, `smoke8_athena_vs_dgx.json`)

Equivalent by the registered reading. Per-image mean |difference| Athena vs stored DGX A43 file: D20 001_03 0.023,
002_03 0.020, 003_03 0.022, 004_03 0.017; B20 draws 0–3: 0.032, 0.033, 0.047, 0.059 (pooled 0.032); max 1, 1, 1, 1,
1, 2, 3, 4; glint cosine 0.99989–0.99995. Image statistics move by at most 0.0098 between-image SD.

### A100 speed (Athena; batch 16 in production)

Inversion (250 steps): 3.01–3.19 s per image in production (3.28–3.38 s at batch 8–12 in the smoke job). Render: 20
steps 0.24–0.27 s, 100 steps 1.24–1.42 s per image. Unpack of the 2.9 GB pack into the RAM disk 7–32 s.

### Set A validity (FRLL, 102 persons; `validity/setA_validity.csv`, full: `/mnt/t7/smad_next/DG1/validity/setA/`)

Glint cosine to the raw FRLL photos; verification at 0.239399 (FMR 1e-3); asymmetry and Laplacian variance in the face
box of the 256 frame; median [IQR]; every face found (914 of 914).

| Rung (pool) | n | cos host | cos partner | verify host / partner / both | asymmetry | Laplacian var. | PNG bytes (median) |
|---|---|---|---|---|---|---|---|
| genuine, same storage (A_G) | 102 | 0.984 [0.981, 0.987] | — | 1.00 | 14.1 [11.5, 16.8] | 289 [254, 328] | 77,087 |
| reconstruction 20 (A_REC20) | 102 | 0.964 [0.959, 0.968] | — | 1.00 | 12.8 [10.3, 16.1] | 158 [133, 183] | 62,101 |
| reconstruction 100 (A_REC100) | 102 | 0.980 [0.978, 0.983] | — | 1.00 | 13.6 [11.1, 16.6] | 214 [187, 248] | 73,758 |
| mirror mix 20 (A_MIR20) | 102 | 0.902 [0.878, 0.928] | — | 1.00 | 4.1 [3.6, 4.3] | 224 [180, 266] | 66,966 |
| mirror mix 100 (A_MIR100) | 102 | 0.896 [0.874, 0.916] | — | 1.00 | 6.0 [5.5, 6.5] | 529 [461, 589] | 84,149 |
| two-person morph 20 (A_X20) | 100 | 0.534 [0.452, 0.596] | 0.535 [0.464, 0.613] | 1.00 / 0.99 / 0.99 | 11.8 [9.8, 14.0] | 198 [171, 237] | 68,603 |
| two-person morph 100 (A_X100) | 100 | 0.541 [0.459, 0.600] | 0.541 [0.470, 0.611] | 1.00 / 0.99 / 0.99 | 13.2 [11.5, 15.6] | 497 [459, 556] | 86,436 |
| neutral+smiling mix 20, confounded (A_CONF20) | 102 | 0.895 [0.858, 0.915] | 0.885 [0.844, 0.911] | 1.00 / 1.00 / 1.00 | 14.3 [12.1, 17.2] | 269 [213, 340] | 71,762 |
| neutral+smiling mix 100, confounded (A_CONF100) | 102 | 0.885 [0.852, 0.903] | 0.874 [0.837, 0.897] | 1.00 / 1.00 / 1.00 | 16.0 [13.8, 18.7] | 570 [471, 708] | 85,468 |

Descriptive (amendment 1): no detector statement follows from these columns. Plain facts: 99 of 100 two-person
morphs verify against both contributors at both step counts (gate G-b asks ≥ 70%); every one-person rung verifies
against its host; 100-step renders have 2.5–3.4 times the Laplacian variance of 20-step renders of the same rung; the
mirror mix has about a third of the asymmetry of the photo.

### Set B validity (FRGC and colorFERET, 536 hosts, 20 steps; `validity/setB_summary.csv`, `validity/setB_manifest.csv`)

References: the AR1 source frames of the host photo H and of the second photo (S of the host for SAME; S of the
partner for X and DOSE); "indep." = the independent AR1 reference photo R (another session, 534 hosts). Median [IQR].
Every face found (3,616 of 3,616).

| Rung (pool) | n | cos host | cos partner | verify host / partner / both | both, indep. refs | asymmetry | Laplacian var. | PNG bytes |
|---|---|---|---|---|---|---|---|---|
| genuine H and S, same storage (B_G) | 1,072 | 0.989 [0.986, 0.992] | — | 1.00 | — | 13.4 [10.1, 19.1] | 171 [133, 211] | 84,400 |
| reconstruction (B_REC20) | 536 | 0.959 [0.952, 0.965] | — | 1.00 | — | 12.4 [9.1, 17.9] | 87 [65, 114] | 59,805 |
| mirror mix (B_MIR20) | 536 | 0.891 [0.859, 0.915] | — | 1.00 | — | 3.3 [2.9, 3.8] | 109 [78, 146] | 64,649 |
| same-person mix (B_SAME20) | 536 | 0.885 [0.846, 0.908] | 0.885 [0.843, 0.909] | 1.00 / 1.00 / 1.00 | — | 12.8 [10.4, 17.1] | 128 [95, 168] | 66,792 |
| two-person morph (B_X20) | 536 | 0.566 [0.492, 0.634] | 0.569 [0.486, 0.634] | 0.996 / 0.987 / 0.983 | 0.959 | 10.9 [8.3, 14.9] | 96 [77, 121] | 64,417 |
| dose α 0.1 (B_DOSE10_20) | 100 | 0.936 [0.921, 0.946] | 0.281 [0.227, 0.346] | 1.00 / 0.73 / 0.73 | 0.66 | 13.5 | 87 | 60,274 |
| dose α 0.2 | 100 | 0.866 [0.838, 0.891] | 0.336 [0.289, 0.400] | 1.00 / 0.90 / 0.90 | 0.83 | 13.0 | 92 | 62,121 |
| dose α 0.3 | 100 | 0.774 [0.730, 0.812] | 0.416 [0.332, 0.470] | 1.00 / 0.96 / 0.96 | 0.90 | 12.3 | 94 | 63,372 |
| dose α 0.4 | 100 | 0.676 [0.618, 0.724] | 0.486 [0.405, 0.561] | 1.00 / 0.99 / 0.99 | 0.95 | 12.0 | 98 | 64,000 |

Two-person morphs verifying both contributors: 527 of 536 (0.983); unflagged subset 456 of 464 (0.983); FRGC 0.981,
colorFERET 0.991. Flags (review finding 6, `dg1_manifest_extra.py`): input photos with a black wedge (share of exact-black
pixels > 0.01): 55 of 1,072 photos (26 H, 29 S); greyscale photos (channel spread ≤ 2): 7 (2 H, 5 S), entering 7 SAME
and 7 X images; probable twin pairs: 4 X images; shared capture date: 16 X images; flagged X images 72 of 536, flagged
SAME images 54. Per-image columns for PN1 role, test-read, validation-reserved host / partner, partner cycle, PD1
training person and pair disagreement are in `setB_manifest.csv`. Descriptive only (amendment 1).

### Add-on shard 0 validity (67 hosts, partial; `validity/addon_s0_validity.csv`)

Descriptive, one shard of eight (shard 0 holds mostly colorFERET hosts, so its cosines are lower than set B overall).
Glint cosine to host / partner (median) and verify-both share: REC20 0.965, REC100 0.990; MIR20 0.866; SAME20 0.850 /
0.850, 1.00; SAME100 0.849 / 0.852, 1.00; X20 0.461 / 0.486, 0.985; X100 0.480 / 0.490, 0.985; **fresh-noise render
FRESH1_20 0.330 (verifies the host in 0.81), FRESH2_20 0.329 (0.85), FRESH1_100 0.325 (0.82)**; noise-only mix with the
partner NOISEX 0.744 / 0.253 (both 0.58); semantic-only mix with the partner SEMX 0.578 / 0.231 (both 0.45); noise-only
and semantic-only mixes with the host's own second photo NOISES 0.855 / 0.786, SEMS 0.818 / 0.746 (both 1.00);
two-person dose α 0.1–0.4: host 0.934 → 0.587, partner 0.195 → 0.380, both 0.23 → 0.94; same-person dose: host 0.960 →
0.879. Plain fact worth noting for the readings: with fresh noise and the host's own semantic code, DiffAE keeps much
less of the host's identity (cosine about 0.33) than the reconstruction from the photo's own noise map (0.96).

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
- 18:31 smoke 3544197: `module load Python/3.12.3` refused without `GCCcore/13.3.0` (4 s).
- 18:47 smoke 3544215: numpy 2.5.4 ended up in the venv although numpy 1.26.4 installed first; DiffAE cannot import
  `numpy.lib.function_base` under numpy 2. Cause of the upgrade not identified (no pinned package declares numpy ≥ 2).
  Fix: numpy and pillow in the constraints file, version assertions in the environment check (11 min lost, 0.185 GPU-h).
- 18:35 and later: a `flock -w 120` on the single shared lock timed out silently while other owners uploaded; since
  18:38 there are two locks (commands / transfers).
- First design copied the 2.9 GB pack into `$SCRATCH_LOCAL` before extracting it; Athena's local scratch is 4 GB, so it
  would have failed; switched to `$MEMFS` and extraction straight from the project store before any production job.
- 19:33: node t0010 ran 6 times slower (18.8 s per inversion); two production tasks cancelled after about 10 min and
  rerun with t0010 excluded (0.31 GPU-hours lost).
- 19:31: first DGX check of the add-on died with CUDA out-of-memory at model load (shared GB10); retried, passed.
- 21:10: greyscale flag first counted 0 photos (exact R = G = B test); aligned grey photos keep 1–2 grey levels of
  channel noise; rule changed to channel spread ≤ 2 (7 photos, as the review found).
- 18:12: two shell-logic faults found by reading before any Athena job ran (manifest check that `set -e` would not stop
  on; environment rebuild possible from parallel tasks). Fixed (timeline 18:12).

## 8. Observations and ideas

- In A43's pair list the 100 neutral pairs cover only 86 of the 102 FRLL persons; 16 persons have no two-person morph
  in set A (they still have every one-person rung).
- The DGX GPU was at 96% use with about 20 processes and 5 GB of free host memory at 17:19 (swap full); the AD1b full
  run (PID 1953728) holds 13 GB.

- Two faces in one photo (review finding 8): part 1 of the alignment logged 263 iterations for 262 files, i.e. one photo
  (`frgc_04700_S`, identified by the reviewer) had two dlib detections. `align.py` writes the crop of the FIRST
  detection and skips the second (`work_landmark` returns when the output file exists), and the reviewer's re-run shows
  the first detection is the 268-px face, so the aligned file is the right face. The AD1b README's note ('the second face
  overwrote the first') does not match the code; told to the lead.

## 9. Open items and next steps

1. Add-on tasks 3545907_2 … _7: when each ends (`sacct -j 3545907 -X`), fetch only the image tars:
   `bash src/DG1/dg1_fetch.sh addon_s2 … addon_s7` (check `df -h /mnt/t7` first; about 85 MB each). Leave the
   `DG1_addon_s<k>_codes.tar` files on Athena (lead's rule; about 265 MB each).
2. Validity for each add-on shard: `.venv-spark/bin/python -I src/DG1/dg1_validity.py manifest --gen-root
   /mnt/t7/smad_next/DG1/gen/addon_s<k> --pool experiments/AR1/pool.csv --out-dir /mnt/t7/smad_next/DG1/validity/addon_s<k>
   --gen-run athena_DG1_addon`; then `dg1_merge_manifests.py --out /mnt/t7/smad_next/DG1/validity/addon/manifest.csv
   <validity/addon_s0..7>:<addon_s0..7>` and `dg1_manifest_extra.py ... --gen-root /mnt/t7/smad_next/DG1/gen --out-dir
   /mnt/t7/smad_next/DG1/validity/addon`; run-to-run check per shard as `addon_s0_rerun_check.json`.
3. The reading rules (amendment 1) bind every scoring experiment; the scoring itself is not part of DG1.
4. Question for the lead: delete the local copy of the base pack `/mnt/t7/smad_next/DG1/packs/dg1_pack.tar` (2.7 GB, also
   on Athena with sha256 670b55f1…)? Not deleted without a yes.
5. Review question 3 (are `frgc:04637`/`04638` and `frgc:04692`/`04856` twins) is open; the flag column covers both.

## 10. Handover state

21:20, 11 Nov. Running: Athena add-on array 3545907, tasks 2–7 pending (account plgmultivision-gpu-a100, node t0010
excluded, 2:00 limit; logs `/net/pr2/projects/plgrid/plggrestoration/smad-next/logs/DG1-addon-3545907_<k>.out`; results
`.../results/DG1/DG1_addon_s<k>.tar` and `_codes.tar`). If a task fails: its tar is still written (task script); read
`out_addon_s<k>/addon_s<k>.log` inside it; a rerun of one shard: `sbatch --array=<k> packs/DG1/dg1_addon.sbatch` after
moving its result tars aside (the task refuses existing tars). DGX: validity manifests of add-on shards 0 and 1 running
in the background (`/mnt/t7/smad_next/DG1/validity_addon_01.log`). Nothing else running.
Compute spent on Athena (sacct, 1 GPU billed per job): smoke 0.27, set A 0.49, set B 1.92, lost on node t0010 0.31,
add-on tasks 0–1 0.79: **3.77 GPU-hours**; add-on remainder estimated 2.4. DGX GB10 about 1 GPU-hour (shared 8-image
checks, embeddings) plus CPU alignment. On T7: about 4 GB under `/mnt/t7/smad_next/DG1/`.

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

## Platform-equivalence check from the frozen read (FZ2), recorded 12 Nov by the FZ2 owner (review FZ2 F1)

The add-on re-renders REC, SAME, X and MIR at 20 steps of every set-B host; production set B rendered the same jobs.
Matched by (rung, host, partner): 2,144 of 2,144 images. Byte-identical PNGs: Athena shards (add-on shards 0–1 against
production) 470 of 536; rented RTX 3090 shards 0 of 1,608. Agreement of per-image values (production vs add-on):
frozen SMDD head s401 score Spearman 0.99973 (largest difference 0.055); face-box Laplacian variance Spearman 0.999994;
FZ2's P_XS probe score 0.99975 (probes refitted per run). A far larger platform-equivalence check than the 8-image gate:
DG1 images from the A100 and the RTX 3090 are equivalent for every statistic FZ2 reads. File
`platform_reproducibility_fz2.json`; code `src/FZ2/fz2_platform_repro.py`.
