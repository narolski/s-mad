# Results review: ablation arm without matched splice negatives (Sp), seeds 403-405 (13 Nov 2026)

Reviewer: results-reviewer agent (Opus), read-only; saved by the AB1 owner (the reviewer could not write files).
Recomputation code: `src/PN1/sp_review_recompute.py` (copied from the reviewer's scratch folder).

Verdict: the registered "falsified" follows and every printed number recomputes exactly (all 9 tars match their
.sha256; sp_read.py 3ff01108 as pinned; floor3 development AUC 0.9014). The plain-words sentence over-read it: both
predictions had little room (S0 at the floor in every arm including B; S0-vs-S4 AUC near the ceiling; a 3-statistic
floor at 0.90). The result shows Sp did not learn an S0-type seam cue, not that the matched negatives are inert.

Findings: F1 (major) replacement sentence with floor and ceiling context; F2 (major) same-seed pairs share only the
initialisation, landmark_combined differences +0.065 / +0.043 / +0.039 near the about 0.04 between-arm noise, 3 of 3
positive by chance 1/8; F3 (major) the S3 rise is partly built in; threshold-free S3-vs-S4 AUC Sp 0.684 / 0.705 / 0.703
against Sb 0.786 / 0.793 / 0.781, S4 flagged 0.91-0.92 against 0.71-0.85; F4 (moderate, post hoc, training rows) Sb
flags 43 / 40 / 47 of 156 training S3 negatives and misses 5 / 8 / 4 training S4, no other training error (0.991), Sp
fits 99.96-99.98%: S3 against S4 is the one conflict Sb cannot fit (bears on PR1 Z1 underfit; predicts AB1 H-ab4
falsified); F5 (moderate) operating point: Sp flags 0.085 / 0.154 / 0.116 of native FFHQ genuine (Sb 0.024-0.050, B
0.052-0.107); Sp storage share at B's level (B 0.234 / 0.326 / 0.278), orientation only; F6 (minor) platform verified
(GPU-5bd20020, host e8bf0b3abe77, same container, common_py b5d42a99, 6,250 steps, limit 0, 19,797 rows); scorer and
TF32 fixed by the pack pins, not recorded per fit; F7 (minor) state the excess over a floor of 0.90.

May say (descriptive, development, n = 3, one A100): Sp flags more S3, ranks S3 against S4 worse, flags more FFHQ
genuine images, has higher landmark_combined AUC. May not say: Sp is better; S0 against S3 attribution; storage; SBI or
SelfMAD; benchmarks. Call S0 "seam-matched in size, not in kind".

New hypotheses: H-new-1 the S3 negatives, not S0, are the active constraint in Sb (arms "Sb minus S0 only", "Sb minus S3
only", about 4 H100-h, needs the author, post-deadline); H-new-2 fitting S3 against S4 costs at least +0.03
landmark_combined (Sp − Sb ≥ +0.03 on ≥ 4 of 5 at 408-412; 0 GPU, register before the AB1 read with disclosure);
H-new-3 the S3/S0 negatives reduce the storage reaction (Sp C2P Δf at amsl112 above Sb's on ≥ 4 of 5 at 408-412; 0 GPU,
register before the AB1 read). Also zero-GPU: S0 against the genuine rung per arm; training-misfit S3 rows against blend
and tone statistics; Jaccard overlap of flagged S3 images across seeds; a note in AB1 that H-ab4 is expected to be
falsified for floor and ceiling reasons.
