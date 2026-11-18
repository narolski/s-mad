# Baseline eval ledger — MADation B/L + MixFaceNet (retrains) — state after continuation start, 2026-11-15T19:0xZ

Single source of truth for the "baseline eval" task 1. No scientific scores of retrains exist yet; nothing below invents numbers. Verified receipts carry SHA256.

## Family × seed matrix (retrains, AD5)

| Family / arm | s401 | s402 | s403 | s404 | s405 | Technical admission (metadata-only) |
|---|---|---|---|---|---|---|
| MADation B/16 | OK | OK | OK | OK | OK | DONE — `technical_admission_20261115_v1` (COMPLETE receipt, 14 archives) |
| MADation L/14 | OK | OK | OK | OK | OK | DONE — same receipt |
| MixFaceNet X | OK | OK | OK | OK | OK | DONE — v1 for 401/402 + **`technical_admission_20261115_v2_Xremaining` for 403–405 (executed this session, exit 0, 3/3 identity_OK + header_OK)** |
| SelfMAD S | OK | OK | (collected? no — job COMPLETED 19:19 cluster tz) | (COMPLETED 19:33) | RUNNING | v1 covers 401/402 only; 403–405 packets must follow |

## What is verified (checksums)

- Phase-1 release + packet + review pins: `ROOT_TECHNICAL_RELEASE.json` (packet `c811212a…`, sources `9157b18c…/3f0f71a3…/2c270fe1…`, review `c6433a84…` = GO). Verified unchanged this session before execution.
- Phase-2 (X remaining): packet SHA re-measured = `2d49789343e9835df85a14aaaf38561c5af26c6d9e9cb7df8cd1132257e606f6` == pinned in independent review `8d4c144d…` (GO). Root release created with external pin `30044b77…`; executed CPU-only create-only → `/mnt/t7/smad_next/AD5/technical_admission_20261115_v2_Xremaining/TECHNICAL_METADATA.json`, identity checks equal-expected for task/seed/arm and checkpoint headers regular/nonempty for all three archives.
- Durability of archives (metadata, not scores): `POST_LIMITS_RECOVERY_20261115.md` — 14 archives / 17,205,616,640 bytes verified by native+local+sidecar SHA; Athena MADation B 5/5 and L 5/5; WCSS MixFaceNet full. Recovery receipts in `/mnt/t7/smad_next/coordination_20261114/post_limits_recovery_20261115T174931Z/`.
- Scheduler identity: WCSS job 6310127 array (SelfMAD) — 401/402/403/404 COMPLETED, 405 RUNNING (MONITOR_20261115T1851Z.md).

## What is genuinely NOT done (must not be paper-implied as done)

1. **No scientific admission.** Every retrain is `COLLECTED_TECHNICAL_ONLY` — header presence + identity predicates, explicitly not admission (`COMPLETE` = `TECHNICAL_ONLY_NOT_ADMISSION`). Remaining required gates per HANDOFF: loss-log/epoch completion reconciliation, checkpoint conversion (MADation `a36_madation.py convert` CPU equivalence; MixFaceNet strict arch/key/shape/finite on registered epoch100; SelfMAD epoch_index 99 + finite tensors), scoped input manifest (corrected MAD22 + approved dev controls only, `APPROVED_INPUT_EXPECTED_HASHES.csv`=765fe5cd…), per-model scoped inference under `GO_AD5_SINGLE_MODEL_SCOPED_INFERENCE`, numerical postflight + reviewed MAD22-only reporting adapter.
2. **No retrain MAD22 numbers in the manuscript.** `results.tex` currently carries only RW (released weights) baseline rows + frozen Sb 403–407 seeds. Seed-variability retrain table stays pending until (1).
3. **SelfMAD 403–405 archive collection** pending (405 running; ETA ≈ 13:00 CET 16 Nov; see OPERATIONAL_CLAIM_VERDICT_20261115.md).

## Measured runtime basis for the remaining scoped inference (native GB10, noTTA/TF32-off, batch1, VIS3 v2r1 full)

- ViT-B/16-class @224: 8.36 ms/response; SelfMAD hrnet_w18 @384: 19.5 ms/response.
- Projection for the approved eval population (7,127 rows, METADATA_CAPTURE): ≈ 1.0–2.4 min GPU forward per model-seed at batch 1; I/O+preprocess dominate → ≈ tens of minutes CPU-side for 7,127 crops. GB10 handle-fast; Vast.ai unnecessary (operator confirmed no purchase).

## Tonight's completion state

- Tonight (this continuation) completed the last pending metadata-only gate (X 403–405). The numeric chain remains deliberately gated and is NOT unlocked by continuation alone: it needs the per-step releases with independent review exactly like phases already done. Ledger updated instead of rushing scientific reads.
