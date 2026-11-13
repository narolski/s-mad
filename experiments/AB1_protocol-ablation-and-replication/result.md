# Which part of the training protocol removes which shortcut, and does the result replicate (AB1): result

Read once on 13 Nov 2026 at 14:31 CET by the AB1 owner, as registered (prereg.md with amendments 1-2 and deviation D1;
reader `src/AB1/ab1_read.py` 74ecdf7a…, `--branch R`). Development data only (FFHQ hold-out and landmark_combined, our
FRGC / colorFERET development ladder and splices); no benchmark or sealed set; the 191-host test ladder was not read.
No arm here is a method candidate. Results review done 13 Nov (`REVIEW_AB1_20261113.md`; every number and verdict
recomputed independently; corrections F1-F9 applied below).

## What was run

- 40 networks: arms A (plain), B (protocol negatives), Sb (protocol negatives plus face-spliced morphs with matched
  negatives), Sp (Sb without the matched splice negatives), SbZ (Sb without the warp-only images), SbH (Sb without the
  native halves), SbS (Sb without the stored-small copies), AS (plain plus stored-small copies only), at seeds 408-412;
  CLIP ViT-B/16 LoRA, FS1 recipe, 6,250 steps, last checkpoint. WCSS job 6310270_[0-39], 12:29-14:22, all exit 0, all on
  NVIDIA H100 (27 distinct GPUs; drivers 595.91.07 and 595.112.07; the same Python environment ~/dmenv, torch 2.11 cu128),
  35-55 min each (A and AS slower). Smoke 6310091 passed.
- Every network scored inside its own fit job (pn1_score.py, TF32 on, all 21,277 rows). All 40 tars passed the reader's
  provenance checks (sha256, H100, steps, pack, overlay, task arm, item count, finite loss, evaluation and training
  manifest hashes). Two verified copies: WCSS Lustre `results/AB1` and `/mnt/t7/smad_next/AB1/results/`.
- The conditional arm Sb trained twice as long (SbL) was not run (the lead put the decision to the author).
- Raw output `ab1_read.json` (this folder), stdout `/mnt/t7/smad_next/AB1/ab1_read_stdout_20261113.txt`; tables made by
  `src/AB1/ab1_tables.py` (`ab1_tables.md`).

## Registered verdicts

