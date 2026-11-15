# Round 3 vetting, lens "Making the measured shortcuts unusable by construction"

11 Nov 2026. Reviewer role: hostile but constructive CVPR area chair with an image-forensics and
morph-detection background. Reviewed file: `ideas/round3/nuisance_ideas.md` (three ideas).

What I did: read the brief, `CONSOLIDATED_v2.md`, the cue table, the class definitions and the experiment
records named below; made light reads of existing CSV, JSON and markdown result files; listed the data
paths the first tests name; opened 12 arXiv abstract pages. What I did not do: no experiment, no GPU, no
cluster, no git, no image loaded, no sealed file opened (no `valx.csv`, nothing named FST or A12SP, nothing
under `/home/narolski/.config/smad-next/`).

Limit of the novelty check: the session's web-search budget ran out after two queries. Prior work below is
what I could open directly by its arXiv address. Forensics-specific searches for ideas 2 and 3 did not run.
Every novelty statement is marked accordingly.

## Terms

- S-MAD = single-image morphing attack detection. EER = equal error rate. AUC = area under the ROC curve.
- Flag rate = share of genuine images called a morph. Miss = share of morphs not flagged.
- Own rule = the network's own decision, probability of morph above 0.5 (logit above 0).
- Development threshold = the threshold that flags 5% of the 5,033 development genuine photos (FERET, FRGC).
- IED = inter-eye distance in pixels. E7 pool = the 204 FRLL genuine photos shrunk to a morph family's
  median IED and enlarged again by the unchanged alignment ("history-matched").
- MADation recipe = CLIP (a pretrained image-text encoder) with LoRA (low-rank adaptation) and a linear
  header, trained on SMDD (the standard synthetic training set). "ViT-L/14 recipe retrains" = our five
  retrains of that recipe on SMDD only, usual loss, last checkpoint (rows "M3L" in the files). "ViT-B/16
  recipe retrains" = eight retrains of the smaller variant (rows "M3").
- Ladder rungs: R0 camera photo; R1 photo with a storage history; R2w warp only; R3 same-person morph; R4
  two-person morph.

## 0. Verdicts

| Idea | Verdict | Impact | Feasible by 14 Nov | Shortcut-proof | Novelty |
|---|---|---|---|---|---|
| 1. Training with a false-alarm limit for every storage history | revise | 5 | 6 | 3 | 3 |
| 2. Train only on what the measured cues cannot explain | revise | 4 | 4 | 4 | 3 |
| 3. Canonical view: one storage band and frame for every input | drop as a method | 3 | 3 | 4 | 2 |

One finding decides most of this review. All three ideas aim at storage history. In the existing score
files the recipe that all three build on (ViT-L/14) does not show a storage-history failure. It shows
three other things: scores that sit far below 0.5 for some morph families, a response to JPEG compression,
and a response to the tight frame. Section 1 gives the numbers.

## 1. What I read in the record (my own reads of existing files; UNREVIEWED unless marked)

All files in this block are in `/home/narolski/smad-next/experiments/EV1_fixed-threshold-reread/` (the
fixed-threshold re-read of existing scores, EV1), on our 512-pixel frames.

