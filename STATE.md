# State of the method (Sb) — one page, keep it one page

Updated 2026-11-18. Read this first; update it last. Everything else in the repo is archive.
Rule for this phase: most compute goes to making Sb better; audits only for results that will be claimed.

## What Sb is

CLIP ViT-B/16 + LoRA (rank 2), 6,250 updates, batch 256, constant LR, last checkpoint, no selection.
Only the training data are special: plain morphs + processing negatives (warp-only, warped halves,
stored-small copies) + two-person face splices as positives + same-person splices and seam-only
images as negatives. 8,386 balanced rows from FRGC and color FERET.
Frozen networks: seeds 403-407, `weights/sb_frozen_s403-407/`. Paper submitted 17 Nov 2026 (CVPR #21469).

## Where it stands (EER %, lower is better; 5-seed means)

| Test | Sb | Best other | Note |
|---|---|---|---|
| MAD22, aligned-history genuine, mean of 4 families | 3.37 | 9.70 (MADation B/16 + our data) | development-exposed |
| MAD22 Webmorph | 10.39 (seeds 5.2-15.6) | 11.44 | weakest MAD22 cell, large seed spread |
| MAD22 FaceMorpher | 3.67 | 0.98 (SelfMAD) | cell is solvable by shortcuts |
| FRLL-Morphs aMSL | 11.85 | 2.94 (SelfMAD) | **not best on any FRLL family** |
| FRLL-Morphs Webmorph | 11.69 | 2.21 (MADation B/16) | |
| FRLL-Morphs StyleGAN | 10.87 | 9.08 (MixFaceNet-MAD) | |
| FRLL-Morphs FaceMorpher / OpenCV | 2.35 / 1.37 | 0.57 / 0.16 | |

Control results: two-person vs same-person ranking +0.048 AUC over the count-balanced arm, but
whole-frame same-person morphs are still flagged 85% of the time; one-photo GAN renders flagged
78-90%; blend-vs-warp AUC 0.889 vs 0.925 for simple image statistics; false alarms on enlarged
genuine photos at most 2.7% (plain baseline up to 39%).

## The three biggest weaknesses

1. **Landmark morphs from pipelines we did not train on (FRLL aMSL, Webmorph).** Our data make
   MADation worse there too (aMSL 4.9 -> 9.5, Webmorph 4.1 -> 12.7), so the cause is the recipe, not the
   backbone. Likely: our morphs come from too few morphing pipelines and blending styles.
2. **Same-person manipulations are still called attacks** (85% whole-frame, 36-41% splices), and Sb
   underfits its own same-person splice rows (26-37% of training rows flagged). The network has not
   learned "two identities"; it has learned "manipulated face region" less strongly than before.
3. **Fragile training.** Webmorph EER varies threefold across seeds; the same data in MADation's
   training code gives 9.7 instead of 3.4 on MAD22 (mostly MIPGAN). Something in schedule, LR or
   sampling matters and is not understood.

## Tried and did not help (do not repeat without a new idea)

Tail-risk objectives; paired ranking loss; matched hard negatives; matched negatives without splice
positives (BN vs BV); stored-small copies alone. Not run or not finished: twice-as-long training
(SbL), 512-px input (RZ1), multi-source data with FFHQ and CelebA-HQ (MS1, built but not read),
ViT-L/14.

## Next three experiments (in order)

1. **Build the development benchmark first.** Held-out persons; morphs from at least four pipelines
   (incl. an aMSL-style and a Webmorph-style one built by us); matched-history genuine photos; one
   command, one table, scored for every candidate. Without it there is no feedback signal, and the
   sealed benchmarks stay closed. No GPU needed.
2. **Pipeline diversity (weakness 1).** Add morphs from two or three more landmark pipelines and
   blending styles to the Sb data at a fixed row count. Success: aMSL-style and Webmorph-style
   development EER drop by a third without losing the storage and mugshot results.
3. **Training stability (weakness 3).** Same data, 5 seeds each: constant vs cosine LR, 1x vs 2x
   length, with and without per-batch class balance. Success: Webmorph-style seed spread halves.
   This also tells us why MADation's code gives a different network.

Then weakness 2 (identity signal): needs a new idea, e.g. an identity-embedding consistency input or
pairs of same-person / two-person splices that differ only in the donor; design before running.

## Where things are

- Weights: `weights/` (118 small networks in git); comparator retrains on Google Drive
  `pwrdrive:smad-cvpr2027-weights/` and T7.
- Training data pack of Sb: `/mnt/t7/smad_next/PN1/pn1_pack_fs.tar`; manifests in `experiments/`.
- Paper: repo `smad-cvpr-2027` (main = submitted version; branch `supplement-reorg` = supplement,
  due 23 Nov AoE).
- History and all older experiments: `NOTEBOOK.md`.
