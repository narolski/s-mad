# Compute heartbeat — 2026-11-14T15:51:56Z

Read-only WCSS observation at approximately 15:52 UTC / 16:52 CET, one batched query under `/tmp/opencode/wcss-client.lock` with `ssh -n`. No jobs were changed, no rental made, and no candidate or sealed payload opened.

## New scheduler changes

- SbFM supplementary scoring **6319579 COMPLETED**, exit `0:0`, 16:41:14 CET. Local output/sidecar are not present, so durable arrival is **unverified**. Registered WCSS destination: `/lustre/pd03/hpc-narolski-1790461090/smad-next/results/AB1FMSUPP/AB1FMSUPP_20261114.tar` and `/lustre/pd03/hpc-narolski-1790461090/smad-next/results/AB1FMSUPP/AB1FMSUPP_20261114.tar.sha256`. Next step: opaque collection and archive/sidecar hash check, then preserve the separate scientific read gate.
- Battery array **6316724**: tasks 0–9 completed exit 0; 10–12 running; 13–14 pending. No durable output receipt was checked; scientific outputs remain closed.
- RZ1 512 px **6319490**: all 15 tasks still running. SPRINT5 arrays **6321090/6321194/6321244/6321261**: all 50 fits still pending Priority.
- AD5 MixFaceNet 401–402 completed, 403–404 running, 405 pending; SelfMAD 401–402 running, 403–405 pending. IDistill production **6312778** remains running and on HOLD. DINOv3/comparator/IDistill diagnostic completions and MADation diagnostic failure are known earlier events, not new in this cycle.

## Cached state and metadata

- Athena cache at 16:00 CET still reports `plgmorphgeneral` unavailable; no Athena login/query was made, so job state is unknown.
- E3 opaque seed-source freeze is complete (15 archives/sidecars, seeds 403–407), metadata-only; no NEXT admission/read. Paired-ranking and breadth readers have code-only acceptance, no collector/read release. IDistill corrected smoke is technically PASS, but production remains HOLD; the new MADation first-backward diagnostic is reviewed GO but not submitted. LA1 diagnostic review is done; HQ identity binding remains blocked.
- GX generation metadata is unchanged; GX fit remains NOT_READY. No durable final outputs were confirmed for running/pending fit arrays.

## Queue update and sources

Updated only the five stale job records in `COMPUTE_QUEUE.json` (6319579, 6319264, 6319491, 6319494, 6319495) with observed state/time, scheduler evidence, and separate `result_admission`; SbFM includes its registered archive/sidecar paths and explicitly unverified durability. Queue JSON parsed and the copied remote SHA256 matched.

Sources: `AGENTS.md`, imported `CONTINUE.md`, `AGENT_STATUS.md`, `NOTEBOOK.md`, delivery `README.md`/`COMPUTE_POLICY.json`/updated `COMPUTE_QUEUE.json`, and previous `COMPUTE_HEARTBEAT_20261114T152955Z.md`; one WCSS `squeue`+`sacct` response; Athena `athena_project_watch/latest.json`; `src/recovery_20261114/sbfm_supplement/{config.json,ab1fm_supplement.sbatch}` and `coordination_20261114/SBFM_SUPPLEMENT_SUBMISSION_RECEIPT.json`; `ROOT_PROGRESS_FOLLOWTHROUGH_20261114T153855Z.md`, `SOL_AD5_FIRST_BACKWARD_INDEPENDENT_REVIEW_20261114.md`, `ROOT_E3_FREEZE_REVIEW_20261114.md`, `BB2_second-backbone/seed_mode_L.json`, and paired-ranking/breadth code-only review receipts.
