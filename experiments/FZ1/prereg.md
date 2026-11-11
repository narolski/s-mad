# FZ1 Do frozen foundation features read the mixing step of a morph, where adapted detectors do not?

Written 11 Nov 2026, about 15:45 CET, by the FZ1 owner, **before any new score, feature or statistic was
computed**. Known before writing: the reviewer preview numbers quoted in the task message (released MADation FE
ViT-L/14 on A43: B20 vs D20 0.655 [0.581, 0.731], B vs D 0.852 [0.799, 0.903], C vs D 0.721, D vs R0 0.459,
D20 vs R0 0.561, StyleGAN3 morph vs one-identity render 0.505) and AD1 / AG5 results. P1 is therefore **post
hoc** (a re-read). P2, P3 and P4 are new.

- **Hypothesis H-new-3 (plain words):** the frozen OpenAI CLIP ViT-L/14 image features carry a read-out of
  latent mixing in diffusion-autoencoder (DiffAE) morphs. A linear head on those features, trained on SMDD only,
  ranks our same-pair DiffAE morphs above one-photo DiffAE reconstructions, without ranking reconstructions above
  camera photos. Adapting the encoder on SMDD (the full MADation release) replaces this with processing-history
  cues.

## Data (no new images)

- **A43** (`/mnt/t7/smad_heldout/a43/data/manifests/a43.csv`, sha ce3a264a…): A = 200 published MorDIFF morphs;
  B / B20 = our same-pair DiffAE morphs at 100 / 20 decoding steps (200 each); C / C20 = same-person mixes
  (neutral + smiling of one person, 102 each); D / D20 = one-photo reconstructions (204 each); E = the genuine photo
  through DiffAE's aligner and the A43 storage (204); R0 = the FRLL camera photos of the MorDIFF cell
  (`mordiff_bona`, 204 eval rows in the same manifest). Images used: the 512 frames the releases scored
  (`a43/frames/...`, eval `eval/...`).
- **R1** = the existing E7 copies of the R0 photos (`eval.csv` `mordiff`/`resmatch`, 204; sha 86d055d3…).
- **FRLL-Morphs landmark families** (`eval.csv` `frllm`: amsl 2,175, facemorpher 1,222, opencv 1,221, webmorph
  1,221 `orig` morphs), genuine native = `frll_bona`/`orig` (204), genuine E7 = the family's `resmatch` (204).
  **MorDIFF** benchmark = `mordiff`/`orig` (1,000) against `mordiff_bona`/`orig` (native) and `mordiff`/`resmatch`
  (E7). The old MAD22 rows of `eval.csv` are not used.
- **StyleGAN3**: H3 morphs (`h3sg3.csv` `h3_sg3`/`orig`, 423), H3 one-identity renders (`h3_bona`/`orig`, 423),
  A37 spread-matched renders (`a37spread.csv` `orig`, 423); 512 frames.
- **SMDD** (P3 training only): the 40,000 SMDD rows of `smadcvpr_data/manifests/train.csv` (`source = smdd`;
  25,000 bona fide `os25k_bf_t`, 15,000 morphs `m15k_t`; SMDD's own 256-px release-train files; every SMDD row has
  `val = 0`). No FRLL, FERET, FRGC or other image enters any P3 head.
- FRLL images enter only (a) evaluation and (b) the cross-validated probes of P2 / P4, which are labelled
  **diagnostics of the images**, never detectors.

## Image input and features (P2, P3)

