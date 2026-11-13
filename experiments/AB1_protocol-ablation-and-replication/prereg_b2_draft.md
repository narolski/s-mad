# DRAFT (not registered, nothing run): AB1 follow-up batch B2, five follow-ups of the results review

Status: draft for the author's decision, written 13 Nov 2026 ~15:10 CET by the AB1 owner after the AB1 read
(result.md, review `REVIEW_AB1_20261113.md`). It becomes binding only at a commit that removes "DRAFT" after (1) the
author's yes, (2) a pre-run check (experiment-reviewer, Opus) with fixes applied. **Disclosure:** every prediction below
was set after seeing seeds 408-412 of AB1 (and 403-405 of Sp); the new arms are new networks at the same seeds, so a
seed is shared with the AB1 networks they are compared with (paired within seed), and the predictions are post hoc in
origin. No arm is a method candidate.

## Common to all arms

- Recipe, pack, platform, scoring and reads exactly as AB1 (prereg.md sections 3-4): CLIP ViT-B/16 LoRA, FS1 `train.py`
  and flags, last checkpoint; WCSS H100 only; every network scored inside its own fit job (pn1_score.py, TF32 on, all
  21,277 rows of ab1_eval.csv); development data only; no new image operation (manifests made by dropping or repeating
  rows of FS1's `train_Sb.csv`, `src/AB1/mk_ab1b.py`).
- Seeds 408-412; each new arm is compared with AB1's networks at the same seed (Sb, Sp, SbH, SbS, A).
- Seed counting, inclusive integer margins, provenance checks and "not read (too few seeds)" exactly as AB1 (section 5,
  amendment 2). Per-seed rule: **supported** if the direction holds on ≥ 4 of 5 seeds (4 of 4 when n = 4),
  **falsified** if it holds on ≤ 1 (≤ 1 of 4), otherwise "inconclusive, no claim". Single read when all have ended.
- Built (not uploaded or submitted): `/mnt/t7/smad_next/AB1/b2/` (manifests, `ab1b2_overlay.tar` d2038b98…, summary);
  `src/AB1/run_b2.sh` 5e8df7d2…; `src/AB1/wcss/ab1b2_fit.sbatch` f73a778d… (25 fits, limit 1:15); SbL uses the
  already registered `src/AB1/wcss/ab1_long.sbatch` (ad1c822e…, run.sh v2, 5 fits, limit 4:00). A reader extension
  (`ab1b2_read.py`) is written and mock-tested before the pre-run check.

## Arms (manifests built; `ab1b2_summary.json`)

| Arm | Rows dropped from Sb | Unique | Repeated for volume | Rows after balance | sha256 |
|---|---|---|---|---|---|
| **SbR** random-drop control | 1,704 random unique rows (SbH's count; rng 20261151) | 3,831 | 1,704 (SbH's rule) | 8,424 | 0c9ddfb7… |
| **SbH61** Sb without the stored-small copies of halves only | af0_half61 363 | 5,172 | 363 | 8,548 | 0c8c253c… |
| **SbSp** Sb without the stored-small copies and the matched splice negatives | af0_photo61, af0_half61, af0_u5061, lad_S0, lad_S3 | 4,240 | 1,295 | 8,560 | 07b9e6ea… |
| **SbnS0** Sb without the seam-only splice negatives only | lad_S0 156 | 5,379 | 0 (as Sp) | 8,074 | 90d4a267… |
| **SbnS3** Sb without the same-person splice negatives only | lad_S3 156 | 5,379 | 0 (as Sp) | 8,074 | 17009309… |
| **SbL** Sb trained twice as long | none; 12,500 steps | 5,535 | – | 8,386 | train_Sb 2cf3fda3… |

## Hypotheses (from the review; both outcomes stated)

- **B2-1 (SbH's effects come from repeats; review H-new-4).** SbR − Sb reproduces at least half of SbH − Sb in development
  S3 placement (SbH − Sb mean −0.080) and in landmark_combined (SbH − Sb mean −0.032): SbR − Sb ≤ ½ × (SbH − Sb) of the
  same seed for both reads. Supported: SbH's secondary cells are a repetition effect, not about the halves. Falsified
  (both SbR − Sb within ±0.01 of 0 on ≥ 4 of 5): repetition does not explain them; the halves (or their removal's
  content) do.
- **B2-2 (reverse storage cue; review H-new-2).** SbH61 − Sb in C2P Δm at amsl112 ≥ +0.05. Supported: the per-pass weight
  of stored-small genuine copies pushes stored genuine photos toward the genuine side (a reverse storage cue, a caveat
  for the paper). Falsified (rise < +0.02 on ≥ 4 of 5): no reverse cue from the stored copies of halves.
- **B2-3 (two additive storage routes; review H-new-3).** SbSp − Sb in C2P Δf at fm61 ≥ +0.06. Supported: removing both the
  stored copies and the matched negatives costs more than either alone (SbS +0.054, Sp +0.024 on average): the routes
  add. Falsified (rise ≤ +0.054 on ≥ 4 of 5, i.e. no more than SbS alone): the matched negatives add nothing once the
  stored copies are gone. Printed: SbSp's C2P per-seed passes against A.
- **B2-4 (Sb under-trained; the registered SbL rule, prereg section 6, unchanged)** plus **B2-4t (one cue links S3 flags and
  landmark detection; review H-new-1, competing prediction):** SbL lowers development S3 placement by ≥ 0.10 and
  landmark_combined falls by ≥ 0.01 against Sb on ≥ 4 of 5. B2-4t falsified if SbL lowers S3 by ≥ 0.10 and
  landmark_combined rises by ≥ +0.01 on ≥ 4 of 5 (then SbL's registered "supported" holds). Supported B2-4t: the
  same-person suppression and landmark detection trade off along training. C2P printed for SbL as a guard.
- **B2-5 (which matched negative carries the S3 effect; Sp review H-new-1).** SbnS0 − Sb in S3 placement within ±0.10 AND in
  landmark_combined within ±0.03 on ≥ 4 of 5, while SbnS3 − Sp in S3 placement within ±0.10 on ≥ 4 of 5. Supported: the
  same-person negatives (S3), not the seam-only ones (S0), keep same-person splices down. Falsified if SbnS0 − Sb in S3
  placement is ≥ +0.15 on ≥ 2 of 5 seeds (S0 matters). Otherwise inconclusive. S3-vs-S4 AUC printed for both.

## Budget and order

- 25 fits with `ab1b2_fit.sbatch` (about 36-55 min each on H100, measured in AB1) ≈ 16-18 H100-hours; SbL 5 fits at
  12,500 steps (about 75-110 min each) ≈ 7-9 H100-hours. **Total about 23-27 H100-hours, 30 fits.** With about 20 free
  H100s the batch ends about 2.5 h after it starts (SbL is the long pole).
- Order on approval: author's yes → reader extension and mock → pre-run check → registration commit → upload
  (ab1b2_overlay.tar, run_b2.sh, ab1b2_fit.sbatch; ab1_long.sbatch is already on Lustre) → dispatcher's queue.
  No smoke is needed beyond AB1's (same code path; run_b2.sh differs only in overlay, arm list and results folder);
  the pre-run check decides whether a 100-step smoke of one B2 arm is required.
