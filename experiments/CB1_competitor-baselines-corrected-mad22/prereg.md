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

## Amendment 2 (13 Nov 2026, 00:32 CET; after the C1 gate of the first 23 networks, before any reading is looked at)

C1 result on the 224-px networks (es.pt; score version without flip): M6, M8, M8O pass for every seed (median row
difference <= 2e-4, maximum <= 4.4e-3). PW-MAD (M5) fails the maximum criterion on seeds 1, 2, 6 (max 0.016 / 0.029 /
0.030; seed 6 also median 1.4e-3) while its EER agrees within 0.5 points in 9-10 of 10 cells for every seed. The stored
scores were computed on WCSS H100 with TF32, ours on the GB10 with TF32: a platform difference, not a loader difference
(medians 1e-6 to 7e-4). Rule from here: an arm is read on the networks that pass C1 if at least 3 do; the count and the
excluded seeds are printed with the reading; fewer than 3: no reading. This is a selection on a technical check, made
before any benchmark reading of these networks was looked at.

## Amendment 3 (13 Nov 2026, 02:00 CET; IDistill on the DGX GPU; coordinator's yes at about 01:50; before any IDistill run)

WCSS forecasts 15 Nov 01:00 for every pending job of ours (after the retrain cut-off), so IDistill runs on the DGX GB10
after the CNN re-score and the A45 arms have finished, one GPU process at a time, `nice -n 10`, thread caps 2.
- One seed (401). The paper's settings exactly as in section 7 (autoencoder: UNet, latent 128, 300 epochs, batch 32,
  lr 1e-4, SMDD bona fide crops; classifier: ResNet-18 product fusion, latent 128, lr 1e-4, batch 16, prefusion KD
  loss with weight 1, at most 250 epochs, authors' early stopping), the same job script (`cb1_idistill.sbatch` with
  `CB1_PIP=dgx`), the same packs (idistill_code.tar v3, idistill_data.tar aa161436..., smdd_train_cropped.tar 3189e52a...).
- Stack deviation, stated plainly: torch 2.12.1+cu130, torchvision 0.27.1, numpy 1.26.4, OpenCV 4.11, scikit-learn
  1.9, Pillow 12.2 on ARM / GB10 (program venv), plus pandas 2.2.3, tensorboard 2.21, facenet-pytorch 2.5.2 from
  `/mnt/t7/smad_next/CB1/site_idistill_dgx`, instead of the authors' torch 2.0.1 / x86 stack. Tonight's TT1 diagnostic
  found that this stack changes ViT logits by 0.06-0.09 at inference; numerical equivalence with the authors' stack is
  NOT established, and with one seed the seed spread is unknown.
- Checkpoints reported: (a) "selected on the SMDD validation split" (`.valbest`, no test data); (b) "test-selected as
  in the authors' code" (best five-family FRLL-Morphs mean EER every 5 epochs); (c) "stopping epoch set by test-set early
  stopping" (`.last`), descriptive.
- Reproduction gate (on checkpoint (b), the authors' rule, FRLL-Morphs native genuine, morph score id1 x id2): binding:
  five-family mean EER within M = max(0.30 x 2.90, 1.5) = 1.5 points of 2.90; descriptive: per family within max(1.5,
  25%) of 4.00 / 2.05 / 2.46 / 1.96 / 4.01 and the paper's BPCER at APCER 1% and 20%. With one seed there is no seed
  interval; the point estimate decides, with the two-way person bootstrap 95% interval printed.
- Row label by outcome: "our retrain on a different stack, one seed: reproduces within tolerance" or "our retrain on a
  different stack, one seed: does not reproduce"; checkpoint (a) is reported beside on both benchmarks with its E7
  column. If the author funds the rented variant, the DGX run continues as a second, separately labelled run.
- Stop rule: the step rate is measured in the first ten minutes; if the projected end is after 14 Nov 16:00 the
  coordinator is told before the run continues.

## Amendment 4 (13 Nov 2026, about 03:58 CET; after the results review, before any IDistill score exists)

- IDistill gate and crop failures. The SMDD release crop script returns no crop for 416 of 1,222 FRLL FaceMorpher morphs
  (and 9 of 1,221 OpenCV). The authors' pipeline evaluates only the crops their script writes (a failed file is simply
  absent from their test CSV), so the binding gate of amendment 3 is computed on the written crops; the worst-case
  analysis of amendment 1 F8 (a morph without a crop counts as accepted) is printed beside and is not binding.
