# Running on Athena (Cyfronet, PLGrid)

Verified live on 11 Nov 2026 from the DGX. The author's instruction: use as much of Athena as is
useful. Budget: 30,000 GPU-hours on the grant `plgrestorearc` (669 used by 11 Nov), valid to 16 Aug 2027.

## Access

- `ssh -o BatchMode=yes plgpnarolski@athena.cyfronet.pl '<command>'` from the DGX. Key login only.
- **Never repeat a failed login.** One attempt; if refused, stop and tell the lead. Repeated failures
  got our address blocked on two other login nodes on 11 Nov.
- Take the lock for every connection, one command per connection:
  `flock -w 120 /tmp/smadnext-athena.lock ssh -o BatchMode=yes plgpnarolski@athena.cyfronet.pl '...'`
  (rsync: `flock -w 600 /tmp/smadnext-athena.lock rsync ...`).
- Use `bash -lc "..."` on the remote side when you need `module`.

## Account, partition, billing

- Account `plgrestorearc-gpu-a100` (30,000 GPU-hours to 16 Aug 2027; it appeared in `hpc-grants` on 11 Nov at
  17:20). `plgmultivision-gpu-a100` is the author's fallback.
- **11 Nov 17:25: Slurm does not accept either account yet** ("Invalid account or account/partition combination";
  the user has no Slurm association although both grants are listed). Do not submit and do not probe: the lead's
  watcher `src/athena/wait_and_submit_smoke.sh` asks every 20 minutes and the lead tells owners when it works.
- Partition `plgrid-gpu-a100`: A100 with 40 GB, 8 per node, x86, limit 48 hours.
- Billing is one GPU-hour per GPU and hour while a job stays within 16 CPU cores and 128 GB per GPU.
  Ask for `-c 8 --mem=64G --gres=gpu:1` unless you need more.
- Athena is **GPU-only**: no CPU-only workloads (data builds, statistics). Those stay on the DGX or
  go to the WCSS CPU partition.

## Cyfronet rules that bind us

1. Nothing is computed, compiled or installed on the login node. Environments are built inside a job.
2. Work in node-local scratch: add `#SBATCH -C localfs` and use `$SCRATCH_LOCAL`. Never `/tmp`.
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

## Job template

`src/athena/ad4_vitl_array.sbatch` is the model: `#!/bin/bash -l`, account, partition, one GPU,
`-C localfs`, `set -eo pipefail`, module load, `set -u`, work in `$SCRATCH_LOCAL`, exit non-zero on
failure, one result tar with a `.sha256` beside it.

## Who may submit what

- An owner may submit its own smoke job (at most 1 GPU-hour) once the command has run on 8 images on
  the DGX or cannot be run there for a stated reason.
- After its smoke job has passed and its pre-registration exists, an owner may submit production jobs
  up to 150 GPU-hours per experiment. More needs the lead.
- Every job ID, its purpose and its GPU-hours go into the experiment's `result.md`. `scancel` only for
  your own jobs.
- Results are copied back to `/mnt/t7/smad_next/<ID>/` with a hash check before they are read.
