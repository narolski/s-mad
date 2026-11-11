# Signal isolation by paired differences (PD1), diffusion-autoencoder family: result

Owner run, 11 Nov 2026. Pre-registration: `prereg.md` (16:56 CET, before any computation). Code `src/PD1/diffae/`.
Large outputs `/mnt/t7/smad_next/PD1/diffae/`. STATUS: first pass only; the full run is in progress.

## First end-to-end pass (CLIP ViT-L/14 pooled, fold 0 held out, 18:11 CET)

Training hosts: 129 DiffAE blocks (FERET and FRGC), 258 persons, 516 hosts; fold 0 holds 26 blocks = 104 hosts
(52 same-person mixes, 52 two-person morphs). Heads fitted on the other four folds. Two-way person bootstrap,
B = 10,000. All renders 20 decoding steps, all images 256 px lossless PNG. File `first_pass.json`.

Rungs: genuine photo (x0), pass-through reconstruction (x1), same-person mix (x2), two-person morph (x3).

**Q1, direction consistency (held-out share of hosts moving the expected way; AUC of the one projection):**

| Step | Share [95%] | Projection AUC [95%] | Fixed reading |
|---|---|---|---|
| pipeline trace (x0 to x1) | 1.000 [1.000, 1.000] | 0.913 [0.872, 0.954] | consistent direction |
| same-person mixing (x1 to x2) | 0.942 [0.894, 0.981] | 0.871 [0.822, 0.918] | consistent direction |
| second identity (x2 to x3) | 0.856 [0.648, 0.986] | 0.793 [0.700, 0.883] | not consistent (lower bound 0.648) |
| whole morph (x1 to x3) | 0.913 [0.808, 0.987] | 0.793 [0.689, 0.890] | consistent direction |
| genuine to morph (x0 to x3) | 0.990 [0.943, 1.000] | 0.944 [0.870, 0.988] | consistent direction |

**Q3, one-person head (H1: trained on same-person mix against reconstruction of the same host) and the
two-person comparator (H2: trained on two-person morph against reconstruction):**

| Contrast (held-out) | H1 AUC [95%] | H2 AUC [95%] | Best single statistic (folded AUC) | H1 excess over it [95%] |
|---|---|---|---|---|
| x3 vs x1 (morph vs reconstruction) | **0.955 [0.892, 0.993]** | 0.983 [0.955, 1.000] | PNG size 0.731 | **+0.225 [0.116, 0.353]** |
| x3 vs x0 (morph vs genuine photo) | 0.876 [0.758, 0.966] | 0.948 [0.884, 0.997] | PNG size 0.877 | −0.001 [−0.173, 0.183] |
| x2 vs x1 (training task) | 0.978 [0.950, 0.997] | 0.991 | PNG size 0.764 | +0.214 |
| x1 vs x0 (reconstruction vs photo) | 0.260 [0.208, 0.304] | 0.229 | PNG size 0.945 | (reconstructions score below photos) |
| x3 vs x2 (two-person vs same-person mix) | 0.249 [0.149, 0.358] | 0.438 [0.278, 0.606] | Laplacian variance 0.573 | (same-person mixes score above morphs) |

Paired shares (H1): s(x3) > s(x1) in 0.99 [0.95, 1.00] of held-out hosts; s(x1) > s(x0) in 0.04. A head on the seven
statistics trained the same way as H1 reaches 0.742 for x3 vs x1. C chosen = 0.01 for both heads.

Reading of the first pass (one fold, not the registered verdict): on DiffAE renders the one-person head separates
two-person morphs from reconstructions well above the simple-statistic floor, but it ranks same-person mixes above
two-person morphs (0.25), so what it reads is the mixing step, not a second identity. Genuine photos score above
reconstructions. Softened genuine photos and the remaining folds, feature sets, projections and benchmark cells
follow.
