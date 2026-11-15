# BB2 rented variant: runbook (prepared 13 Nov 2026 ~00:50 for the author's 09:00 decision; nothing rented)

Why: WCSS smoke job 6308946 is PENDING (priority 682); Slurm's forecast for our other WCSS jobs is 15 Nov 01:00, after
the experiment stage ends.

## What the registration (4393990) allows

- Platform: the registration names WCSS H100 (prereg sections 4, 9). Any rented platform needs a **platform deviation
  committed before any rented fit** (as FS1-D1/D3 did). Text to commit: GPU type, image, software (FS1's rented stack:
  `pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime`, timm 1.0.27, numpy 1.26.4, pillow 10.2.0 — the same software as the
  CLIP fits), machine layout, and: "WCSS job 6308946 is cancelled before any rented fit starts; no WCSS BB2 fit is ever
  read; the nine fits come from one GPU type".
- Batch: the registered memory rule (prereg section 4) is applied unchanged to the rented card's own smoke: batch 256
  in one pass only if the 256 x 1 smoke completes with peak memory.used ≤ 72 GiB, else 128 x 2.
  - **80 GB cards (A100 80 GB, H100 80 GB):** the rule decides; 256 x 1 is expected to fit (about 70 GB measured on
    the DGX, so it may come out either way); no amendment beyond the platform deviation.
  - **48 GB cards (L40S, RTX 6000 Ada, A6000):** 256 x 1 cannot fit; the same rule then selects 128 x 2 (about 36 GB
    expected). Allowed by the registered rule text; only the platform deviation is needed.
  - **40 GB cards (A100 40 GB):** 128 x 2 is expected to need about 37 GB plus overhead and may not fit; any smaller
    micro-batch (64 x 4) is **not registered** and would need an amendment. Do not rent 40 GB cards for BB2.
- Feature check: `featcheck.py` against `featref_cpu.npz` (tolerance 1e-3) runs in the rented smoke; no fit if it fails.
- Seeds whole on one machine (arms of a seed compared within one GPU), all machines of one GPU type.

## Layouts, wall time, cost (estimates; the smoke measures the real step rate)

Basis: CLIP ViT-B/16 ran at 1.53 it/s on an A100-SXM4 (pn1a); DINOv3 ViT-L/16 needs about 3.5x the compute, so about
0.44 it/s on an A100 (6,250 steps ≈ 4.0 h + about 0.2 h pack copy and scoring = 4.2 h per fit); H100 about 2x A100
(2.2 h); 48 GB cards at 128 x 2 about 4.5-6 h (5 h used). Setup per machine about 1.5 h (upload 10 GB at the ~3 MB/s
seen on the FS1 host, pip, smoke), in parallel across machines. Prices are assumptions (not checked; Vast not touched):
H100 80 GB 2.4 USD/h, A100 80 GB 1.2 USD/h, 48 GB card 0.75 USD/h. A machine is released when its own queue is fetched
and verified.

| GPU | machines (seeds) | wall time | cost |
|---|---|---|---|
| H100 80 GB | 1 (403, 404, 405) | 1.5 + 9 x 2.2 ≈ 21 h | ≈ 51 USD |
| H100 80 GB | 2 (403+405, 404) | 1.5 + 6 x 2.2 ≈ 15 h | ≈ 55 USD |
| H100 80 GB | 3 (one seed each) | 1.5 + 3 x 2.2 ≈ 8 h | ≈ 58 USD |
| A100 80 GB | 1 | ≈ 39 h (misses 14 Nov 18:00 if started 13 Nov 09:00-10:00) | ≈ 47 USD |
| A100 80 GB | 2 | ≈ 27 h | ≈ 49 USD |
| A100 80 GB | 3 | ≈ 14 h | ≈ 51 USD |
| 48 GB card (128 x 2) | 1 | ≈ 47 h (misses the deadline) | ≈ 35 USD |
| 48 GB card (128 x 2) | 2 | ≈ 32 h (borderline) | ≈ 36 USD |
| 48 GB card (128 x 2) | 3 | ≈ 17 h | ≈ 37 USD |

Deadline (registered): seeds whose three fits are fetched by 14 Nov 18:00 are read. Only three H100s come near the
lead's 13 Nov 18:00 target (start 10:00 -> about 18:00, before reading and review).

## Commands (DGX; HOST PORT LEASE from the lead; Q = all | s403 | s404 | s405 | s403s405 ...)

```
cd /home/narolski/smad-next/src/BB2/rented
# 0. platform deviation committed in experiments/BB2_second-backbone/prereg.md (text above); then cancel WCSS 6308946:
flock -w 600 /tmp/opencode/wcss-client.lock ssh -o BatchMode=yes narolski@ui.wcss.pl '/opt/slurm/current/bin/scancel 6308946; /opt/slurm/current/bin/sacct -j 6308946 -X -n -o JobID,State'
# per machine (one lease folder each, e.g. /mnt/t7/smad_next/vast/bb2a):
bash drive_bb2.sh HOST PORT LEASE Q upload     # 10 GB; resumable (rsync --partial)
bash drive_bb2.sh HOST PORT LEASE Q setup      # must end SETUP_OK
bash drive_bb2.sh HOST PORT LEASE Q smoke      # detached, about 15-25 min
bash drive_bb2.sh HOST PORT LEASE Q status     # smoke.txt: BB2_SMOKE_MODE 256x1 rc .. BB2_PEAK_MIB .., step 100/100 .. it/s,
                                               # BB2_FEATCHECK_RC 0, BB2_SMOKE_MODE 128x2 rc 0
# memory rule: 256x1 rc 0 and peak <= 73728 MiB -> "256 1", else (128x2 rc 0) "128 2"; record in the README; same on every machine
bash drive_bb2.sh HOST PORT LEASE Q queue 256 1   # or: queue 128 2
bash drive_bb2.sh HOST PORT LEASE Q pull       # at each expected end; RELEASE (LEASE/RELEASE) only when kept
```

Machine layouts: 1 machine `Q=all`; 2 machines `Q=s403s405` and `Q=s404`; 3 machines `Q=s403`, `Q=s404`, `Q=s405`.
Disk: at least 45 GB free under /workspace (pack 8.75 + its copy + extraction + overlay at one time).

## Keep rule (OWNER_BRIEF 12 Nov: nothing is released while it holds the only copy)

`pull` writes LEASE/RELEASE only when (1) every task of the queue has its tar on `/mnt/t7/smad_next/BB2/results/`
with a sha256 equal to the remote file and to its .sha256 (the tar holds `last_trainable.pt` = the trained weights,
meta.json, train.log, scores), or the remote confirms a failure (non-zero rc after its one rerun, no tar, ALL_DONE),
(2) every remote log file is copied and verified against a remote sha256 listing, (3) the remote queue wrote ALL_DONE.
An unreachable host never leads to a decision. sha256 lists go to LEASE/kept_tars.sha256 and LEASE/remote_logs.sha256
and are copied into the experiment folder. Not kept: full last.pt (its sha256 is in each tar), work folders.

## Remote failure rules (as registered)

Non-finite loss: never rerun. Out of memory: rerun once at 128 x 2, labelled (`rerun/<task>`). Other failure: rerun
once unchanged, labelled. Tested locally with a stand-in run.sh (scratch mock): OOM -> 128/2 rerun, non-finite -> no
rerun, refused batch 256/2.
