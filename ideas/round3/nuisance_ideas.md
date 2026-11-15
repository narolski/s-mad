# Round 3 ideas, nuisance lens: constraints under which the measured cues cannot help

11 Nov 2026, about 18:30 CET. Idea generator for round 3, lens "nuisance". Thinking only. Nothing was run,
trained, scored or built for this page. I made light reads of existing result files (JSON, CSV, markdown) and
directory listings. No sealed file was opened (no `valx.csv`, nothing named FST or A12SP, nothing under
`/home/narolski/.config/smad-next/`). No image was loaded. I did not read the other generators' files in this
folder, so overlap with them is independent agreement, not copying.

## Terms

- S-MAD = single-image morphing attack detection (one image in, "morph or genuine" out).
- AUC = area under the ROC curve (0.5 is chance). EER = equal error rate in percent.
- FA = false-alarm rate: the share of genuine images called a morph. Miss = the share of morphs not flagged.
- IED = inter-eye distance in pixels. CLIP = a pretrained image-text encoder. LoRA = low-rank adaptation, a
  light way to fine-tune it. MADation recipe = CLIP with LoRA and a linear header, trained on SMDD.
- SMDD = the standard synthetic training set (25,000 genuine renders, 15,000 landmark morphs).
- Ladder rungs: R0 camera photo; R1 the same photo with a storage history; R2w warp only; R3m photo blended
  with its mirror; R3 morph of two photos of one person; R4 morph of two persons.
- Existing shrink path = the registered shrink-and-enlarge call `prep_eval.degrade(img, "R", scale)`, followed
  by the unchanged alignment where the frame needs it. It made the history-matched copies ("E7").
- Environment = one kind of genuine image: source pool by storage history (by expression where known).
- Own rule = a network's own decision, probability of morph above 0.5 (logit above 0). No threshold is fitted
  on any test pool.
- Cue vector = the simple measurements of an image that the audit has shown to separate classes somewhere:
  26 statistics of `smadcvpr/cue_floor.stats`, PNG size, six colour statistics, zero-border share, a geometry
  smile probability, and labels we know by construction (pool, tool, history dose, partner).

## 1. What "the cue cannot help" can mean

The record uses the phrase in three different senses. Each needs a different proof, and a reviewer's
"you only moved the shortcut" needs a different answer for each.

1. **The cue is not in the input.** A fixed preprocessing step removes it for every image. Proof: no probe of
   any kind can read the cue from the processed images. This is the strongest sense. It costs every signal
   that lives in the same place as the cue.
2. **The cue cannot cause a flag.** Training limits the false-alarm rate in every genuine environment at one
   fixed decision rule. Proof: flag rates on environments that were left out of training. The network may
   still "see" the cue. It cannot turn a genuine image into a flagged one.
3. **The cue is not rewarded.** Training gives no credit for anything a model of the measured cues already
   explains. Proof: the score is unrelated to each measured cue among genuine photos, and a deliberately
   planted cue is not picked up. This is the only sense available for cues we may not or cannot change in an
   image (colour, capture detail, expression, partner).

The three ideas below are one per sense. They are complements, not rivals.

| Measured cue | Idea 1: limit per history | Idea 2: residual of the cue model | Idea 3: canonical view |
|---|---|---|---|
| Storage history (shrink-and-enlarge, stored small) | cannot cause a flag; tested on left-out doses, processes and pools | dose is in the cue vector; not rewarded | absent above the common band |
| Softness (blending or resampling) | softened genuine environments cannot be flagged | 27 statistics in the cue vector; R3 against R4 is the control | absent above the band; softness inside the band stays |
| Border left by alignment | not removed by the idea; the read uses the same constant-colour blanking in both classes | border share in the cue vector | identical mask for every image: absent |
| Capture detail and expression of the genuine class | environments split by pool and expression; unseen pools tested | smile probability, file size and backdrop statistics in the cue vector | not removed inside the band |
| Generator fingerprint | one-photo reconstructions are their own environment (both class policies printed) | "is a render" label in the cue vector | only the part above the band |
| Five fixed partners in SMDD | prerequisite: balanced partners (the SMDD rebuild, SM1) | partner label in the cue vector: release morphs give no gradient | not addressed |
| File attributes | not in pixels | file size in the cue vector | not in pixels; every image is re-stored |

## 2. Facts I build on

Measured and reviewed (from the brief and the reviews):

- SelfMAD release at its own rule: 0% of unprocessed genuine photos flagged, 44.6% after a 50%
  shrink-and-enlarge, 55 to 79% with the diffusion benchmarks' histories, 97.1% stored small
  (`experiments/EV1_fixed-threshold-reread/AM2_B1_rule05.csv`, review `experiments/reviews/REVIEW_EV1_20261111.md`).
