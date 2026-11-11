# Signal isolation by paired differences (PD1), diffusion-autoencoder family: result

Owner run, 11 Nov 2026, 16:56 to 20:00 CET. Pre-registration `prereg.md` (16:56 CET, before any computation).
Code `src/PD1/diffae/` (`pd1_items.py`, `pd1_feats.py`, `pd1_stats.py`, `pd1_fr.py`, `pd1_analysis.py`,
`pd1_rescore.py`, `pd1_mirror.py`, `pd1_report.py`, `run_*.sh`). Large outputs `/mnt/t7/smad_next/PD1/diffae/`
(item list `lists/items.csv` sha 20c463d4…, features `feat/{clip,dino}/`, statistics `stats/`, glintr100 embeddings
`fr/`, final heads `heads/`, out-of-fold scores `oof_<feature>.npz`). Small results in this folder:
`results_<feature>.json` (everything), `readings.csv`, `q1.csv`, `q2_cos.csv`, `q3q4.csv`, `flags.csv`,
`external.csv`, `bench.csv`, `q5.csv`, `mirror.json/.csv`, `first_pass.json`. Report facts only.

Rungs, in words: genuine photo (x0); pass-through image = DiffAE reconstruction of the photo alone (x1); same-person
mix = DiffAE mix of two photos of the same person (x2); two-person morph (x3); mirror mix = the photo mixed with its
own mirror image (xm, FRLL only). One-person head (H1) = linear head trained only on x2 against x1 of the same host;
two-person head (H2) = the same recipe on x3 against x1. Simple-statistic floor = the best of seven simple image
statistics (Laplacian variance, high-frequency energy, mirror asymmetry, three channel standard deviations, PNG size).

## Data actually used

- **Training hosts:** 129 complete DiffAE blocks (102 from `diffae-expanded123-v1`, 27 from `confirmation64-diffae-v1`;
  `diffae-roi102-v1` holds no images of its own, it is a read-out of the same 102 blocks). 258 FERET and FRGC persons,
  516 hosts (captures), 1,548 images: 516 photos, 516 reconstructions, 258 same-person mixes, 258 two-person morphs, all
  256 px lossless PNG, all renders 20 decoding steps. Excluded before any computation: `confirm64-feret-F-05` (a val10
  person). No mirror mix and no graded mix exist for these hosts.
- **FRLL (evaluation and diagnostics only, never in a fit):** 256 lossless photos (204), 20-step reconstructions (204),
  100-step reconstructions (204), same-person mixes at 20 and 100 steps (102 each, neutral + smiling: confounded),
  same-pair two-person morphs at 20 and 100 steps (200 each); the A43 stored-size frames (published MorDIFF 200, our
  morphs, mixes, reconstructions, the photo stored small); native photos R0 (204) and their E7 copies R1 (204).
  Mirror mixes: AD1b smoke only, **4 FRLL persons** (AD1b's full run had not written its renders when this page was
  written; see "Not verified").
- **Softening material:** 1,200 SMDD genuine renders with their existing shrunk copies (80 px) from the morph-free
  networks data (A47 I-3): 600 to fit the softening direction, 600 held out for flag rates.
- **Benchmark cells:** registered `eval.csv` (sha 86d055d3…): MorDIFF (1,000 morphs) and DiM A, DiM C, Fast-DiM,
  Fast-DiM-ODE, Greedy-DiM, Greedy-DiM-S (499 or 500 each), FRLL genuine photos native (204) and history-matched (204 per
  family).
- **Features:** CLIP ViT-L/14 pooled (768), CLIP ViT-L/14 mean patch token (1,024), DINOv3 ViT-L/16 pooled (1,024),
  frozen, 224 input via the existing loader, fp32. 12,627 images per model. **DINOv3 "pooled" is the timm default
  average of the patch tokens, so the registered DINOv3 mean-patch set is identical to it (max |Δ| = 0) and was not
  analysed separately**; three distinct feature sets. Reuse check against FZ1's caches on 72 A43 frames: CLIP max
  |Δ| 1.9e-6, DINOv3 0 (pass).
