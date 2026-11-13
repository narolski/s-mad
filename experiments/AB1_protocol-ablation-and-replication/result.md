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
negative arms. Zero GPU: sharpness enrichment of flipped persons.