- MADation ViT-B/16 release on our frames: the 63 to 65 pixel history raises the score of 99 to 100% of FRLL
  photos by 1.3 to 1.6 logits (`AM2_B2_logit_shift.csv`).
- Miss rates depend on the threshold pool. Protecting every history-matched pool raises the family-mean miss
  of the releases to 66 / 79 / 87% (`AM2_B3_*`).
- A two-person landmark morph has 0.52 times the Laplacian variance of its own warped halves; that number
  alone separates morph from halves at AUC 0.76 (512 px) to 0.87 (224 px) (`ideas/CONSOLIDATED_v2.md`, measured
  by the forensics reviewer, raw text in `ideas/ROUND2_vetting_raw.json`).
- A network that never saw a morph (SMDD renders against their shrunk copies) reaches 0.00% on MorDIFF and
  0.00 to 1.17% on DiM at its last checkpoint (`01_EVIDENCE_DOSSIER.md` rows for A47 I-3).
- One earlier training change did remove the shrunk-photo response: the same random processing chain on both
  classes (A22; A30 amendment 6: shrunk FFHQ photos flagged 19 to 40% before, 4 to 8% after, at a cost of 0.4
  to 1.5 points). Source: the record check in `ROUND2_vetting_raw.json`; A30 amendment 6 was not opened at
  its primary file by that check or by me. That chain used resample, JPEG and blur code that is not on
  today's allowed list.

Light reads I made today. These are existing files; the readings are mine and **unreviewed**:

- **R1. The same-person morph is the softness-matched rung.** PNG size does not separate two-person from
  same-person morphs (AUC 0.508 OpenCV, 0.516 FaceMorpher) but separates two-person morphs from warp-only
  images (0.315 and 0.313, that is 0.69 folded). Probes on detector features still read two-person against
  same-person at 0.86 to 0.93 for the MADation and SelfMAD rows (0.68 to 0.70 for MixFaceNet-MAD). Files:
  `experiments/AR1/baselines.json`, `experiments/AR1/gate_c.json` (partial; the landmark ladder (AR1) is still
  running).
- **R2. The mirror self-morph carries a trivial cue of its own.** A 32-pixel thumbnail model separates
  mirror self-morphs from two-person morphs at 0.93 and from warp-only images at 0.89; probes on CLIP-based
  detector features separate mirror from two-person at 0.99 to 1.00. Same two files. A mirror blend is
  symmetric, and that is easy to read.
- **R3. A plain head on frozen CLIP at 224 is not where the history failure sits.** A cross-tool logistic
  head (photo or warp-only against two-person morph) flags 3.2 to 5.6% of FRLL history-matched photos at the
  threshold that flags 10% of its own negatives (`experiments/AF0/cn0.json`, the clean-negative test, CN0).
- **R4. The MADation ViT-L/14 recipe retrains are already near zero miss on FRLL landmark cells at one fixed
  threshold.** Miss at the development 5% threshold 0.02 to 0.3%; at the threshold that protects every pool
  4 to 22%; on diffusion cells 82 to 92% (`experiments/EV1_fixed-threshold-reread/A2_family_means.csv`, rows
  M3L, alpha 0.05).
- **R5. Giving both classes the same processing costs these networks nothing on FRLL landmark cells.** With
  morphs and genuine photos both through the 50% resample, or both blurred, the AUC of the five ViT-L/14
  recipe retrains stays at 0.999 to 1.000, and the ViT-L/14 release stays at 0.879 / 1.000 / 1.000 / 0.998
  against 0.884 / 1.000 / 0.997 / 0.990 native (`A3_crossed.csv`, same folder).
- **R6. The earlier consistency loss was tested at mild doses.** The plan of that experiment (A49) lists
  shrink scales 1.0, 0.75 and 0.5 and JPEG quality 85 or 95, a Jensen-Shannon term on probabilities, and a
  mean probability change that was already 0.036 to 0.046 without the loss
  (`/home/narolski/mambamorph-code/experiments/DINOv3_P1_PLAN_20261108.md`,
  `.../A49_dinov3/RESULTS_20261108.md`). It did not test the benchmark's 3.3 times histories.

Derived by me (arithmetic on measured numbers; **not measured as such**):

- **D1. The training doses miss the test dose.** On our frames a FRLL photo has IED 202.3 px in a 512 frame
  (EV1 README section 7), so 88 px at a 224 input. The diffusion and MAD22 FaceMorpher histories hold detail
  only up to IED 61 to 70 px (medians 61 to 65), which is about 0.7 to 0.8 of what the input can carry. The AMSL history (112.7 px) is
  above what the input can carry, so a 224 network can barely see it. SMDD renders have an inter-eye
  distance of about 63 px in a 256 frame (SM1 README section 5), so about 55 px at 224. The 0.3125 shrink
  used for the history-crossed arm puts their detail at about 20 px, which is 0.36 of the input. So training
  holds doses 1.0 and 0.36, and the benchmark sits at 0.7, between them.

