# Running on Athena (Cyfronet, PLGrid)

Verified live on 11 Nov 2026 from the DGX. The author's instruction: use as much of Athena as is
useful. Budget: 30,000 GPU-hours on the grant `plgrestorearc` (669 used by 11 Nov), valid to 16 Aug 2027.

## Access

- `ssh -o BatchMode=yes plgpnarolski@athena.cyfronet.pl '<command>'` from the DGX. Key login only.
- **Never repeat a failed login.** One attempt; if refused, stop and tell the lead. Repeated failures
  got our address blocked on two other login nodes on 11 Nov.
- Two locks, so that large uploads do not block short commands (at most two connections at a time):
  - short commands (sbatch, squeue, sacct, tail, ls), one command per connection:
    `flock -w 300 /tmp/smadnext-athena-cmd.lock ssh -o BatchMode=yes plgpnarolski@athena.cyfronet.pl '...'`
  - transfers of packs and results (rsync, scp): `flock -w 1800 /tmp/smadnext-athena.lock rsync ...`
  - if `flock` times out it prints nothing and returns 1: that is a local wait, not a refused login; wait and try again.
- Use `bash -lc "..."` on the remote side when you need `module`.

## Account, partition, billing

- Account `plgrestorearc-gpu-a100` (30,000 GPU-hours to 16 Aug 2027; it appeared in `hpc-grants` on 11 Nov at
  17:20). `plgmultivision-gpu-a100` is the author's fallback.
- 11 Nov 18:25: Slurm accepts both accounts (it refused them from 17:20 to 18:05, until the user's association was
  synchronised after the access service was activated). First job: 3544186, the environment build and smoke test.
  To see what Slurm accepts for the user: `sacctmgr -nP show assoc user=plgpnarolski format=Account,Partition`;
  to test without creating a job: `sbatch --test-only -A <account> -p plgrid-gpu-a100 ... --wrap true`.
- Priority (11 Nov 19:44): jobs on `plgrestorearc-gpu-a100` have a fair-share factor of 0.36 (the group's earlier use);
  `plgmultivision-gpu-a100` is unused and has 1.0, which more than doubles a job's priority. With the author's
  approval the 20 LoRA fits of the SMDD rebuild (SM1) are charged there. The account of a PENDING job can be
  changed in place: `scontrol update JobId=<id> Account=plgmultivision-gpu-a100`. Other experiments stay on
  `plgrestorearc` unless the lead says otherwise. See priorities with `sprio -u plgpnarolski`.
- Partition `plgrid-gpu-a100`: A100 with 40 GB, 8 per node, x86, limit 48 hours.
- Billing is one GPU-hour per GPU and hour while a job stays within 16 CPU cores and 128 GB per GPU.
  Ask for `-c 8 --mem=64G --gres=gpu:1` unless you need more.
- Athena is **GPU-only**: no CPU-only workloads (data builds, statistics). Those stay on the DGX or
  go to the WCSS CPU partition.

## Cyfronet rules that bind us

1. Nothing is computed, compiled or installed on the login node. Environments are built inside a job.
2. Work area inside a job (measured 11 Nov, jobs 3544200 and 3544201):
   - `-C localfs` gives `$SCRATCH_LOCAL`, but it is only **4.0 GB**. The first smoke job died there
     ("No space left on device" while copying an 11 GB pack). Use it only for small work.
   - `-C memfs` gives `$MEMFS`, a RAM disk (nodes have 1 TB of RAM). It counts toward `--mem`. **Use this for
     packs and extracted data**, with `--mem` large enough for the data plus the process, and at most
     `--mem=120G` per GPU so that the job is still billed as one GPU.
   - `$SCRATCH` (`/net/tscratch/people/plgpnarolski`, Lustre) exists on compute nodes; `$TMPDIR` points into
     it by default. Use it only for a few large files, never for many small ones; files are purged after
     30 days. Never `/tmp` (the root file system has 14 GB).
3. Large inputs travel as one tar; results come back as one tar per task.

## Storage

- Project folder: `/net/pr2/projects/plgrid/plggrestoration/smad-next` (group store, about 2 TiB free;
  keep our total under 200 GB). Sub-folders: `packs/<ID>/`, `tasks/`, `results/<ID>/`, `logs/`,
  `venv/` (shared environment), `staging/<ID>/`.
- The personal scratch path printed by `$SCRATCH` does not exist on the login node; do not rely on it.

## Software

- `module load Python/3.10.4`, then the shared environment `.../smad-next/venv` (torch 2.2.1 with CUDA
  12.1, timm 1.0.27, numpy 1.26.4, pillow 10.2.0, safetensors 0.8.0, huggingface_hub 0.36.2): the same
  versions as the WCSS container and the rented machines. It is built by `src/athena/env_and_smoke.sbatch`.
- An experiment that needs other packages builds its own environment under
  `.../smad-next/envs/<ID>/` inside a job, with pinned versions written to its log.

## Container image (verified 11 Nov 2026, job 3545843)

- Docker is not installed on Athena. Apptainer 1.4.5 exists **on compute nodes only** (not on the login node) and
  runs Docker images. Building an image from a definition file works without root rights inside a job (211 s).
- Image: `/net/pr2/projects/plgrid/plggrestoration/smad-next/containers/smad_torch221_cu121_v1.sif` (3.7 GB,
  sha256 `fedeff10a26d14edad624fffc048fc197509618ba5012519c47699dd6419649f`). Contents: the public image
  `pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime` (python 3.10.13, torch 2.2.1, CUDA 12.1; the image the rented
  machines use) plus timm 1.0.27, huggingface_hub 0.36.2, safetensors 0.8.0, numpy 1.26.4, pyyaml 6.0.3,
  pillow 10.2.0. Definition file: `src/athena/containers/smad_torch221_cu121_v1.def`; test job:
  `src/athena/apptainer_test.sbatch`.
- Use inside a job: `apptainer exec --nv -B $G:$G -B $MEMFS:$MEMFS $G/containers/smad_torch221_cu121_v1.sif python ...`
  (`G` = the project folder). When building, set `APPTAINER_CACHEDIR` and `APPTAINER_TMPDIR` into `$MEMFS`.
- Rules: a **new** experiment runs from the image. An experiment that needs other packages builds its own image
  the same way under a new name (`smad_<what>_v1.sif`, definition file in `src/`, hash in its README); an image
  file is never overwritten. An experiment that has started with a Python environment finishes with it: software
  does not change inside one experiment.
- The DGX is an ARM machine and cannot run this image; it keeps its own environment. The same image file can be
  copied to WCSS, which also has Apptainer.

## Job template

`src/athena/ad4_vitl_array.sbatch` is the model: `#!/bin/bash -l`, account, partition, one GPU,
`-C memfs`, `--mem=120G`, `set -eo pipefail`, module load, `set -u`, work in `$MEMFS`, exit non-zero on
failure, one result tar with a `.sha256` beside it.

## Who may submit what

- An owner may submit its own smoke job (at most 1 GPU-hour) once the command has run on 8 images on
  the DGX or cannot be run there for a stated reason.
- After its smoke job has passed and its pre-registration exists, an owner may submit production jobs
  up to 150 GPU-hours per experiment. More needs the lead.
- Every job ID, its purpose and its GPU-hours go into the experiment's `result.md`. `scancel` only for
  your own jobs.
- Results are copied back to `/mnt/t7/smad_next/<ID>/` with a hash check before they are read.