All images go through the existing loader `mambamorph-code/smadcvpr/common.ImageItems(res=224)` (its PIL
bilinear resize is the only resize; no new resize code). Horizontal flip (a pixel permutation, as in the
releases' TTA) is used only for the P3 training augmentation.

| Backbone | Weights (local cache, offline) | Input convention | Feature |
|---|---|---|---|
| **CLIP-L/14, MADation input (primary)** | OpenAI CLIP ViT-L/14 at 224: timm `vit_large_patch14_clip_224.openai` tensors (`torch.load(weights_only=True)`), loaded into timm `vit_large_patch14_clip_quickgelu_224` (OpenAI CLIP uses QuickGELU; the A36 port of the MADation release uses this architecture) | BGR, (x − 0.5) / 0.5 (MADation `FaceDataset`) | 768-d projected embedding (`encode_image`), L2-normalised |
| CLIP-L/14, CLIP-native input (descriptive) | same | RGB, CLIP mean / std | same |
| DINOv3 ViT-L/16 | timm `vit_large_patch16_dinov3.lvd1689m` | RGB, its pretrained mean / std, 224 | timm pooled pre-logits |
| DINOv2 ViT-L/14 | timm `vit_large_patch14_dinov2.lvd142m`, img_size 224 (timm interpolates the position table) | RGB, ImageNet mean / std | timm pooled pre-logits (CLS after the final norm) |

Checks before any probe or head is fitted (CLIP primary): (i) every CLIP tensor equals the frozen encoder stored in
the released FE ViT-L/14 (`net.*` of its `model.safetensors`), max |Δ| reported; (ii) the released FE head applied to
our features reproduces the A43 `score_noTTA` of the FE ViT-L/14 release on 8 images per arm, |Δ| ≤ 2e-3. If (ii)
fails, the CLIP rows of P2 / P3 stop and the failure is reported. Precision: fp32 weights, no autocast; TF32
matmuls allowed if needed for throughput, recorded, and the check (ii) is run under the same setting.

## P1 (post hoc re-read; no new computation on images)

From the existing per-image score files: A43 `a43_out/a43/<net>/rel/scores_a43.npz` (`score_noTTA`), A12REL
`scores_eval.npz` (R1, benchmarks, `frll_bona`), A12REL `scores_h3sg3.npz`, a41g X4 `scores_a37spread.npz`.
Networks: released MADation FE ViT-L/14 (subject); FE ViT-B/16, FS ViT-L/14, FS ViT-B/16 (descriptive).

- AUCs (positive = first named): B20 vs D20, B vs D, C20 vs D20, C vs D, B20 vs C20, B vs C, D vs R0, D20 vs R0,
  E vs R0, R1 vs R0, A vs R0, B20 vs R0; StyleGAN3 morph vs one-identity render, morph vs spread-matched render.
- R0 → R1 flag-rate change at the network's own MorDIFF EER threshold (full cell: `mordiff_bona` 204 vs `mordiff`
  1,000; flag = score ≥ t); paired on the same 204 photos. Also with the threshold from the 200 sampled published
  morphs (AD1's choice), descriptive.
- Within-person neutral-above-smiling AUC: per FRLL person, 1 if s(neutral `_03`) > s(smiling `_08`), 0.5 on a
  tie, 0 otherwise, averaged over the 102 persons; on `frll_bona`/`orig` (primary) and on R0 = `mordiff_bona`.
- Benchmark EER, native and E7 genuine class, for the four FRLL-Morphs landmark families and MorDIFF (so the P3
  heads can be compared with the release).
- "Reproduced" = the six preview point AUCs equal to three decimals. Intervals use a different draw and may differ.

## P2 (readability probe = gate G-c)

- Contrasts. A43: B20 vs D20, B vs D, C20 vs D20, B20 vs C20. StyleGAN3: H3 morph vs H3 one-identity render, H3
  morph vs A37 spread-matched render.
- Probe: `StandardScaler` + L2 `LogisticRegression` (lbfgs, max_iter 5000), C chosen inside each training part from
  {1e-3, 1e-2, 1e-1, 1, 10} by 3-fold grouped CV (max AUC, ties to the smaller C), then refit on the training part.
- Folds. A43: the 102 FRLL persons are split into 5 folds by a permutation with seed 401 (one assignment for all
  contrasts and backbones). An image is tested in the fold of its host person (`src_a`); the training part is every
  image with **no** person in the test fold. Limitation stated in advance: a test morph's second contributor can sit
  in the training part (in both classes). StyleGAN3: 5 folds by `pair` (seed 401); morph, render and spread-matched
  render of a pair always share a fold.
- Metric: AUC of the pooled out-of-fold probabilities, 95% interval from the person bootstrap of AD1 (pigeonhole
  two-way draw, seed [20261107, 43, 1], B = 10,000) for A43, the pair bootstrap of AG5 (seed [20261111, 5, 1],
  B = 10,000) for StyleGAN3. Robustness (descriptive): the whole probe repeated with fold seeds 402–405; range
  reported.
- **Fixed readings:** AUC ≥ 0.75 with lower bound > 0.65 = "readable from frozen features"; AUC < 0.60 = "not
  readable by this probe"; otherwise "intermediate". The `11_AUDIT_PLAN.md` G-c wording (below 0.65 → "neither
  the released detectors nor a probe trained for it read …") is printed beside each cell.

## P3 (H-new-3 proper: SMDD-only heads on frozen CLIP-L/14)

- Recipe: the MADation FE head recipe from the release's own training code (`baselines/MADation/src`,
  `MAD_training_only_header`, ViT-L/14 line of `train.sh`), on cached features of the frozen encoder (CLIP-L/14,
  MADation input): `Linear(768, 2)` on `F.normalize(encode_image(x))`; `BCEWithLogitsLoss` on one-hot targets
  (class 0 = attack, class 1 = bona fide); AdamW lr 1e-2, betas (0.9, 0.999), weight decay 0.05 on all header
  parameters; the release's scheduler (cosine with eta_min = lr after a factor-1 warm-up, i.e. constant lr);
  40 epochs; global batch 256 (32 × 8 GPUs), reshuffled each epoch, last incomplete batch dropped; gradient-norm
  clip 5; random horizontal flip p = 0.5 per image per step (orig or flipped feature). One deviation: the encoder
  input comes from our loader (PIL bilinear from the file, BGR, (x − 0.5) / 0.5), which equals the release's
  `cv2.imread` → `Resize([224, 224])` → `Normalize(0.5, 0.5)` up to channel order of an identical per-channel
  resize.
