# Compute heartbeat — 2026-11-14T16:51:56Z

One bounded read-only cycle; scheduler observed at 16:52:59 UTC. A single WCSS batch used the shared flock and nested `ssh -n`, with `/opt/slurm/current/bin/squeue` and `sacct`.

- RZ1 array 6319490: tasks 4 and 5 newly `COMPLETED` 0:0 at 17:42:22 and 17:43:51 CET, corresponding to `Sb512_s409` and `SbMR512_s409`. Tasks 0–5 are complete; tasks 6–14 are running (6/15 done, 9 running). The current collection receipt does not cover tasks 4/5; archive/sidecar durability remains unverified. Next step: opaque collection and hash/sidecar verification only.
- MixFaceNet 6310125 seeds 403/404 are complete and already covered by `/mnt/t7/smad_next/coordination_20261114/new_completion_collection_20261114T164056Z/COLLECTION_VERIFIED.json`; seed 405 is running. Do not recollect 403/404.
- SPRINT5 arrays 6321090/1194/1244/1261 and AD5 first-backward diagnostic 6321768 remain `PENDING` / `Priority`, elapsed 0, end `Unknown`; these are not successes. No failures in the returned tracked records.
- Athena cached watcher: latest checked 17:00:02 CET, project `plgmorphgeneral` unavailable / association not visible. No login attempted; current job state **unknown**.
- GX/DGX: `nvidia-smi` at 16:52:59 UTC reports NVIDIA GB10, 0% utilization, memory N/A. This is hardware utilization only. Generation/fit metadata remains the stale cached evidence (generation 10:37 CET; readiness 10:53 CET, fit/admission NOT_READY); current fit state **unknown**.

Sources: `AGENTS.md`, imported `CONTINUE.md`, `AGENT_STATUS.md`, `NOTEBOOK.md`, delivery `README.md`, `COMPUTE_POLICY.json`, `COMPUTE_QUEUE.json`; prior heartbeat `COMPUTE_HEARTBEAT_20261114T163156Z.md` and its corrective addendum; `ROOT_COMPUTE_SNAPSHOT_20261114T163156Z.json`; cached Athena watcher; `new_completion_collection_20261114T164056Z/COLLECTION_VERIFIED.json`; one WCSS batch. Battery/RZ1 earlier completions and SbFM remain covered by their prior verified receipts; no recollection. No queue edit, job mutation, GPU rental, timer, candidate/sealed/member/score access, raw stdout access, or scientific read.
