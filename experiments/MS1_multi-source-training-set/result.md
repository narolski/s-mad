# Multi-source training set for threshold transfer (MS1): result

Registered read, run once on 13 Nov 2026 (`date`: Fri Nov 13 09:48:53 AM CET 2026) with `src/MS1/ms1_read.py`
(sha256 `416b8930…`, committed at e69e063 before any tar existed) on the 15 fit tars and the three held-out tars in
`/mnt/t7/smad_next/MS1/results_rented/` (all sha256-verified; second copies in `/home/narolski/ms1_results_copy`).
Output `ms1_read.json`. Registration: part 2 at f748da4, deviations MS1-D1 (5eadc1b) and MS1-D2 (86b4b69, all fits and
scoring on NVIDIA L40S 48 GB). Owner's numbers; NOT yet reviewed. Development data only; never a benchmark claim.

Read seeds: 403, 404, 405, 406, 407 (all 15 fits finite and verified; no seed lost).

## Registered verdicts

| read | Sb (per seed 403-407) | SbM3 (per seed) | medians | test | verdict |
|---|---|---|---|---|---|
| **P1-S** own-rule flags, CFD neutral (831 images, 827 persons) | 0.035, 0.043, 0.034, 0.104, 0.018 | 0.000, 0.001, 0.000, 0.002, 0.000 | 0.035 vs 0.000 (ratio 0.00) | Mann-Whitney U 25/25, p = 0.004 (≤ 0.025) | **supported** |
| **P1-T** own-rule flags, mean over 7 TT1 families | 0.014, 0.042, 0.013, 0.013, 0.017 | 0.008, 0.003, 0.009, 0.004, 0.002 | 0.014 vs 0.004 (ratio 0.30) | U 25/25, p = 0.004 | **untestable at the own rule (floor)**: median(Sb) 0.014 < 0.03 |
| P1-T without MSU-MFSD (printed) | median 0.0165 | median 0.0050 | ratio 0.30 | p = 0.004 | floor |
| **P2** source-offset AUC, TT1 vs development camera photos | 0.9995, 0.9988, 0.9991, 0.9970, 0.9997 | 0.9940, 0.9934, 0.9724, 0.9975, 0.9906 | 0.9991 vs 0.9934 (diff 0.0057) | U 24/25, p = 0.008 | **inconclusive, no claim** (diff < 0.05) |
| **P3** own-rule flags, MS1 FFHQ hold-out photos (300; trained source for SbM3, new persons) | median 0.037 | median 0.0067 | | | **supported** (SbM3 ≤ 0.05) |

Guards (medians across seeds; all hold):
- G1 FFHQ landmark_combined AUC: Sb 0.8735, SbM3 0.8611 (≥ Sb − 0.03; in-source for SbM3 and biased in its favour; no
  improvement claimed).
- G2 development R4 vs R2w AUC 1.000 vs 1.000; AF0 validation u50 vs photo AUC 1.000 vs 1.000; own-rule miss 0.000 vs
  0.000 (at ceiling: this guard cannot detect a cost).
- G3 storage shift at 112.7 px on development camera photos: Sb −0.015 SD, SbM3 −0.021 SD (|SbM3| ≤ |Sb| + 0.10).

Registered sentences:
- P1-S: "With the three-source protocol, genuine flag rates at the network's own rule fall on a sharp unseen studio
  source (CFD), 5 seeds." The effect, if any, belongs to the three-source protocol (photos, morphs, controls, more
  rows, a smaller splice share); nothing is attributed to source diversity alone.
- P1-T: "inconclusive, no claim" (floor).
- MS1 rule of FINAL section 1 (both co-primaries supported and every guard holding): not met (P1-T at the floor).

## Data-volume control SbV (printed, no claim either way)

| read | Sb | SbV | SbM3 | SbV lower than Sb | SbM3 lower than SbV |
|---|---|---|---|---|---|
| CFD flags (median) | 0.0349 | 0.0385 | 0.0000 | p = 0.48; support rule not met | U 25/25, p = 0.004 |
| TT1 F (median) | 0.0141 | 0.0159 | 0.0043 | p = 0.42 | p = 0.004 |
| P2 offset AUC | 0.9991 | 0.9993 | 0.9934 | p = 0.79 | p = 0.004 |
| P3 hold-out flags | 0.0367 | 0.0333 | 0.0067 | p = 0.40 | p = 0.004 |
| G1 landmark_combined AUC | 0.8735 | 0.8618 | 0.8611 | | |

Splice share of attack rows: Sb 0.1026, SbM3 0.0641, SbV 0.1050. SbV (Sb's rows oversampled to SbM3's 13,414) does not
lower the unseen-source flags; the fall is not reproduced by the row count alone.

## Printed only

- TT1 per-family own-rule flags (medians over seeds), Sb / SbM3 / SbV: replay_attack 0.000 / 0.000 / 0.005; msu_mfsd
  0.000 / 0.000 / 0.000; oulu_npu 0.018 / 0.005 / 0.021; casia_fasd 0.000 / 0.000 / 0.000; lfw_calfw 0.011 / 0.005 /
  0.009; cfp_ff 0.041 / 0.011 / 0.055; agedb_30 0.025 / 0.009 / 0.022. SbM3's median is below Sb's in 4 of 7 families.
- KDEF neutral straight (140): own-rule flags 0.000 for every network.
- At τ_cam (5% false alarms on development camera photos; about −3.3 to −3.5 logits) TT1 genuine photos are flagged at
  0.97-1.00 by every arm and CFD at 0.44-0.67 (Sb), 0.07-0.23 (SbM3), 0.41-0.63 (SbV): τ_cam is degenerate for unseen
  sources (as FS1 review F10).
- FFHQ (trained source for SbM3): ffhqm HN2 genuine own-rule flags Sb 0.048, SbM3 0.0025; MS1 hold-out u50 vs photo AUC
  Sb 0.991, SbM3 0.9997; FS1 contrast-2 paired storage share Sb 0.155, SbM3 0.236; MS1 hold-out storage shift Sb
  −0.20 / −0.13 SD (61.2 / 112.7 px), SbM3 −0.03 / −0.02 SD.
- **Mixed TF32 setting (TF32 on vs off), same GPU** (label fixed before the read, c0df1c9): CFD offset AUC against
  development camera photos Sb 0.90-0.97, SbM3 0.78-0.90, SbV 0.89-0.96; TT1 border references R_cam_border(k)
  own-rule flags (medians) Sb 0.002-0.072, SbM3 0.002-0.082, SbV 0.000-0.058; R_cam 0.000-0.005; R_cam_geo224
  0.000-0.012.

## Caveats

- P1-S rests on CFD alone (a studio source like FRGC); CFD frames are shrunk about 2.7x into the frame.
- KDEF flags are 0 for every network: no information.
- Post-result review pending.