- Seeds 401, 402, 403, 404, 405 (torch seed for initialisation, shuffling and flips). Last epoch. No selection.
- Score = softmax probability of class 0 (attack) = sigmoid(z0 − z1), as the A36 release adapter.
- **Prediction:** B vs D ≥ 0.75 **and** D vs R0 ≤ 0.60 (point AUCs, same seed) in at least 4 of 5 seeds.
  **Falsified** if fewer than 3 seeds reach B vs D ≥ 0.70. Otherwise "neither supported nor falsified".
- Also reported per seed (descriptive, intervals): B20 vs D20, C vs D, C20 vs D20, B20 vs C20, E vs R0, D20 vs R0,
  R1 vs R0, A vs R0, the two StyleGAN3 contrasts; benchmark EER native and E7 for the four FRLL-Morphs landmark
  families and MorDIFF (person bootstrap, B = 2,000); R0 → R1 flag-rate change at the head's own MorDIFF EER
  threshold; neutral-above-smiling AUC; Spearman correlation of each head's A43 scores with the released FE
  ViT-L/14 scores.

## P4 (what is being read: simple-statistic floors)

- Contrasts B vs D and B20 vs D20. Statistics, on the same 224 loader input the features see (primary), and on
  the central 256 × 256 of the 512 frame, which lies inside the photo for every A43 file (descriptive, no border):
  high-frequency energy (share of 2-D FFT power of the luma image, mean removed, at radial frequency above half
  Nyquist); Laplacian variance (`cv2.Laplacian`, ksize 1, luma); mean |image − mirror image| over RGB; per-channel
  standard deviation (R, G, B: three statistics); PNG size (bytes of the stored A43 file). Seven statistics.
- AUC of each statistic alone (folded around 0.5, since the direction is not fixed in advance; the folding is
  marked) with the person bootstrap; logistic regression on all seven with the P2 probe routine and folds.
- **Reading fixed here:** a statistic "matches the probe" when the 95% paired bootstrap interval of
  (CLIP-L/14 probe AUC − folded statistic AUC) includes 0 or lies below 0. If one smoothness statistic (HF
  energy or Laplacian variance) matches, this is stated plainly.

## Guards, gates, limits

- G-a (reproduction of published numbers): not applicable to the probes; the P3 heads are new and labelled as our
  re-trains of the FE recipe, never as the release.
- G-b for A43 holds from AD1 (oracle 1.000; B20 verifies against both contributors in 99.5%); for StyleGAN3 it
  fails (48%, AG5), so StyleGAN3 probe cells are read as "absence or presence of a separating direction", not
  as identity reading.
- No ensembles, no score fusion, no seed picking; every seed is printed.
- **Stop rule and budget:** GPU feature extraction ≤ 2 shared GB10-hours, GPU memory < 12 GB, at most 6 CPU
  processes; heads and probes on CPU. If check (ii) fails, CLIP P2 / P3 stop.
- **Commands (each tested on 8 images per group first):** `src/FZ1/fz1_p1.py`, `src/FZ1/fz1_feats.py`,
  `src/FZ1/fz1_probe.py`, `src/FZ1/fz1_heads.py`, `src/FZ1/fz1_stats.py` (spark venv, `python -I`).
  Feature caches in `/mnt/t7/smad_next/FZ1/`.
- **Pre-run review:** not run by the owner (zero-cost re-reads plus CPU heads on cached features; lead to decide).
- **Result:** `experiments/FZ1/result.md`.
