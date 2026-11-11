# PD1 GAN family: adversarial verification (redo), 11 Nov 2026

Scripts (own code, CPU, 2 threads, nice 10, one process): `vlib.py`, `v1_recompute.py` (leakage + headline),
`v3_stats.py` (37 own image statistics), `v2_attacks.py` (latent, set-H directions, statistic heads),
`v4_blank_feats.py` (CLIP ViT-L/14 on CPU, face ellipse or surround blanked to grey in memory; unblanked check vs
owner cache min cosine 0.99999958), `v5_blank_and_final.py` (blanked heads; own final heads on H, FRLL E7, SMDD).
Outputs: `v*_*.json`, `v*.log`, `v1_oof.npz`, `v3_stats.npz`, `v4_blank_feats.npz`.

## Corrected verdict: mixed

Registered rule reproduces ("works"), but the transferred signal is GAN latent closeness to the mean code, which
one-identity renders carry equally; nothing two-person-specific is detected.

## Key numbers (G = 64 blocks; folds by block, own seeds 7/8/9; CI = block bootstrap)
- Leakage: 0 subjects in >1 block; max cross-block FR cosine 0.30; all render sources inside their block; train/test
  image sets disjoint (asserted).
- One-person head, x3 vs x1: CLIP pooled 0.79-0.82 (seed 7: 0.811 [0.771, 0.852]); CLIP patch 0.79-0.80; DINOv3
  0.79-0.82. Two-person head 0.79-0.83. Owner saved OOF re-read: 0.802 / 0.798 / 0.775.
- Unpaired one-person head: 0.77-0.81 / 0.81-0.82 / 0.82-0.85 (paired loss does not matter).
- Statistics heads trained the same one-person way: owner 7 stats 0.60-0.63; own 37 stats 0.61-0.65; face-only 0.55-0.58;
  surround-only 0.56-0.59. Excess of feature heads over these: about +0.15 to +0.20 (holds).
- Latent closeness alone: x3 vs x1 0.9998, x3 vs x2 0.95, x2 vs x1 0.92.
- Head trained on set H one-identity spread (x1s vs x1, CASIA, no mixing, no G data) applied to G: x3 vs x1 0.808
  [0.773, 0.845] CLIP pooled, 0.814 patch, 0.739 DINOv3. Raw H spread direction: 0.77 / 0.80 / 0.71.
- Head trained on set H morph-beyond-spread (x3 vs x1s) applied to G: 0.46 / 0.31 / 0.39.
- Residual of one-person head score after a closeness fit on one-person renders only: x3 vs x1 0.52 [0.47, 0.56]
  (CLIP pooled), 0.55, 0.54.
- Regressor of closeness trained on reconstructions only: 0.58-0.61 (within-rung latent variation is not what is read).
- Same-person mixes: x2 vs x1 0.69-0.76; at the 5%-of-x1 threshold 13-26% of x2 and 14-38% of x3 flagged.
- Blanking (refit, CLIP pooled): face only 0.78-0.80; surround only 0.75-0.76 (patch: 0.79-0.82 / 0.74-0.76).
- Own final heads: H x3 vs x1s 0.465 [0.438, 0.493] / 0.462 / 0.480; H x1s vs x1 0.84 / 0.88 / 0.87;
  primary FRLL E7 flag 8/204 = 3.9% [1.7, 7.6] CLIP pooled.
- Camera photo: x1 vs x0 0.52 (head does not read the render/photo frame); x3 vs x0 0.85, but file bytes alone 1.00.
