# AD6 score pipeline — readiness & skyline manifest
Written 2026-11-16 ~07:15 CET (06:15Z) by the continuity agent, after the operator's autonomy-mode
dispatch (priorities 1-3) and the "ACCEPT QUEUE" decision (no hold release, no queue acceleration).

## Status: READY-TO-FIRE (dry-run tested 2026-11-16T06:15Z)

| Stage | Tool | Verified |
|---|---|---|
| 1. Pull from WCSS | `src/AD6/dgx/fetch_ad6_wcss.sh` (tar-over-ssh via gx10, flock `/tmp/opencode/wcss-client.lock`, sha256 -c per tar) | YES: route tested live, lustre results dir reachable and (correctly) empty at 06:15Z |
| 2. Prep + score | `src/AD6/dgx/score_ad6_dgx_20261116.sh` (AD5-registered path `ad5_score_athena.py`, frozen RS1 regen crops, score_v1/score_v2 manifests, tags `ad6v1`/`ad6v2`, namespaced `h_` prefix) | YES: bash -n clean + dry run (15×NO_TAR, exits 0, receipts machinery exercised in AD5 real run) |
| 3. Receipts | `scores_h_sbr/RECEIPTS_sha256.csv` (filename, sha256, bytes; npz integrity asserted: keys id+feat) | script-tested on AD5 npz schema |
| 4. Aggregate | extend `retrain_eer_aggregate_20261116.py` loop to Hsbr rows when 60/60 npz present | pending (needs first real npz to smoke-test) |

## Fixed inputs (unchanged, sha-verified registrations)
- Frozen crops/manifests: `/mnt/t7/smad_next/RS1/regen_pack` + `/mnt/t7/smad_next/RS1/regen_run/score_v1.csv`
  (28 254 rows) + `score_v2.csv` (29 050 rows) — same 15 Nov author-ruled read population.
- Training data registration: `train_Sb_6250x256.csv` sha256 `5fd26e32…`; pack `ad6_sb_pack.tar` sha `2b5b2880…`;
  code `ad6w_code.tar` sha `968001b…` (AD6 epoch-1 save patch inside; prereg commit 3c799ff, dispatch ce72441).
- Prereg: `experiments/AD6_matched-recipe-comparator-retrains/prereg.md` success criterion: sign test ≥13/17
  families Hsbr < H_native.

## Skyline — expected artifacts (append-only; every one receipted)
- 30 tars on WCSS: `/lustre/pd03/hpc-narolski-1790461090/smad-next/AD6/results/{madation_B_sbr_s401..405,
  madation_L_sbr_s401..405, mixfacenet_X_sbr_s401..405}.tar.(+sha256)` (backbone/header or mixfacenet_SMDD.pth,
  training.log, job.json, SHA256SUMS).
- 60 npz on GB10: `/home/narolski/ad6_stage/scores_h_sbr/feat_h_<task>__ad6{v1,v2}.npz` plus log per attempt.
- Aggregate: Hsbr block (3 arms × 5 seeds → mean ± over seeds) per family in the same format as
  RETRAIN_COHORT_EER_TABLE_20261116 (S → H_native → Hsbr), v1 primary / v2 validation.

## Space policy (constraint, not a choice)
- `/mnt/t7` is 100% full (793 MB free) — AD6 writes ONLY under `/home/narolski/ad6_stage/`.
- 60 npz ≈ 3.6 GB; converted AD6 weights are deleted after both versions of a seed are receipted; pulled tars
  deleted after scoring (SHAs retained in RECEIPTS csv); script aborts scoring below 6 GB free on /home.

## Execution order when arrays land (per monitor cycle, automatic)
1. `fetch_ad6_wcss.sh` → verify OK/BAD per tar (BAD → refetch; job-side retry = resubmit array task).
2. `score_ad6_dgx_20261116.sh` (reading only completed, hash-verified tars; ~11 min/seed×2 versions per AD5
   measurement for B; L slower; X fastest).
3. On 60/60: receipts commit + aggregate extension (separate dated commit, values computed from CSV not memory).

## Queue reality (accepted by operator 2026-11-16 ~06:30Z)
- prognoza squeue --start: B array ~06:02Z (07:03 CET) tomorrow window → earliest npz ~08:05Z; L ~12:41Z
  (13:41 CET); X N/A (TL 1:00 keeps retry loop short). Hold mv30-ABC stays held (JobHeldUser) — operator decision.
- GB10 twin mixfacenet_X_sbr_s401 continues (redundancy, not a result source); after it finishes ~13:09 CET the
  GPU is free for any overflow scoring.
