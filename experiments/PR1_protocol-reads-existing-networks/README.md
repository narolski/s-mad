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

## Files
- `prereg.md` registration; `pr1_read_mock.json` mock test output; `z_read.json` the registered read (once).
- Code: `src/PR1/` (pins in `src/PR1/SHA256SUMS`). Large outputs: `/mnt/t7/smad_next/PR1/`.

## Handover state
Registration committed; pre-run review pending; nothing read.