- **Face recognition for Q5:** glintr100 through AR1's route, 516 of 516 training photos embedded.

## Fixed readings (registered), all three feature sets

| Feature set | One-person head, morph vs reconstruction (x3 vs x1) [95%] | Floor (PNG size) | Excess [95%] | FRLL E7 genuine photos flagged at the 5% native threshold [exact 95%] | Reading |
|---|---|---|---|---|---|
| **CLIP pooled (primary)** | **0.948 [0.921, 0.970]** | 0.773 | **+0.175 [0.125, 0.229]** | **2.0% [0.5, 4.9]** | **works** |
| CLIP mean patch | 0.877 [0.830, 0.917] | 0.773 | +0.104 [0.041, 0.167] | 4.4% [2.0, 8.2] | works |
| DINOv3 pooled | 0.913 [0.867, 0.950] | 0.773 | +0.140 [0.077, 0.202] | 3.9% [1.7, 7.6] | works |

Held-out hosts, 5 folds by person (block), pooled out-of-fold, two-way person bootstrap B = 10,000. The floor
statistic is PNG file size (morphs larger than reconstructions); Laplacian variance alone gives 0.521 for this
contrast. A head on the seven statistics trained the same way as H1 reaches 0.746. Under the registered rule the idea
**works** for this family on every feature set.

## What the one-person head actually reads (CLIP pooled; the other two feature sets agree in sign)