## 3. Ideas, ranked

### Idea 1. Training with a false-alarm limit for every storage history ("fixed-rule training")

**One line.** Train the standard recipe so that, at the network's own rule, no kind of genuine image is
flagged more than 1% of the time, and prove it on kinds that were left out of training.

**Signal.** The same signal as the base recipe: the trace of mixing two captures (double contours and
superposed textures in landmark morphs; the code-mixing trace where generator ladders are in training). The
idea adds no new signal. It fixes where genuine scores may sit.

**Which cue, in which sense.** Storage history and resampling softness: they cannot cause a flag (sense 2).
Warp without blending: the same. Capture source and expression: as far as the training pools vary in them,
and tested on pools never trained on.

**Why this is more than the protocol on the table.** The protocol on the table changes the data (crossed
histories) and keeps the usual loss. The usual loss balances the average. The audit measures the tail of
each pool at one threshold. A network can have 5% false alarms on average and 30% on the softest pool. Here
the tail of every pool is the training constraint, and the decision rule is part of the network. The audit
of released detectors and the claim about ours are then the same table.

**Design.**

- Training images (no FRLL, FFHQ or FEI person): the rebuilt SMDD arms of the SMDD rebuild (SM1: balanced
  partners, warped halves, shrunk copies); the landmark material on FRGC and colorFERET persons from the
  alpha-field probe (AF0: 663 persons, photos, warp-only images, halves, uniform 0.5 morphs) with softened
  copies through the existing shrink path. Optional: the generator ladders, with one-photo reconstructions
  as their own environment.
- Genuine environments: pool (SMDD render, FRGC, colorFERET) by state (as stored; shrink path at each
  strength; warp-only or half; half then shrink), split by expression where it is labelled. Every batch
  draws equally from the environments.
- Dose grid (answers D1): strengths between 0.36 and 1.0 of the input. For 512 frames these are the
  registered targets 61.2 and 112.7 px. For SMDD renders they are the same call at scales 0.75 and 0.5 beside
  0.3125. The two new scale values need the author's yes.
- Morphs carry histories too, on both sides of the blend: morph then shrink; shrink the sources, then morph.
  So "soft" is in both classes at every dose and the blend trace is not always the last thing erased.
- Objective: logit s. Morphs: mean of softplus(-s). Genuine images of environment e: mean of softplus(s + 1)
  with weight w_e. Every few hundred steps, measure FA_e = share of held-out training-pool persons of
  environment e with s above 0, and raise w_e when FA_e is above 1%, lower it (not below 1) when it is not.
  This is a plain constrained fit: lowest miss subject to FA_e at most 1% for every e.
- Architecture: the MADation recipe unchanged (CLIP ViT-L/14, LoRA, linear header). One network.
- Fixed in advance: training length, last checkpoint, seed list. Nothing is selected on a benchmark.
- Test time: one image, one forward pass, flag if s is above 0. EER and AUC are printed as well for the
  published tables.
- Optional arm, not core: a one-sided hinge on photo and processed-copy pairs (the copy may not score more
  than half a logit above its photo). It is optional because the earlier consistency loss failed (R6 says
  why that test was weak, but the record check advises against making it the fallback).

**How the ladder proves it.** One table at the own rule, on persons never trained on. Rows: R0; R1 for every
family's history pool; R2w; softened R2w; three kinds of left-out environment: a dose not used in training
(the 61.2 px copies, or the 63 to 65 px FRLL pools), processes never used in training (the existing JPEG 50,
blur and 50% resample files of the FRLL photos), and pools never used in training (FRLL, FFHQ with its five
history pools, FEI). Pass: every row at most 5% observed with an upper Clopper-Pearson bound of at most 10%.
R4 per tool gives the miss. R3 and R3m go into the single-subject table. The released detectors are printed
in the same table from numbers that exist (SelfMAD 0 / 45 / 55 to 79 / 97%).

**Cost in benchmark error.** Expected, not measured: at most 1 to 2 EER points on landmark cells (the earlier
symmetric-processing result cost 0.4 to 1.5 points, see section 2; and R5 says both-class processing is free
for this recipe on FRLL landmark cells). Diffusion and GAN cells: the limit cannot create signal. Today the
recipe misses 82 to 92% of diffusion morphs once every pool is protected (R4). Native diffusion numbers will
fall to what the generator ladders teach.

**Why a reviewer cannot say "you moved the shortcut".** The claim is about outputs: no genuine environment,
including three kinds never trained on, exceeds the limit at a fixed rule. A cue could still help only if
it is absent from every protected genuine environment and present in morphs. If a left-out environment
fails, the table shows it. What I do not claim: that the features no longer encode history. They will. The
claim is the author's own error definition: a processed genuine image is not called a morph.

