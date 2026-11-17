# MONITOR — AD6 Hsbr scoring COMPLETE 30/30 — 2026-11-17T05:35Z

- 15/15 names × ad6v1+ad6v2 = 30 feat npz + 30 scores npz in /home/narolski/ad6_stage/scores_h_sbr/,
  all receipted in RECEIPTS_sha256.csv (30 lines), missing_ids 0 for every npz (prod athena_manifest id space).
- L arm: 5/5 tars (1,711,595,520 B each) cat-stream pulled with local==sidecar==far-side sha256 checks:
  s401 67081a96…, s402 a3b278ae…, s403 8f78d042…, s404 0896f71b…, s405 0c42fa11…. One 90s-window DISK_LOW
  gate check fired mid-s404 (5.9G<6G) but v2 attempt passed within the gate margin (6.0G) — scored 631s, no recovery rerun needed.
- All tars + converted weights deleted by score_ad6_dgx_20261116.sh per seed after receipt (space policy); /home 12G free.
- Aggregate re-run: L block appended to RETRAIN_COHORT_EER_TABLE_20261116.md (per-block idempotence markers);
  csv extended to 3 arms (B/L/X × v1/v2, per-seed + mean/sd) and column alignment bug (row/header grouping mismatch)
  fixed; dated receipt AD6_H_SBR_EER_20261117/{ad6_h_sbr_eer.md,ad6_h_sbr_eer.csv}. Commits: 3a1e72f, 19e08b6.
- Spot checks (independent recompute from npz + manifest + final_metrics pins): FRLL/amsl B s401 v1 = 13.73 MATCH;
  FRLL/amsl L s405 v1 = 11.26 MATCH.
- Flagged (data, not pipeline): MAD22/MorDiff L **v2** elevated for ALL 5 seeds (25.00-40.20, mean 34.02±6.96 vs
  v1 4.33±0.96). Same v2 population has n=1000 M_mordiff rows vs 944 in v1. B v2 (8.82/1.47/3.20/1.96/1.47) and
  X v2 (28.40/25.49/23.77/22.20/24.60) do not show this blow-up. No scoring-failure evidence (identical code path
  for all arms/seeds; receipts clean); treat as result for main's Panel C / H6 review.
- Prereg note (main owns interpretation): success criterion "sign test ≥13/17 families Hsbr < H_native" is now
  computable from the committed csv for B and X (L included); NOT assessed here — main owns Panel C fill + H6.
