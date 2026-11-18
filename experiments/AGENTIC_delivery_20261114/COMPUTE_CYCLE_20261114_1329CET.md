# Compute status cycle — 2026-11-14 13:29 CET

One bounded read-only coordination cycle compared with `COMPUTE_CYCLE_20261114_1302CET.md`. No job, rental, or timer mutations. No non-XAI candidate payloads or sealed scores were opened.

## WCSS changes

Fresh `squeue` and `sacct` observation through `ui.wcss.pl`, with `/tmp/opencode/wcss-client.lock` held on `gx10-c326` and Slurm binaries under `/opt/slurm/current/bin`.

| Work | 13:02 CET | 13:29 CET |
|---|---|---|
| DINOv3 rescore 6319264 | RUNNING | COMPLETED, exit 0, elapsed 00:44:23 |
| 512 px fits 6319490_[0-14] | All PENDING | Tasks 0–3 RUNNING; 4–14 PENDING (Priority) |
| Comparator rescore 6319491 | PENDING | RUNNING, elapsed 00:20:49 |
| IDistill diagnostic 6319494 | COMPLETED, exit 0 | Unchanged |
| MADation diagnostic 6319495_[401] | PENDING | FAILED, elapsed 00:01:30, exit 1 |
| SbFM supplementary score 6319579 | PENDING | PENDING (Priority) |
| IDistill production 6312778 | RUNNING, elapsed 06:18:41 | RUNNING, elapsed 06:44:50; original smoke 6312775 remains TIMEOUT |
| SelfMAD 6310127 | Seeds 401–402 RUNNING, 403–405 PENDING | Same seeds/states; elapsed times increased |
| MixFaceNet 6310125 | 401–402 COMPLETED; 403–404 RUNNING; 405 PENDING | Same states; elapsed times increased |
| GX generation 6315653/54/55 | Listed tasks COMPLETED, exit 0 | Unchanged |

The 6319495 failure is a new scheduler failure; no logs or output payloads were opened. Preserve it and its existing receipt. 6319264 completion is scheduler metadata only; no result was collected or inspected here.

## Athena

No new association check has run since 13:00:02 CET. The saved result still says `plgmorphgeneral` is unavailable to the account. The next existing timer is 14:00 CET. I made no Athena login or scheduler query; current job state remains **unknown**.

## DGX Sol XAI pilot and output metadata

The author-reported completion is confirmed by the XAI handoff and independent results review records: seven frozen models, 21 completed model-condition maps, and independent GO for displaying the bounded private descriptive pilot. The reviewer reports checking 119 manifest-file sizes/hashes and all 21 map arrays; this cycle read only the XAI handoff/review and file metadata, not the score CSV, raw maps, or other experiment payloads. The independent review approves display with narrow descriptive claims, not population, causal-shortcut, or detector-improvement conclusions. Failed A and Sb_fp32 attempts remain preserved and excluded; Sb_fp64 is the reviewed completion.

Output package is at `/home/narolski/smad-next/manuscript_cvpr2027/figures/shortcut_attribution_20261114/`. The output manifest is 24,140 bytes and the score CSV is 9,981 bytes; handoff/review metadata provide their hashes. **Persistence issue:** this package currently resides on the root filesystem `/dev/nvme0n1p2`, not the required durable `/mnt/t7` filesystem. Root is 98% used (about 19.9 GB available). No durable copy or matching `/mnt/t7/smad_next` receipt was found/verified. I did not copy or alter the package; the lead should arrange and verify a durable copy without changing the reviewed source package.

## Vast fallback readiness

No new evidence makes a Vast fallback task READY for <= USD 10. GX ten-fit/scoring remains NOT_READY in the queue; the current WCSS work is already underway on registered resources. No quote work or purchase was done.

## Significant changes and handoff

- New: DINOv3 6319264 completed; first four 512 fits and comparator rescore started; MADation diagnostic 6319495 failed.
- New: XAI pilot completion and independent display GO are documented, with 21 maps; output package has not been verified on durable storage and is presently on a 98%-full root filesystem.
- Athena association remains unavailable at last check; no authentication attempt was repeated.
