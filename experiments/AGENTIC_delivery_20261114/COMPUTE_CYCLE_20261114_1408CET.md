# Compute status cycle — 2026-11-14 14:08 CET

One bounded read-only cycle. No job, rental, timer, or experiment mutations; no candidate payloads or sealed scores were opened.

## WCSS

Fresh accounting query completed through the required nested SSH path on `gx10-c326`, under `/tmp/opencode/wcss-client.lock`, using `/opt/slurm/current/bin/sacct` on `ui.wcss.pl`. This confirms the earlier missing-path issue was only from checking the Slurm installation on the wrong host.

- DINOv3 rescoring `6319264`: `COMPLETED`, exit `0:0`, 44m23s (12:23:19–13:07:42 CET).
- Comparator refit/rescore `6319491`: `COMPLETED`, exit `0:0`, 39m00s (13:07:15–13:46:15 CET).
- 512 px array `6319490`: tasks 0–5 `RUNNING` at poll time; tasks 6–14 `PENDING`. Running elapsed times ranged 19m57s–59m37s. No completion or scientific eligibility is inferred.
- IDistill diagnostic `6319494`: `COMPLETED`, exit `0:0`, 3m11s (12:53:00–12:56:11 CET).
- MADation launch-blocking diagnostic `6319495_401`: `FAILED`, exit `1:0`, 1m30s (13:07:15–13:08:45 CET). Root cause remains unresolved; no retry was made.
- SbFM supplementary scoring `6319579`: `PENDING`.

Accounting status is operational metadata only; no score or candidate output was read. Existing partial/failed job outcomes are preserved.

## Athena

Read the saved hourly check at `/mnt/t7/smad_next/coordination_20261114/athena_project_watch/latest.json`, timestamp `14:00:21 CET`: `plgmorphgeneral` remains unavailable to `plgpnarolski` (`association_visible: false`, status `not_available`). No Athena login or scheduler query was attempted; Athena job state remains unknown.

## DGX / durable output metadata

The XAI backup receipt at `/mnt/t7/smad_next/XAI/backup_20261114/XAI_DURABLE_COPY_RECEIPT_20261114T123518_431783Z.json` reports `VERIFIED_DURABLE_COPY`: 144 files, 100,486,394 bytes, source preserved, and relative paths, sizes, and SHA256 values equal. Independently checked receipt SHA256: `0265ec3440eadf32813350b1d4018253066ecc5a44c742715da57d64f7db095f`. `/mnt/t7` has 155 GB available (92% used). This verifies durability only; publication clearance remains pending.

## Sources and limits

Read `/home/narolski/mambamorph/AGENTS.md`, its S-MAD continuation brief, `/home/narolski/smad-next/AGENT_STATUS.md`, `NOTEBOOK.md`, and the agentic delivery README, compute policy, queue, and prior 13:48 cycle report. Queue and notebook entries were treated as historical context; live WCSS state above comes from this cycle's accounting query. No closed score payloads were inspected.