| Contrast, held-out hosts | H1 (one-person) | H2 (two-person) | Best single statistic |
|---|---|---|---|
| x3 vs x1, morph vs reconstruction | 0.948 [0.921, 0.970] | 0.989 [0.977, 0.996] | 0.773 (PNG size) |
| x2 vs x1, same-person mix vs reconstruction (H1's training task) | 0.981 [0.971, 0.990] | 0.991 | 0.791 (PNG size) |
| **x3 vs x2, two-person morph vs same-person mix** | **0.288 [0.229, 0.352]** | 0.456 [0.384, 0.529] | 0.544 (Laplacian variance) |
| x1 vs x0, reconstruction vs genuine photo | 0.276 [0.253, 0.298] | 0.232 [0.208, 0.256] | 0.961 (PNG size) |
| x3 vs x0, morph vs genuine photo | 0.876 [0.828, 0.918] | 0.939 [0.911, 0.961] | **0.906 (PNG size)** |

- Same-person mixes score **above** two-person morphs for every feature set (H1 x3 vs x2: CLIP pooled 0.288, CLIP
  patch 0.369, DINOv3 0.376). A head trained on two-person morphs does not separate them from same-person mixes either
  (0.456, 0.582, 0.545). The signal caught is the DiffAE mixing step, not a second identity.
- Reconstructions score **below** genuine photos (x1 vs x0 0.28 / 0.40 / 0.47).
- For morph against genuine photo on these hosts, PNG size alone (0.906) is at or above every H1 (0.876 / 0.825 /
  0.918; excess −0.030, −0.081, +0.012). This contrast is not part of the registered reading.
- Paired shares (CLIP pooled H1): s(x3) > s(x1) in 98.3% [96.0, 99.8] of held-out hosts; s(x2) > s(x1) in 99.6%;
  s(x1) > s(x0) in 9.9%. Per-fold x3-vs-x1 AUC 0.943 to 0.961.
- Cohort transfer (fit on the 102 expanded123 blocks, scored on the 27 confirmation blocks, CLIP pooled):
  H1 x3 vs x1 0.942 [0.850, 0.995], H2 0.991.

## Q1 Direction consistency (held-out hosts)

| Step | CLIP pooled share [95%] / projection AUC | CLIP mean patch | DINOv3 pooled | Reading (all three) |
|---|---|---|---|---|
| pipeline trace (x0 to x1) | 1.000 [1.000, 1.000] / 0.896 | 1.000 / 0.882 | 1.000 / 0.979 | consistent |
| same-person mixing (x1 to x2) | 0.944 [0.922, 0.965] / 0.895 | 0.994 / 0.928 | 0.988 / 0.910 | consistent |
| second identity (x2 to x3) | 0.812 [0.726, 0.884] / 0.762 | 0.855 [0.787, 0.914] / 0.766 | 0.859 [0.785, 0.919] / 0.791 | consistent |
| whole morph (x1 to x3) | 0.926 [0.885, 0.961] / 0.834 | 0.948 / 0.853 | 0.955 / 0.850 | consistent |
| genuine to morph (x0 to x3) | 0.981 [0.951, 0.998] / 0.918 | 0.988 / 0.929 | 0.998 / 0.982 | consistent |

Diagnostic (FRLL, training direction applied unchanged, no reading): pipeline 204 of 204 hosts, whole morph at 256 px
91.0% (CLIP pooled), mirror mix 4 of 4.

## Q2 Geometry (cross-validated split-half cosines, 200 splits; 95% from 1,000 block bootstraps)

| Pair | CLIP pooled | CLIP mean patch | DINOv3 pooled | Reading |
|---|---|---|---|---|
| same-person mixing vs whole morph | **0.76 [0.67, 0.76]** | 0.73 [0.62, 0.72] | 0.81 [0.73, 0.82] | aligned (≥ 0.5): the direction learned from same-person mixes is the direction of real morphs |
| same-person mixing vs softening (SMDD) | −0.19 [−0.21, −0.15] | −0.13 | −0.11 | not softness |
| same-person mixing vs pipeline trace | −0.05 [−0.09, −0.01] | −0.06 | 0.19 | not the pipeline trace |
| same-person mixing vs second identity | **−0.70** | −0.34 | −0.36 | (no rule) anti-aligned |
| whole morph vs softening | −0.22 | −0.09 | 0.06 | (no rule) |

Split-half reliabilities 0.76 to 1.00 (the point value of the reliability can exceed its bootstrap upper bound because
the replicates resample with duplicates). Upper bounds of several off-diagonal intervals sit at the point value for the
same reason; the intervals are printed as computed. Diagnostics on FRLL (CLIP pooled; directions from FRLL images
only, no fit): the SMDD softening direction agrees with the FRLL E7 direction (cos 0.53) and the FRLL stored-small
direction (0.54) (CLIP patch 0.18 / 0.14, DINOv3 0.32 / 0.19); the FRLL whole-morph direction at 256 px is aligned with
the training mixing direction (0.67); the 4-person mirror-mix direction has cos 0.62 with it (reliability 0.58).

## Q3 Softened genuine photos (final heads fit on all 516 hosts; FRLL and SMDD scoring only)

| Pool (threshold flags 5% of the untouched photos) | CLIP pooled H1 | CLIP patch H1 | DINOv3 H1 | CLIP pooled H2 |
|---|---|---|---|---|
| FRLL E7 copies (primary) | 2.0% [0.5, 4.9], shift −0.18 sd | 4.4% [2.0, 8.2] | 3.9% [1.7, 7.6] | 1.5% |
| FRLL photo stored small (A43 arm E) | 0.0% [0.0, 1.8] | 2.9% | 3.4% | 0.5% |
| SMDD held-out shrunk copies (600) | 0.0% [0.0, 0.6] | 2.3% | 1.8% | 0.0% |

Softened genuine photos are not flagged more than untouched ones; their mean score moves down or stays (−0.53 to
+0.17 sd).

## Q4 Trace subtraction (refit inside each fold after removing directions fitted on training material only)

| Feature set | none | softening k=1 | softening k=5 | pipeline | softening + pipeline |
|---|---|---|---|---|---|
| CLIP pooled: H1 x3 vs x1 / FRLL E7 flag | 0.948 / 2.0% | 0.950 / 2.5% | 0.950 / 2.5% | 0.936 / 2.5% | 0.934 / 2.9% |
| CLIP mean patch | 0.877 / 4.4% | 0.880 / 6.4% | 0.892 / 5.4% | 0.898 / 5.4% | 0.897 / 5.9% |
| DINOv3 pooled | 0.913 / 3.9% | 0.915 / 4.9% | 0.915 / 4.9% | 0.912 / 3.9% | 0.912 / 4.9% |

Fixed readings: every projected head **keeps its separation** (drop < 0.05; the largest drop is 0.014). "Loses its
reaction to softened genuine photos": **not met** by the registered wording in every cell, because the unprojected
heads had no reaction to lose (2.0 to 4.4%) and the projected rates are equal or 0.5 to 2 points higher. Removing the
pipeline direction moves reconstructions to the level of genuine photos (H1 x1 vs x0 0.276 → 0.512, CLIP pooled) and
raises morph vs genuine photo to 0.950; same-person mixes still score above morphs (x3 vs x2 0.30 to 0.38). All
projections leave the x3-vs-x1 excess over the floor at +0.106 or more.

## Q5 Dose and second identity

- Graded mixing: not testable (no graded DiffAE mixes exist; all renders at α = 0.5).
- Contributor dissimilarity (1 − glintr100 cosine of the two contributors' photos), 258 training morphs, block
  bootstrap:

| Feature set | ρ with the morph's H1 score [95%] | Reading | ρ with the paired step s(x3) − s(x1) | Reading |
|---|---|---|---|---|
| CLIP pooled | +0.242 [0.102, 0.378] | rises with dissimilarity | +0.078 [−0.071, 0.224] | no rise detected |
| CLIP mean patch | +0.369 [0.229, 0.495] | rises | +0.156 [0.008, 0.300] | rises |
| DINOv3 pooled | +0.309 [0.182, 0.429] | rises | +0.136 [−0.012, 0.278] | no rise detected |

Descriptive: the DiffAE semantic-code distance of the two contributors correlates more strongly (ρ +0.45 to +0.58 with
the score, +0.40 to +0.56 with the paired step). Same-person mixes (dissimilarity near 0) nevertheless score highest
(x3 vs x2 above), so the relation is not monotone across the rungs.

## External scoring, no refit (FRLL persons; descriptive; equal step count and storage only)

| Contrast | CLIP pooled H1 | CLIP patch H1 | DINOv3 H1 | CLIP pooled H2 |
|---|---|---|---|---|
| 256 px, 20 steps: our morph vs reconstruction (B20 vs D20) | 0.886 [0.82, 0.94] | 0.816 | 0.943 | 0.978 |
| same, neutral pairs only | 0.903 [0.82, 0.96] | 0.840 | 0.953 | 0.987 |
| 256 px, 20 steps: morph vs genuine photo | 0.851 [0.78, 0.92] | 0.696 | 0.803 | 0.927 |
| 256 px: reconstruction vs genuine photo | 0.421 [0.39, 0.44] | 0.354 | 0.246 | 0.286 |
| 256 px, 100 steps: morph vs reconstruction | 0.889 [0.83, 0.94] | 0.842 | 0.928 | 0.947 |
| stored size, 20 steps: morph vs reconstruction | 0.778 [0.70, 0.86] | 0.803 | 0.857 | 0.916 |
| stored size, 100 steps: morph vs reconstruction | 0.670 [0.59, 0.75] | 0.853 | 0.842 | 0.795 |
| stored size: photo stored small vs native photo | 0.410 | 0.387 | 0.471 | 0.379 |
| stored size: published MorDIFF vs native photo (step count of the release not verified) | 0.680 [0.59, 0.77] | 0.581 | 0.603 | 0.702 |
| mirror mix vs its reconstruction (4 persons, AD1b smoke) | 1.000 (4 of 4 paired) | 0.938 | 1.000 | 1.000 |
| same-person mix (neutral + smiling) vs reconstruction | 0.989 (confounded, no conclusion) | 0.983 | 0.997 | 0.994 |

## Benchmark cells (descriptive, no refit; FRLL genuine photos in 512 frames, training images are DiffAE 256 crops)

One-person head H1, AUC against native genuine photos [95%], EER, AUC against history-matched genuine photos, share of
history-matched photos flagged at the 5% native threshold:

| Cell (morph file size) | CLIP pooled | CLIP mean patch | DINOv3 pooled |
|---|---|---|---|
| MorDIFF (about 150 × 195 px) | 0.680 [0.62, 0.74], EER 38.8%, E7 0.724, flag 2.0% | 0.591, EER 43.6% | 0.638, EER 40.1% |
| DiM A (256 px) | 0.968 [0.94, 0.99], EER 9.4%, E7 0.968, flag 4.9% | 0.900, 17.6% | 0.969, 10.7% |
| DiM C | 0.956, EER 10.9%, E7 0.955 | 0.746, 33.8% | 0.778, 30.3% |
| Fast-DiM | 0.973, EER 9.4%, E7 0.973 | 0.875, 19.7% | 0.857, 22.0% |
| Fast-DiM-ODE | 0.989, EER 4.9%, E7 0.989 | 0.961, 9.4% | 0.969, 9.3% |
| Greedy-DiM | 0.832 [0.78, 0.88], EER 27.4%, E7 0.821 | 0.671, 39.8% | 0.684, 37.2% |
| Greedy-DiM-S | 0.978, EER 8.8%, E7 0.978 | 0.908, 16.3% | 0.936, 15.1% |

History-matched genuine photos are flagged at 2.0 to 4.9% (CLIP pooled), so these cells do not move with photo history;
the neutral-only genuine column moves AUCs by at most 0.05. H2 (two-person head, CLIP pooled): MorDIFF 0.711, DiM
families 0.882 to 0.995. With softening and pipeline removed (CLIP pooled H1): MorDIFF 0.759, DiM 0.864 to 0.990.
Full table `bench.csv` (all heads, variants, EERs and intervals).

## What failed or deviated

- AD1b's full mirror-mix run had not written renders when the analysis ran; mirror mixes rest on 4 FRLL persons.
- DINOv3 mean patch duplicates DINOv3 pooled (timm averages patch tokens); the registered fourth set is void.
- The FRLL person bootstrap of the external and benchmark tables first drew over 140 IDs (38 without images). All
  external blocks were re-scored with the saved final heads over the 102 real persons and AD1's seed
  (`pd1_rescore.py`; point estimates identical, asserted; intervals changed in the third decimal). The first-draw files
  are kept in `/mnt/t7/smad_next/PD1/diffae/results_*_firstdraw.json`.
- Statistics for the SMDD and benchmark images were not computed (job stopped; no registered reading uses them).
- CUDA out-of-memory at model load on the shared GB10 (twice); handled by retries. For about 48 minutes (17:24 to
  18:12) my statistics job ran beside the 4-process feature extraction (5 processes; 3 of them idle loader workers).
- Q4 "loses its reaction" cannot be met when there is no reaction: reported as not met, with the rates.

## Not verified / limits

- No DiM-pipeline reconstructions or same-person DiM mixes exist, so the DiM benchmark separation cannot be split into
  pipeline and mixing steps; that the heads read mixing there (and not DiM rendering) is not verified. On FRLL, our
  20-step reconstructions score below genuine photos (0.42), which argues against a pure render detector for our renders.
- The softening direction comes from SMDD renders, not from the training hosts; its agreement with the FRLL softening
  directions is 0.53 / 0.54 for CLIP pooled but only 0.14 to 0.32 for the other two feature sets.
- Same-person pairs: 94 of 132 FERET person pairs are two photos of one session (expression change); FRGC session
  structure not checked. FRLL same-person mixes mix neutral and smiling photos and give no conclusion.
- The published MorDIFF decoding step count is not verified; MorDIFF and our stored-size images are about 150 px, and
  every head separates less at that storage (0.67 to 0.86) than at 256 px (0.82 to 0.94).
- One feature extraction per image (no augmentation), convex heads with no seed; no network was trained.
