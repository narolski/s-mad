# Registered reads of the existing fresh-seed protocol networks (PR1): record

Owner: PR1 owner agent (Opus), started 13 Nov 2026 08:43 CET. Follows `DOCUMENTATION.md`. Facts only.

## What this is
Registered reads (no training) of the 15 fresh-seed protocol networks (FS1: A, B, Sb x seeds 403-407) on development
data: Z0 fact check of the strategist's cited numbers, Z1 training-row fit, Z2 calibration / operating point, Z3 tool
transfer, Z4 one-person rows (warp-only, same-person, mirror, seam-only, splice), Z5 storage evasion (after the C2P and
MS1 owners' reads), Z6 softness; GD0 GAN and diffusion families of FFHQ (new scoring on the rented A100 pn1fs), with
GD1 (DG1 diffusion ladder) and GD2 (AG1 MIPGAN controls) if their frames exist. Rules: `prereg.md`.

## Log
- 08:43-09:20: read OWNER_BRIEF, NOTEBOOK, morning report, strategist report, FS1 review, FS1/C2P registrations,
  TT1 pins. Found: FS1 tars hold `scores_train.npz` (5,535 unique training rows, eval mode, TF32 on), so Z1 needs no
  GPU. All Z reads use stored scores. Lead asked (09:05) to add SA1 gap reads: Z4, Z5, Z6, GD1, GD2.
- Reader `src/PR1/pr1_read.py` tested on mock scores only (`pr1_read_mock.json`, random logits over the true ids).
- `src/PR1/rescore_tf32.py` is a byte copy of `src/TT1/rescore_tf32.py` (sha256 0d0b6b6f...).

- 09:00-09:15: lead's go for pn1fs (hold "pr1" in QUEUES); order agreed with the TT1 owner (after DONE_FS, then
  DONE_sp or NO_SP for at most 30 min, then the FS1 queue lock). GD pack built (`/mnt/t7/smad_next/PR1/pr1_gd.tar`
  40aa95d2…, 11,042 rows; test pack daff078c…). Upload to `/workspace/pr1/packs` started at 30 MB/s.
  GD0 cues: `/mnt/t7/smad_next/PR1/cues/gd0.npz` (cues27 unchanged, via `src/PR1/cues_gd.py`).
- Pre-run review GO WITH FIXES (`experiments/reviews/PRERUN_PR1_20261113.md`); amendments 1-2 registered (4320366).
  Code no longer deletes anything (F1). A DGX code smoke test of `remote_gd.sh` passed: 2 networks, 64 gate rows,
  34-row pack, in `/mnt/t7/smad_next/PR1/smoke_dgx/` (scores never read; DGX is not a scoring platform).
- 09:16-09:20: part 1 read once (`z_read.json`); result.md part 1; results review started.
- Dead end: the first GD1 host check required partners to be test hosts too; partners of test hosts are often
  development hosts, so the builder follows the section 6a rule (contributors outside PN1 training and validation).
- Note: the GD reader's mock run (`gd_read_mock.json`) computed the GD0 cue baselines on the real cue file; they are
  printed baselines, not a rule, and were not looked at before the read.

## Files
- `prereg.md` registration; `pr1_read_mock.json` mock test output; `z_read.json` the registered read (once).
- Code: `src/PR1/` (pins in `src/PR1/SHA256SUMS`). Large outputs: `/mnt/t7/smad_next/PR1/`.

## Handover state (13 Nov, about 12:10 CET)
- Done, reviewed, corrections applied:
  - part 1 (Z0-Z4, Z6; 6aa02f8, 90caa9e);
  - amendment 3 (Z1b, Z3b; ea24c3d);
  - Z2b / Z2b-τ5 (read 11:30 after TT1 commit b82163c);
  - GD0-GD2: scored on pn1fs 11:01-11:15 CET, gate 15/15 byte-identical, tar bf560f53… with two verified copies in
    `/mnt/t7/smad_next/PR1/results/` and `results_copy2/`; read once (5a10e33; review applied d6cf22c).
- pn1fs: PR1 has nothing left there. `/workspace/pr1` holds packs, the result tar and the empty `work_*` folders. The
  lead touches DONE_pr1 (two verified local copies exist).
- Open:
  - Z5 re-copy after the C2P-R read, and Z5 for SbM3 after the MS1 read. Rules are registered; a small reader
    has to be committed before each read.
  - Optional follow-ups proposed by the part-2 review:
    - an amendment-4 printed table;
    - 27-statistic cues on the GD1 and GD2 rows;
    - MS1 SbM3/SbV on the GD pack (about 0.5 GPU-h).