| # | Read | File |
|---|---|---|
| F1 | ViT-L/14 recipe retrains at their own rule: 0.0% (rounded) of every genuine pool flagged (23 pools per seed: FRLL original, JPEG 90/70/50, blur, 50% resample, 12 E7 pools, tight MorDIFF frame, FEI, development photos). Morphs flagged at the same rule: FaceMorpher 88 to 98%, OpenCV 95 to 98%, WebMorph 14 to 59%, **AMSL 0.0%**, MorDIFF at most 0.8%, DiM-C 1 to 10%, Greedy-DiM-S 19 to 24%, StyleGAN at most 0.1% | `AM2_B1_rule05.csv`, rows "M3L seed 1..5" |
| F2 | Same networks at the development threshold: every shrink-history pool (11 E7 pools, 50% resample, blur) 0.0 to 4.9% flagged; FRLL original 0.5 to 4.4%; **JPEG 70: 8 to 26%; JPEG 50: 23 to 50%; tight MorDIFF frame without history: 43 to 76%; with history: 59 to 87%** | `A1_false_alarms.csv`, block M3L, alpha 0.05 |
| F3 | ViT-B/16 recipe retrains at the development threshold: six DiM-history pools 23 to 67% flagged; AMSL-history pool 1.5 to 29% against 0 to 7% for the original photos; 50% resample 2 to 36%; JPEG 50 at most 8%. At their own rule the DiM-history pools are flagged 0 to 73% (seven of eight seeds at 4% or more) | `A1_false_alarms.csv` block M3; `AM2_B1_rule05.csv` |
| F4 | ViT-L/14 recipe retrains, threshold taken from any single shrink-history pool: miss on FRLL AMSL, FaceMorpher, OpenCV and WebMorph is 0.00 on all five seeds. With JPEG 50 as the threshold pool the AMSL miss is 0 to 46%; with the tight MorDIFF frame 14 to 68%. The pool that binds the "every pool protected" threshold is in the tight MorDIFF frame on all five seeds (with the 65 px history on three, without it on two). In the full frame the same 63 to 65 px history adds nothing (F2) | `AM2_B3_miss_by_threshold_pool.csv`; column `binding_pool` of `A2_family_means.csv` |
| F5 | ViT-L/14 recipe retrains, AUC on the four FRLL landmark cells: native 0.999 to 1.000; against history-matched photos 1.000; both classes 50% resampled 0.999 to 1.000; genuine JPEG 50 against original morphs 0.919 to 0.996 on AMSL. ViT-B/16 retrains on AMSL: native 0.897 to 1.000, against 50% resampled photos 0.618 to 0.956 | `A3_crossed.csv` |

Other files:

| # | Read | File | Status |
|---|---|---|---|
| F6 | A ViT-B/16 network that never saw a morph (SMDD renders against their shrunk copies), last checkpoint, 3 seeds: corrected MAD22 FaceMorpher 0.00% EER native and **0.55% against history-matched photos**; MorDIFF 0.00 and **5.25%**; DiM-C 0.00 and 21.8%; the other DiM families 47.7 to 69.2% | `/home/narolski/mambamorph-code/smadcvpr/results/A47/a47_read.md`, table "I-3 morph-free" | reviewed earlier ("accept-qualified" per `01_EVIDENCE_DOSSIER.md`) |
| F7 | The registered shrink call does nothing when the scale is 1 or more: `if scale is not None and scale < 1.0: return cv2.resize(..., INTER_AREA)`, else the image is returned unchanged | `/home/narolski/mambamorph-code/smadcvpr/prep_eval.py`, lines 119 to 125 | code read |
| F8 | Two-person against same-person morphs (OpenCV engine, 536 hosts): PNG size 0.508, but a 32-pixel thumbnail 0.384 (0.616 folded) and background statistics 0.413 (0.587 folded) | `experiments/AR1/baselines.json` | unreviewed, experiment running |
| F9 | Simple-statistic floors on the ladder (one fold): warp-only against two-person morph 0.912 (one band-power number); photo against two-person morph 0.955 (one Haar energy). Excess of the two-person head: 0.068 and 0.031 | `experiments/PD1_signal-isolation-paired-differences/landmark/result.md` | unreviewed |
| F10 | Processed variants (JPEG 90/70/50, blur, 50% resample) exist only for FRLL and MAD22 rows. The development photos and all training pools have the original variant only | `/home/narolski/mambamorph-code/smadcvpr_data/manifests/eval.csv` (row counts) | counted |

Data paths checked by listing (all exist): the four DINOv3 mean-token files in
`/mnt/t7/smad_next/PD1/landmark/feat/dinov3_512/`; CLIP tokens for `ar1`, `af0_w1`, `af0_w2`, `bench_s` and
`ar1soft` in `/mnt/t7/smad_next/AF0/feat/clip224/`; `/mnt/t7/smad_next/AF0/lists/ar1soft.csv` (1,200 rows:
R0 and R2w at 112.7 and 61.2 px, 200 hosts); `/mnt/t7/smad_next/AF0/img/soft/{amsl112,fm61}` (745 and 742
files); `/mnt/t7/smad_next/AF0/cues/{ar1,bench_s,af0_w1,h1}.npz`; `/mnt/t7/smad_next/AR1/img/frgcferet/opencv/{R2w,R3,R3m,R4}`
(536 files each); `/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z/e7/FaceMorpher` (204
files); `/mnt/t7/smad_heldout/a43/data/manifests/a43.csv`; `src/C_cue_checks/c_checks.py`; `src/SM1/expr_geom.py`.
Missing at the time of my listing: DINOv3 tokens for `ar1soft`; any feature of the 612 FRLL variant frames;
cue statistics for `ar1soft` and `af0_w2`; any softened copy of a ladder morph.