| Hypothesis | Verdict | Key numbers |
|---|---|---|
| R1, Sb: C2P, first test at seeds 408-412 | **inconclusive, no claim** | passes 5 of 5 seeds at fm61, 3 of 5 at amsl112 (A's control met 5 of 5 at both). Fails at amsl112 on 409 and 411 only on the |Δm| bar: Sb's mean genuine logit moves toward genuine by 0.12 and 0.07 SD, more than a third of A's +0.28 / +0.19; Δf there is 0.000 |
| R1, B | **inconclusive, no claim** | passes 2 of 5 at fm61 (Δf +0.021 to +0.100), 4 of 5 at amsl112 |
| H-new-1 (storage evasion), Sb and B | **falsified** for both | Δm_att between −0.06 and +0.07 SD at both sizes (Sb −0.06 to +0.04; B −0.00 to +0.07) |
| R2, contrast 1 | **replicated** (5 of 5) | Sb − B +0.15 to +0.21; Sb − A +0.12 to +0.14; not shown to exceed the best single statistic (Sb 0.873-0.906 against 0.886, point estimate above on 4 of 5; the registered 2.5% bound of Sb − floor is above 0 on 1 of 5 seeds: −0.011, −0.013, +0.001, −0.018, −0.033) |
| H-ab1: stored-small copies carry the storage reduction | **falsified** | SbS Δf / A Δf: fm61 0.20-0.29, amsl112 0.20-0.37 (≤ 1/3 on 5 and 4 of 5) |
| H-ab1s: stored-small copies alone suffice on the plain recipe | **falsified** | AS passes C2P on 0 of 5 at fm61 (Δf +0.065 to +0.144; A +0.265 to +0.385), 3 of 5 at amsl112 |
| H-ab2: warp-only images carry the warp reduction | **falsified** (seed-mean rule) | SbZ − Sb warp-only placement mean −0.001 [−0.007, +0.005]; but see below: A places 0-0.5% too |
| H-ab3: native halves carry the softness reduction | **falsified** | SbH − Sb development storage rise mean +0.000 [−0.001, +0.002], on a pool where A reacts (+0.044 to +0.088) |
| H-ab3s: stored-small copies carry the development storage rise | **falsified** (seed-mean; per-seed rule inconclusive) | SbS − Sb mean +0.018 [+0.013, +0.023]; SbS 0.015-0.024 against A 0.044-0.088 |
| H-ab4: registered Sp predictions | **falsified** (expected, floor and ceiling) | Sp S0 placed 0.01-0.04 (Sb 0.00); S0-vs-S4 AUC Sp 0.989-0.994, Sb 0.989-0.992 |
| H-sp1: Sp − Sb landmark_combined ≥ +0.03 | **inconclusive, no claim** (2 of 5) | +0.028, +0.030, +0.010, +0.015, +0.044 |
| H-sp2: Sp's C2P Δf at amsl112 above Sb's | **inconclusive, no claim** (3 of 5) | Sp − Sb +0.007, +0.007, +0.007, −0.003, −0.010 |
| H-sp3: Sp S3 placement ≥ Sb + 0.20 | **supported** (5 of 5) | Sp − Sb +0.35, +0.35, +0.33, +0.32, +0.36 (Sp 0.70-0.74, Sb 0.36-0.41) |
| H-sp3b: Sp S3-vs-S4 AUC below Sb's | **supported** (5 of 5) | Sp − Sb −0.085, −0.095, −0.057, −0.070, −0.079 |
| SbL | not run (condition not met) | |

Plain words, within the registered limits (development data, 5 seeds, one GPU model):
- Contrast 1 replicates on new seeds and a new platform (seed and GPU model change together): Sb ranks FFHQ landmark
  morphs above B and A by 0.12-0.21 AUC, but is not shown to exceed the best single statistic (the registered bound is
  above 0 on 1 of 5 seeds).
- The replacement storage test, read for the first time on these seeds, is inconclusive for Sb: at the decision rule
  Sb's storage reaction is at most +0.045 at the trained size and +0.021 at 112.7 px on every seed, against A's +0.27
  to +0.39 and +0.06 to +0.15; the registered rule fails on two seeds at 112.7 px only because Sb's scores move toward
  the genuine side by more than a third of A's (absolute) shift. In Sb, stored copies of genuine photos score slightly
  more genuine than the originals (median −0.07 to −0.14 SD at 112.7 px); that, not a flag rise, is why seeds 409 and
  411 miss the two-sided mean bar (Sb's native genuine SD, 0.92-1.36, is also smaller than A's, 1.44-2.07, which enlarges
  |Δm| in SD units). No storage evasion (H-new-1 falsified).
- The storage reduction is spread across components rather than carried by one. Without the stored-small copies, Sb
  no longer meets the storage-test bars at the trained size (SbS fails C2P: 0 of 5 seeds at fm61, Δf +0.055 to +0.110),
  but it keeps only a fifth to just over a third of A's reaction (ρ 0.20-0.29 at fm61, 0.20-0.38 at 112.7 px). Stored-
  small copies added to the plain recipe are not enough either (AS: 0 of 5 at fm61). Removing the matched splice
  negatives adds a smaller rise (+0.024 [+0.017, +0.031], below the +0.05 bar). Removing the warp-only images or the
  native halves adds none.
- H-ab2 cannot be read on the development warp-only pool (A places 0-0.5%). H-ab3 is falsified on a pool where A
  does react (+0.04 to +0.09): given their stored-small copies, the native halves are not needed for the development
  storage rise (a narrow contrast, since SbH keeps af0_half61). For H-ab3s, "falsified" means only that a rise of +0.05
  is excluded: the stored-small copies carry a small, consistent part of it (SbS − Sb +0.013 to +0.022 on every seed;
  SbS 0.015-0.024 against A's 0.044-0.088).
- The matched splice negatives (S0 and S3 together) are what keeps same-person splices down: without them Sp flags
  0.70-0.74 of same-person splices against Sb's 0.36-0.41, and ranks them closer to two-person splices (S3-vs-S4 AUC
  0.69-0.72 against 0.76-0.80). This is set after seeing seeds 403-405 and confirmed on 408-412; part of the rise is
  built in (Sp never sees S3 negatives); no S0-against-S3 attribution. Sb flags 29-35% of its own training same-person
  splices on every seed, so the reduction is about the training fit carried over to held-out persons from the same
  generator, not a demonstrated generalisation; the ranking change (H-sp3b) is the informative part. Sp's
  landmark_combined gain is not established (H-sp1 inconclusive): the 403-405 gain (+0.039 to +0.065) roughly halved on
  new seeds (+0.010 to +0.044, mean +0.026; shrinkage expected after a direction chosen from the data), positive on 5 of
  5, below the +0.03 margin on 3.

## Per-network table

Per network, seeds 408 / 409 / 410 / 411 / 412 (WCSS H100; own rule logit > 0; development data only)

| Read | A | B | Sb | Sp | SbZ | SbH | SbS | AS |
|---|---|---|---|---|---|---|---|---|
| landmark_combined AUC | 0.772 / 0.749 / 0.770 / 0.771 / 0.748 | 0.745 / 0.680 / 0.726 / 0.732 / 0.726 | 0.894 / 0.892 / 0.906 / 0.888 / 0.873 | 0.921 / 0.923 / 0.916 / 0.902 / 0.918 | 0.881 / 0.867 / 0.905 / 0.871 / 0.864 | 0.870 / 0.845 / 0.877 / 0.853 / 0.848 | 0.913 / 0.915 / 0.913 / 0.903 / 0.904 | 0.749 / 0.733 / 0.735 / 0.750 / 0.744 |
| C2P Δf fm61 | +0.351 / +0.268 / +0.385 / +0.271 / +0.265 | +0.100 / +0.048 / +0.079 / +0.021 / +0.072 | +0.021 / +0.000 / +0.045 / +0.010 / +0.021 | +0.045 / +0.034 / +0.065 / +0.031 / +0.041 | +0.024 / +0.000 / +0.034 / +0.000 / +0.024 | +0.010 / +0.014 / +0.014 / -0.003 / +0.017 | +0.069 / +0.062 / +0.110 / +0.072 / +0.055 | +0.144 / +0.072 / +0.100 / +0.065 / +0.093 |
| C2P Δf fm61 upper 95% | +0.405 / +0.320 / +0.443 / +0.326 / +0.316 | +0.134 / +0.076 / +0.113 / +0.041 / +0.103 | +0.041 / +0.021 / +0.069 / +0.031 / +0.041 | +0.072 / +0.065 / +0.100 / +0.058 / +0.069 | +0.045 / +0.010 / +0.055 / +0.021 / +0.041 | +0.027 / +0.031 / +0.031 / +0.017 / +0.034 | +0.100 / +0.093 / +0.151 / +0.103 / +0.082 | +0.186 / +0.103 / +0.137 / +0.096 / +0.127 |
| C2P Δm fm61 (genuine SD) | +1.10 / +1.13 / +1.26 / +0.95 / +1.01 | +0.30 / +0.14 / +0.23 / -0.05 / +0.17 | -0.06 / -0.17 / +0.02 / -0.08 / -0.08 | +0.09 / -0.06 / +0.08 / -0.03 / +0.03 | -0.09 / -0.20 / +0.01 / -0.12 / -0.10 | -0.14 / -0.25 / -0.07 / -0.17 / -0.16 | +0.24 / +0.14 / +0.34 / +0.20 / +0.14 | +0.42 / +0.26 / +0.30 / +0.07 / +0.30 |
| C2P Δm_att fm61 | +0.04 / +0.14 / +0.06 / +0.08 / +0.11 | +0.04 / +0.07 / +0.02 / +0.02 / +0.02 | -0.01 / +0.02 / +0.04 / +0.02 / +0.03 | +0.03 / +0.02 / +0.03 / +0.03 / +0.02 | -0.00 / +0.02 / +0.04 / +0.02 / +0.03 | -0.03 / -0.01 / +0.04 / +0.01 / +0.01 | +0.13 / +0.09 / +0.08 / +0.07 / +0.13 | +0.04 / +0.07 / +0.03 / +0.02 / +0.04 |
| C2P Δf amsl112 | +0.152 / +0.066 / +0.114 / +0.055 / +0.072 | +0.034 / +0.007 / +0.028 / +0.003 / +0.014 | +0.007 / +0.000 / +0.021 / +0.000 / +0.021 | +0.014 / +0.007 / +0.028 / -0.003 / +0.010 | +0.014 / -0.003 / +0.014 / -0.003 / +0.017 | +0.014 / +0.000 / +0.000 / +0.000 / +0.007 | +0.031 / +0.021 / +0.034 / +0.021 / +0.024 | +0.041 / +0.017 / +0.034 / +0.007 / +0.024 |
| C2P Δf amsl112 upper 95% | +0.193 / +0.097 / +0.152 / +0.083 / +0.107 | +0.062 / +0.024 / +0.052 / +0.021 / +0.028 | +0.017 / +0.010 / +0.038 / +0.010 / +0.041 | +0.038 / +0.028 / +0.052 / +0.014 / +0.028 | +0.028 / +0.007 / +0.031 / +0.017 / +0.034 | +0.028 / +0.014 / +0.010 / +0.021 / +0.017 | +0.059 / +0.038 / +0.055 / +0.041 / +0.045 | +0.069 / +0.038 / +0.059 / +0.021 / +0.041 |
| C2P Δm amsl112 (genuine SD) | +0.40 / +0.28 / +0.32 / +0.19 / +0.27 | +0.07 / -0.03 / +0.04 / -0.08 / +0.00 | -0.06 / -0.12 / -0.03 / -0.07 / -0.05 | +0.01 / -0.08 / -0.00 / -0.06 / -0.03 | -0.07 / -0.14 / -0.04 / -0.08 / -0.07 | -0.10 / -0.17 / -0.08 / -0.10 / -0.11 | +0.06 / -0.02 / +0.07 / +0.04 / +0.03 | +0.14 / +0.03 / +0.06 / -0.04 / +0.05 |
| C2P Δm_att amsl112 | +0.03 / +0.04 / +0.04 / +0.02 / +0.02 | +0.02 / +0.01 / +0.01 / -0.00 / -0.00 | -0.06 / -0.01 / +0.01 / -0.00 / -0.01 | +0.01 / +0.00 / +0.02 / +0.01 / -0.00 | -0.07 / -0.01 / +0.02 / -0.01 / -0.01 | -0.09 / -0.02 / +0.01 / -0.01 / -0.03 | +0.01 / +0.02 / +0.02 / +0.02 / +0.03 | +0.02 / +0.02 / +0.02 / -0.00 / -0.01 |
| FFHQ hold-out native photos flagged | 0.137 / 0.060 / 0.103 / 0.083 / 0.087 | 0.070 / 0.047 / 0.103 / 0.090 / 0.050 | 0.043 / 0.077 / 0.087 / 0.143 / 0.043 | 0.073 / 0.100 / 0.117 / 0.170 / 0.077 | 0.030 / 0.060 / 0.087 / 0.127 / 0.037 | 0.023 / 0.043 / 0.067 / 0.097 / 0.033 | 0.043 / 0.073 / 0.093 / 0.130 / 0.053 | 0.077 / 0.050 / 0.103 / 0.103 / 0.050 |
| dev camera photos flagged (226) | 0.004 / 0.000 / 0.000 / 0.000 / 0.000 | 0.000 / 0.000 / 0.000 / 0.000 / 0.000 | 0.000 / 0.000 / 0.000 / 0.000 / 0.000 | 0.004 / 0.000 / 0.000 / 0.000 / 0.000 | 0.000 / 0.000 / 0.000 / 0.000 / 0.000 | 0.000 / 0.000 / 0.000 / 0.000 / 0.000 | 0.000 / 0.000 / 0.000 / 0.000 / 0.000 | 0.004 / 0.000 / 0.000 / 0.000 / 0.000 |
| dev storage rise Δsoft (452 vs 226) | +0.088 / +0.044 / +0.066 / +0.064 / +0.049 | +0.002 / +0.000 / +0.002 / +0.000 / +0.002 | +0.000 / +0.002 / +0.000 / +0.002 / +0.002 | +0.007 / +0.004 / +0.009 / +0.004 / +0.009 | +0.000 / +0.002 / +0.002 / +0.002 / +0.004 | +0.000 / +0.002 / +0.002 / +0.002 / +0.002 | +0.020 / +0.024 / +0.020 / +0.015 / +0.015 | +0.004 / +0.000 / +0.009 / +0.000 / +0.004 |
| dev warp-only placed (371) | 0.003 / 0.000 / 0.005 / 0.000 / 0.003 | 0.000 / 0.000 / 0.005 / 0.000 / 0.000 | 0.000 / 0.022 / 0.000 / 0.008 / 0.005 | 0.016 / 0.019 / 0.027 / 0.030 / 0.040 | 0.000 / 0.016 / 0.000 / 0.003 / 0.011 | 0.008 / 0.022 / 0.008 / 0.022 / 0.008 | 0.000 / 0.008 / 0.000 / 0.000 / 0.003 | 0.003 / 0.000 / 0.005 / 0.000 / 0.000 |
| dev halves placed (610) | 0.003 / 0.002 / 0.000 / 0.000 / 0.002 | 0.000 / 0.000 / 0.000 / 0.000 / 0.000 | 0.000 / 0.051 / 0.000 / 0.015 / 0.010 | 0.010 / 0.038 / 0.049 / 0.054 / 0.061 | 0.000 / 0.044 / 0.000 / 0.005 / 0.025 | 0.015 / 0.051 / 0.016 / 0.049 / 0.015 | 0.000 / 0.016 / 0.000 / 0.000 / 0.005 | 0.000 / 0.000 / 0.000 / 0.000 / 0.000 |
| dev S3 placed (100) | 0.05 / 0.04 / 0.05 / 0.07 / 0.06 | 0.04 / 0.01 / 0.02 / 0.02 / 0.04 | 0.37 / 0.36 / 0.41 / 0.38 / 0.37 | 0.72 / 0.71 / 0.74 / 0.70 / 0.73 | 0.36 / 0.29 / 0.41 / 0.30 / 0.36 | 0.32 / 0.28 / 0.32 / 0.29 / 0.28 | 0.34 / 0.33 / 0.40 / 0.36 / 0.37 | 0.04 / 0.03 / 0.03 / 0.03 / 0.05 |
| dev S0 placed (100) | 0.00 / 0.00 / 0.01 / 0.01 / 0.00 | 0.00 / 0.00 / 0.01 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.02 / 0.04 / 0.01 / 0.02 / 0.02 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.01 / 0.01 / 0.01 |
| dev S0-vs-S4 AUC | 0.831 / 0.841 / 0.861 / 0.828 / 0.846 | 0.762 / 0.773 / 0.732 / 0.767 / 0.779 | 0.992 / 0.991 / 0.989 / 0.992 / 0.991 | 0.991 / 0.992 / 0.989 / 0.994 / 0.994 | 0.991 / 0.990 / 0.987 / 0.990 / 0.990 | 0.989 / 0.988 / 0.986 / 0.991 / 0.987 | 0.994 / 0.994 / 0.989 / 0.994 / 0.993 | 0.782 / 0.826 / 0.773 / 0.796 / 0.809 |
| dev S3-vs-S4 AUC | 0.559 / 0.598 / 0.593 / 0.585 / 0.594 | 0.569 / 0.596 / 0.601 / 0.592 / 0.591 | 0.776 / 0.804 / 0.755 / 0.792 / 0.789 | 0.691 / 0.710 / 0.698 / 0.722 / 0.710 | 0.781 / 0.805 / 0.754 / 0.801 / 0.796 | 0.785 / 0.812 / 0.773 / 0.814 / 0.796 | 0.786 / 0.804 / 0.761 / 0.792 / 0.791 | 0.577 / 0.612 / 0.607 / 0.597 / 0.597 |


Floor (best single statistic on landmark_combined): 0.886; 27-statistic baseline 0.814.

Training-row flags (printed): Sb flags 0.29-0.35 of its own training same-person splice negatives (0.32 at seed 408)
and misses about 6% of its training two-person splices at seed 408; every other training row kind is fitted (0 or 1).
SbH fits its training S3 best (0.20-0.22 flagged). Full table in
`ab1_read.json` (`train_flag_by_kind`).

## Secondary attribution table (seed-mean rule; no multiplicity correction)

- SbZ|c2p_fm61: not needed for it, given the others (mean -0.003 [-0.011, +0.006])
- SbZ|c2p_amsl112: not needed for it, given the others (mean -0.002 [-0.009, +0.004])
- SbZ|warp: not needed for it, given the others (mean -0.001 [-0.007, +0.005])
- SbZ|dsoft: not needed for it, given the others (mean +0.001 [-0.001, +0.002])
- SbZ|S3: not needed for it, given the others (mean -0.034 [-0.081, +0.013])
- SbZ|S0: not needed for it, given the others (mean +0.000 [+0.000, +0.000])
- SbH|c2p_fm61: not needed for it, given the others (mean -0.009 [-0.029, +0.011])
- SbH|c2p_amsl112: not needed for it, given the others (mean -0.006 [-0.020, +0.009])
- SbH|warp: not needed for it, given the others (mean +0.006 [-0.000, +0.013])
- SbH|dsoft: not needed for it, given the others (mean +0.000 [-0.001, +0.002])
- SbH|S3: not needed for it, given the others (mean -0.080 [-0.102, -0.058])
- SbH|S0: not needed for it, given the others (mean +0.000 [+0.000, +0.000])
- SbS|c2p_fm61: removing it brings the reaction back (mean +0.054 [+0.038, +0.070])
- SbS|c2p_amsl112: not needed for it, given the others (mean +0.017 [+0.006, +0.027])
- SbS|warp: not needed for it, given the others (mean -0.005 [-0.012, +0.002])
- SbS|dsoft: not needed for it, given the others (mean +0.018 [+0.013, +0.023])
- SbS|S3: not needed for it, given the others (mean -0.018 [-0.034, -0.002])
- SbS|S0: not needed for it, given the others (mean +0.000 [+0.000, +0.000])
- Sp|c2p_fm61: not needed for it, given the others (mean +0.024 [+0.017, +0.031])
- Sp|c2p_amsl112: not needed for it, given the others (mean +0.001 [-0.008, +0.011])
- Sp|warp: not needed for it, given the others (mean +0.019 [+0.002, +0.037])
- Sp|dsoft: not needed for it, given the others (mean +0.005 [+0.002, +0.009])
- Sp|S3: removing it brings the reaction back (mean +0.342 [+0.322, +0.362])
- Sp|S0: not needed for it, given the others (mean +0.022 [+0.008, +0.036])

## What could not be verified / limits

- One GPU model (H100) with two driver versions across 27 GPUs; arms and seeds are spread over nodes, so within-seed
  comparisons are not on one GPU. The A100-to-H100 difference on one FS1 network was small (p99 0.005, max 0.026
  logits) and enters nothing here.
- Volume matching gives repeated rows extra weight; omission arms see each remaining image 1.2-1.4 times as often.
  SbH's lower S3 placement (−0.080 [−0.102, −0.058]) and lower landmark_combined AUC (−0.032 [−0.044, −0.020]) cannot be
  separated from its 1.44 passes per image (the random-drop control was not run).
- The development warp-only, halves and camera-photo pools sit at the floor for every arm, so H-ab2 and H-ab3 cannot
  distinguish "the component is not needed" from "there is nothing to reduce on this pool".
- Amendment-2 directions were set after seeing seeds 403-405 (disclosed); the margin-free tests are weak evidence.

## Post hoc readings from the results review (descriptive, no pass mark; reviewer's code `src/AB1/review/`, output `review_recompute.json`)

- Across Sb, SbZ, SbH and SbS (20 networks), S3 placement and landmark_combined AUC correlate within seed at r = 0.73
  (p = 0.0003); Spearman over all 25 splice-trained networks 0.79: in these arms, whatever lowers same-person splice
  flags also lowers landmark detection.
- The FFHQ persons whose flag flips under fm61 storage in AS and SbS are mostly a subset of A's (A&AS 17-28 of 22-44
  against chance 6-15; A&SbS 10-21 of 16-32 against chance 4-12).
