# MONITOR 2026-11-17T0600Z (07:00 CET) — AD6 Athena twin CLOSING NOTE (mission complete, no arms needed)

- **Course change (operator)**: WCSS completed ALL AD6 HOLD arms overnight (H1 B 5/5, H2 L 5/5, H3 X 5/5 tars +
  sha receipts; scoring on the DGX). The Athena redundancy is no longer needed. Per instruction: our array
  **3556520_[401-405] (ad6athB) scancelled by us at ~05:55 CET** — it was still PENDING (ReqNodeNotAvail),
  so NOTHING ran from it: zero additional GPU-hours were spent on the array. Old pre-existing job 3555043
  (smadnext-RS1, not from this session) left untouched. Cancellation confirmed: squeue shows only 3555043 pending.
- **Timeline (CET) 16-17 Nov:**
  - 19:32 — Athena verified UP after morning outage; partitions/accounts confirmed; python3.9 found (3.9.25).
  - 19:35-19:40 — 4 AD6 packs (9,160,458,598 B total) uploaded in ONE rsync; far-side sha256 ALL OK
    (v3 wheel pack = 189968df…07d anchor match).
  - 20:15-20:31 — first interactive smoke attempt (srun --pty 4-GPU, alloc 3556444) queued 11 min, never
    scheduled (partition GPU-full), revoked; switched to batch smoke.
  - 20:31-20:33 — smoke #1 (job 3556457, 1 GPU): env path proven (venv 72 s; `3.9.25 2.1.2+cu121 12.1
    NVIDIA A100-SXM4-40GB`, driver 595.91.07), then FAILED silently at 1:36.
  - 20:40-20:45 — smoke #2 (3556490, instrumented set -x/ERR): root cause = DGX-native data pack —
    `ad6_sb_pack.tar` (2b5b2880) has ALL data members as symlinks into /mnt/t7; manifest guard died at the
    dangling link; 339k/1.6M train rows reference the lad_* link farm (unrunnable outside the DGX as shipped).
  - 20:45 — FIX (site adaptation, recipe/CSV content UNCHANGED): dereferenced rebuild `ad6_sb_pack_athena_v1.tar`
    (1,918,525,440 B, sha baa5abe39fb5…6d5a), streamed in one transfer, sha-registered; sbatch switched to it.
  - 20:57-21:26 — **SMOKE PASS**: job 3556503, ARM=B seed 401, 1 GPU BPG=64: real iterations 0→3900, steady
    131.3-131.5 samples/s, loss 0.618→0.034-0.046, zero NCCL/CUDA errors; ended TIMEOUT 00:30:26 (as designed).
  - 21:00 — **H1 array 3556520_[401-405] submitted** (4×A100, global batch 256 = registered recipe, TL 12 h,
    nice 100) — never started: partition GPU-full from ~21:30 onward (all 24 usable nodes at 8/8 GPUs allocated
    by 23:00, 25/48 nodes fail* since the evening).
  - 05:55 — WCSS delivered H1-H3 → Athena twin scancelled as duplicate prevention; cadence (loop 6ff370b7) stopped.
- **GPU-hours spent on Athena**: ~3.5 total (smokes 1.6 + 1.6 + 0.5, 1 GPU each). **Saved by cancellation: the
  array's ~30-60 expected production GPU-h** (and its scheduler slot for other users).
- **Artifacts left on Athena** (`/net/pr2/projects/plgrid/plggrestoration/smad-next/AD6/`, 9.7 GB): packs/
  (4 sha-verified packs + the athena data pack), logs/keep/madation_B_v3sbr_s401 (full smoke evidence log),
  empty results/. Repo receipts: src/AD6/athena/ad6w_athena_v1.sbatch + MONITOR_athena_20261116T1955Z/2005Z.
  No HOLDS rows depended on Athena; HOLDS grid note stands as "redundancy source, not needed".
- **Verdict**: mission closed — Athena proven ready end-to-end (packs verified, env v3 verified on A100,
  training at 131 samples/s) with zero recipe/register deviations; nothing submitted beyond ~3.5 smoke GPU-h.