## 2. Idea 1: training with a false-alarm limit for every storage history

### Novelty

Opened by me (abstract pages only):

- Sagawa, Koh, Hashimoto, Liang, "Distributionally Robust Neural Networks for Group Shifts", ICLR 2020,
  https://arxiv.org/abs/1911.08731. Worst-group training. Its central result bites here: a network that fits
  the training set has near-zero worst-group training loss too, so the group objective alone changes
  nothing; strong regularisation or early stopping is needed.
- Cotter et al., "Optimization with Non-Differentiable Constraints with Applications to Fairness, Recall,
  Churn, and Other Goals", https://arxiv.org/abs/1809.04198. Rate constraints with multipliers. The weight
  update in the idea is this scheme.
- Tong, Feng, Li, "Neyman-Pearson classification algorithms and NP receiver operating characteristics",
  Science Advances 2018, https://arxiv.org/abs/1608.03109. Lowest miss under a false-alarm bound. The page
  states that limiting the empirical false-alarm rate is not enough to hold the bound on new data.
- Sun et al., "Rethinking Domain Generalization for Face Anti-spoofing: Separability and Alignment", CVPR
  2023, https://arxiv.org/abs/2303.13662. One classifier shared across domains through invariant risk
  minimisation, in face presentation attack detection. Closest in the neighbouring field.
- Kashiani et al., "Towards Generalizable Morph Attack Detection with Consistency Regularization", IJCB
  2023, https://arxiv.org/abs/2308.10392. Consistency across augmented copies in morph detection. No rate
  constraint and no fixed rule on the abstract page.
- Ju et al., "Improving Fairness in Deepfake Detection", https://arxiv.org/abs/2306.16635. Group-wise losses
  over demographic groups. Not over processing histories.

What remains new, as far as I could check: a false-alarm limit per processing history as the training
constraint in morph detection, proved on left-out histories, with the decision rule shipped as part of the
network. My one search in morph detection found no such paper. NOT verified: a full search (budget used up).
The loss itself is not new and must not be claimed.

### Strongest objection

The constraint is slack exactly where the idea applies it.

1. The recipe it constrains already flags 0.0% of every genuine pool at its own rule (F1) and at most 4.9%
   of every shrink-history pool at the development threshold (F2). There is no storage-history violation
   to remove on the ViT-L/14 recipe.
2. What that recipe does fail on is outside the idea. JPEG (23 to 50% at quality 50) cannot be trained on:
   no JPEG code is allowed and no JPEG copy of a training photo exists (F10). The tight frame (43 to 76%)
   is declared out of scope ("not removed by the idea").
3. The write-up's "4 to 22% when every pool is protected" is bound by pools in the tight frame (F4). With
   a threshold from any full-frame shrink-history pool the landmark miss is 0.00. History matters for this
   recipe only on top of the tight frame (59 to 87% against 43 to 76%, F2).
4. At the own rule the recipe's failure is on the miss side: AMSL 0% detected, WebMorph 14 to 59% (F1),
   although the ranking is near perfect (F5). A limit on false alarms pushes genuine scores down. It does
   not raise the scores of morphs from an unseen tool.
5. In a LoRA fit the training-pool flag rate reaches zero within a few hundred steps. The weights then
   never rise, and the "constrained fit" is balanced sampling plus a margin (Sagawa et al. above).

So the headline table "releases fail, ours is held to 5%" has a problem: the leading baseline recipe is
held to 0% without the method. The contrast exists for SelfMAD and, weaker, for ViT-B/16.

### Cheapest confound that gives the same numbers

A score offset between capture domains. A network that puts every camera photo far below its rule passes
"every left-out genuine pool at most 5%" with no invariance at all. The SMDD-trained recipe does exactly
this (0% flags, 0% of AMSL detected). Control: never print a flag rate without the miss at the same rule,
and require the usual-loss arm to violate the limit before the constrained arm is credited.