- Post hoc (Note 2, registered before computing, zero GPU, decides nothing; reviewed): the net storage flag increase on
  FFHQ hold-out photos does not come disproportionately from the sharpest quartile (lapvar_face; chance share 0.25,
  0.25-0.27 among photos not flagged at native). A: fm61 0.17-0.23 (net 77-112), amsl112 0.14-0.26 (net 16-44), not
  enriched. AS: fm61 0.07-0.19, amsl112 0.17-0.50 (net 2-12), inconclusive. SbS: fm61 0.06-0.33, amsl112 0.00-0.22 (net
  6-10), not enriched; the amsl112 reads rest on few persons. At fm61 sharp photos are, if anything, under-represented
  among flipped persons in all three arms (pooled 0.13-0.19). (`ab1_sharp.json`, `src/AB1/ab1_sharp.py`.)
- FFHQ hold-out warp-only images (ms1ffhq "zero", not at the floor): excess placement over native photos A +0.06 to
  +0.10, Sb +0.03 to +0.06; SbZ − Sb −0.027 to −0.007 (removing warp-only images does not raise it).
- Mean Δm at amsl112 orders with the per-pass weight of stored-small genuine copies: SbH −0.11, SbZ −0.08, Sb −0.07,
  Sp −0.03, SbS +0.04.

