# RECEIPT — SelfMAD s405 scoring (AD5 cohort completion) — 2026-11-16T12:20Z

## Trigger
- 6310127_405 (SelfMAD seed 405, WCSS r14-4) COMPLETED at 12:02:58Z, elapsed 63,792 s (17.72 h; consistent
  with 401: 63,827 s / 402: 63,293 s / 403: 63,284 s / 404: 63,758 s). job.json: {"task":"selfmad_S_s405",
  "seed":405,"job":"6310127_405","host":"r14-4.lem.kdm.wcss.pl","gpu":"NVIDIA H100","seconds":63660}.

## Pull + verification (deviation documented)
- WCSS: sha256 server-side verified before transfer; selfmad_S_s405.tar.sha256 =
  560905e18b01bbd41e32ad1b0722f2b63e3f8ca0eb46e735f72a8c6b141cbeca.
- Transfer: plain `cat` over ssh gx10->WCSS stream to /home/narolski/ad6_stage/selfmad_s405/ (t7 is 100% FULL
  — 789 MB free — cannot hold the 1,714,083,840-byte tar; documented deviation from the s401-404 pull that
  wrote to t7). Local sha256 after transfer == 560905e1... (independent of the in-stream remote check:
  the tar -cf/-x variant corrupted twice at the same offset — DO NOT reuse for big pulls; plain cat verified clean).
- Extract on /home; epoch_100.tar c216108a... OK, losses.logs a75b3f25... OK (inner SHA256SUMS).
- Conversion (same registered convert_selfmad.py): src epoch_100.tar, epoch_index 99, 1,956 tensors ==
  release tensors (same_keys, same_shapes), model.safetensors sha256 3fb117e537f21afee2a35282955d93f9180d76c7583d206e1aac490f11959a43.

## Scoring
- Runner: src/AD5/score/score_selfmad_s405_dgx_20261116.sh (exact replica of registered run_selfmad_dgx.sh
  flow: same ad5_score_dgx.py, pins 56bb1244/42806acb asserted inside, same part lists 10 x 2,500, same
  retry, same merge). 10/10 parts scored, no retries needed, first try each.
- Merged npz: /mnt/t7/smad_next/AD5/scores_selfmad/scores_own_selfmad_S_s405__ad5.npz
  sha256 aa68a5e069bd40225250bda93cf39b208f3946ff650d12a3fead6da08c51f21c
  rows 23,145, uniq 23,145, finite True, mode own, ids identical to s401 npz (roster match).

## Independent spot-check (2026-11-16T12:15Z)
- FRLL/amsl s405 EER recomputed from npz + RS1 manifest + final_metrics pin: 7.17 (aggregate says 7.17) MATCH.
- FRLL/webmorph s405 EER: 24.41 (aggregate says 24.41) MATCH.

## Aggregate update
- retrain_eer_aggregate_20261116.py extended s401-404 -> s401-405 (commit c745230 rerun 12:17Z):
  SelfMAD block now 5/5 seeds, missing_ids 0 for all five npz. Output refreshed
  (aggregate.md -> RETRAIN_COHORT_EER_TABLE_20261116.md; aggregate.csv unchanged — no selfmad columns there,
  same as before).
- Qualifier (4) updated to 5/5; known gap unchanged: SelfMAD x MAD22 FaceMorpher/OpenCV/Webmorph/MIPGAN_I/II
  = n/a (H5, missing own-mode E7 crops — queue planned, not silently dropped).
