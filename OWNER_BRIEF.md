# Brief for hypothesis owners

Read this, then `NOTEBOOK.md`, `11_AUDIT_PLAN.md` (ladder, gates, verdict rules), `10_ASSET_INVENTORY.md`
and `12_STATE_AT_HANDOVER.md`. Your task message names your experiment IDs.

## What you deliver

In `experiments/<ID>/`: `prereg.md` (from `prereg/TEMPLATE.md`, written before any score is read),
`result.md` (numbers with intervals, source paths, what failed, what you could not verify), small
result files (CSV/JSON). Code in `src/<ID>/`. Large outputs in `/mnt/t7/smad_next/<ID>/`.
Write only inside those three places. Do not run `git add`, `commit` or `push`; the lead commits.

**Disk space (11 Nov 20:39: the data drive `/mnt/t7` reached 100% and writes failed).** Before any write of more than
1 GB check `df -h /mnt/t7` and keep at least 50 GB free. Large packs, image sets and feature files that are needed
on Athena stay on Athena (the project folder has 10 TB); copy back to the DGX only what will be read here (score
files, small tables, images that a DGX step really needs). Do not keep a second local copy of something that
exists unpacked (a tar of a folder that is still there). You may remove your own unfinished temporary files.
Anything else is deleted only with the author's approval: send the lead a list (path, size, where the verified
copy is) instead of deleting.

**DGX load (11 Nov, measured load average 189 on 20 cores).** Start every DGX process with
`OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 nice -n 10 ...`; at most 2 such
processes per owner besides one GPU job. Numerical libraries otherwise start 20 threads each and slow everyone.
GPU work of more than about half an hour belongs on Athena (`ATHENA.md`), from the container image.

