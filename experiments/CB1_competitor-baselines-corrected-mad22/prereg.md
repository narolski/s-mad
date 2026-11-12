# Competitor baselines on the corrected MAD22 and FRLL-Morphs (CB1): registration

Written 12 Nov 2026, 23:35-23:55 CET (`date` at start: Thu Nov 12 11:22:32 PM CET 2026), before any CB1 score is read.
Owner: CB1 owner (agent), for Paweł Narolski. Repository commit before this file: 681f6a5 (branch sprint-plan-v2).
Author's instruction (12 Nov, about 23:40, via the lead): our retrains were read on the wrong MAD22 copy; re-score on
the correct sets; also work on FD-MAD and IDistill.

This experiment AUDITS competitor methods only (released weights, our retrains and re-implementations of published
recipes). No network of ours (PN1 / MS1 family) is scored. Nothing here feeds any choice about our method. Never opened:
`manifests/valx.csv`, any FST or A12-SP file. `prep_eval.py` / `prep_gtest.py` are not edited. No new image code: every
input is an existing aligned frame or an existing E7 file.

## 1. Questions

Q1. For every comparison row of the paper (FRLL-Morphs: PW-MAD, MixFaceNet-MAD, Inception-MAD, OrthoMAD, MADation,
IDistill, SelfMAD, FD-MAD; MAD22: MADation, MixFaceNet-MAD, Inception-MAD, MorphHRNet, FD-MAD), what do we hold and what
row can we honestly print?
Q2. Do our retrains of the published CNN recipes reproduce the published number on the corrected MAD22 (204 genuine +
4,483 morphs, five families) and on FRLL-Morphs (five families)?
Q3. Can IDistill be retrained faithfully from the authors' code, and does it reproduce its published FRLL-Morphs numbers?
Q4. Does our FD-MAD re-implementation (global branch, and the fused branch if it runs) reproduce the published numbers?

## 2. Data (fixed)

- Corrected MAD22: `/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z/native/` (canonical512 two-eye
  alignment, CPU backend; 204 BonaFide, FaceMorpher 1,000, MIPGAN-I 1,000, MIPGAN-II 999, OpenCV 984, Webmorph 500) and
  `e7/<family>/` (history-matched genuine pools, 204 each). Raw source:
  `/mnt/t7/smad_heldout/mad22_incoming/marco_owncloud_20261109T103840Z/author_files/original_sorted/`.
- FRLL-Morphs: rows of `smadcvpr_data/manifests/eval.csv` (sha256 86d055d3...) with set frllm: genuine `frll_bona`
  variant orig (204), morphs variant orig (AMSL 2,175, FaceMorpher 1,222, OpenCV 1,221, StyleGAN2 1,222, WebMorph
  1,221), history-matched genuine pools variant `resmatch` (the E7 pools, 204 per family).
- Gate rows only (never a result): the OLD MAD22 subset rows of eval.csv (185 genuine + 4,069 morphs, orig; resmatch
  185 per family). Used only to reproduce the stored A12-BR / A45 numbers with our scorer.
- Image list: `/mnt/t7/smad_next/CB1/manifests/cb1_cnn_images.csv` (19,171 rows, sha256 10686dec...), built by
  `src/CB1/build_manifest.py` (reads files only).
- Known caveat, stated in every table: the FRLL-Morphs frames come from the old aligner run, the corrected MAD22 frames
  from the CPU-backend run of the same canonical512 procedure; the materialisation receipt says the two runs differ in
  bytes on 4,209 of 4,254 shared MAD22 rows. The MAD22 genuine photos are the FRLL photos, so the shift between the
  two runs is measured directly on the same 204 photos (check C2 below).

## 3. Networks (fixed list)