Second confound, for the head test: a softness window. On whole-frame Laplacian variance the two registered
doses roughly bracket the morph (photo 1.0; 112.7 px copy about 0.28 to 0.38; morph about 0.21; 61.2 px
copy about 0.09; my arithmetic from cue-table row 11a and the round-2 reviewer's numbers, different pools,
not measured as such). A head can learn "morph = this softness window" and pass every genuine row. Control:
softened morphs (61.2 px copies of R4) must still be flagged, and corrected MAD22 FaceMorpher must be read
against its own history-matched photos (soft against soft).

### Contradictions with the record

- "The limit makes storage history unable to cause a flag" presumes it causes flags in this recipe. F1, F2
  and F4 say it does not for ViT-L/14. It does for ViT-B/16 (F3).
- "A 224 network can barely see the 112.7 px history": the ViT-B/16 retrains flag 1.5 to 29% of the
  AMSL-history pool against 0 to 7% of the original photos (F3). A history above the input's band still
  leaves a readable trace.
- The cue table already lists the ViT-L/14 recipe as robust to the history control (row 5).

### Feasibility by 14 Nov

Head test: data exist (checked). To extract: DINOv3 tokens for the 1,200 softened images and the 612 FRLL
variant frames. Full version: needs the SMDD rebuild arms (only arm c is built), new scale values (author's
yes), softened morphs, then about 65 A100-hours on Athena, which accepts jobs since 18:26. Possible if the
data are built on 12 Nov.

### Revised design

1. The method is the crossed data, environment-balanced batches and a fixed genuine-side margin on the
   unchanged recipe. The per-environment weight update is an ablation arm, kept only if it beats balanced
   batches.
2. A violation is shown first: the usual-loss arm on the same data must exceed the limit in a left-out
   environment. If it does not, the constraint is reported as not needed.
3. The storage-history claim is tested on the ViT-B/16 recipe, where the failure is measured (F3). The
   ViT-L/14 network is the headline and must keep its landmark numbers.
4. Environments on both sides: genuine pool by state, and morph tool by state (as built; morph then shrink
   at 112.7 and 61.2 px).
5. The frame becomes an environment: the same constant-colour blanking in the tight-frame geometry for
   genuine images and morphs (an allowed operation), because the tight frame is the pool that binds.
6. JPEG rows are printed as uncontrolled until the author rules on the registered JPEG branch (section 6).
7. Training length, early stop or weight decay, and the seed list are fixed in advance; all seeds printed.
8. Two operating points for every detector: own rule and development threshold. Always the pair (flag
   rate, miss).
9. The claim is joint: every left-out genuine pool at most 5% flagged, and miss on AMSL and WebMorph at the
   same rule far below the SMDD-trained recipe (100% and 41 to 86% missed at its own rule, F1).
10. Border-free read: corrected MAD22 OpenCV and Webmorph, whose morph files have the photos' size.
11. Diffusion and GAN cells under both class policies; no claim that the limit creates signal.

### First test: fixed-rule head test, revised (NU1r)

- Step 0, before any fit: build 61.2 and 112.7 px copies of the 536 OpenCV-style R4 morphs with the verified
  path (`src/AF0/soften.py`; approved scope "our own morphs"; CPU, under one hour on the loaded DGX).
- Features: DINOv3 ViT-L/16 at 512, mean patch token. Existing:
  `/mnt/t7/smad_next/PD1/landmark/feat/dinov3_512/af0_{ar1,af0_w1,af0_w2,bench_s}_mean.npz`. To extract:
  the 1,200 images of `/mnt/t7/smad_next/AF0/lists/ar1soft.csv`, the 1,072 softened R4 copies, the 612
  FRLL frames of variants jpeg50, blur1, resample50 in `eval.csv`. CLIP ViT-L/14 at 224 printed beside.
- Heads: logistic, 5 folds by person, partner-safe. E: usual loss, unprocessed negatives. X: usual loss,
  112.7 px negatives pooled. XB: as X with environment-balanced weights. C: the constrained fit (2% per
  training environment, out of fold).
- Training: ladder R0, R2w (OpenCV-style), their 112.7 px copies, AF0 photos and warp-only images;
  positives: ladder R4, its 112.7 px copies, AF0 uniform 0.5 morphs. Held out: all 61.2 px copies, every
  FRLL and MAD22 image, FaceMorpher.