- FD-MAD wording (prereg section 8 applies): rows read "partial re-implementation; does not reach the published
  number"; global-branch arms are compared with the published global-only means (MAD22 16.62, FRLL 2.08) as the
  primary comparison, the fused numbers printed beside; fused at 256 gets no reading (local branch not functional:
  s_local median about 1e-6).
- The C1 actually used is the row-wise comparison with stored scores (amendment 1); the comparison with the A12 report
  values in section 6 was not used, because those values are computed on the E7 genuine pool with the flip-averaged
  score (results review F1). A table of A12-style versus CB1-style EERs is added (`review_addons/a12style_vs_cb1.csv`).

## Amendment 5 (13 Nov 2026, about 09:05 CET; lead's request for the shortcut audit table SA1, gap item 10; before any new score)

Audits of released weights (benchmark and development data allowed for released detectors). Cells and how each is
filled; "existing" = a committed or stored score file, read only.
- 5-ViTL, 5-MFN (border / frame alone; same 204 FRLL photos, MorDIFF tight frame against FRLL orig frame, median
  paired logit shift with 95% interval, as 5-ViTB / 5-SelfMAD): (a) our-frames path, existing EV1 file
  `experiments/EV1_fixed-threshold-reread/AM2_B4_border_pairing.csv` (computed 11 Nov, never stated in EV1's result);
  (b) own-crop path, existing RS1 pools Galn_mordiff vs Galn_frll (both crop variants, RS1 score files through RS1's
  analyse.py), paired by photo.
- 13-MFN (diffusion render path, AD1 main contrast R2 = D20 reconstruction vs R4 = B20 our morph, AUC with two-way
  person bootstrap): (a) our-frames path, NEW scores of the A43 frames (`/mnt/t7/smad_heldout/a43/data/manifests/a43.csv`,
  2,024 rows) in the 'rel' mode of the other releases; (b) own-crop path, existing RS1 value (corrected crop) printed
  beside.
- 14-MFN (GAN one-person render, AG1 metrics as for the other releases: R2 > R3 and R3 > R4 AUC on the primary pool
  mip1/frll, and same-person (R3) and two-person (R4) flag rates at the corrected-MAD22 EER threshold (MIPGAN-I family,
  as AG1)): NEW 'rel' scores of the 7,229 AG1 frames and of the 5,707 corrected-MAD22 aligned frames (threshold).
- 16-MFN (expression; EER change neutral-only minus all genuine, FRLL-Morphs): existing C1b row "MixFaceNet-MAD, our
  frames (desc.)" (`experiments/C1b/result.md`); cited, nothing computed.
- 10-SelfMAD (crop path): own crop on raw files with raw genuine photos against the same morphs with our aligned genuine
  frames through the own crop, FRLL five-family mean EER (as 10-released for MixFaceNet), from existing SelfMAD score
  files if both genuine pools exist; otherwise reported as not computable without new scoring.
- Also, from existing RS1 files: 4-ViTL (own-rule flag rate on the 2,000 FFHQ photos, own crop) and 19-MFN (own 0.5
  rule miss and flag rates, RS1 `rs1_pool_rates.csv`).
New scoring: `src/CB1/score_mfn_rel.py` (a12_released.py adapter and common.ImageItems from the AG1 job root, imported
unchanged; checkpoint sha256 3d507c8b...), on the DGX CPU (the DGX GPU runs IDistill; WCSS's controller refuses
submissions; Athena's main partition is reserved). Reproduction gate before any reading: 212 eval.csv rows (every 40th
FRLL-Morphs / MorDIFF orig row) against the stored A12REL MixFaceNet scores of the same release and mode
(`smadcvpr_runs/A12_scored/A12REL/mixfacenet_mad_smdd/scores_eval.npz`): median |logit difference| <= 0.05 and maximum
<= 0.5; failing that, no new-score cell is read. Smoke (8 rows): logits within 0.02 of the stored GPU values.
Everything is labelled "benchmark audit, our scoring, not reviewed" until a review.

## Amendment 6 (13 Nov 2026, about 09:05 CET; pre-run check of amendment 5: GO WITH FIXES; before any new A43 / AG1 score exists or is read)

Only the reproduction gate (212 eval rows) has been scored so far: median |logit difference| 0.0057, max 0.070: PASS.
- 14-MFN: read on the AG1 pool mip1/primary (FERET + FRGC, as the existing 14-ViTB / ViTL / SelfMAD cells), mip1/frll
  printed beside. Threshold: AG1's own "corrected-MAD22" EER threshold, FRLL R0 against the published MIPGAN-I files
  inside the AG1 frames, through the AG1 reader's `eer_thr` (the reader `src/AG1/ag1_read.py` is imported unchanged with
  only its release tuple set to the MixFaceNet release; its outputs go to a new folder; MixFaceNet is not added to the
  other releases' Holm family). The 5,707 corrected-MAD22 frames are not scored (dropped).
- Validity rule (binding, per reader): the release must rank the benchmark correctly on our frames: AG1 R0 > PUB AUC
  above 0.5 with the 95% interval excluding 0.5; AD1 published MorDIFF (A) against the FRLL photos R0 above 0.5 with the
  interval excluding 0.5. If it fails, the cell reads "not interpretable: release reversed on our frames" and only the
  own-crop value (13: RS1 corrected crop B20 vs D20) is printed.
- 16-MFN: the C1b row is printed with its caveat (EERs 75-98% on four FRLL-Morphs cells, reversed, descriptive), not
  summarised as "change < 1.5 pts"; the own-crop neutral / smiling EERs from `RS1/rs1_expression.csv` are a separate,
  labelled side value.
- Score fields: `logit_noTTA` only (the flip-averaged `score` is not used). Checks before reading: list ids equal the
  manifest ids in order, every row present, every value finite; AD1 consistency check binding: the A43 rows that are
  eval.csv frames (FRLL photos R0) against the stored A12REL MixFaceNet eval scores, same rule as the gate. The scorer
  bypasses `a12_released.py`'s own scope guards (registered-list and unlock checks); acceptable for released weights
  under the early-unseal ruling, stated here.
- 4-ViTL: labelled "own crop (RS1)", both crop variants with n (v1 1,934, v2 1,997 FFHQ photos) and the miss rate on
  morphs at the same 0.5 rule.
- 5-MFN(b) / 5-ViTL(b): median paired shift, person bootstrap B 2,000, seed 20261111 (EV1's seed); the black-border
  fractions of both pools after the own crop (`RS1/rs1_border.csv`) printed beside, since the own crop re-detects the
  face and may cut the border away.
- 10-SelfMAD: labelled "SelfMAD's own preprocessing (dlib crop), not the SMDD crop script"; same five FRLL families.

## Amendment 7 (13 Nov 2026, about 10:15 CET; POST HOC, after the SA1-cell review; zero GPU)

Lead's request after review H-new-1. Post hoc, descriptive; no verdict word.
(A) MixFaceNet-MAD release, our frames ('rel', stored A12REL eval scores): per-image black-border share of the 512-px
eval frames (share of pixels with all three channels 0; a pixel read, nothing written), for FRLL-Morphs orig morphs,
the 204 FRLL photos (orig) and the E7 (resmatch) pools. Readings: Spearman correlation of logit with border share inside
each morph family; AUC per family on all morphs and on border-matched morphs (border share <= 0.005, the genuine photos'
range), with the person bootstrap of the earlier cells (B 2,000, seed 20261111).
(B) For the released detectors on their own crop path (MADation ViT-B/16, ViT-L/14, MixFaceNet-MAD, both crop
variants; SelfMAD own preprocessing where pools exist): split of the native -> history-matched EER rise into an
aligner-path step (raw genuine -> our aligned genuine frame without history) and a storage-history step (aligned native
-> aligned E7), from the existing pools in `cb1_released_rs1_bpcer.csv` and the SelfMAD pools; the black-frame share of
every genuine and morph pool after the own crop from `RS1/rs1_border.csv`. If the black share of the history-matched
genuine pool equals that of the aligned native pool, the black frame contributes nothing to the history step on that path.
Statement of which existing files allow the split and what would need new scoring.