Mechanism-table wording allowed by the review (development data, 5 seeds, H100, arms made by dropping rows; never
"removes"; never "R1 passed for Sb"): stored-small copies are needed to meet the storage bars at the trained size, are
not enough alone, and are not the only carrier; matched splice negatives (S0 + S3 together) halve same-person splice
flags and change their ranking, close to built in, no S0/S3 split; warp-only images and seam-only splices are not
testable on the development pools; native halves are not needed for the development storage rise given their stored
copies.

Follow-ups proposed by the review (each needs registration and the author; about 6-12 H100-hours each): a random-drop
control repeated like SbH; Sb without af0_half61 only (reverse storage cue); Sb without both the stored copies and the
matched negatives (additivity); SbL with the trade-off prediction added before it runs; S3-only against S0-only
negative arms. Zero GPU: sharpness enrichment of flipped persons, done (Note 2): not enriched for A and SbS, inconclusive for AS.

## landmark_combined at matched history (amendments 3-3d, post hoc): not read (Fri Nov 13 20:38 CET 2026)

Both history routes were run once, in the registered order, and both are **not read** by rules fixed before the
balancing products existed (amendments 3b and 3c/3d):
- (a) 1:1 history-balanced subset (adversary's lcomb_bal, ADV amendment 3, 104ee36; rows 1b152ae5…, build c7311e7d…,
  converged): **125 morphs and 125 genuine photos, below the registered minimum of 150 per class → H-hb1 not read**
  (`ab1_hb_read.json`; reader 2ff58b5b…). The descriptive prints required by amendment 3b (covariate table, random-subset
  null, seed-mean with joint bootstrap, AUC decomposition, probit gain) are on record in that file, labelled
  descriptive, with no verdict; no conclusion about the gain is drawn from them.
