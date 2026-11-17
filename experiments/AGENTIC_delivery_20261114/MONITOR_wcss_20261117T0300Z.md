# MONITOR WCSS 2026-11-17T0300Z (04:00 CET) — FINAL: all 15/15 AD6 HOLD training tars landed

## Verdict
**All three missing HOLD training grids are COMPLETE on WCSS.** Every task: seed-tar + `.sha256` receipt in
`/lustre/pd03/hpc-narolski-1790461090/smad-next/AD6/results/` (+ per-task `pip_freeze.txt`, `job.json`,
`SHA256SUMS` inside tars). Spot sha verification server-side: `madation_L_v3sbr_s405.tar: OK`,
`mixfacenet_X_sbr_s405.tar: OK` (s405: `0c42fa11...11d3c37d`). All 15 sha files present, zero failed tasks,
zero scancels.

## Registered results (jobs, all v3 stack torch 2.1.2+cu121, recipe unchanged, seeds 401-405)
| Grid | Job | Result | Wall evidence |
|---|---|---|---|
| H1 MADation ViT-B/16 | 6340883_[401-405] (4xH100, nice 40) | **5/5** `madation_B_v3sbr_s40*.tar` | ~1.0 h/seed, 480–536 samples/s, final Loss ~0.013–0.019 |
| H3 MixFaceNet-MAD | 6340884_[401-405] (1xH100, nice 41, TL 8:00) | **5/5** `mixfacenet_X_sbr_s40*.tar` | 2.32 s/it constant, ~4.0 h/seed, final Train Loss 0.0067 Acc 0.9976 (agrees with GB10 twin s401) |
| H2 MADation ViT-L/14 | 6340885_[401-405] (4xH100, nice 42, TL 6:00) | **5/5** `madation_L_v3sbr_s40*.tar` | ~1.2 h/seed, 372 samples/s, final Loss ~0.002–0.008 |

Timeline: smoke 6340410 PASS 19:39Z → resubmit 18:32-18:33Z (6340883/84/85) → X start 20:41Z, B start 00:00Z,
L start 01:19Z (queue Priority/Resources wait was the only delay) → last tar 03:00Z. TL margins held
(B sleep-safe 6:00, L ~1.5 h/seed < 6:00, X 4.0 < 8:00).

## HOLDS ledger
- H1, H2, H3: TRAINING COMPLETE 5/5 (HOLDS_20261116.md updated).
- H4: done earlier; H5/H6 unchanged (H6 watcher follows scoring).
- Remaining WCSS-side secondary work: **scoring** — pipeline on /home (commit f987c31); gate conditions
  (smoke PASS, full B/L receipts) are met; B/X scoreable now, L too. Handoff to main included in this file.

## POLLING LOOP c761556c — CANCELLED (mission complete; nothing left to poll).

## Rows for main agent
- Scoring handoff: run scoring for `madation_{B,L}_v3sbr_s4*.tar` (B/16 & L/14 retrain checkpoints) and
  `mixfacenet_X_sbr_s4*.tar`; env qualifier text required downstream is in
  AD6_WHEELS_V3_AMENDMENT_20261116T1015Z.md (v3 qualifier paragraph).
- /mnt/t7 100%-full issue (AD6_DISPATCH) still open for scoring intermediates — decision/cleanup needed
  before large npz writes.