- Reads at each head's own rule and at the threshold that flags 5% of held-out-fold R0: flag rate on FRLL
  native, the seven landmark E7 pools, the three variant sets, the 61.2 px genuine copies; miss on the
  seven landmark cells, on the 61.2 px R4 copies, and on MAD22 FaceMorpher against its E7 pool.
- Cost: about 0.5 GPU-hours of extraction, CPU under one hour, 3 to 5 hours wall.

Pass: (a) head E or X flags more than 10% of some left-out pool (a violation exists); (b) head C flags at
most 10% of every left-out pool of 200 images or more (point value at most 5%); (c) C's family-mean miss is
at least 3 points below XB at a threshold matched to C's worst-pool flag rate; (d) C misses at most 20% of
the 61.2 px R4 copies. Then one ViT-B/16 pair on Athena (balanced against constrained).

Kill the constraint (keep the table and the data protocol): XB already holds every left-out pool at 10% or
less, or (c) fails. Kill the head-level line: C exceeds 10% on a left-out pool, or misses more than 20% of
the softened morphs.

Scores: impact 5, feasibility 6, shortcut-proofness 3, novelty 3. The fixed-rule table is useful to the
paper, but the loss is known and its lever is slack on the leading recipe. It limits outputs on listed
environments only and does nothing for JPEG, capture source or generator traces.

## 3. Idea 2: train only on what the measured cues cannot explain

### Novelty

Opened by me (abstract pages only):

- Clark, Yatskar, Zettlemoyer, "Don't Take the Easy Way Out: Ensemble Based Methods for Avoiding Known
  Dataset Biases", EMNLP 2019, https://arxiv.org/abs/1909.03683. A bias-only model trained first, then
  ensembled with the main model during training. This is the proposed loss.
- He, Zha, Wang, "Unlearn Dataset Bias in Natural Language Inference by Fitting the Residual", 2019,
  https://arxiv.org/abs/1908.10763. Biased model from features known to carry the bias; main model fits the
  residual.
- Bahng et al., "Learning De-biased Representations with Biased Representations", ICML 2020,
  https://arxiv.org/abs/1910.02806. The vision version: be different from a model that is biased by design.
- Puli et al., "Out-of-distribution Generalization in the Presence of Nuisance-Induced Spurious
  Correlations", https://arxiv.org/abs/2107.00520, and Makar et al., "Causally motivated Shortcut Removal
  Using Auxiliary Labels", AISTATS 2022, https://arxiv.org/abs/2105.06422. Make label and nuisance
  independent with known nuisance labels. The idea's "overlap weights" arm belongs here.
- Grommelt et al., "Fake or JPEG? Revealing Common Biases in Generated Image Detection Datasets", 2024,
  https://arxiv.org/abs/2403.17608. Closest in image forensics: measured JPEG and size cues in a detection
  set, removed at the data level, more than 11 points better across generators.

What remains new: the bias model taken from a measured audit of a morph benchmark, and the cue model's
out-of-fold AUC as an acceptance rule for a training set. NOT verified: whether a product-of-experts loss
with hand-made cue features exists in forensics or morph detection (search did not run). RUBi was not opened.

### Strongest objection

The "by construction" claim is wrong. The loss is minimised by f(x) = log-odds(label given image) minus
b(x). Wherever the image says more than the cues, the detector learns to subtract the cue model. Our heads
reach 0.98 to 1.00 on the ladder, so this is the normal case. At test time f alone then scores a soft
genuine image lower and a sharp morph higher. That is dependence on the cue with the sign reversed, not
independence. The price falls on soft morphs, and morph files are stored small in 8 of 17 cells.

Three more points.

- The cue vector contains the physical footprint of the signal. Blending lowers band power, and one
  band-power number already gives 0.912 for warp-only against two-person morphs (F9). Boosted trees on 27
  statistics will pass the idea's own 0.95 overlap limit on the ladder. The first test as written is
  inadmissible by the idea's own rule.
- Columns defined only for morphs (tool, partner) predict the label perfectly. The offset then saturates
  and every example gets the same small, label-aligned gradient: the usual fit at a lower rate.
- The cue model is global. A network can read local softness (face against hairline) that 27 whole-frame
  numbers cannot express. The planted corner mark proves the mechanism only for a cue the model captures
  exactly.