- (b) Inverse-probability weights over all 3,000 rows (adversary's lcomb_ipw, 35f25a7; weights 4513d214…, build
  c5ba5eff…): **effective sample size 8.0 morphs (413.8 genuine), build report usable = false → H-hb1w not read**
  (`ab1_hbw_read.json`; reader 78e0f2e4…).
- By amendment 3d item 8, no further weighting, trimming, overlap or matching route is added for H-hb1.

Statement (wording corrected by the results review, `REVIEW_AB1_A3_20261113.md` in this folder): **FFHQ landmark_combined
could not be balanced on resampling history at the registered size from existing images**: matching on the round-0
surround score and pre-alignment eye distance converged only at 125 morphs and 125 genuine photos (registered minimum
150 per class), and inverse-probability weights left an effective sample size of 8.0 morphs (minimum 300; one morph
weight of about 1,039, the top 1% of morphs carrying about 72% of the morph weight). The classes do not overlap in the
recorded `scale` column of `ffhqm_meta.csv` (every morph 1.0, every genuine photo 0.25; read as the alignment resize
factor, a data fact, not verified further), and the surround alone separates them at 0.79 (one statistic) to 0.94
(gbt) on all 3,000 rows (`ADV floors/lcomb_regional.json`). On the 125/125 subset the adversary's face-region and
pixel-only floors stay at 0.94-0.95 (`lcomb_bal.json`). **The candidate's gain on this contrast at matched history
therefore remains untested.** R2's "replicated" stands with the qualifier: "on a development set whose surround
carries a resampling-history cue (0.79 single statistic, 0.94 gbt) and which in-distribution shortcut models separate
at 0.96-0.98; whether the gain holds at matched history is untested." All changes made after the subset size or the
effective sample size were known could only prevent a verdict, not produce one.

