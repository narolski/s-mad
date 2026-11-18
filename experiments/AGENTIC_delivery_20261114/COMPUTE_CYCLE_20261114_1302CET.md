# Compute status cycle — 2026-11-14 13:02 CET

One bounded read-only coordination cycle. No jobs were submitted, cancelled, or modified; no rental was initiated. No candidate payloads or sealed scores were opened.

## WCSS

Fresh scheduler observation at approximately 13:02 CET. Commands ran through `ui.wcss.pl`, while holding `/tmp/opencode/wcss-client.lock` on `gx10-c326`; Slurm binaries were taken from `/opt/slurm/current/bin`.

| Work | Current state | Durability / qualification |
|---|---|---|
| DINOv3 rescore 6319264 | RUNNING, 00:38:36 elapsed | No output inspected. |
| Resolution fits 6319490_[0-14] | PENDING, Priority | No guaranteed start. |
| Comparator rescore 6319491 | PENDING, Priority | Existing submission preserved. |
| IDistill diagnostic 6319494 | COMPLETED, exit 0, 00:03:11 | Scheduler completion only; diagnostic output not inspected. |
| MADation diagnostic 6319495_[401] | PENDING, Priority | No outcome yet. |
| SbFM supplementary score 6319579 | PENDING, Priority | No score output inspected. |
| IDistill production 6312778 | RUNNING, 06:18:41 elapsed | Earlier required smoke 6312775 is TIMEOUT; production remains ineligible for adoption on that smoke. |
| SelfMAD 6310127 | Seeds 401–402 RUNNING; 403–405 PENDING, array limit 2 | No result payload inspected. |
| MixFaceNet 6310125 | Seeds 403–404 RUNNING; 405 PENDING, array limit 2; 401–402 COMPLETED | Completion is scheduler metadata only; no scientific output inspected. |
| GX generation 6315653/6315654/6315655 | Listed tasks COMPLETED, exit 0 | Generation metadata does not establish image admission, training manifests, or fit readiness. |

The original queue statement that pending tasks remain pending is stale. All states above are from this fresh scheduler response. The WCSS request to the local GX host initially found no local Slurm binaries; the correct WCSS endpoint was then queried once under the required lock. No WCSS authentication failure occurred.

## Athena

Latest scheduled association check ran successfully at 13:00:02 CET. `plgmorphgeneral` is still not visible to the submitting account; visible associations are `plgmultivision-gpu-a100` and `plgrestorearc-gpu-a100`. Status is `not_available`. I did not attempt an Athena login or query; scheduler state remains **unknown**. Existing pending jobs remain untouched.

## DGX Sol pilot and persistence

The author reports that Sol has started the authorized small XAI A/B/Sb pilot on three development images. I did not connect to DGX Sol, inspect its running process, or touch its files. Therefore its live scheduler/process state and durable-output/sidecar metadata are **unknown** in this cycle. The general policy still requires durable results under `/mnt/t7/smad_next`, but this pilot's actual destination and persistence receipt were not verified.

On the accessible GX host, the durable tree is present and timestamped records were available, but these do not identify the DGX pilot's output. No claim about pilot completion or persistence is made.

## Vast fallback readiness

No task is currently evidenced as `READY` for a Vast fallback costing at most USD 10. The GX ten-fit/scoring item remains `NOT_READY` in `COMPUTE_QUEUE.json`, with reviewed image/identity admission, training manifests/runner, floors/amendment, and independent review outstanding. Other queued jobs are already on their registered WCSS/Athena destinations; there is no reviewed portable fallback workload identified in the current queue. The cap remains USD 10 and paid H100 remains prohibited. This is a readiness assessment only; no quote research or purchase was done.

## Handoffs

- Preserve all existing jobs and failures; the only new terminal state observed was IDistill diagnostic 6319494 completed successfully at scheduler level.
- Keep Athena state unknown until the project association becomes visible through its scheduled check; do not retry rejected account access.
- Ask the lead to verify DGX Sol pilot's output destination and durable-copy metadata after Sol's pilot completes, without interrupting it.
- No READY Vast task identified; no rental action indicated.