### Cheapest confound that gives the same numbers

Over-correction. "History-matched pools at most 10% flagged" and "absolute cue correlation at most 0.2"
are both met by a head that learned "soft means less morph-like". Controls: print the signed correlation;
make the soft-against-soft cell mandatory (corrected MAD22 FaceMorpher against its E7 photos, both in the
`bench_s` list; and 61.2 px copies of ladder R4); the miss there must not rise against the usual fit.

### Contradictions with the record

- "Two-person against same-person morphs is the rung where softness is equal by measurement" rests on one
  number (PNG size 0.51). The same file gives 0.616 for a 32-pixel thumbnail and 0.587 for background
  statistics on that contrast (F8). It is not a cue-free rung until the full 27-statistic floor is printed.
- The conditional AUC inside strata of a cue model already failed once: on benchmark cells no stratum held
  both classes (EV1 README, section 7). It can be measured on the ladder only, and with wide intervals.

### Feasibility by 14 Nov

First test: no GPU; features and cue files exist (checked). Full version: cue statistics for about 100,000
training images on a saturated CPU machine (Athena is GPU-only), and a training set that passes the overlap
rule, which needs softened morphs and a dose grid first. Low to moderate.

### Revised design

1. The cue model becomes an acceptance test for any training set: boosted trees on the 27 statistics, the
   colour statistics and the border share, out of fold by person; no column that exists for one class only.
2. Acceptance: out-of-fold AUC at most 0.90 and at least 150 images per class with absolute log-odds below
   2. Otherwise the set is crossed further before any fit. This replaces the one-number Laplacian rule.
3. The method arm is the usual loss with clipped inverse weights 1 / p(label given cues), so that label and
   cues are independent in the weighted set. Its optimum has no minus-b term.
4. The logit-offset fit is a comparison arm only.
5. Signed cue correlation is reported, never the absolute value alone.
6. The soft-against-soft rows are mandatory.
7. Role in the paper: a price column per cell (error with cue-balanced weights minus error with the usual
   loss). No state-of-the-art claim rests on it.
8. Leaving one cue family out stays, to state how far the protection reaches.
9. The LoRA stage (one ViT-B/16 pair) runs only if the head test passes.

### First test: cue-balance test, revised (NU2r)

- Step A, admissibility (CPU, about 20 minutes). Cue model for R4 against R0 and R2w, OpenCV-style engine,
  536 hosts, 5 partner-safe folds by person. Cues: `/mnt/t7/smad_next/AF0/cues/ar1.npz` (26 statistics and
  PNG size). Report out-of-fold AUC and the count of images per class with absolute log-odds below 2.
- Step B, only if admissible. Features `/mnt/t7/smad_next/PD1/landmark/feat/dinov3_512/af0_ar1_mean.npz`
  and `af0_bench_s_mean.npz` (DINOv3 ViT-L/16 at 512, mean patch token). Three logistic heads: usual,
  inverse-weighted, logit offset. Reads on held-out hosts and on `bench_s` with cues from
  `/mnt/t7/smad_next/AF0/cues/bench_s.npz`: signed rank correlation of the score with the cue log-odds among
  FRLL genuine photos; flag rate on each landmark E7 pool at the threshold that flags 5% of native FRLL
  photos; EER on MAD22 FaceMorpher against its E7 pool; EER on the seven landmark cells; AUC of R3 against
  R4.
- Cost: 0 GPU-hours, under 1 CPU-hour, 1 to 2 hours wall.

Pass: Step A admissible; the weighted head halves the worst E7 flag rate or brings it to 10% or less;
signed correlation within plus or minus 0.2; MAD22 FaceMorpher against E7 at most 2 points above the usual
head; family-mean EER on the seven cells within 3 points of the usual head.

Kill as a method (keep the acceptance rule): Step A gives AUC above 0.95 or fewer than 150 mixed images per
class, and softened morphs are not built by the evening of 12 Nov. Kill the offset arm: signed correlation
below minus 0.2. Kill the weighted arm: landmark EER up by more than 5 points with no fall in E7 flags, or
the usual head already at 10% or less on every E7 pool (no room; then one ViT-B/16 pair decides, as the
generator wrote).

Scores: impact 4, feasibility 4, shortcut-proofness 4, novelty 3. The acceptance rule and the price column
are worth having; the loss is known and does not do what the write-up says. It protects against listed
whole-frame cues only.

