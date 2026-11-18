# Compute heartbeat — 2026-11-14T19:17:58Z

One bounded read-only cycle; WCSS and DGX observed at 19:18:46 UTC. One batched WCSS read used the shared flock, nested `ssh -n`, and absolute Slurm paths.

- **SPRINT5:** 44/50 tasks complete, 3 running, 3 pending. Pair 6321090 is 9/15 complete; tasks 9–11 running and 12–14 pending. Tasks 6–8 newly completed 0:0 (19:50:52, 19:54:54, 20:05:24 CET). Fixed array mapping is seed503: task 6 BCE, task 7 paired-BCE, task 8 paired-rank. Expected remote archives and sidecars are:
  - `/lustre/pd03/hpc-narolski-1790461090/smad-next/results/SPRINT5_1/production_v3/SPRINT5_1_production_v3_bce_s503.tar` and `.tar.sha256`
  - `/lustre/pd03/hpc-narolski-1790461090/smad-next/results/SPRINT5_1/production_v3/SPRINT5_1_production_v3_paired_bce_s503.tar` and `.tar.sha256`
  - `/lustre/pd03/hpc-narolski-1790461090/smad-next/results/SPRINT5_1/production_v3/SPRINT5_1_production_v3_paired_rank_s503.tar` and `.tar.sha256`
  Existing verified receipts cover seed501/502, not seed503; no seed503 receipt/hash/size is present in inspected metadata, so archival durability remains unverified. Breadth 10/10, tail 15/15 and HN 10/10 remain complete and durably collected.
- RZ1 6319490 remains 15/15 complete and root-verified durable. Battery 6316724 (15/15), SbFM 6319579, BB2L/RZ1R and AB1 comparator outputs have prior opaque receipts; no recollection.
- MixFaceNet 6310125 seed405 running; seeds401–404 complete (403/404 collected). SelfMAD 6310127 seeds401/402 running, 403–405 pending. IDistill 6312778 running/HOLD. AD5 diagnostic 6321768 remains failed (1:0); technical packet already collected, no retry.
- **Synthetic SDPA probe 6323083:** WCSS wrapper `COMPLETED` 0:0 at 19:56:17 CET. Root acceptance record `ROOT_SDPA_TECHNICAL_RESULT_ACCEPTANCE_20261114T190258Z.json` says default backend failed with illegal instruction in efficient SDPA backward; math-only synthetic forward/backward passed finite checks. Training recovery, numerical backend equivalence, and production release are not established. This is not a scientific or operator PASS. A separately reviewed real one-step smoke is being prepared, not submitted. The requested journal directory `/lustre/pd03/hpc-narolski-1790461090/smad-next/AD5/dispatch/ad5_sdpa_launcher_v1_20261114` was not present from this session; no raw logs read.
- Athena cache checked 20:00:00 CET: `plgmorphgeneral` unavailable, association not visible; current job state unknown. No login attempted.
- GX/DGX `nvidia-smi` at 19:18:46 UTC: GB10 at 0%, memory N/A. Hardware utilization only; generation/readiness metadata remains stale (10:37/10:53 CET), current fit state unknown.

Sources: required AGENTS/CONTINUE, `AGENT_STATUS.md`, `NOTEBOOK.md`, delivery README/policy/queue (including pair seed501/502 collection metadata), previous heartbeat `COMPUTE_HEARTBEAT_20261114T185258Z.md`, `ROOT_SDPA_TECHNICAL_RESULT_ACCEPTANCE_20261114T190258Z.json`, cached Athena watcher, collection receipts under `/mnt/t7/smad_next/coordination_20261114/`, and this cycle's single successful WCSS SSH batch to alias `ui.wcss.pl` under the shared flock (authentication succeeded; no login failure). Queue not edited. No member/NPZ/score/checkpoint/candidate/sealed/raw-stdout access, scientific read, job mutation, rental, or timer.

## Corrigendum — journal location

The earlier note that the SDPA journal directory was not present was based on the wrong host surface and is withdrawn. That path is on WCSS, not gx10; its current presence was **UNKNOWN_NOT_QUERIED_ON_NATIVE_HOST** in this cycle. Root's accepted technical result and verified 25-file collection remain authoritative for the captured state; no loss is implied.
