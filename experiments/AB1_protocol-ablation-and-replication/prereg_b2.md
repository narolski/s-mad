# AB1 follow-up batch B2: four row-drop ablation groups following the AB1 results review (registrationStatus: registered at the git commit that adds this file under this name (written 13 Nov 2026 15:10-15:40 CET by the
AB1 owner), after the pre-run check `PRERUN_AB1B2_20261113.md`; no B2 network exists at that commit. Approval: the lead,
13 Nov ~15:20, under the author's standing instruction for today to schedule the necessary experiments and fill the
clusters (these are row-drop ablations of the registered recipe, no new image operation, no method claim). The arm Sb
trained twice as long (SbL) is NOT part of B2: AB1 section 6 reserves it for the author's decision.

**Disclosure.** Every prediction below was set after seeing the AB1 results at seeds 408-412 (result.md, review
`REVIEW_AB1_20261113.md`) and the Sp results at 403-405. The new arms are new networks at the same seeds and are compared
within seed with AB1 networks already read (Sb, Sp, SbH, SbS, A); the predictions are post hoc in origin. No arm is a
method candidate.

.

## Common to all arms

- Recipe, pack, platform, scoring and reads exactly as AB1 (prereg.md sections 3-4): CLIP ViT-B/16 LoRA, FS1 `train.py`
  and flags, last checkpoint; WCSS H100 only; every network scored inside its own fit job (pn1_score.py, TF32 on, all
  21,277 rows of ab1_eval.csv); development data only; no new image operation (manifests made by dropping or repeating
  rows of FS1's `train_Sb.csv`, `src/AB1/mk_ab1b.py`).
- Seeds 408-412; each new arm is compared with AB1's networks at the same seed (Sb, Sp, SbH, SbS, A).
- Seed counting, inclusive integer margins, provenance checks and "not read (too few seeds)" exactly as AB1 (section 5,
  amendment 2). Single read when all have ended. Four post hoc tests (plus the B2-5b companion), no multiplicity
  correction; all results are labelled "post hoc, development data, same seeds as the networks that generated the
  hypotheses".
- Built: `/mnt/t7/smad_next/AB1/b2/` (manifests, `ab1b2_overlay.tar` d2038b98…, `ab1b2_summary.json`; builder
  `src/AB1/mk_ab1b.py`); task script `src/AB1/run_b2.sh` 5e8df7d2…; job `src/AB1/wcss/ab1b2_fit.sbatch` (sha256 in `pins_b2.sha256`) (25
  fits, array 0-24, seed by seed, limit 1:15, unthrottled). Reader `src/AB1/ab1b2_read.py` (sha256 in `pins_b2.sha256`),
  mock-tested (full; two seeds dropped) and run on the real AB1 tars with no B2 tar present (loading path only).
  Results: WCSS `results/AB1B2`, copy `/mnt/t7/smad_next/AB1/b2/results`.

## Arms (manifests built; `ab1b2_summary.json`)

| Arm | Rows dropped from Sb | Unique | Repeated for volume | Rows after balance | sha256 |
|---|---|---|---|---|---|
| **SbR** random-drop control | 1,704 random unique rows (SbH's count; drop rng 20261151, volume rng 20261154) | 3,831 | 1,704 (SbH's rule) | 8,424 | 0c9ddfb7… |
| **SbH61** Sb without the stored-small copies of halves only | af0_half61 363 | 5,172 | 363 | 8,548 | 0c8c253c… |
| **SbSp** Sb without the stored-small copies and the matched splice negatives | af0_photo61, af0_half61, af0_u5061, lad_S0, lad_S3 | 4,240 | 1,295 | 8,560 | 07b9e6ea… |
| **SbnS0** Sb without the seam-only splice negatives only | lad_S0 156 | 5,379 | 0 (as Sp) | 8,074 | 90d4a267… |
| **SbnS3** Sb without the same-person splice negatives only | lad_S3 156 | 5,379 | 0 (as Sp) | 8,074 | 17009309… |

Per-kind share of training rows after the class balance (stated covariates; the balancer refills strata, so removing
one kind re-weights the others; check improvement 1):

| Arm | rows | S3 negatives | S0 negatives | stored genuine (photo61 + half61) | native halves | S4 attacks |
|---|---|---|---|---|---|---|
| Sb | 8,386 | 1.86% | 1.86% | 7.36% | 20.32% | 5.13% |
| SbH | 7,200 | 3.04% | 3.08% | 12.61% | 0.00% | 4.32% |
| SbS | 8,692 | 2.15% | 2.09% | 0.00% | 23.88% | 5.79% |
| Sp | 7,762 | 0.00% | 0.00% | 7.95% | 21.95% | 4.84% |
| SbR | 8,424 | 1.85% | 2.02% | 7.57% | 20.04% | 5.40% |
| SbH61 | 8,548 | 1.97% | 2.02% | 5.31% | 21.24% | 5.47% |
| SbSp | 8,560 | 0.00% | 0.00% | 0.00% | 26.07% | 5.85% |
| SbnS0 | 8,074 | 1.93% | 0.00% | 7.64% | 21.10% | 5.03% |
| SbnS3 | 8,074 | 0.00% | 1.93% | 7.64% | 21.10% | 5.03% |

## Hypotheses (from the review; both outcomes stated; amended by the pre-run check before registration)

- **B2-1 (SbH's effects come from repeats; review H-new-4).** SbR − Sb reproduces at least half of SbH − Sb in development
  S3 placement (SbH − Sb mean −0.080) and in landmark_combined (SbH − Sb mean −0.032): per seed, SbH − Sb < 0 for both
  reads and SbR − Sb ≤ ½ × (SbH − Sb) for both (S3 in integer counts of 100). Supported: an effect of fewer unique images plus repetition (the two cannot be separated). Falsified (on ≥ 4 of 5
  seeds, with SbH − Sb < 0 in both reads, SbR − Sb > ¼ × (SbH − Sb) in both): fewer unique images plus repetition does
  not explain it; the halves' content or the re-weighting of the remaining kinds (SbH's S3-negative share 3.04% against
  Sb's 1.86% and SbR's 1.85%) may; SbR does not test the re-weighting. SbR − SbH is printed per seed (both differences
  share Sb's seed noise; existing arm pairs show 0-8 counts and 0.007-0.031 AUC of seed noise).
- B2-1, B2-2, B2-3 and B2-5b use AB1's verdict function: supported if the supporting condition holds on ≥ 4 of 5 read
  seeds (4 of 4), falsified if the falsifying condition holds on ≥ 4 of 5 (4 of 4), otherwise inconclusive; ≤ 3 read
  seeds: "not read". B2-5 has its own rule above.
- **B2-2 (reverse storage cue; review H-new-2).** Dose stated before the run: SbH61 lowers the stored-genuine share from
  7.36% to 5.31% (the balancer refills the stored stratum with af0_photo61, 254 → 454 rows); the dose-response across
  AB1 arms (about −0.012 Δm per percentage point) predicts SbH61 − Sb ≈ +0.025 in C2P Δm at amsl112. **Supported** if
  SbH61 − Sb ≥ +0.02 on ≥ 4 of 5 seeds: the per-pass weight of stored-small genuine copies pushes stored genuine photos
  toward the genuine side, in proportion (a reverse storage cue, a caveat for the paper). **Falsified** if ≤ 0 on ≥ 4
  of 5: no detectable effect at a 28% lower weight. Between-arm seed noise in Δm is about 0.02 (disclosed), so
  "inconclusive" is likely; the test is weak.
- **B2-3 (two additive storage routes; review H-new-3).** **Supported** if, at the same seed, SbSp − Sb in C2P Δf at fm61
  is ≥ +0.06 AND SbSp − SbS ≥ +0.01 (check F2: SbS − Sb alone is already ≥ +0.06 on 3 of 5 seeds), on ≥ 4 of 5: removing
  both the stored copies and the matched negatives costs more than removing the stored copies alone; the routes add.
  The expected additive gap (Sp − Sb, +0.020 to +0.034) is about two to three times the noise; SbSp − SbS is printed per
  seed. Falsified (SbSp − SbS ≤ 0 in Δf at fm61 on ≥ 4 of 5, i.e. no more than SbS at the same seed): the matched
  negatives add nothing once the stored copies are gone. Printed: SbSp's C2P per-seed passes against A.
- **B2-4** (SbL) is not registered here (author's decision).
- **B2-5 (which matched negative carries the S3 effect; Sp review H-new-1).** SbnS0 − Sb in S3 placement within ±0.10 AND in
  landmark_combined within ±0.03 on ≥ 4 of 5, while SbnS3 − Sp in S3 placement within ±0.10 on ≥ 4 of 5. Supported: the
  same-person negatives (S3), not the seam-only ones (S0), keep same-person splices down. Falsified if SbnS0 − Sb in S3
  placement is ≥ +0.15 (15 counts of 100) on ≥ 2 of 5 seeds (S0 matters); falsified takes precedence. Otherwise
  inconclusive. All S3 margins are integer counts of 100 (inclusive). Support is close to built in: SbnS3 never sees S3
  negatives and Sb fits only 65-71% of its own training S3 (review F4).
- **B2-5b (threshold-free companion of B2-5).** S3-vs-S4 AUC: SbnS0 within 0.03 of Sb AND SbnS3 within 0.03 of Sp on ≥ 4
  of 5 → supported (the ranking change also belongs to the S3 negatives); SbnS0 − Sb ≤ −0.05 on ≥ 4 of 5 → falsified
  (removing the S0 negatives alone already degrades the ranking); otherwise inconclusive.

## Budget and order

- 25 fits (Sb-family fits took 35-36 min on H100 in AB1) ≈ 15 H100-hours; limit 1:15 (about 2.1× margin); with about
  20 free H100s about 1.5 h.
- Order: reader and mock → pre-run check → registration commit → upload (ab1b2_overlay.tar, run_b2.sh,
  ab1b2_fit.sbatch to packs/AB1) → dispatcher's queue, unthrottled. No new smoke: run_b2.sh differs from the smoked and
  40-times-run run.sh v2 only in the overlay, its SUMS file name, the arm list and the results folder (diff in the
  README); the pre-run check may require one.
- Read once when all 25 have ended (or at 14 Nov 12:00 with those present), two verified copies first.

## Pre-run check (`PRERUN_AB1B2_20261113.md`)

GO WITH FIXES; applied before this commit: F1 B2-2 dose stated and bars set to +0.02 / ≤ 0 with the weakness disclosed;
F2 B2-3 support also needs SbSp − SbS ≥ +0.01; F3 B2-1 wording names the re-weighting alternative and falsification is
"SbR − Sb > ¼ × (SbH − Sb) in both reads"; F4 pins file, job header, README, the obsolete "≤ 1 seed" line removed,
SbR's volume rng named; F5 reader asserts the c2p_read and evaluation-manifest pins. Improvements taken: per-kind
share table; B2-5b registered; multiplicity and post hoc labelling. Not taken: an arm holding the S3-negative share
fixed while removing halves (new weighting code; author); replacing SbH61 by a larger weight change (overlaps SbS).
