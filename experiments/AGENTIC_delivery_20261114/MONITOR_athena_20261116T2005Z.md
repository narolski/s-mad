# MONITOR 2026-11-16T2005Z (21:05 CET) — AD6 HOLD arms onto Athena: SMOKE PASS, H1 array submitted

- **Pack upload + sha verdict: COMPLETE.** 9,160,458,598 bytes in one rsync (transfer flock, 4m22s): far-side OK
  for ad6w_code (968001b0…), ad5w_wheels39 (3bd18ded…), ad6_sb_pack (2b5b2880…), ad6w_wheels39_v3
  (189968dfed80828feed091cbc4c78e754e2e77ffe8f2bcabb6c2049d246cc07d == local anchor).
- **ROOT CAUSE FOUND (site diff, data pack):** ad6_sb_pack.tar (2b5b2880) is DGX-native — only 2 real files, ALL
  data members are symlinks into /mnt/t7 (AF0/SM1/AR1 trees); the train CSV references the lad_* link farm in
  339,123/1,600,000 rows. Smoke #1 (3556457) died silently at 1:36; instrumented smoke #2 (3556490) caught it:
  ERR line 42 `[ -f $S/data/manifests/train_Sb.csv ]` — dangling symlink on Athena. ENV fully proven before death:
  venv built 72 s, `3.9.25 2.1.2+cu121 12.1 NVIDIA A100-SXM4-40GB`, driver 595.91.07, all 4 pack shas OK in-job.
- **ATHENA FIX (data-source twin; training CSV content byte-identical, recipe/code/env-v3 UNCHANGED):** dereferenced
  rebuild of the same pack with `tar -h` on the DGX: `ad6_sb_pack_athena_v1.tar` 1,918,525,440 B, sha
  baa5abe39fb5daf7f6b5bf41a911ebbb7d08f768994125f3cb99208c7c0f6d5a, streamed in ONE transfer, sidecar sha in packs/.
  Sbatch `src/AD6/athena/ad6w_athena_v1.sbatch` verifies the athena data pack instead (3 other packs unchanged).
- **SMOKE verdict: PASS** (criterion: real iterations at sane rate + durable lustre logs), evidence from
  `$L/logs/keep/madation_B_v3sbr_s401/train_stdout.log`, smoke job 3556503 (1 GPU, AD6_BPG=64, TL 30 min, t0007):
    `Speed 125–131 samples/sec  Loss 0.6908→0.667  Global Step: 100→250 (of 25000)  Required: 3 hours`
  No NCCL/CUDA errors; A100-40G fits per-GPU batch 64 (WCSS H100 layout) — the 4-GPU production needs no other
  multiplier. Smoke prints an explicit `SMOKE BPG OVERRIDE` line (global 64≠256) so the deviation is auditable.
- **H1 ARRAY SUBMITTED: 3556520_[401-405]** `ad6athB` ARM=B (MADation ViT-B/16 LoRA), --gres=gpu:4 -c 32 --mem=96G
  -C memfs, TL 12:00, nice 100, exclude t0010/t0014/t0020, global batch 256 (registered recipe), seeds 401-405,
  one result tar + sha per seed to $L/results/, live train logs in $L/logs/keep/. PENDING at submit (partition
  GPU-full at ~21:00 CET: 25/48 nodes fail*, mix nodes 8/8 GPUs allocated; S1 started within ~2 min of a GPU
  freeing earlier tonight). Rate model: 4 GPUs × ~130 samples/s ≈ 520 samples/s → 1.6M samples ≈ 50-60 min/seed
  CPU-bound-side, 1.5-2.5 h/seed if the WCSS loader cap binds; 5 seeds ≈ 5-12 h wallclock.
- GPU-hours booked: smoke ~2 (S1 1.6 + S2 1.6 + S3 0.5 1-GPU) + array worst case 5×48, expected ~30-50.
- Cadence 30 min via scheduled loop 6ff370b7; next check pulls squeue + tars in $L/results + step rates.
- Open risks: (a) scheduler capacity for 4-GPU tasks (may queue into the night; WCSS sister jobs 6340883/85 are
  the primary data source — Athena is redundancy); (b) memfs RAM of mix nodes near-full for other users
  (--mem=96G fits nodes with ≥100G free); (c) if a full-mix partition persists, H1 ATHENA twin slips past the
  WCSS ETAs — escalate only if WCSS also slips.