**First test, at most one day, existing data (fixed-rule head test, NU1).**

- Features (frozen, mean patch token): DINOv3 ViT-L/16 at 512 from
  `/mnt/t7/smad_next/PD1/landmark/feat/dinov3_512/af0_{ar1,af0_w1,af0_w2,bench_s}_mean.npz`; CLIP ViT-L/14 at
  224 from `/mnt/t7/smad_next/AF0/feat/clip224/{ar1,af0_w1,af0_w2,bench_s}.tokens.npy`. New extraction of
  files that exist: the 1,200 softened genuine-side images of `/mnt/t7/smad_next/AF0/lists/ar1soft.csv` and
  the 612 FRLL genuine frames of variants jpeg50, blur1 and resample50 in
  `/home/narolski/mambamorph-code/smadcvpr_data/manifests/eval.csv`.
- DINOv3 at 512 decides: a 512 input can carry the histories that a 224 input cannot (D1), and the dense
  head on these tokens already reacted to warp-only images (0.73 standard deviations on FaceMorpher, AF0
  first pass, unreviewed). CLIP at 224 is printed beside (R3 says a plain head on it may already pass, which
  leaves no room to show an effect).
- Training (5 folds by person, the partner-safe folds of the paired-differences landmark study, PD1): genuine
  environments = ladder R0, R2w (OpenCV-style engine), their 112.7 px softened copies (200 hosts), AF0 photos
  and warp-only images; positives = ladder R4 (OpenCV-style) and AF0 uniform 0.5 morphs. Held out of
  training: the 61.2 px copies, every FRLL image, FaceMorpher.
- Heads (logistic): E = usual loss, unprocessed negatives; X = usual loss with softened negatives pooled (the
  protocol on the table); C = the constrained fit (limit 2% per training environment, out of fold).
- Read at each head's own rule: FA on FRLL native, the seven FRLL and MAD22 landmark history pools, the three
  variant sets and the held-out 61.2 px copies; miss on the seven landmark cells of `bench_s` and on held-out
  R4. For E and X also the miss at a post hoc threshold moved until their worst-pool FA equals C's. That is
  the fair baseline: crossed data plus a worst-pool threshold.

**Kill and pass.** Kill: head C has more than 10% false alarms on any left-out pool of at least 200 images
while its training environments are at or below 2% (the limit does not transfer); or its family-mean miss
is not at least 3 points below head X at the matched threshold and X needs a test-pool threshold to get
there (the objective adds nothing). Pass: worst left-out pool at most 10% (point value at most 5%) and miss
at least 3 points below matched X, or family-mean miss at most 5%.

**Path to state of the art.** Landmark cells: the recipe is already strong at one threshold (R4, R5); the
constraint is expected to keep that and to give the one table where the released detectors fail and ours
does not. Bar to beat on our frames: our own ViT-L/14 recipe retrains, not the release (see observation 4).
Diffusion and GAN cells: only as far as the ladders in training carry; printed under both class policies.

**Compute.** First test: about 0.3 GPU-hours of feature extraction, heads on CPU, 2 to 4 hours wall on the
loaded DGX. Full: three arms (release SMDD, crossed rebuild with the usual loss, crossed rebuild with the
limit) by five seeds, CLIP ViT-L/14. One fit took 1.94 H100-hours in the record (A12BR); I estimate 3.5
A100-hours (scaled from the measured ViT-B/16 timing in AD4, not measured). About 55 A100-hours plus 5 for
scoring; under a day on Athena with 8 parallel jobs.

**Risks.** The limit may not transfer to unseen capture sources; the record shows one release flagging 73%,
55% and 14% of three photo pools at one threshold (cue table row 12). At a 1% limit there are few tail
events per environment, so the weights are noisy; 2% is the fallback. It creates no signal. Rate-constrained
training exists outside morph detection (from memory: Neyman-Pearson classification; group-robust
optimisation, Sagawa et al. 2020; rate constraints, Cotter et al. 2019); I know of no use in morph detection,
and this must be checked before a novelty claim.

### Idea 2. Train only on what the measured cues cannot explain ("the audit as the bias model")

**One line.** Turn the audit's cue table into a frozen cue model, add its output to the detector's logit
during training only, and score with the detector alone, so that nothing the measured cues explain is
rewarded.

**Signal.** Evidence of mixing that the cue vector does not carry: double contours, a second face's
structure, texture from two captures. By construction it is not sharpness, band power, colour, border,
file size, pool, dose, partner or smile.

