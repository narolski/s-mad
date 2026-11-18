# Compute heartbeat — 2026-11-14T17:11:56Z

One bounded read-only cycle; WCSS observed at 2026-11-14T17:12:23Z. One batched `squeue`/`sacct` call used the shared flock, nested `ssh -n`, and absolute Slurm executable paths.

- SPRINT5: 6321090 task 0 is `RUNNING`; its other 14 tasks and all 35 tasks in arrays 6321194/6321244/6321261 remain `PENDING` (1 running, 49 pending total). 6321768 AD5 first-backward diagnostic remains `PENDING`/Priority. No completion or failure in these jobs.
- RZ1 6319490: tasks 0–5 completed (0:0), tasks 6–14 running (6/15 done, 9 running). New tasks 4/5 (`Sb512_s409`, `SbMR512_s409`) still need opaque collection and archive/sidecar verification; no members were opened.
- MixFaceNet 6310125 seeds 403/404 are covered by verified collection receipt; 405 running. SelfMAD 401/402 running, 403–405 pending. IDistill production 6312778 running and remains HOLD. Battery array 6316724 (15/15) and SbFM 6319579 have prior verified opaque-collection receipts; no recollection. Other tracked completed/failed entries are historical; no new failure surfaced.
- Athena: cached watcher last checked 17:00:02 CET; `plgmorphgeneral` unavailable and association not visible. No login attempted; current job state unknown.
- GX/DGX: `nvidia-smi` at 17:12:23 UTC reports GB10 at 0% utilization, memory N/A. This is utilization only. Fit/admission readiness has no fresh metadata; prior generation/readiness receipts remain stale (10:37/10:53 CET); current fit state unknown.

Sources: `AGENTS.md`, imported `CONTINUE.md`, `AGENT_STATUS.md`, `NOTEBOOK.md`, delivery `README.md`, `COMPUTE_POLICY.json`, fresh `COMPUTE_QUEUE.json`, prior `COMPUTE_HEARTBEAT_20261114T165156Z.md`, root snapshot/addendum `ROOT_COMPUTE_SNAPSHOT_20261114T163156Z.json` and its heartbeat addendum, cached Athena watcher, collection receipts under `/mnt/t7/smad_next/coordination_20261114/`, and this cycle's single WCSS batch. Queue not edited. No job mutation, GPU rental, timer, candidate/sealed/member/score/checkpoint/raw-stdout access, or scientific read.
