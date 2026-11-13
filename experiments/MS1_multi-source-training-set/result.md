# Multi-source training set for threshold transfer (MS1): result

Registered read, run once on 13 Nov 2026 (`date`: Fri Nov 13 09:48:53 AM CET 2026) with `src/MS1/ms1_read.py`
(sha256 `416b8930…`, committed at e69e063 before any tar existed) on the 15 fit tars and the three held-out tars in
`/mnt/t7/smad_next/MS1/results_rented/` (all sha256-verified; second copies in `/home/narolski/ms1_results_copy`).
Output `ms1_read.json`. Registration: part 2 at f748da4, deviations MS1-D1 (5eadc1b) and MS1-D2 (86b4b69, all fits and
scoring on NVIDIA L40S 48 GB). Reviewed (REVIEW_MS1_20261113.md). Development data only; never a benchmark claim.

Read seeds: 403, 404, 405, 406, 407 (all 15 fits finite and verified; no seed lost).

## Registered verdicts

| read | Sb (per seed 403-407) | SbM3 (per seed) | medians | test | verdict |
|---|---|---|---|---|---|
| **P1-S** own-rule flags, CFD neutral (831 images, 827 persons) | 0.035, 0.043, 0.034, 0.104, 0.018 | 0.000, 0.001, 0.000, 0.002, 0.000 | 0.035 vs 0.000 (ratio 0.00) | Mann-Whitney U 25/25, p = 0.004 (≤ 0.025) | **supported** (registered rule). Read with the printed costs below; the gain lies between the genuine floor and the attack mode: at a threshold set at the 5th percentile of development attacks both arms flag 0 of 831 CFD images in every seed. |
| **P1-T** own-rule flags, mean over 7 TT1 families | 0.014, 0.042, 0.013, 0.013, 0.017 | 0.008, 0.003, 0.009, 0.004, 0.002 | 0.014 vs 0.004 (ratio 0.30) | U 25/25, p = 0.004 | **untestable at the own rule (floor)**: median(Sb) 0.014 < 0.03 |
| P1-T without MSU-MFSD (printed) | median 0.0165 | median 0.0050 | ratio 0.30 | p = 0.004 | floor |
| **P2** source-offset AUC, TT1 vs development camera photos | 0.9995, 0.9988, 0.9991, 0.9970, 0.9997 | 0.9940, 0.9934, 0.9724, 0.9975, 0.9906 | 0.9991 vs 0.9934 (diff 0.0057) | U 24/25, p = 0.008 | **inconclusive, no claim** (diff < 0.05) |
| **P3** own-rule flags, MS1 FFHQ hold-out photos (300; trained source for SbM3, new persons) | median 0.037 | median 0.0067 | | | **supported** (SbM3 ≤ 0.05), but non-discriminating: Sb's median 0.037 also meets the bound. Printed: Sb 0.017-0.067 vs SbM3 0.007-0.013 (complete separation; unregistered contrast; FFHQ is trained for SbM3). |

Guards (medians across seeds; all hold):
- G1 FFHQ landmark_combined AUC: Sb 0.8735, SbM3 0.8611 (≥ Sb − 0.03; in-source for SbM3 and biased in its favour; no
  improvement claimed).
- G2 development R4 vs R2w AUC 1.000 vs 1.000; AF0 validation u50 vs photo AUC 1.000 vs 1.000; own-rule miss 0.000 vs
  0.000 (at ceiling: this guard cannot detect a cost).
- G3 storage shift at 112.7 px on development camera photos: Sb −0.015 SD, SbM3 −0.021 SD (|SbM3| ≤ |Sb| + 0.10).

Printed costs not covered by G1-G3 (G1 reads AUC only; G2 is at ceiling; post-result review REVIEW_MS1_20261113.md,
recomputed by the reviewer): own-rule miss on FFHQ landmark_combined morphs Sb median 0.271 vs SbM3 0.585 (U 24/25,
p = 0.008; SbV 0.312) while its genuine flags fall 0.064 → 0.007 and AUC is unchanged; development S4 vs S0/S3 AUC
0.891 vs 0.881 (complete separation); S0/S3 own-rule flags 0.18 vs 0.22. Rank read on CFD (same TF32 setting):
AUC(CFD vs R_cam) Sb 0.964 vs SbM3 0.901; logit anchors on training-source photos and attacks unchanged within 0.05.

Registered sentences:
- P1-S: 'With the three-source protocol, genuine flag rates at the network's own rule fall on a sharp unseen studio
  source (CFD), 5 seeds' (Sb median 3.5%, SbM3 0.0%). No attack pool exists on CFD, and on the one unseen-pipeline
  attack pool the same change doubles own-rule misses (printed); the result is not evidence that the operating point
  transfers. The effect belongs to the three-source protocol (photos, morphs, controls, more rows, a smaller splice
  share, lower exposure per FRGC/colorFERET image).
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