**Which cue, in which sense.** All cues that can be computed per training image: not rewarded (sense 3).
This includes the cues we are not allowed or not able to equalise by an image operation: colour statistics,
capture detail, expression, partner, pool. For those, a statistical control is the only lever under the
allowed-operations list.

**Why it is new here.** The paper's two halves were criticised for not meeting. Here the audit's output is
the method's input: every cue the audit measures becomes a column of the cue vector. A cue found later
becomes one more column and one more retrain.

**Design.**

- Cue vector c(x), measurement only, existing unchanged code: the 26 statistics of `smadcvpr/cue_floor.stats`
  and PNG size; six colour statistics and zero-border share (`src/C_cue_checks/c_checks.py`); the geometry
  smile probability of the SMDD rebuild (`src/SM1/expr_geom.py`); labels known by construction (source pool,
  tool, history dose, partner).
- Cue model: gradient-boosted trees from c(x) to the label, fitted in folds by person so that every training
  image gets an out-of-fold log-odds b(x), calibrated, clipped to plus or minus 4.
- Overlap rule for the training set: the cue model's out-of-fold AUC must lie between 0.6 and 0.9. Above
  0.95 almost no image is left to learn from (on the SMDD release one sharpness number already gives 0.99),
  so more crossed data must be added first (dose grid, histories on both sides of the blend, balanced
  partners). This replaces the one-number acceptance of the rebuild (Laplacian AUC at most 0.65) by the same
  test on the whole cue vector.
- Detector: the MADation recipe. Loss: cross-entropy of sigmoid(f(x) + b(x)) against the label. At test time
  only f(x) is computed. The cue model is never evaluated on a test image, so there is no fusion.
- Why this does what it says: if b is the true log-odds given the cues, then no function of the cues alone
  lowers the loss. The gradient on an image is sigmoid(f + b) minus the label, which is near zero wherever
  the cues already decide correctly. The fit is driven by soft genuine images and sharp morphs.
- Operating point: f alone has no calibrated zero. Use the constraint of idea 1 on top, or one threshold
  from a crossed development pool. The two ideas combine.
- Cheaper arm for comparison: the usual loss with overlap weights from the same cue model.

**How the ladder proves it.**

1. Flags at one fixed rule on R0, R1, R2w and the left-out environments, as in idea 1.
2. Score against cue among genuine photos: the largest absolute rank correlation between the score and any
   cue, within one pool (FRLL 204; FFHQ 2,000), at most 0.2. The same number for every released detector can
   be computed tonight on CPU from existing scores and statistics.
3. Cue-conditional AUC: R2w against R4 within fifths of b(x). This is "what is left when the measured cues
   cannot help", as a number.
4. R3 against R4, never trained on: the rung where blend softness is equal by measurement (R1 in section 2).
5. Planted cue: train twice on a set in which a harmless mark (a constant-colour corner square, an allowed
   operation) sits on 80% of morphs and 20% of genuine images. The usual loss must pick it up (AUC with the
   mark reversed far below AUC with the mark agreeing). With the mark's presence in c(x), the residual fit
   must not (gap at most 0.03). This shows the mechanism, not just a clean data set.
6. Leave one cue family out: drop the high-frequency statistics from c(x), retrain, repeat read 2 for those
   statistics. This says how far the protection reaches beyond the listed cues. I expect: not far. The paper
   should say so.

**Cost in benchmark error.** Expected: cells that cues solve get worse (a network with no morph in training
already reaches 2.6% or better on 9 to 10 of 12 scored cells; EV1 README section 8). Print per cell the
"price": native EER of the residual fit minus that of the usual loss on the same data, beside the same
difference on the history-matched column. The claim is that the second is zero or negative.

**Why a reviewer cannot say "you moved the shortcut".** For the measured cues there are three separate
facts: no reward in training (by the loss), no relation to the score among genuine photos of unseen pools
(read 2), and no uptake of a planted cue (read 5). For unmeasured cues nothing is claimed; read 6 measures
the reach, and the protocol says how to add a cue.

**First test, at most one day, existing data, no new image (cue-residual head test, NU2).**

- Data: ladder R0, R2w, R3, R4 of the 536 hosts, OpenCV-style engine (`/mnt/t7/smad_next/AR1/img/frgcferet/`).
  Features: `/mnt/t7/smad_next/PD1/landmark/feat/dinov3_512/af0_ar1_mean.npz` and the CLIP mean patch token.
  Cues: `/mnt/t7/smad_next/AF0/cues/ar1.npz` (26 statistics and PNG size per image). FRLL and MAD22 landmark
  cells with native and history-matched genuine photos: `af0_bench_s_mean.npz`, `AF0/cues/bench_s.npz`.
- Heads (logistic, 5 folds by person, partner-safe): usual loss; overlap-weighted; residual (offset = cue
  model fitted inside the training folds). Contrast: R4 against R0 and R2w.