Our retrains / re-implementations in our pipeline (trained on SMDD aligned into our 512 frames; augmentations that the
program forbids removed; inputs = our aligned frame resized by PIL bilinear to the recipe's size):
- A12-BR R x d0 primaries (local copy BK = `/mnt/t7/wcss_backups/smadcvpr/runs/A12BR/`): M1 Inception-MAD (Inception-v3,
  scratch, 299; 5 seeds), M2 MorphHRNet-style (HRNet-W48, scratch, 256; 5), M5 PW-MAD (DenseNet-121 to transition2 +
  pixel map, 224; 8), M6 OrthoMAD (ResNet-18 + orthogonal heads, 224; 5), M8 MixFaceNet-MAD (our pipeline, 224; 5),
  M8O MixFaceNet-MAD by the official SMDD training procedure re-implemented (224; 5), and descriptively M4 SelfMAD-style
  (HRNet-W18 IN-1k, 384; 5). Checkpoint list with sha256: `/mnt/t7/smad_next/CB1/manifests/cb1_nets_bk.tsv` (es.pt of
  each matches the A36 network list). Primary checkpoint: es.pt (the A12-BR registered network); last.pt printed beside.
- A45 arms (WCSS only, to be copied): incep_ofc (Inception-v3 by the official SMDD procedure, 224; 5 seeds) and
  hrnet_w18 (MorphHRNet recipe at W18, 256; 5 seeds). Primary checkpoint: last.pt (A45's registered rule); es.pt beside.
- Released weights already scored by the own-crop re-score (RS1): MADation ViT-B/16 and ViT-L/14, MixFaceNet-MAD,
  SelfMAD. Not re-scored; their rows are cited from `experiments/RS1_own-crop-rescore/` unless a row is missing.
- FD-MAD re-implementation (`/home/narolski/mambamorph-code-a45/smadcvpr/a45_fdmad.py`): global branch at 256 (primary)
  and 512 (disclosed variant), seeds 1-3; fused branch only if its landmark input can be supplied without new image
  code (section 6).
- IDistill retrain (section 7).

## 4. Scoring (fixed)

`src/CB1/score_cnn.py`: network built by the pinned `archs_a12.build_a12` (code root
`/home/narolski/mambamorph-code-a36/smadcvpr`: common.py b5d42a99..., archs_a12.py bedfeb86..., archs_v2.py 15eb6458...,
mixfacenet_port.py ba35736b...; for the A45 arms the A45 job-root copy of archs_a12.py, sha256 d7617dd1..., when
fetched), strict state-dict load with `weights_only=True`; loader `common.ImageItems` unchanged. Stored per image:
logit without flip, probability without flip, flip-averaged probability. **Primary score = logit without flip**
(the published methods use no flip; logits avoid ties of saturated probabilities). Platform: DGX GB10 (shared GPU),
thread caps as in OWNER_BRIEF.md.

## 5. Metrics and readings (fixed)

Per network and family: EER; BPCER at APCER = 1, 5, 10, 20% (threshold set on the morphs of that family so that the
share of morphs scored below it is at most the APCER; BPCER = share of genuine photos at or above it); morph = positive.
Two genuine pools per family: native genuine (all 204 photos) and the history-matched E7 pool of that family (204).
Intervals: two-way person bootstrap over the 102 FRLL persons (genuine weighted by its person's draw count, a morph by
the product of its two contributors' counts), B = 2,000, seed 0; for an arm: the seed mean with the bootstrap of the
seed mean (same person draws for every seed) and the 90% seed t-interval.

Reproduction reading per arm, on the native genuine pool (the published protocol), primary checkpoint and score:
- Mean level: Delta = (seed mean of the five-family mean EER) - (published five-family mean); margin
  M = max(0.30 x published, 1.5) points; 90% seed t-interval of Delta inside (-M, +M): **"reproduces the published
  number on the corrected set"**; lower bound above +M: **"does not reproduce (worse)"**; upper bound below -M: "does not
  reproduce (better)"; otherwise "inconclusive".
- Per family (descriptive): |seed mean - published| <= max(1.5, 25% of published) (the RS1 window).
- Published numbers: FRLL-Morphs as in the manuscript table (PW-MAD 15.18/2.20/2.42/16.64/16.65, mean 10.62;
  MixFaceNet-MAD 15.18/3.87/4.39/8.99/12.35, 8.96; Inception-MAD 10.79/3.17/5.38/11.37/9.86, 8.11; OrthoMAD
  9.50/0.98/0.73/6.54/15.23, 6.60 [the IDistill paper prints OrthoMAD AMSL 14.80, not 9.50: both printed]; IDistill
  4.00/2.05/2.46/1.96/4.01, 2.90; FD-MAD 0/0/0/9.25/0, 1.85); MAD22 (FaceMorpher, OpenCV, Webmorph, MIPGAN-I,
  MIPGAN-II): MixFaceNet-MAD 4.60/8.33/18.20/16.70/20.62, 13.69; Inception-MAD 0.00/7.52/18.00/10.90/16.22, 10.53;
  MorphHRNet 5.90/5.69/9.80/15.30/10.41, 9.42; FD-MAD 0.00/2.54/18.40/2.45/7.21, 6.12. PW-MAD and OrthoMAD have no
  published MAD22 number, MorphHRNet no per-family FRLL number: those rows are descriptive.
- History-matched column: the same metrics with the E7 pool, printed beside; no verdict attaches to it.

Paper label per method row (section 5 of the task): "released weights, our scoring"; "our retrain, reproduces"; "our
retrain, does not reproduce"; "as reported, not verified". For our retrains in our pipeline the label carries
"(re-implementation in our pipeline: our frames, forbidden augmentations removed)".

## 6. Checks (fixed, before any reading)

- C1 (reproduction gate of the scorer). On the gate rows (old MAD22 subset) and the FRLL-Morphs rows, the per-family
  EER of every A12-BR network must match the stored value in
  `mambamorph-code/experiments/A12-BR_benchmark_recipes/raw/A12_3e_report.json` (`networks[].main.family_eer`)
  within 0.5 EER points in at least 9 of 10 cells for each network, for the score version that A12 used (determined on
  M1 seed 1 only, then fixed for all). For the A45 arms the stored A45 per-cell values (`results/A45/a45_read.json`) play
  that role. A network that fails C1 is printed as "scorer does not reproduce the stored number" and gets no verdict.
- C2 (pipeline shift). On the 204 FRLL photos: score of the old-aligner frame (FRLL-Morphs genuine) against the
  CPU-backend frame (corrected MAD22 genuine), per network: median absolute logit difference and Kendall tau; printed.
- C3. No row from the old MAD22 subset enters any result table.

## 7. IDistill (fixed plan; retrain on WCSS)

Code: github.com/NetoPedro/IDistill commit 0473bb43007bb0088e90d226b59a2208d7e45856 (HEAD, 7 Sep 2023), no LICENSE file
(the README has none either): used unchanged for research audit, not redistributed. Paper: arXiv 2306.03002, local copy
`/mnt/t7/smad_next/CB1/literature/idistill_2306.03002.pdf`.
Faithful configuration from the paper (section IV) where it and the README differ: autoencoder UNet (code
`autoencoder_utils.UNetAutoencoder`), latent 128, 300 epochs, lr 1e-4, batch 32, Adam, MSE, SMDD bona fide only;
classifier ResNet-18 with the product fusion y = 1 - id1 * id2 (paper Eq. 3 = code `resnet18_mult`), latent 128, Adam lr
1e-4, batch 16, loss BCE + KD of Eq. 6-8 = code `--loss_measure prefusion` with weight 1 (paper Eq. 9), at most 250
epochs (README); data SMDD train (25,000 bona fide + 15,000 morphs, the code's 85/15 split, seed 420), faces cropped by
the SMDD release crop script (the code reads `*_cropped` folders), contributor latents from the 25,000 `os25k_m_t`
images. Model selection: the authors' code selects the checkpoint every 5 epochs by the mean EER on the five FRLL-Morphs
test sets. That is test-set selection; we run it as the authors' code does (labelled "test-selected as in the authors'
code") and also keep and report the last checkpoint ("no test selection"). Seeds: 401-403 for the classifier (one
autoencoder, seed 420 as in the code).
Reproduction gate: test-selected checkpoint, FRLL-Morphs native genuine, per family within max(1.5, 25%) of 4.00 /
2.05 / 2.46 / 1.96 / 4.01 and mean within M = max(0.30 x 2.90, 1.5) = 1.5 points. Then both checkpoints are scored on
the corrected MAD22 and FRLL-Morphs with the E7 pools, by the authors' preprocessing (their crop of the raw file, 224,
mean/std 0.5). Smoke before production: one epoch of each stage on 64 images. Deviations (paths, logging, wandb off) are
listed as a patch file.
If the code cannot be run faithfully by 13 Nov 12:00, the paper may state only "IDistill: as reported, not verified".

## 8. FD-MAD (fixed)

Re-score the existing re-implementation (`a45_fdmad.py`, unchanged, imported and called) on the CB1 image list: global
256 (primary) and 512, seeds 1-3, retrained on the same SMDD rows (fast, CPU). Fused branch: only if the 5-point
landmarks it needs exist for SMDD and for every evaluation frame without new image code; otherwise reported as not run
with the reason. Gate: the A45 stored global-only scores on eval.csv must be reproduced (EER per cell within 0.5) before
any corrected-set reading. Reading as in section 5 against FD-MAD's published numbers, labelled "partial
re-implementation (global branch only)" when only that branch ran; it is never called a failure to reproduce FD-MAD.

## 9. Budget and stop rules

Scoring: DGX GPU, under 2 GPU-hours. IDistill: at most 4 WCSS H100 at once, about 20 H100-hours. FD-MAD: DGX CPU at 2
threads, or WCSS CPU. Decisive rows by 13 Nov 18:00; whatever is unfinished then is printed as incomplete.

## 10. Pre-run review

To be requested from the experiment-reviewer before the IDistill production jobs; the scoring of existing networks
(sections 3-6) is a re-score of fixed networks with a fixed rule and starts on registration.

## Amendment 1 (13 Nov 2026, 00:05 CET; after the pre-run review, before any CB1 score is read)

Pre-run review: GO WITH FIXES (experiment-reviewer, 13 Nov about 00:00; findings F1-F11, recorded in README). Changes:
- F1. IDistill's early stopping is driven by the FRLL-Morphs test sets, so its last checkpoint is also test-dependent.
  Three checkpoints are kept and reported: "test-selected as in the authors' code" (the gate checkpoint), "selected on
  the SMDD validation split" (new patch line: saved whenever the code's own 15% SMDD validation EER improves; the label
  for a no-test-selection row), and "stopping epoch set by test-set early stopping" (the `.last` file).
- F2. FRLL-Morphs morph file names are `AAA_BBB`; the person parser read them as one person. Fixed in
  `build_manifest.py`; new list `/mnt/t7/smad_next/CB1/manifests/cb1_cnn_images_v2.csv` (sha256 aa140e91..., same ids and
  paths in the same order as v1, so existing score files stay valid; 7,051 contributor fields corrected). Ten
  FRLL-Morphs morph files name one person twice (e.g. facemorpher `036_036`); they are kept (they are part of the
  published set) and listed.
- F3. IDistill morph score = id1 x id2 (outputs[3] x outputs[4]), written in double precision; y~ kept beside it.
- F5. C1 is row-wise and binding: on the score version chosen on M1 seed 1 (and A45 incep_ofc seed 1), median absolute
  probability difference <= 1e-3 and maximum <= 1e-2 over all gate and FRLL-Morphs rows, and EER within 0.5 points in at
  least 9 of 10 cells. Networks without stored scores or failing C1 get no reading (enforced in `analyse_cnn.py`). FD-MAD
  C1-F: the same row-wise rule against `/mnt/t7/smad_heldout/a45/fdmad/fdmad_global_r<res>_s<seed>/scores_eval.npz`.
  IDistill has no stored score; its gate is the published-number gate of section 7.
- F6. M4 (SelfMAD-style) gets no reproduction reading (descriptive). OrthoMAD FRLL is read against 9.50 (manuscript)
  and, printed beside, against 14.80 (IDistill Table I). IDistill gate: seed mean over 401-403 of the test-selected
  checkpoint; binding: five-family mean within 1.5 points of 2.90; per-family windows and the paper's BPCER at APCER 1%
  (21.10 / 4.26 / 6.14 / 8.51 / 14.41) and 20% (2.85 / 0.16 / 0.16 / 0.08 / 0.33) printed descriptively.
- F7. For IDistill (morphs cropped from raw files, E7 photos cropped from aligned frames) the history effect is read as
  E7 minus aligned-native genuine (both aligned frames through the same crop), not against the raw genuine pool.
- F8. Crop failures (SMDD crop script finds no face, or a strip) are counted per folder. A morph without a crop counts
  as accepted (scored as the most bona-fide-like value); the analysis that excludes them is printed beside. Training
  morphs dropped for missing contributor latents are counted.
- F9. Running a competitor's own preprocessing unchanged (IDistill: the SMDD release MTCNN crop and the authors' resize
  to 224) follows the precedent of the own-crop re-score (RS1) and the AD5 authors'-code retrains; no image code of ours.
- F10. The CUDA seed stays 0 as in the authors' code (the patch seeds CPU/numpy/random with the seed); the 85/15 split
  stays at the authors' seed 420.
- Platform: the coordinator declined a rental for tonight; IDistill waits on the WCSS queue. Fallback wording if it
  cannot finish by the retrain cut-off of 14 Nov 18:00: "IDistill: as reported, not verified; the authors' code selects
  its checkpoint on the FRLL-Morphs test sets".