**Descriptive prints, not evidence, not for the paper:** in `ab1_hb_read.json` and `ab1_hbw_read.json`, the `verdicts`
blocks' per-seed counts (k_shrinks, k_stays: these are the counts behind the verdict the gate blocked and must never be
reported as a result), every g_bal and g_w value with its intervals, the null percentiles, the balanced and weighted
per-network AUCs, the probit gains, the decomposition AUCs, the within-quintile differences, and the covariate table
(citable only for the data facts above, never about the networks).

## Pipeline-matched contrasts (amendments 4 and 4b, post hoc): read once (Fri Nov 13 20:56 CET 2026)

Reader `src/AB1/ab1_pm_read.py` (ba6efdad…), AB1 H100 fit-job scores of A, B, Sb at 408-412 (all 15 read), output
`ab1_pm_read.json`. Label: recipe at replication seeds 408-412, development plus clean test hosts, post hoc, not
held-out; the frozen networks' recipe at fresh seeds 408-412 on H100; the frozen networks 403-407 themselves were not
read on this contrast. One of several AB1 post hoc reads (two contrasts × two comparators, no correction). R4 is a trained positive (OpenCV engine) in all three arms; R3
is in no training list; Sb alone has same-person splice negatives, so an Sb − B gain on R4 vs R3 reads as transfer from
those negatives to whole-frame same-person morphs; Sb vs B does not separate this from Sb's face-spliced positives or
its larger unique-image count (the Sb − Sp contrast, not yet read, would).

| Contrast (decides) | Sb − B seed-mean [95% component bootstrap] | per seed | Sb − A seed-mean [95%] | Verdict (B / A) |
|---|---|---|---|---|
| R4 vs R3, OpenCV, D-stratified, dev + 80 clean test hosts (primary) | +0.042 [+0.019, +0.070] | +0.054 +0.051 +0.055 +0.014 +0.036 | +0.063 [+0.037, +0.097] | **present / present** |
| S4 vs S3, D-stratified, 80 clean test hosts (secondary; asymmetric: Sb is trained on S4/S3) | +0.118 [+0.069, +0.245] | +0.091 +0.168 +0.113 +0.119 +0.099 | +0.123 [+0.077, +0.240] | **present / present** |