- Reads on held-out hosts and on FRLL: largest absolute rank correlation of score with any cue among genuine
  photos; cue-conditional AUC of R2w against R4; AUC of R3 against R4; share of history-matched FRLL photos
  flagged at the threshold that flags 5% of native FRLL photos; EER on the seven landmark cells.

**Kill and pass.** Kill: the usual-loss head shows a cue correlation of at least 0.3 and the residual head
does not at least halve it; or the residual head's cue-conditional AUC is below 0.70; or its held-out-tool
AUC falls by more than 0.05. Pass: cue correlation at most 0.2 on FRLL genuine photos, cue-conditional AUC
at least 0.80, every history-matched pool at most 10% flagged. If the usual-loss head already has a cue
correlation below 0.3 and flags at most 10%, frozen pooled features are uninformative for this idea; then
the decisive test is one pair of LoRA fits on Athena on the ViT-B/16 recipe, where the record has a rise of
11.4 points on diffusion cells under history matching: kill if the residual fit's rise is more than half
of the usual fit's.

**Path to state of the art.** It is a change of loss on the recipe that already leads on landmark cells, so
it keeps the backbone, the data and the comparison. Its table is the price column above. Where the price is
large the cell was cue-solved, and the paper says so with the morph-free row beside it.

**Compute.** First test: 0 GPU-hours (features and cues exist), under one CPU-hour, 1 to 2 hours wall.
Full: cue statistics for about 100,000 training images (about 8 core-hours, my estimate); five residual
fits (about 18 A100-hours; the usual-loss arm is shared with idea 1); the planted-cue pair on ViT-B/16
(about 5 A100-hours). About 25 GPU-hours.

**Risks.** After crossing, the residual loss may add nothing over the usual loss. If the cues explain
almost everything (the simple-statistic floor for warp-only against two-person is 0.91 in the first pass of
the paired-differences landmark study, unreviewed), few images drive the fit and seeds will spread. The
protection covers listed cues only. The technique is known in language tasks (from memory: product of
experts and learned mixin, Clark et al. 2019; residual fitting, He et al. 2019; RUBi, Cadene et al. 2019);
the new part is the bias model taken from a measured audit, and that claim needs a novelty check.

### Idea 3. Canonical view: one storage band and one frame for every input, by construction

**One line.** Run the existing shrink path with one fixed target on every image, at training and at test,
and blank the same frame region in every image, so that storage history above the band and the border are
not in the network's input at all.

**Signal.** What survives at the benchmark's own lowest storage band: contours doubled by more than a few
pixels (hairline, ears, face outline, collar), coarse double structure inside the face, and how average the
face is. It cannot read fine softness, because no input has fine detail.

**Which cue, in which sense.** Storage history, fine softness, JPEG grid, the high-frequency part of the
generator fingerprint, file attributes: absent above the band (sense 1). Border and background: absent
(identical mask). Not removed: softness inside the band, capture detail inside the band, expression, the
low-frequency part of the generator fingerprint, partners.

**Why it is worth a slot.** In 8 of 17 cells the morph files themselves hold detail only up to an inter-eye
distance of 61 to 70 px (MAD22 FaceMorpher, MorDIFF, six DiM families; EV1 review and
`family_native_ied_targets.json`). A network that needs more than that is using something the
morph files in those cells do not contain. And it is the only design here where the proof does not depend
on which head we trained: the cue is gone for any reader.

**Design.**

- Front end T, the same code path for every image, no decision: (1) the unchanged alignment; (2) the existing
  shrink path with scale = tau / native IED, which is the registered history-matching branch with one
  constant in place of the family median; (3) constant-colour blanking outside one fixed mask.
- tau: first choice 61.2 px (a registered strength). Second arm 48 px, because inputs that are natively at
  61 to 65 px otherwise pass almost unchanged and may still show their route.
- Network: the MADation recipe on T(x), trained on the crossed rebuild after T. One network, one image.
- Certificate, in three parts. (a) Any probe: the strongest readers we have (a logistic probe on frozen CLIP
  patch tokens, which reads history at AUC 1.0 on untreated frames per the record check; the same on DINOv3
  patch tokens at 512; a small network from scratch; a LoRA fit) must not separate T(R0) from T(R1) on
  held-out persons: AUC at most 0.55, upper bound at most 0.60. (b) The network with no morph in training, refitted on T(render)
  against T(shrunk render), must be at chance on its own task and on every cell. The experiment that
  reached 0.00% on MorDIFF without a morph can then no longer be run. (c) Border share AUC exactly 0.5.
- If the band costs too much on splice-type families: a second network that sees the native image and is
  anchored to the canonical one. Morphs: usual loss. Genuine images: the native score may not exceed the
  canonical network's score of T(x) by more than a margin. The reported network may then use fine evidence
  to raise morph scores, while its genuine scores are tied to a history-free target. One network at test.