**Documentation (author's instruction, 11 Nov).** Every experiment folder also holds a `README.md` that follows
`DOCUMENTATION.md`: the full record of what was done, including dead ends, exact commands, paths, hashes and the
handover state. Write it for the work done so far, then update it at every milestone, before every long wait and
at least hourly. Nothing that matters stays in `/tmp`, `/dev/shm` or a scratchpad.
Report facts only. The lead draws conclusions.

## Naming (author's request, 11 Nov)

Name an experiment by a plain description with its ID in brackets ("the landmark ladder (AR1)"), never by a bare ID, in every file, table heading and report. Define a rung in words on first use ("warp-only image (R2w)"). The list of names is `EXPERIMENTS.md`. New folders: `experiments/<ID>_<short-name>/`.

## Hard rules

- Never open, list contents of, or grep files whose name contains `fst`, `valx` (except the allowed
  `valx_a.csv`), `A12SP` or `A12-SP`. Never read train90/val10 scores.
- Never edit `prep_eval.py` or `prep_gtest.py`. No new blur, resize, resampling or compression code.
  Allowed image operations: the approved warp script `h1_build.py`, the unchanged OpenCV and
  FaceMorpher morphers, constant-colour region blanking, existing E7 outputs, lossless PNG storage.
- Corrected MAD22 only (paths in `10_ASSET_INVENTORY.md`, section B).
- FRLL persons never enter any training or refit. One network per result; no ensembles, score fusion
  or seed picking. Seeds 401 to 405; last checkpoint. No detector may gate on resolution, file size,
  format or source.
- Third-party code and weights are untrusted: `python3 -I`, `weights_only=True`, each download in its
  own empty directory. Do not redistribute weights. No emails to anyone.
- Do not delete or move anything you did not create. Do not stop other processes (Codex controllers
  run on this machine: PIDs in `12_STATE_AT_HANDOVER.md`). Never leave results only in `/tmp` or
  `/dev/shm`.
- No spending: do not touch Vast. Ask the lead.
- Test every command on 8 images with its real command line before a full run.
- You may spawn Sonnet or Haiku helpers for bounded jobs (loaders, manifests, log parsing, figures).

## Machines

- DGX (this machine, ARM, one GB10 GPU shared with other jobs). Python:
  `/home/narolski/mambamorph-code/.venv-spark/bin/python`. DiffAE:
  `/mnt/t7/thirdparty/diffae_venv/bin/python -I`. Keep GPU memory use modest; check `nvidia-smi` first.
- WCSS (x86, H100). Every connection goes through the shared lock, one command per connection:
  `flock -w 60 /tmp/opencode/wcss-client.lock ssh -o BatchMode=yes narolski@ui.wcss.pl '<cmd>'`.
  Slurm binaries: `/opt/slurm/current/bin/`. Python there: `~/dmenv/bin/python` (torch 2.11, cu128).
  Do not run heavy work on the login node. Do not call `sbatch`, `scancel` or `scontrol` yourself.

## The WCSS slot queue

48 generic one-GPU jobs are already queued (`src/wcss/slot.sh`; arrays 6301498 with 6-hour slots and
6301499 with 14-hour slots; 8 CPUs, 64 GB RAM, 200 GB local scratch). When a slot starts it runs tasks
from `/lustre/pd03/hpc-narolski-1790461090/smad-next/queue/ready/`. A task is a directory with:

- `run.sh`: runs with `TASK_DIR` (the task directory, on Lustre) and `TASK_WORK` (local scratch, cwd).
  All heavy IO in `$TMPDIR` or `$TASK_WORK`: copy one tar pack in, write there, tar results, copy one
  tar back to `/lustre/pd03/hpc-narolski-1790461090/smad-next/results/<ID>/`. Never thousands of
  small files on Lustre, no Python libraries on Lustre. Exit non-zero on any failure (`set -euo pipefail`).
- `est_minutes`: honest upper estimate; a slot only starts a task that fits its remaining time.

You prepare task directories under `.../smad-next/staging/<ID>/` (not `ready/`), with packs under
`.../smad-next/packs/<ID>/`. The lead reviews and moves them to `ready/`. Name tasks
`<ID>_<arm>_s<seed>`. A task must be idempotent and must not depend on another task's output unless
it checks for it and exits non-zero when missing.

## WCSS CPU jobs

Work that needs no GPU may run on `lem-cpu-short` (measured 11 Nov: jobs there started within a
minute, while GPU jobs wait for many hours). Suitable: building landmark morphs and self-morphs, cue
baselines, file and colour statistics, bootstrap analysis, heads on cached features, and x86 import
or one-iteration smoke tests of generator code. Same rules as GPU tasks: `--extra=FORCE_RM_TMPDIR`,
all IO in `$TMPDIR`, one tar in and one tar out. Stage CPU tasks under
`.../smad-next/staging/<ID>/cpu/` with `run.sh`, `est_minutes` and a `cpus` file (cores needed); the
lead submits them directly, since no queue position needs holding.

## Rented machines: nothing is released while it holds the only copy (lead, 12 Nov 2026)

Two losses happened on 12 Nov: the face codes of diffusion add-on shard 7 (DG1) and the eleven original result tars of the MIPGAN controls (AG1: 1024 px PNGs and latents, about 3.5 GB). In both cases the driver removed or never fetched the local copy and then released the machine.

- Before a driver writes RELEASE, every file that exists only on the rented machine and cannot be regenerated bit for bit (original images, latents, codes, trained weights, logs) must have a verified copy on `/mnt/t7`, or on Athena project storage, with its sha256 recorded in the experiment folder.
- "One tar at a time" applies to working copies during processing. It does not permit deleting the last copy. If the disk floor prevents keeping it, the driver stops without RELEASE and the owner asks the lead.
- Trained weights of every fit are kept (they are needed for the sealed final benchmark read).
- The README of each experiment lists what is kept, where, and what was deliberately not kept.

## Cluster jobs: no placeholders, every job carries its work (lead, 12 Nov 2026, on the author's instruction)

What happened: on 11 Nov the lead queued 108 generic "slot" jobs on WCSS (`src/wcss/slot.sh`) that were meant to pick up tasks placed later in a queue folder. WCSS then became unreachable. On 12 Nov between 12:50 and 19:21 the slots started, found nothing to run and idled: about 69 H100 GPU-hours and 108 queue positions were spent on nothing. The author called this a serious failure, and it is the lead's.

Rules from now on, for every cluster (WCSS, Athena) and every owner:

- **No placeholder, dummy, slot or "hold my place" jobs.** A job is submitted only when its complete workload (code, pack, lists, with pins) is already on the cluster and the job script runs it by itself. Nothing a job needs may arrive after submission.
- **A job that finds nothing to do exits within one minute** and says so in its log. No waiting loops on a GPU.
- **Every submitted job has a named owner and an expected start and end** written in the experiment README at submission. The owner checks it at the expected end.
- **The lead lists every queue at each check** (job, owner, workload, state) and cancels anything of ours that has no owner or no workload.
- **If access to a cluster is lost,** the lead tells the author at once which of our jobs are queued there and what each will do if it starts unattended. Jobs that would waste time unattended are the reason for the first rule: there must be none.
- `src/wcss/slot.sh` is retired and refuses to run.

## Cluster dispatcher and the submission queue (13 Nov 2026, on the author's instruction)

A persistent dispatcher agent checks WCSS, Athena, the DGX GPU and the rented machines every 10 minutes (brief: `src/dispatch/DISPATCHER_BRIEF.md`; state: `/mnt/t7/smad_next/dispatch/STATE.md`). It tells you when your job fails or ends and asks you for ready workloads when GPUs are free. Answer it briefly.

If `sbatch` is refused because the Slurm controller does not answer, do not wait and do not loop: write the submission to `/mnt/t7/smad_next/dispatch/submit_queue/<cluster>_<owner>_<name>.cmd` (header lines with `#`: your agent ID, the registration commit, what the job is, expected run time; then one line with the exact login-node command, starting with `cd` and containing one `sbatch`, on WCSS with `--extra=FORCE_RM_TMPDIR`). The dispatcher submits it as soon as the controller answers and sends you the job ID. Only registered, pre-run-reviewed, smoke-tested workloads go in the queue (a smoke test itself may go in).

## Shared work tree: no manual stash (13 Nov 2026)

All owners commit in the same work tree. Twice today a manual `git stash` / `git stash pop` applied or removed another owner's uncommitted files. Rules: never run `git stash`, `git stash pop`, `git checkout -- <path>` or `git restore` on a path that is not yours; add and commit only your own paths (`git add <your paths>`), then `git pull --rebase --autostash origin sprint-plan-v2` and `git push`. If the pull reports a conflict in a file that is not yours, stop and tell the lead. The entry `stash@{0}` (11:43, SA1 edits already committed in cc59dc9) is kept as a backup: do not pop or drop it.

## Five standing roles (13 Nov 2026, on the author's instruction "Implement these changes, please!")

The author approved five additions to the workflow. They are persistent agents with their own folders; none of them changes a registration that is already committed or a job that is already queued.

1. **Ideas and literature (IDEAS).** Searches what is known about signals that genuinely indicate two identities in one image and about shortcut-robust training, and keeps a ranked mechanism ledger (`experiments/IDEAS_mechanism-ledger/LEDGER.md`): for each mechanism the physical reason it should exist, the evidence, and the cheapest test that would kill it. It proposes; it runs no experiment and opens no data.
2. **Shared test battery (BATTERY).** One versioned command (`src/battery/`) that takes any trained network and produces every row of the shortcut audit table on development data, with the platform check built in, so that owners stop writing their own scorers and readers. From the release of battery v1 (announced by the lead after its pre-run check and its regression test against today's reviewed numbers), every NEW arm scores the battery rows inside its fit job and is read with the battery reader; an owner adds only the reads specific to its hypothesis. Arms registered before that keep their own readers.
3. **Standing adversary (ADVERSARY).** For every contrast an arm claims, fits the best shortcut-only model on the same rows (hand-made statistics, border, resolution and enlargement, storage, rendering, blend energy), cross-fitted, and publishes the floor (`src/adversary/`, `experiments/ADV_shortcut-floors/`). From its release, a registered gain counts only beside its adversary floor, and the floor is fixed before the arm is read.
4. **Data building (DATA).** Owns the data catalogue (`DATA_CATALOG.md`: every dataset and derived product with path, checksum, licence terms, persons, and status: closed benchmark, sealed, development, training) and builds new data products with manifests on request (paired controls, further engines, renders, look-alikes). Owners who need new data ask DATA through the lead; products already being built by an owner tonight (the GAN morphs of GX1, the border rows, the second-engine block) stay with that owner and are entered into the catalogue when done. No new image operation without the author's word; nothing is deleted.
5. **Record keeper (RECORDS).** Checks every report before the lead passes it on: each commit hash exists and has the stated content, each time matches the machine clock or git, each headline number matches the committed result file. To make that mechanical, every owner report from now on ends with a block headed `CLAIMS:` listing, one per line, `commit <hash> <one-line subject>`, `file <path> sha256 <first 16 hex>`, and `number <label> = <value> @ <file>:<json path or line>`. Report only what you have checked in git yourself; RECORDS re-checks it.

Unchanged: registration before any run, the pre-run check and the post-result review, the cluster dispatcher, the closed benchmark sets, the frozen candidate and its single MAD22 read.