Checks of the rule: unstratified seed-mean gains agree in sign (R4 vs R3: +0.046 against B, +0.065 against A); the
development and clean-test seed means agree in sign (Sb − B +0.024 on the 100 development hosts, +0.098 on the 80
clean test hosts), so no cap applies; 151 components (largest 6); interval half-width 0.026 (B) and 0.030 (A).
The sign agrees on both host sets (unstratified +0.036 development, +0.065 clean80); on the development hosts alone the
gain is not distinguishable from zero (reviewer's bootstrap [−0.013, +0.066], seed 411 negative; descriptive), and on
either subset alone the D strata hold only about 60% of rows. The S4-vs-S3 clean80 interval uses the 1,246 of 2,000
draws in which every network's stratified AUC was readable (unregistered conditioning); on clean80 the strata hold 60% of
rows; the unstratified seed-mean gain is +0.169 (reviewer's interval [+0.13, +0.20]).
At its own rule Sb still flags 85% of same-person whole-frame morphs (B 92%, A 98%; development + clean80, seed means;
reviewer's recomputation); every arm separates R3 from bona fide photos at 0.996-1.000; the gain is in ranking, not in
rejecting same-person morphs.

Printed (no verdict): R4 vs R3 Sb − B on dev+clean69 +0.036, test191 +0.070, test159 (not shape-linked) +0.064;
FaceMorpher R4 vs R3 (the less-trained check) Sb − B +0.044 on dev + clean80, +0.072 on test191. S4 vs S3 Sb − B on
dev+clean80 +0.175, on development hosts alone +0.212. Example levels at seed 408 (dev + clean80, D-stratified): R4 vs R3
Sb 0.870, B 0.816, A 0.793; FaceMorpher Sb 0.857, B 0.803, A 0.777; S4 vs S3 on clean80 Sb 0.628, B 0.537, A 0.525.

Adversary floors (printed; "exceeds" = lower 95% bound of the host-bootstrap AUC difference > 0, `check.exceeds`,
unstratified, on the adversary's row sets — ri = all 291 hosts, test = 191 — not the deciding host set): on ri_R4_vs_R3 (all-cue floor 0.793,
nuisance 0.705) Sb's AUC 0.849-0.866 exceeds the all-cue floor on 5 of 5 seeds, B (0.798-0.814) and A (0.772-0.802) on 0
of 5; on test_cv_R4_vs_R3 (floor 0.774) Sb exceeds it on 4 of 5, B and A on 0; on test_fm_R4_vs_R3 (floor 0.796) none of
the three exceeds it (Sb 0.799-0.835). On the splice contrasts (ri_S4_vs_S3 floor 0.773, dev_S4_vs_S3 0.82,
test_S4_vs_S3 0.754) no network exceeds the all-cue floor (Sb 0.715-0.804); Sb exceeds the nuisance floor on 3 of 5
(ri), 1 of 5 (dev) and 2 of 5 (test). The adversary's same-data transfer learner is not yet committed (not printed).

What this licenses (registered wording, qualified by the results review `REVIEW_AB1_A4_20261113.md`): on development data
and clean test hosts, Sb ranks two-person above same-person whole-frame morphs better than the protocol-only and plain
recipes, on a contrast whose negative class (R3) no arm was trained on. Sb exceeds the all-cue floor on the pooled
291-host contrast on 5 of 5 seeds and on test_cv on 4 of 5, not on test_fm; B and A never exceed it, i.e. B and A sit at
what simple morph cues achieve. Read as consistent with transfer from Sb's same-person splice negatives (not separated
from its splice positives or image count). All recipes still flag most same-person morphs. Post hoc, not held-out
evidence; no generalisation, benchmark or frozen-network claim. The S4-vs-S3 gain shows
what Sb's splice training buys on new persons (asymmetric by design), and does not exceed the adversary's all-cue floor.
Results review done 13 Nov (verdicts recomputed independently and reproduced to the third decimal; F1-F7 applied).

## Pipeline-matched contrasts, second round (amendments 5 and 5b, post hoc): read once (Fri Nov 13 21:18 CET 2026)

Reader `src/AB1/ab1_pm2_read.py` (77ace4b3…; imports ab1_pm_read.py ba6efdad… unchanged); outputs
`ab1_pm2_read_Sp.json` (seeds 408-412, H100) and `ab1_pm2_read_FS1.json` (seeds 403-407, A100 PCIe; all 15 FS1 tars
and the 3 Sp 403-405 tars passed the loader checks). Deciding statistic fixed in 5b: R4 vs R3 stratified (0 of 2,000
draws unreadable); S4 vs S3 on the 80 clean test hosts unstratified (754 of 2,000 stratified draws unreadable, 37.7%),
with the stratified seed-mean > 0 required.

**The pipeline-matched family (10 verdicts; registered 95% rule; 99.5% intervals printed as a sensitivity check).** Only
the five R4-vs-R3 verdicts carry new information; the S4-vs-S3 verdicts are expected from training by design. Intervals
are host-resampling bootstraps, conditional on the five trained networks; each 99.5% tail rests on 5 of 2,000 draws
(approximate); the rows share networks, so a Bonferroni reading is conservative; the family covers registered verdicts
only (the printed subsets, FaceMorpher rows and earlier AB1 reads are further looks). Seed-level t intervals (n = 5,
results review) also exclude zero: row 1 [+0.020, +0.064], row 5 [+0.030, +0.069], row 7 [+0.033, +0.068], row 8
[+0.060, +0.102].

| # | Pair, seeds (platform) | Contrast (decides) | Seed-mean gain | 95% interval | 99.5% interval | Verdict |
|---|---|---|---|---|---|---|
| 1 | Sb − B, 408-412 (H100), amendment 4 | R4 vs R3, dev + clean80, stratified | +0.042 | [+0.019, +0.070] | [+0.008, +0.081] | present |
| 2 | Sb − A, 408-412 (H100), amendment 4 | R4 vs R3 | +0.063 | [+0.037, +0.097] | [+0.025, +0.113] | present |
| 3 | Sb − B, 408-412, amendment 4 | S4 vs S3, clean80 (read stratified in amendment 4; unstratified re-print +0.169) | +0.118 | [+0.069, +0.245] (unstratified [+0.136, +0.204]) | [+0.123, +0.221] (unstr.) | present (stands as read) |
| 4 | Sb − A, 408-412, amendment 4 | S4 vs S3, clean80 (unstratified re-print +0.163) | +0.123 | [+0.077, +0.240] (unstratified [+0.130, +0.197]) | [+0.117, +0.209] (unstr.) | present (stands as read) |
| 5 | Sb − Sp, 408-412 (H100) | R4 vs R3, stratified | +0.049 | [+0.028, +0.073] | [+0.019, +0.083] | **present** |
| 6 | Sb − Sp, 408-412 | S4 vs S3, clean80, unstratified | +0.084 | [+0.056, +0.110] | [+0.041, +0.121] | present (near-certain by design) |
| 7 | Sb − B, 403-407 (A100, FS1) | R4 vs R3, stratified | +0.051 | [+0.027, +0.080] | [+0.021, +0.097] | **present** |
| 8 | Sb − A, 403-407 (FS1) | R4 vs R3, stratified | +0.081 | [+0.053, +0.118] | [+0.043, +0.136] | **present** |
| 9 | Sb − B, 403-407 (FS1) | S4 vs S3, clean80, unstratified | +0.182 | [+0.143, +0.219] | [+0.128, +0.234] | present |
| 10 | Sb − A, 403-407 (FS1) | S4 vs S3, clean80, unstratified | +0.174 | [+0.139, +0.207] | [+0.126, +0.222] | present |

Per seed (R4 vs R3, stratified): Sb − Sp +0.060 +0.067 +0.052 +0.027 +0.041; FS1 Sb − B +0.054 +0.034 +0.055 +0.070 +0.042;
FS1 Sb − A +0.085 +0.070 +0.072 +0.109 +0.069. Sign agreement between development and clean test hosts holds for rows 5,
7 and 8 (Sb − Sp +0.049 / +0.069; FS1 Sb − B +0.047 / +0.089; FS1 Sb − A +0.083 / +0.128).

**Decomposition at 408-412 (printed, descriptive; wording of the results review `REVIEW_AB1_A5_20261113.md`):** Sb − B
(+0.042) splits exactly into Sb − Sp (+0.049 [+0.028, +0.073], 5 of 5 seeds) and Sp − B (−0.008 [−0.033, +0.022]). Under
the rule Sp − B reads "absent" before the cap and "inconclusive" after it (development −0.025, clean test +0.029). On
the pooled hosts, the S4 positives without the matched negatives add no detectable R4-vs-R3 gain (upper bound +0.022).
With the positives present, removing the 312 matched S0 + S3 negatives, and with them 624 training rows and the
class-mix shift, removes Sb's gain. On the 80 clean test hosts alone, Sp − B is +0.029 (4 of 5 seeds positive; interval
includes 0), so a share of up to about a third from the positives is not excluded there. Whether the negatives would
work without the S4 positives is untested.
On S4 vs S3 (clean test hosts), Sp − B is +0.085 unstratified but −0.002 D-stratified (strata hold about 60% of rows;
37.7% of draws unreadable). Sb − Sp is +0.084 unstratified and +0.120 stratified. Within D strata, the gain over B comes
from the matched negatives, not the positives (descriptive). FaceMorpher R4 vs R3 (printed; the less-trained engine,
where Sb is not above the adversary floor): Sb − Sp +0.067, Sp − B −0.023; FS1 Sb − B +0.056. Clean-host-only subsets are
reported unstratified only (stratified intervals there are fragile, e.g. FS1 Sb − B [−0.009, +0.141] with 627 of 1,000
draws readable).
Sb − Sp at 403-405 (A100, 3 seeds; descriptive, not read): R4 vs R3 +0.035 [+0.015, +0.062]; S4 vs S3 clean80 +0.091.

**What this licenses (registered wording, post hoc, development plus clean test hosts, not held-out):**
- 408-412 (recipe at replication seeds, H100): removing the matched same-person and seam-only splice negatives (Sp: −312
  negatives, −624 rows at equal steps) loses Sb's better ranking of two-person over same-person whole-frame morphs; Sp is
  not better than B on the pooled hosts. Count and class-mix are not controlled; the interaction with the positives is
  untested; S0 and S3 are not separated.
- 403-407 (FS1): a re-read of the frozen networks 403-407 with the amendment-4 statistic on development + clean test
  hosts; direction previously printed (PR1 Z4 unstratified, test191; BD1 S4 vs S3); adds the D-stratified statistic and
  the clean-host restriction only; not independent, not blind, not held-out. "present" licenses a statement about the
  frozen Sb networks themselves on these development rows; no change to the frozen candidate follows; rows 9-10 add
  nothing beyond BD1. This read must not be cited as corroborating the sealed MAD22 read.
- Ranking is not rejection (amendment-4 review F3): all recipes still flag most same-person morphs at their own rule.

Paper wording allowed (post hoc, development data, not held-out): "In a development-data ablation, removing Sb's matched
same-person and seam-only splice negatives removed its advantage in ranking two-person above same-person whole-frame
morphs (−0.049 AUC, 5 of 5 seeds). Splice positives alone gave no detectable advantage (−0.008 [−0.033, +0.022]). The
frozen networks show the same direction (+0.051 over B, 5 of 5 seeds)." Not allowed: generalisation, benchmark
performance, a volume-controlled effect, an S0-versus-S3 split, or rejection of same-person morphs.
Results review done 13 Nov (all ten verdicts recomputed independently; F1-F7 applied; reviewer's script
`src/AB1/review/a5_recompute.py`, outputs `review_a5_recompute_{sp,fs1}.txt`).