**How the ladder proves it.** Parts (a) to (c) above, then the usual ladder on T(x): R0 against R1 is at
chance for the detector and for probes; R2w against R4 and R3 against R4 are printed with the
simple-statistic floor at the band.

**Cost in benchmark error.** Not known. Hints from existing scores: none lost on FRLL landmark cells when
both classes go through the 50% resample or the blur (R5), but that dose is above what a 224 input sees. At
61 px the mean landmark displacement of a two-person pair (4.2 px at 512, forensics reviewer) becomes about
1.3 pixels, so inner-face doubling mostly turns into wider edges. I expect losses on AMSL and WebMorph, where the periphery is clean. The first test measures it.

**Why a reviewer cannot say "you moved the shortcut".** For history, fine softness and border the answer is
that they are not in the input, shown by probes that are stronger than our detector. The honest remainder
is listed above and is handled by ideas 1 and 2.

**First test, at most one day (canonical-view test, NU3).** Existing data plus about 1,300 shrink-path
copies of our own images (approved scope of the softened-examples wave of AF0: training photos, halves, our
own morphs; CPU minutes).

- Existing: `/mnt/t7/smad_next/AF0/img/soft/fm61` (61.2 px copies of R0 and R2w for 200 ladder hosts) and
  `.../soft/amsl112`; corrected MAD22 FaceMorpher morphs (native median IED 61.2 px, already at the band)
  against the 204 history-matched genuine frames
  `/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z/e7/FaceMorpher` (features in `bench_s`).
- To build with the unchanged path: 61.2 px copies of the 536 OpenCV-style R4 morphs and of R2w for the
  other 336 hosts; 61.2 px copies of the 200 existing 112.7 px copies of R0 (a second pass, for the
  certificate).
- Features: DINOv3 at 512 and CLIP at 224, mean patch token. Heads: logistic, 5 folds by person.
- Reads: (a) probe AUC, T(R0) against T(R1 at 112.7 px); (b) T(R2w) against T(R4), beside the native value
  and the simple-statistic floor at the band; (c) the head trained on canonical ladder images, tested on
  MAD22 FaceMorpher at the band (EER); (d) on existing files only: the photo stored small (arm E of the
  MorDIFF ladder study, A43) against the history-matched pool in the same MorDIFF frame, two genuine routes
  to the same 64 px band; this probe AUC says whether the route still shows.

**Kill and pass.** Kill: read (a) above 0.65 (the cue is still in the input); or read (b) below 0.85 or
within 0.05 of the floor; or read (c) above 10% EER. Pass: (a) at most 0.55; (b) at least 0.95 and at least
0.05 above the floor; (c) at most 5%.

**Path to state of the art.** On published tables the network is scored on the native files; T is part of
the network. On the 8 cells whose morph files are already at the band nothing is lost on the morph side. On
the other landmark cells the cost test decides between the canonical network and the anchored one. If both
lose more than 3 points on two or more landmark cells, the idea is kept as an instrument (a canonical-band
column for every detector) and not as the method.

**Compute.** First test: 20 to 30 CPU-minutes for the copies, about 0.3 GPU-hours of features, 3 to 4
hours wall. Full: T on about 100,000 training images (about 28 core-hours, my estimate; the path detects
face points per image); five fits (about 18 A100-hours); the no-morph control (five ViT-B/16 fits, about 6);
the anchored arm (about 18). About 45 GPU-hours, 1.5 days.

**Risks.** The band may delete the evidence for splice-type morphs. Inputs natively at 61 to 65 px get
almost no shrink, so their route can remain readable; tau = 48 px tests this. Running the path on benchmark
files at test time is a new scope and needs the author's yes. The scale uses the detected eye distance; it
is a normalisation like alignment and not a gate, but it should be stated plainly.

## 4. Alternatives considered and rejected