Splice share of attack rows: Sb 0.1026, SbM3 0.0641, SbV 0.1050. SbV leaves per-image exposure of Sb's images nearly
unchanged (within-stratum oversampling at fixed steps); it controls the manifest length only, not dilution or splice
share.

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
- **Mixed TF32 setting, same GPU** (label fixed before the read, c0df1c9; measured on L40S on 417 R_cam images per
  network: max |Δlogit| 0.002-0.022, 0 own-rule flips in 15 networks): CFD offset AUC against
  development camera photos Sb 0.90-0.97, SbM3 0.78-0.90, SbV 0.89-0.96; TT1 border references R_cam_border(k)
  own-rule flags (medians) Sb 0.002-0.072, SbM3 0.002-0.082, SbV 0.000-0.058; R_cam 0.000-0.005; R_cam_geo224
  0.000-0.012.

## Caveats

- P1-S rests on CFD alone (a studio source like FRGC); CFD frames are shrunk about 2.7x into the frame.
- KDEF flags are 0 for every network: no information.
- Registered printed items not produced: training-row minus held-out logit per kind; FS1 R1-R6 per arm; the smoke gate
  (WCSS smoke cancelled by the lead, 13 Nov 00:00).
- Reviewed: `experiments/reviews/REVIEW_MS1_20261113.md` (verdicts follow; interpretation qualified as above).

# Part 3 (registered at cff1ada; read once at 10:06 on 13 Nov 2026; `ms1_part3.json`; reviewed)

- **H-mem (memorisation / dilution): supported** by the registered rule (M(SbM3) < M(Sb), 5 of 5 seeds; M Sb 0.153,
  0.134, 0.130, 0.143, 0.112; SbM3 0.110, 0.085, 0.097, 0.090, 0.088; SbV 0.163, 0.135, 0.144, 0.150, 0.123). Reviewed
  (REVIEW_MS1_PART3_20261113.md). Robustness (post hoc, printed): 5/5 also in probability units and as a rank AUC
  (training vs held-out rows of the same kind: Sb 0.541-0.557, SbM3 0.514-0.535); 3/5 with medians. The logit gap sits
  in the tails of unsaturated kinds (S4, S3, and FRGC zero/halves); without S3 and S4 it is 2/5. Which kinds carry it
  depends on the scale (logits: zero, halves, S3, S4; rank: R0, R2w, S0, photo). Memorisation is small in both arms.
  SbM3 fits training rows no less tightly than Sb; the gap closes because held-out tails approach the training level.
  Consistent with lower exposure per image or with regularisation by the added source; it does not separate them.
- **H-new-4 (Feminine rating and CFD logits): inconclusive** by the registered rule (Sb ρ > 0.2 in 1 of 4 groups; SbM3
  |ρ| < 0.1 in 2 of 4; Sb ρ < 0.1 in 2 of 4). The registered within-group statistic is confounded by sex (ρ(Feminine,
  sex) = 0.86). Post hoc, within sex: Sb ρ(Feminine) women 0.248 (n = 307; AF 0.24, BF 0.27, WF 0.16, LF 0.00), men
  0.097; SbM3 0.007 and −0.125; SbV as Sb. Sb's female-skewed own-rule flags (AF 0.102, WF 0.073, BF 0.033 against AM
  0.004, WM 0.045, BM 0.013; 1-15 images per cell and seed, seed 406 the largest) are the same signal. Associational,
  development images only; not a demographic-bias claim.
- Printed: FS1 mean logit drop from landmark_complete to landmark_combined morphs Sb 1.67-2.70, SbM3 3.06-4.06, SbV
  1.82-2.63.
- **Printed items (F8):** train-minus-held-out gaps per kind in `ms1_part3.json`; FS1 R1-R6 per arm and seed in
  `ms1_part3.json` (e.g. R1 stratified AUC Sb 0.823-0.887, SbM3 0.856-0.893, SbV 0.816-0.876; R6 AUC loss complete →
  combined Sb 0.110-0.176, SbM3 0.109-0.149); smoke gate: not producible (the WCSS smoke was cancelled before it ran).

# Part 3b (printed-only amendment registered at 616a910; computed once at 10:14 on 13 Nov 2026; `ms1_part3b.json`)

- Rank-AUC memorisation (mean over 11 FRGC / colorFERET kinds): A(SbM3) < A(Sb) on 5 of 5 seeds; A(SbV) < A(Sb) on 1 of
  5. Values in `ms1_part3b.json` (reproduces the reviewer's post hoc 0.541-0.557 vs 0.514-0.535).
- Within-sex ρ(CFD logit, Feminine), medians over seeds: women Sb 0.248, SbM3 0.007, SbV 0.257; men Sb 0.097, SbM3
  −0.125, SbV 0.074. Per race group × sex and flag counts per seed in `ms1_part3b.json`. Printed only; associational.