## 4. Idea 3: canonical view, one storage band and frame for every input

### Novelty

Not searched (budget). Verified neighbours: Grommelt et al. above (equalising JPEG and size at the data
level). From our own class-definition check, not re-opened by me: Scherhag et al. 2020 give both classes
the same post-processing. From memory, NOT verified: detectors built on 112-pixel face-recognition crops
are band-limited by design; fixed input transformations as a defence are known in adversarial robustness.
A fixed degradation of every test input as part of a morph detector was not found by me, but I did not
look. The frame mask is already on the table (cue table row 7; EV1 review follow-up 3).

### Strongest objection

The band does not remove what drives the errors, and it is not "by construction".

1. For the eight cells "already at the band" the canonical view is the identity on the morph and the
   existing E7 control on the photo (F7). That comparison is in the record. A network that never saw a
   morph still reaches 0.55% EER on MAD22 FaceMorpher and 5.25% on MorDIFF against history-matched photos
   (F6). What separates the classes at the band is the route into the band, the generator trace, the
   frame, and on MAD22 FaceMorpher a visible vendor watermark (AF0 README, section 8). The idea lists
   these as "not removed".
2. The path cannot restore detail. Certificate part b ("the no-morph network refitted on T(render) against
   T(shrunk render) must be at chance") cannot hold: a render has IED about 63 px, its shrunk copy about
   20 px, and T leaves the copy untouched (F7). Part b reduces to part a.
3. "A history above the band is not in the input" is an empirical claim. The ViT-B/16 retrains react to a
   112.7 px history through a 224 input that carries 88 px (F3). A box-filter shrink is not an ideal
   low-pass; an earlier resampling changes the roll-off inside the band.
4. The leading recipe does not need it (F1, F2, F5). Its measured failures are JPEG and the frame.
5. The existing call shrinks only when the scale is below 1 (F7). The front end therefore treats inputs
   differently by native resolution. A reviewer, and the binding constraint "no gate on resolution", can
   both object.
6. A 61 px band is below the reported passport minimum (90 px; clause unverified in the EV1 review). "We
   degrade every passport photo before detection" is a hard sell at CVPR.

### Cheapest confound that gives the same numbers

Read (c), "EER at most 5% on MAD22 FaceMorpher at the band", is passed by a network with no morph in
training (0.55%, F6). Route, surround and watermark are enough. Control: print the morph-free network as a
row of read (c), and blank the surround and the bottom band in both classes. Read (a) passes for a trivial
reason: both arms end with the same box filter.

### Feasibility by 14 Nov

The first test is possible (files exist; about 1,300 CPU copies; 0.3 GPU-hours). The method is not: T on
about 100,000 training images on a saturated CPU machine, a new scope for benchmark files at test time, an
author ruling on the resolution branch, and a cost that is expected to hurt AMSL and WebMorph.

### Verdict and what to keep

Drop the canonical band as a method. Keep two pieces elsewhere:

- The common frame mask, the same constant-colour blanking in every image at training and at test, moves
  into the main protocol (idea 1, revised design, point 5). It targets the pool that actually binds.
- The band-matched read exists already as columns: E7 for the eight band cells, and the both-classes 50%
  resample cells of `A3_crossed.csv`, which put the FRLL landmark morphs at 56 to 69 px.

### Check that confirms the drop or revives the idea (existing files, about 0.1 GPU-hours)

Route check: the 204 stored-small photos (arm E of the MorDIFF ladder study, A43; manifest
`/mnt/t7/smad_heldout/a43/data/manifests/a43.csv`) against the E7 MorDIFF frames of the same photos
(`eval.csv`, set mordiff, variant resmatch). Same persons, same tight frame, same band (median IED 65.07
and 65.14 px, border 0.543 and 0.545, `AM2.json`). Logistic probe, 5 folds by person, DINOv3 ViT-L/16 at
512 and CLIP ViT-L/14 at 224 mean tokens (408 frames to extract). Beside it, from `a47_read.md`: the
morph-free network under E7 on the eight band cells.

Revive only if the route probe is at most 0.55 (upper bound at most 0.60) on both features and the
morph-free network is at 40% EER or more on MAD22 FaceMorpher once surround and watermark are blanked in
both classes. Otherwise the drop stands. I expect the drop to stand (the SelfMAD release flags 97% against
79% of these two pools, EV1 review).

Scores: impact 3, feasibility 3, shortcut-proofness 4, novelty 2. Removal from the input is the strongest
kind of protection, but here it removes a cue the leading recipe does not use and leaves the ones the
record shows at work.

## 5. Points that affect the whole programme

1. Re-aim the lens. On the ViT-L/14 recipe the measured genuine-side failures are JPEG compression and the
   tight frame, and the fixed-rule failure is missed morphs (F1, F2, F4). Storage history is a ViT-B/16 and
   SelfMAD result. These are my unreviewed reads; they need the results reviewer before anyone builds on
   them.
2. The fixed-rule table must always print the pair (flag rate, miss). A flag rate alone rewards a detector
   that never fires.
3. No softened ladder morph exists. One CPU job (61.2 and 112.7 px copies of the 536 OpenCV-style R4
   morphs) serves the first tests of ideas 1 and 2 and the soft-against-soft control.
4. JPEG cannot enter training under the allowed list. The registered function that holds the approved
   shrink branch also holds JPEG, blur and 50% resample branches (`prep_eval.degrade`). Running them
   unchanged on training photos needs the author's yes.
5. Corrected MAD22 FaceMorpher is not usable as evidence of morph detection without blanking: watermark,
   surround, and a morph-free network at 0.55% under the history control (F6).
6. "Two-person against same-person" is not yet a softness-free contrast (F8). Print the full statistic
   floor before it carries a claim.
7. Head tests on frozen pooled features have little room (3 to 6% flagged, `experiments/AF0/cn0.json`).
   Each head test above therefore names the condition under which it says nothing and a LoRA pair decides.
8. The generator's contradiction about the recipe on AMSL and WebMorph (AUC 0.999 against "15.0 and 7.8%
   EER") stands unresolved; the checkpoint and frames behind each number must be stated before a bar is set.

## 6. Questions for the author

1. May the registered JPEG, blur and 50% resample branches of `prep_eval.degrade` be run unchanged on
   training photos, warped halves and our own morphs, as was approved for the shrink branch?
2. Is the own rule (0.5) acceptable as a printed operating point for released detectors whose papers
   report EER only? (That no release paper names 0.5 as its operating point is NOT verified.)
3. Is a front end that shrinks only inputs above a fixed IED a "gate on resolution"? (Relevant only if idea
   3 is revived.)

## 7. Prior work opened (abstract pages; nothing else was read)

- https://arxiv.org/abs/1911.08731 (Sagawa et al., found through search)
- https://arxiv.org/abs/1809.04198 (Cotter et al.)
- https://arxiv.org/abs/1608.03109 (Tong, Feng, Li)
- https://arxiv.org/abs/2303.13662 (Sun et al., SA-FAS)
- https://arxiv.org/abs/2308.10392 (Kashiani et al.)
- https://arxiv.org/abs/2306.16635 (Ju et al.)
- https://arxiv.org/abs/1909.03683 (Clark et al.)
- https://arxiv.org/abs/1908.10763 (He et al.)
- https://arxiv.org/abs/1910.02806 (Bahng et al.)
- https://arxiv.org/abs/2107.00520 (Puli et al.)
- https://arxiv.org/abs/2105.06422 (Makar et al.)
- https://arxiv.org/abs/2403.17608 (Grommelt et al.)
- https://arxiv.org/abs/1912.11035 (Wang et al., CNN-generated images; the abstract does not name blur or
  JPEG augmentation, so I do not cite it for that)

One search summary mentioned a NIST study in which preprocessing raises the false-alarm rate of morph
detectors and a file-size-adapted threshold does not help. I did not open the source. Do not cite it.

## 8. Not verified

- Every read in section 1 marked unreviewed. They are single passes over existing files by me.
- The Laplacian arithmetic in section 2 (different photo pools; second-hand numbers).
- That the loss minimiser argument of section 3 shows up at the size predicted on our features. It is
  algebra; the size of the effect is an expectation.
- All novelty statements beyond the pages listed in section 7.
- All compute and wall-time figures. They are estimates from the timings in the records.
- The passport minimum of 90 px between the eyes (quoted from the EV1 review, clause not checked).