| Alternative | Why not |
|---|---|
| Linear erasure of cue directions before the head (LEACE-style) as the main line | The guarantee holds only for a linear head on fixed features, and the landmark numbers need LoRA. History is readable non-linearly at AUC 1.0 from frozen patch tokens and survives per-image normalisation (record check, Astra E2). Round 1 notes three failed projection attempts on 10 Nov (not opened by me). The paired-differences landmark study (PD1, question 4) already tests removal of the softening and pipeline directions. I keep erasure only as a probe, in the certificate of idea 3 |
| Symmetric twin-consistency loss as the main line | It failed once (A49). That test was weak (R6), but the record check advises against making it the fallback, and the per-environment limit of idea 1 reaches the same end with a weaker assumption. Kept as an optional one-sided arm in idea 1 |
| Mirror self-morphs or same-person morphs as training negatives ("every step except the second identity") | The author ruled that a same-person morph counts as a morph. The mirror rung has a trivial symmetry cue (R2), so it would move the shortcut. Same-person morphs need two sessions per person, which SMDD and FFHQ lack. Use R3 as the softness-matched test rung instead (R1) |
| One softened half per morph, matched to the morph's sharpness, as the fix for softness | Good as a test rung. As a training fix it equalises one number; band shape, colour and the rest stay. It needs a per-image scale for the shrink path. Idea 2 covers the whole vector without per-image matching |
| The random resample, JPEG and blur chain on both classes | It worked in the record, but its code is not on today's allowed list. The allowed analogue (the existing path at registered strengths) is in the protocol on the table and in idea 1 |
| A face-recognition backbone at 112 px (round 1) | Blind by bandwidth, like idea 3, but it changes the backbone and loses the controlled comparison with the MADation recipe |
| Non-negative last layer (positive evidence only) | Camera detail can be encoded as the absence of a feature; the sign constraint does not stop that (the literature file's own caveat) |
| Invariant risk penalties across histories | Known to fall back to the usual fit with few environments; idea 1 states the constraint directly |
| Per-pool thresholds or per-history calibration | A gate on source or resolution. Forbidden |
| Adversarial removal of history from the features | Unstable in three days, and the certificate would still have to come from fresh probes |
| Scoring an image against its own shrunk copy and combining the two scores | Combining two scores is fusion. Forbidden |

## 5. For the lead

1. The mirror rung is trivially separable (R2). Heads trained with mirror pairs, such as the one-person head
   of the paired-differences landmark study, may be learning symmetry. Its first-pass 0.945 for warp-only
   against mirror self-morph fits that reading.
2. The same-person morph is the softness-matched rung (R1). "Two-person against same-person" is therefore
   the cleanest existing contrast for "more than softness", and detector features read it at 0.86 to 0.93.
3. The doses in training do not bracket the benchmark's dose in a useful way (D1). The history-crossed arm
   should hold strengths near 0.7 of the input, not only 0.36.
4. The ViT-L/14 recipe retrains show AUC 0.999 or more on all four FRLL landmark cells natively, against
   history-matched photos and with both classes resampled or blurred; 0.98 or more under JPEG; 0.96 or more
   with neutral-only genuine photos (`A3_crossed.csv`, `AM_A3_crossed_neutral.csv`); and a miss of 0.3% or
   less at the development threshold. The round-2 record check quotes 15.0 and 7.8% EER for
   "the ViT-L/14 recipe" on AMSL and WebMorph. The two cannot both describe the same checkpoint and frames.
   Which checkpoint each number comes from should be stated before a bar is set. The cues still uncrossed on
   these cells are the border from our aligner and the JPEG quality of the FRLL-Morphs files.
5. The earlier consistency experiment (A49) is cited as "a consistency loss failed". Its doses were mild and
   its measure was near its floor (R6). It should not be used to dismiss constraints at benchmark doses.
6. No softened copy of a ladder morph exists (`ar1soft` holds R0 and R2w only). "Morph against genuine at
   equal history" cannot be read on the ladder today.
7. Head-level tests of history robustness on frozen CLIP at 224 have no room to show an effect (R3). Use
   DINOv3 at 512, the ViT-B/16 recipe, or LoRA fits.

## 6. Questions for the author

1. May the existing shrink call be run with other values of its own scale parameter (a dose grid for SMDD
   renders: 0.75 and 0.5 beside 0.3125; one fixed target for every input in idea 3)?
2. May the existing shrink path be run on benchmark files at test time, as a fixed preprocessing step of our
   own network, the same for every input (idea 3)?
3. Is the network's own 0.5 rule acceptable as the headline operating point, with EER beside it (idea 1)?
4. Are warp-only images and halves genuine for the purpose of a false-alarm limit? (The SMDD rebuild already
   asked whether a half is a genuine image.)
5. Are one-photo reconstructions a protected environment or only a row of the single-subject table?

## 7. Not verified

- Every number under "Light reads" and "Derived" in section 2. The readings are mine, from files of
  experiments that are still running or unreviewed.
- A30 amendment 6 (the 19 to 40% against 4 to 8% figures) at its primary file.
- The three failed projection attempts of 10 Nov (taken from a round-1 note).
- All prior-work statements. They are from memory. No paper was opened for this page.
- All compute figures beyond the two measured timings (1.94 H100-hours for a ViT-L/14 fit; about 1.1
  A100-hours for a ViT-B/16 fit).
- That `cue_floor.stats` and the geometry smile probe run unchanged on every training pool.
- That the inter-eye distance of SMDD renders (63 px, read from five partner renders) holds for the set.
- Every expected effect, cost and chance stated above. They are my estimates, not measurements.
