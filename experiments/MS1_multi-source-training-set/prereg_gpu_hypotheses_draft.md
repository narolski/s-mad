# DRAFT: GPU follow-ups of the multi-source training set (MS1) and the fourth-source guard

DRAFT only (lead, 13 Nov ~10:10: "draft their registrations but submit nothing; they go to WCSS behind the
method-critical work only if I say so"). Nothing here is registered, built, uploaded or submitted. Source: post-result
review `experiments/reviews/REVIEW_MS1_20261113.md` (H-new-1, H-new-2, H-new-3, H-new-5) and part 3 (H-mem supported:
SbM3's train-minus-held-out gap is smaller on 5 of 5 seeds, mostly on zero, halves, S3 and S4).

Common rules for all three: development data only; one GPU model and one TF32 setting for every score that enters a
comparison (all arms of a comparison trained and scored in the same jobs on the same platform; any rescoring through
`src/TT1/rescore_tf32.py` when the stored logits came from `pn1_score.py`); seeds 403-407; a seed is read only if every
arm of the comparison finished finite and verified; exact one-sided Mann-Whitney with ties half; no seed chosen on a
score; GPU name, UUID, torch, cuDNN and TF32 flags recorded per job; independent pre-run review before submission.

## G1 (review H-new-1): is P1-S an operating-point move? CFD morph pool scored by the existing networks

- Build (author item, hard rule 3: the unchanged OpenCV-style engine on aligned CFD frames): 300 two-person morphs u50
  of CFD neutral frames (the CFD pool already aligned, d6ef6793…), partners drawn within CFD by the AF0 rule (random
  other person, same set; seed 20261113), plus their fm61 stored copies; persons disjoint from nothing else (CFD is
  held out from training). The genuine side is the existing CFD pool.
- Scoring: the 15 kept MS1 networks (Sb, SbM3, SbV × 403-407; `last_trainable.pt` in the result tars) on CFD genuine and
  CFD morphs, all in one job on one GPU model. The L40S leases are released; on any other GPU model every network
  of the comparison is rescored there (genuine and morphs alike), so no score is compared across platforms.
- Prediction (H-new-1): own-rule miss on CFD morphs SbM3 > Sb + 0.02 on ≥ 4 of 5 seeds, while AUC(CFD morphs vs CFD
  genuine) differs by at most 0.01 (median). Falsified if SbM3's miss ≤ Sb's + 0.02 on ≥ 4 of 5 seeds. Printed: SbV;
  the same at an attack-anchored threshold.
- Cost: about 0.5 GPU-h plus the build (CPU, about 10 min).

## G2 (review H-new-2): dilution or diversity? Sb at 0.63x steps

- Arms (one platform, WCSS H100, all trained in this experiment): Sb at 6,250 steps (the recipe), Sb at 3,938 steps
  (0.63 × 6,250, the per-image exposure of FRGC / colorFERET rows in SbM3), SbM3 at 6,250; seeds 403-407 (15 fits,
  about 13 H100-h). Training and scoring command unchanged except `--steps`.
- Prediction if dilution explains P1-S: CFD own-rule flag median of Sb(3,938) ≤ 0.5 × Sb(6,250) with Mann-Whitney
  p ≤ 0.025. Falsified (dilution does not explain it) if the median is ≥ 0.8 × Sb(6,250). SbM3 is the positive control
  (it must again fall below Sb(6,250) by the P1-S rule, else "uninformative").
- Printed: the H-mem gap per kind for all three arms.

## G3 (review H-new-3): does the smaller splice share explain the S4 cost?

- Arms (one platform, all trained here): SbM3, SbM3-S (SbM3 manifest with lad_S4 rows repeated so that the splice share
  of attack rows is 0.103, Sb's), Sb; seeds 403-407 (15 fits, about 13 H100-h).
- Prediction: development S4 vs S0/S3 AUC of SbM3-S ≥ Sb's − 0.005 (median) while CFD own-rule flags stay ≤ 0.01
  (median). Falsified if SbM3-S's S4 vs S0/S3 AUC ≤ SbM3's + 0.002 on ≥ 4 of 5 seeds.

## Fourth source (CelebA-HQ or any other): binding guard, written into the plan now

No fit on a fourth source without a registered **own-rule miss guard on an attack pool from an unseen pipeline**
(review H-new-5): before any SbM4 fit, the registration names an attack pool whose morph pipeline no arm trained on
(e.g. FFHQ landmark_combined, or a pool built from a held-out source with a different engine), its own-rule miss rate
for the comparator and for SbM4 on the same platform, and a fixed margin (proposal: median miss(SbM4) ≤ median
miss(comparator) + 0.05, and not worse on ≥ 4 of 5 seeds by more than 0.10). A failing guard blocks any
operating-point or transfer claim for SbM4. The CelebA-HQ preparation (alignment, persons, overlap) continues as
preparation only.
