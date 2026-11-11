# Round 3, lens "state of the art": three candidate recipes for the network that goes into the paper

11 Nov 2026, evening. Idea generator, lens: strategy for the method. Thinking and light file reads only.
Nothing was trained, scored or generated for this page. No sealed file was opened. I did not read the
other round-3 generators' files.

How to read this page

- S-MAD = single-image morphing attack detection. EER = equal error rate in percent. AUC = area under
  the ROC curve (0.5 is chance). BPCER = share of genuine images flagged. APCER = share of morphs missed.
- LoRA = low-rank adaptation, a light way to fine-tune a pretrained encoder. CLIP ViT-L/14 = the large
  OpenAI CLIP vision transformer with 14-pixel patches. SMDD = the standard synthetic training set
  (25,000 StyleGAN2 genuine renders, 15,000 landmark morphs, 256 pixels).
- Rungs of the ladder (from the brief): R0 camera photo; R1 the same photo with the morphs' storage
  history; R2 the tool or generator run on one photo; R2w warp only; R3m photo blended with its own
  mirror image; R3 morph of two photos of one person; R4 morph of two persons.
- "Inter-eye distance" = distance between the two eye centres in pixels. It is the natural unit for
  "how much detail an image file can hold about a face".
- "Measured" = a number in the record, with its file. "Expected" = my estimate. "Unreviewed" = an
  owner's first number from today that no reviewer has checked.
- Experiments are named by plain description with the ID in brackets.

---

## 0. Summary in twelve lines

1. Three recipes, ranked. They share one backbone family and one evaluation protocol, and they compose.
2. **Recipe 1, the ladder-ordered network.** CLIP ViT-L/14 with LoRA at 224 pixels, the MADation
   recipe, on release-style face crops. New part: the ladder becomes the training objective. Inside
   each host, nuisance steps (storage, warp, softness) are tied to zero score difference; signal steps
   (re-synthesis, mixing of two captures or codes, second person) must raise the score by a margin.
3. **Recipe 2, the canonical-band network.** The same network trained and tested at one fixed, small
   input size, so that every face reaches the network at the inter-eye distance of the smallest
   benchmark files (about 63 pixels). Storage history above that size is then absent from the input by
   construction, not by training.
4. **Recipe 3, the SMDD-Ladder protocol.** The same objective trained only on images derived from
   SMDD renders: the landmark rebuild plus mirror rungs plus the diffusion and GAN generators run on
   SMDD renders. Every camera-photo pool stays held out. This is the row that is comparable with the
   field, and a training set we can release.
5. One fact I measured today that ties the three together: SMDD genuine renders have a median
   inter-eye distance of 63.65 pixels (section 2.1). The three small-storage benchmark families sit at
   61 to 65 pixels. The standard training set and the cells where detectors follow storage history live
   at the same size.
6. Where the published state of the art needs a benchmark cue, on present evidence: FRLL-Morphs AMSL
   (storage and compression of the morph files), FRLL-Morphs StyleGAN2 and MAD22 MIPGAN-I and II
   (generator output against camera photo), MorDIFF at 0.00 to 1.10% (storage history or generator
   output). Section 1 says what to print there instead.
7. Where an honest network can reach or beat the published numbers: FRLL-Morphs FaceMorpher, OpenCV
   and probably WebMorph; MAD22 FaceMorpher, OpenCV and Webmorph; the five-cell MAD22 mean if a
   re-synthesis step is allowed to count (policy O below).
8. The fixed-threshold bar is low and measured: at a threshold that keeps false alarms at 5% on every
   history-matched genuine pool, current detectors miss 63 to 87% of morphs on average over families
   (fixed-threshold re-read (EV1), `experiments/EV1_fixed-threshold-reread/result.md`, item 4; our
   frames). This is the number the paper's network should move most.
9. First tests need no cluster: all three run on crops and feature caches that exist tonight.
10. Compute for everything: about 1,050 A100-hours over three days (830 for recipe 1, 75 and 150 more
    for recipes 2 and 3), under 4% of the Athena grant.
11. Decisions use development pools only. FRLL, FEI, the corrected MAD22, MorDIFF and DiM are scored
    once, after the configuration is frozen.
12. Four author decisions are needed (section 8).

---

## 1. What the record says about each benchmark cell

Published values: MADation Tables 1 and 3 and SelfMAD Table II as copied into
`experiments/RS1_own-crop-rescore/prereg.md` (checked there from the arXiv HTML); FD-MAD averages from
`docs/PLANNING_RECORD.md` line 606 (abstract-level check by a helper, per-cell values not in our record).
"Never saw a morph" = the earlier morph-free experiment (A47, part I-3), CLIP ViT-B/16 recipe trained
on SMDD renders against their shrunk copies, last checkpoint, three seeds, on our frames
(`experiments/AD4/README.md` section 5.4; `01_EVIDENCE_DOSSIER.md` rows 72, 88, 112). "Robust recipe" =
our MADation-recipe ViT-L/14 retrains on SMDD only, five seeds, native then history-matched, on our
frames (`docs/sources/methods_table/gather_regular.md` row 13; old MAD22 subset).

| Cell | Best published EER % | Never saw a morph | Robust recipe, native → matched | My reading |
|---|---|---|---|---|
| FRLL-Morphs FaceMorpher | 0.00 SelfMAD; 0.74 ViT-L/14 | 2.62 | 0.4 → 0.4 | honest reach plausible |
| FRLL-Morphs OpenCV | 0.00 SelfMAD; 0.99 ViT-L/14 | 18.66 | 0.3 → 0.3 | honest reach plausible; see 2.3 |
| FRLL-Morphs WebMorph | 3.42 ViT-B/16; 3.45 SelfMAD | 0.65 | 7.8 → 7.6 (ViT-L/14 release 4.9 → 4.4) | within about one point of honest reach |
| FRLL-Morphs AMSL | 0.99 SelfMAD; 3.85 ViT-B/16 | 0.82 | 15.0 → 14.5 (SelfMAD 2.9 → 33.3) | published level needs the cue |
| FRLL-Morphs StyleGAN2 | 8.99 MixFaceNet-MAD; 10.34 SelfMAD | 27.47 | not in the table read | needs generator-against-camera |
| MAD22 FaceMorpher | 0.00 ViT-B/16; 0.40 ViT-L/14 | 0.00 | 0.6 → 0.5 | honest reach plausible; cell is solvable without morphs |
| MAD22 OpenCV | 2.23 ViT-L/14; 3.85 ViT-B/16 | 31.35 | 8.6 (storage equal in both classes) | clean cell; the main target |
| MAD22 Webmorph | 10.80 ViT-B/16 | 23.64 | 15.8 | clean cell; reachable |
| MAD22 MIPGAN-I | 16.70 MixFaceNet-MAD; 20.32 ViT-L/14 | 75.51 | 0.8 (our frames) | construction cell: generator PNG against camera JPEG |
| MAD22 MIPGAN-II | 9.06 ViT-L/14 | 73.01 | not read | same |
| MAD22 five-cell mean | 6.12 FD-MAD; 10.48 ViT-L/14; 14.05 ViT-B/16 | — | — | reachable only if the GAN cells are |
| MorDIFF | 0.00 FD-MAD; 1.10 ViT-B/16 | 0.00 | weak without diffusion training | published level is reached without any morph |
| Greedy-DiM | 7.60 SelfMAD | 0.22 | ViT-L/14 release 9.8 → 9.8 | honest level about 5 to 10 |

The two MADation means are my arithmetic on its five published cells (52.41 / 5 and 70.23 / 5).

### Where the published level needs a benchmark cue, and what the paper prints instead

- **FRLL-Morphs AMSL.** Measured: a network that never saw a morph reaches 0.82%; the detectors that
  do not move under history matching sit at 14 to 15%; the SelfMAD release goes from 2.9 to 33.3%
  (`01_EVIDENCE_DOSSIER.md` section 2.1). JPEG quality alone separates this cell perfectly (cue matrix
  row 4b). So values of 1 to 4% are not evidence of morph detection. I expect an honest network at 8 to
  14%. Print: native EER, history-matched EER, false alarms on the existing JPEG variants of the genuine
  photos at the fixed threshold, and the morph-free row beside it. Claim only "best among detectors
  that pass the storage control".
- **FRLL-Morphs StyleGAN2, MAD22 MIPGAN-I and II.** These cells compare generator output with camera
  photos (cue matrix row 9a). Measured: no released detector separates a GAN morph from a one-person
  render (best 0.61, StyleGAN3 ladder re-read (AG5)). Unreviewed: a head that reads only mixing reaches
  0.73 to 0.78 on our GAN ladder (paired differences (PD1), GAN part). An AUC of 0.78 is an EER near
  28%. So the published 9 to 20% is not reachable by reading mixing alone, on present evidence. Print:
  native EER under both class policies, the same-generator step (one-person output against two-person
  morph, from the MIPGAN one-person controls (AG1) when they exist), and a reference network trained on
  "reconstruction against camera photo" that never saw a morph.
- **MorDIFF and the DiM families.** Measured: the morph-free network reaches 0.00% on MorDIFF and 0.00
  to 1.17% on six DiM families. So 0.00 to 1.10% is reachable without morph detection. Print: native
  EER, EER against history-matched genuine photos, morph against one-photo reconstruction, and the
  flag rate of stored-small genuine photos at the fixed threshold.
- **Smiling half.** In 12 of 17 cells the genuine class is half smiling. Print a neutral-only genuine
  column for every detector (already the lead's rule).
- **MAD22 FaceMorpher.** FaceMorpher morphs are easy to detect honestly, but the cell is also solved by
  the morph-free network. Print it, mark it "solvable without morphs", keep it out of headline means.

---

## 2. Four observations that shape the design

### 2.1 SMDD lives at the size of the smallest benchmark files (measured today by me, unreviewed)

From the stored landmarks of the 25,000 SMDD genuine renders
(`/mnt/t7/Datasety/downloads/SMDD/smdd_bona_landmarks_if106.npz`, points 38 and 88, times 256): median
inter-eye distance 63.65 pixels, 10th to 90th percentile 59.9 to 65.8, n = 24,997. The SMDD audit
(SM1) prints the same quantity for ten partner renders: 63.2 to 64.0
(`experiments/SM1_smdd-partner-audit-and-rebuild/pairs_summary_audit.json`). I assumed points 38 and 88
are the eye centres (the landmark ladder record names them as a mirror pair).

The registered medians of the small-storage benchmark families are 61.2 (MAD22 FaceMorpher), 63 (DiM)
and 65 (MorDIFF) (`experiments/AF0/result.md` wave 4; `experiments/EV1_fixed-threshold-reread/result.md`
line 43). FRLL photos are near 202 pixels (resample50 gives 101).

Consequences, as hypotheses:
- Every SMDD-trained detector has only ever seen faces at about 63 pixels between the eyes, enlarged
  about 1.5 times by its loader. A camera photo shrunk to 61 to 65 pixels is the only kind of test
  photo that matches the training size. That is where the releases move.
- The registered shrunk copies of SMDD renders (80 pixels wide) are at about 20 pixels between the
  eyes. "Render against its 80-pixel copy" is a very strong softness contrast.

### 2.2 At 224 pixels a tight face crop is already limited to about 95 pixels between the eyes (estimate)

A face-detector crop with a 5% margin is about 2.3 times the inter-eye distance wide. Resized to 224,
the face arrives at roughly 95 pixels between the eyes. Not measured; ten minutes on the existing crop
boxes of the landmark ladder (AR1) would settle it. If it holds:
- Storage histories of 112 to 254 pixels (the FRLL-Morphs families) cannot be seen at 224. This fits
  the record: the ViT-L/14 release moves by −0.004 to −0.007 logits under those histories (EV1 item 3;
  weak evidence, because its scores are saturated on our frames).
- Only the 61 to 65 pixel histories remain visible. Those are below the 90-pixel passport minimum the
  EV1 review quotes (clause not verified in our record).
- So a 224-pixel network needs learned invariance for exactly one band, 61 to 95 pixels.

### 2.3 The only clean landmark cells are MAD22 OpenCV and Webmorph

There the morph files and the genuine photos have the same size (history dose about 1.0), and the
morph-free network is at 31 and 24%. The robust recipe sits at 8.6 and 15.8% there, but at 0.3% on
FRLL-Morphs OpenCV, with the same tool and the same persons. On our frames the FRLL-Morphs landmark
morphs carry a black border from our aligner (border alone AUC 0.99 to 1.00, cue matrix row 7), and
history matching leaves it in place. So part of the "robust on landmark cells" picture may be border.
The own-crop re-score (RS1) will say. For the method this means: measure progress on MAD22 OpenCV and
Webmorph first, and never on our old frames.

### 2.4 Frozen CLIP features, trained on clean negatives, do not import the storage reaction (unreviewed)

The clean-negative test (CN0, `experiments/AF0/cn0.json`): a logistic head on mean-pooled CLIP
ViT-L/14 tokens at 224, trained on warp-only against two-person morphs of one tool and tested on the
other, reaches AUC 0.9998 to 1.000. At the threshold that flags 10% of test warp-only images it flags
3.2 to 5.6% of the FRLL history-matched photos. No simple-statistic floor was computed there (the cue
list is empty). The landmark part of paired differences (PD1) gives the floor on the same kind of
images: a single band-power statistic reaches 0.912, a two-person head on DINOv3 features 0.980, excess
0.068 [0.026, 0.114] (`experiments/PD1_signal-isolation-paired-differences/landmark/result.md`). So the
landmark signal is strong but mostly band power, and the softened-negative arm is decisive.

---

## 3. Recipe 1 (rank 1): the ladder-ordered network

### 3.1 What it reads

Two-capture superposition in landmark morphs, and the mixing step in diffusion and GAN morphs. Each
signal is defined inside one host as the difference between a morph and its own one-capture
counterparts. Storage history, warp and softness are defined inside one host as differences that must
be zero.

### 3.2 What is new against the list in the brief

Items 1 and 2 of the brief are a data protocol (rebuilt SMDD on the MADation recipe) and a probe on
frozen features (paired differences). This recipe turns the ladder into the loss of the LoRA fit, adds
camera-photo and generator ladders, fixes one input pipeline in which published numbers reproduce, and
gives one score with one threshold. Round 1 had a related idea with one linear output per ladder step
("RungHeads"); the record says a second head hurt the first when the backbone is trained. Here there
is one output and the steps become constraints on it. Closest general prior work, from memory, to
verify: conditional variance penalties with grouping (CoRe, Heinze-Deml and Meinshausen), matched-pair
domain generalisation (MatchDG), ordinal and pairwise ranking losses.

### 3.3 Input and preprocessing (same for training and test, for every image)

1. Face crop by the existing RGB face-detector path (`src/AR1/crop_rgb.py`, the unchanged functions of
   the earlier corrective crop). Crops are stored as lossless PNG. No aligner, so no aligner border:
   measured 0% black pixels on such crops, on 8 files per source
   (`experiments/RS1_own-crop-rescore/README.md`, 17:45).
2. The existing loader resize to 224 (bilinear), the MADation normalisation.
3. No flip averaging at test time. The mean of two sigmoids is a fusion of two scores; the releases
   are read without it.

Why this pipeline: on it the MADation ViT-B/16 release reproduces its published regime (AMSL 3.44,
FaceMorpher 0.49 to 0.86, OpenCV 1.47, WebMorph 1.51 to 1.88, MorDIFF 0.99; RS1 README, 17:48). On our
512-pixel frames it does not (AMSL 15.1). A state-of-the-art claim on frames where the baselines do not
reproduce would not survive review.

### 3.4 Backbone and adaptation

CLIP ViT-L/14 (OpenAI weights), LoRA rank 2 on the query and value projections of every block, linear
head: the registered MADation ViT-L/14 recipe of the morph-free networks experiment (AD4), unchanged
(`experiments/AD4/README.md` section 4, training call). Reasons: it is the leading published family; a
helper-checked study of 30 encoders reports CLIP ViT-L/14 with LoRA at 3.7% overall error against
11.3% for SelfMAD; in our record it is the recipe that moves least under history matching; and "nothing changed
but data and loss" is then a controlled comparison with the release. Ablation arms: LoRA rank 8; 336
pixels; ViT-B/16 for screening.

### 3.5 Training data (what is on disk or being built tonight)

Every image has: a host, a family, a rung level, a storage state. Levels:

| Level | Members | Role in the loss |
|---|---|---|
| L0 | camera photo or SMDD render, in any storage state; warp-only images; the morph's own warped halves | label 0; tied together inside a host |
| L1 | generator run on one photo (diffusion reconstruction, GAN inversion) | ranked above L0 and below L3 (policy O), or treated as L0 (policy A) |
| L2 | one-person mixes: mirror self-morph, same-person morph, same-person latent mix | ranked above L0, below L3; no label |
| L3 | two-person morph, in any storage state | label 1; ranked above everything of the same host |

Pools:

1. **SMDD ladder.** The rebuild of the SMDD audit (SM1): 25,000 genuine renders, about 15,000
   rebuilt morphs with balanced partners (each render a partner at most twice), both warped halves of
   every pair, shrunk copies of renders, halves and morphs through the registered call
   (`/mnt/t7/smad_next/SM1/`, arms c, d, e; building). To add on CPU: mirror self-morphs and mirror
   warp-only images of the renders (the landmark ladder's `variants.py`, unchanged).
2. **Camera-photo ladder.** The 663 colorFERET and FRGC persons of the alpha-field probe (AF0; 530 for
   training, 133 kept as the development pool for the threshold), who
   are disjoint from the landmark ladder's (AR1) 536 hosts and from FRLL: 715 photos, 1,000 or more
   uniform two-person morphs, 1,000 warp-only images, 3,120 warped halves, softened copies at the two
   registered strengths 112.7 and 61.2 pixels (`/mnt/t7/smad_next/AF0/img`, `img/soft`). To add on CPU:
   FaceMorpher morphs and warp-only images for the same pairs, mirror self-morphs, same-person morphs
   where a second photo exists, and splice morphs with the approved Poisson script if the author
   allows it on new pairs (section 8). Larger option: also the persons of the earlier training arms
   (62,112 existing landmark morphs), after removing a fixed list of 200 landmark-ladder hosts kept as
   the test ladder.
3. **Camera photos only.** 10,000 FFHQ photos, disjoint from the 2,000 FFHQ test photos, each in
   three storage states. They carry only the equality term and label 0.
4. **Diffusion ladder.** The pinned diffusion autoencoder run unchanged on pool 2 photos, on 6,000
   SMDD renders and on 2,000 FFHQ photos: reconstruction (L1), mix with the mirror image or a second
   photo (L2), two-person mix (L3), 20 decoding steps, a 100-step subset. The Athena generation
   experiment (DG1) keeps its sets as tests: its set B uses the landmark-ladder hosts, so it must not
   enter training (section 9, observation 4).
5. **GAN ladder.** The existing StyleGAN2 inversion and the MIPGAN-style code of the MIPGAN controls
   (AG1), run unchanged on SMDD renders and pool 2 photos: one-photo output (L1), mirror or
   same-person mix (L2), latent-mean and optimised two-person morphs (L3). Optional; enters at wave 2.

Storage crossing: every image of pools 1 to 5 exists in its native state and in the registered shrunk
states. Pairs are formed inside a storage state and across states, in both directions. A morph stored
small against a native genuine image is the benchmark situation. A native morph against a genuine
image stored small is the control situation. Both are in every batch.

Batch: host groups. Each group is one host with eight views drawn from its rungs and storage states.
Sampling shares: half landmark groups (SMDD and camera photos one to one), a fifth diffusion, 15% GAN,
15% camera-only groups. Class weight keeps L0 and L3 balanced.

### 3.6 Objective

With z the logit:

- Label term: binary cross-entropy on L0 (label 0) and L3 (label 1). L1 and L2 carry no label.
- Equality term: for every pair of L0 views of the same host, the squared difference of their logits.
  Weight 1.0. This says: storage, warp and softness must not move the score.
- Order term: for every pair of the same host with a lower and a higher level,
  softplus(m − (z_high − z_low)). Margins in logits: 4 for L0 to L3; 2 for L0 to L1, L0 to L2 and L1
  to L3; 1 for L2 to L3. Weight 0.5.

Two policies for one-photo generator output, to be decided by the author's class ruling:
- **Policy O (ordered).** L1 sits between L0 and L3 as above. The score rises along the ladder. Native
  generator cells then count both steps: re-synthesis and mixing.
- **Policy A (genuine).** L1 is treated as L0: label 0 and tied to its host photo. The network may not
  use re-synthesis at all. It can only read mixing.

Both are trained (wave 1). I recommend policy O if the three-category proposal is accepted: flags on
one-photo output are then reported in their own table and are no error. Policy A is the fallback and
the stricter row. In both, SMDD renders stay L0, as in the standard protocol.

### 3.7 Schedule

The registered recipe: AdamW, constant learning rates 3.33e-6 (LoRA) and 3.33e-5 (head), weight decay
0.05, gradient clip 5, flip augmentation, 6,250 steps at an effective batch of 256 (32 with 8
accumulation steps on ViT-L/14), last checkpoint, no selection, seeds 401 to 405. One extra arm with
12,500 steps, because the data are four to five times larger than SMDD. Cost per fit on one A100:
about 3 hours plus scoring for ViT-L/14 (the task folders' estimate, not measured); 0.87 hours for
ViT-B/16 (measured, AD4 README section 5.5).

### 3.8 Evaluation protocol with one fixed threshold

- **Threshold.** One per network, fixed before any benchmark image is scored: the smallest threshold
  that keeps false alarms at or below 5% on every development genuine pool. Development pools: the 133
  validation persons of the alpha-field probe (photos, warp-only, halves, softened copies), 5,000 SMDD
  evaluation-split renders and their shrunk copies, 2,000 FFHQ development photos in three storage
  states. No FRLL, FEI or benchmark image.
- **Published-table view.** EER per cell on the raw benchmark files through the pipeline of 3.3:
  FRLL-Morphs (5), corrected MAD22 (5), MorDIFF, six DiM families. Genuine class as published (204)
  and neutral-only (102). Baselines through their own preprocessing, labelled reproduced or not (RS1).
- **Fixed-threshold view.** Miss rate per family and false alarms per genuine pool at the threshold:
  unprocessed FRLL, every history-matched pool, stored-small photos, the existing JPEG and blur
  variants, FEI, FFHQ test photos. Headline number: family-mean miss rate with all pools protected.
  Bar: 63 to 87% for current detectors (EV1 item 4).
- **Ladder view.** On the landmark ladder (AR1, 536 hosts never in training), the FRLL clean ladder
  (102 persons, neutral only) and a new FEI ladder (200 persons, CPU build with the approved engines):
  AUC of each step and flag rate of each rung at the threshold.
- **Generator ladders.** The diffusion sets of DG1 and of the earlier MorDIFF controls (A43), the 64
  GAN blocks, the MIPGAN controls (AG1): one-photo output against two-person morph, and camera photo
  against one-photo output, under both class policies.
- **Single-subject table.** Where warp-only images, mirror self-morphs, same-person morphs and
  one-photo generator outputs fall at the threshold. For every detector, ours included.
- **Reference rows, same recipe and pipeline, five seeds each.** A network trained on storage history
  only (renders and photos against their shrunk copies); a network trained on re-synthesis only
  (reconstructions against camera photos, storage crossed, no morph); a label-permuted network. A cell
  where a reference row is within 10 points of ours is marked "solvable without morphs".
- **Intervals.** Person bootstrap over the 102 FRLL persons and over FEI persons; mean and range over
  the five seeds. The reported network is the mean over seeds of single-network results; no seed is
  picked and no scores are averaged across seeds.

### 3.9 Expected benchmark numbers (expectations, not measurements)

Camera-photo protocol, 224, policy O. In brackets where policy A differs.

| Cell | Best published | Expected native EER % | Reasoning |
|---|---|---|---|
| FRLL-Morphs FaceMorpher, OpenCV | 0.00; 0.00 | 0.3 to 1.0 | tools seen in training; robust recipe already at 0.3 to 0.4; a tie with 0.00 inside the interval of 204 photos |
| FRLL-Morphs WebMorph | 3.42 | 3 to 6 | ViT-L/14 release holds at 4.4 under history matching; splice morphs in training should help |
| FRLL-Morphs AMSL | 0.99 | 8 to 14 | history-robust detectors sit at 14 to 15; no route to 1% without the cue |
| FRLL-Morphs StyleGAN2 | 8.99 | 3 to 10 [25 to 40] | re-synthesis step plus mixing [mixing only, AUC about 0.75] |
| MAD22 FaceMorpher | 0.00 | 0.2 to 0.8 | gross artefacts; robust recipe 0.5 under matching |
| MAD22 OpenCV | 2.23 | 1.5 to 4 | same tool as our engine; the earlier paper draft reached 1.35 with FRGC morphs (old MAD22 subset, a cue-prone network, not in this repository's record) |
| MAD22 Webmorph | 10.80 | 6 to 11 | robust recipe 15.8 on SMDD only; camera-photo morphs were the lever before |
| MAD22 MIPGAN-I, II | 16.70; 9.06 | 1 to 6 [25 to 45] | as StyleGAN2; transfer from our generators to MIPGAN files not shown |
| MAD22 five-cell mean | 6.12 | 2.5 to 5.5 [12 to 20] | arithmetic on the rows above |
| MorDIFF | 0.00 | 0.5 to 3 [2 to 8] | mixing readable at 0.95 to 1.00 from frozen features (unreviewed); re-synthesis adds under policy O |
| Greedy-DiM | 7.60 | 2 to 8 [5 to 15] | same generator family as our diffusion ladder; optimised morphs may transfer less |
| Family-mean miss, all pools protected | 63 to 87 | 10 to 25 | the main gain |

Plain statement for the paper. With policy O the network can be state of the art on the corrected
MAD22 (mean and four of five cells), on FRLL-Morphs FaceMorpher, OpenCV and probably WebMorph, and
close on MorDIFF. It will not match AMSL at 1 to 4% or the FRLL-Morphs five-cell mean of 1.85%. With
policy A it loses the GAN cells too. Both gaps are the cells where section 1 shows the published level
is reachable without detecting a morph.

### 3.10 Ladder results it must show (pass marks)

1. Camera photo against the same photo with storage history: folded AUC at most 0.60 (upper bound at
   most 0.65) on every registered pool, including the 61 to 65 pixel pools, on FRLL, FEI and FFHQ.
   Median paired logit shift at most 0.3 standard deviations. False alarms at the threshold at most 10%.
2. Camera photo against warp-only, and halves against softened halves: the same three marks.
3. Warp-only against two-person morph on hosts never trained on: AUC at least 0.97 with both in
   native state, at least 0.95 with both softened, and at least 0.05 above the best simple statistic
   on the same images (lower bound above 0).
4. Same-person morph against two-person morph at least 0.70; mirror self-morph against two-person
   morph at least 0.65. Descriptive, not a gate for the benchmark claim.
5. Diffusion: one-photo reconstruction against two-person morph at least 0.90 on FRLL at 20 and 100
   steps; published MorDIFF against FRLL reconstructions at least 0.85.
6. GAN: one-photo output against two-person morph at least 0.75 on held-out blocks; the spread-matched
   contrast is printed, no mark.
7. Dose: the score rises with the mixing fraction on the graded set (Page trend test).
8. Left-out constructions (trained without them, tested on them): one storage strength (61.2), one
   engine (Poisson or FaceMorpher), one generator family. Marks 1 to 3 relaxed by 0.05 AUC and 5 points.
   Without this block, passing a ladder we trained on is circular.

### 3.11 Ablation table (five seeds per row, ViT-L/14, same steps)

| Row | Change | What it proves |
|---|---|---|
| B0 | MADation recipe on the released SMDD, pipeline of 3.3 | reference; must sit near the release |
| B1 | rebuilt SMDD, balanced partners, same counts | whether the five-partner structure matters |
| B2 | + warped halves and mirror warp-only as genuine | warp and blend softness stop separating the classes |
| B3 | + storage crossing in both classes | the storage reaction goes |
| B4 | + ladder loss (equality and order terms) | the loss adds over the data protocol |
| B5 | + camera-photo ladder | gain on MAD22 OpenCV and Webmorph |
| B6 | + diffusion ladder, policy O; B6A the same with policy A | mixing step on diffusion; price of policy A |
| B7 | + GAN ladder | mixing step on GAN |
| C1 to C6 | full minus one: loss; halves; storage crossing; camera photos; generator ladders; softened morphs | each ingredient is needed |
| D1 to D3 | left-out strength, engine, generator family | not circular |
| E1 to E3 | LoRA rank 8; 336 pixels; 12,500 steps | capacity and input size |
| F1 to F3 | history-only, re-synthesis-only, label-permuted networks | which cells are solvable without morphs |

Columns for every row: mean EER of the seven landmark cells, native and history-matched; mean of the
seven diffusion cells; the three GAN cells; family-mean miss at the threshold; worst false-alarm rate
over nuisance pools; the six step AUCs of 3.10.

### 3.12 First test, one day, existing data, CPU after the feature queue ends

- Data: the alpha-field probe's (AF0) CLIP ViT-L/14 caches at 224, `/mnt/t7/smad_next/AF0/feat/clip224/`
  (lists `af0_w1`, `af0_w2`, `af0_h` halves, `soft`, `ar1`, `ar1soft`, `bench_s`); the landmark
  ladder's images and softened copies. Missing: softened copies of 200 landmark-ladder two-person
  morphs (800 images through the verified `src/AF0/soften.py`, minutes).
- Heads on mean-pooled tokens, trained on the 530 training persons of the probe, five seeds, three
  arms: (i) label term, photos against morphs; (ii) label term with halves, warp-only and softened
  copies as genuine; (iii) arm ii plus the equality and order terms.
- Read on the landmark ladder (536 unseen hosts) and on FRLL: warp-only against two-person morph,
  native and softened, with the simple-statistic floor; paired logit shift from photo to stored photo;
  false alarms on every FRLL history-matched pool at the development threshold; native and matched EER
  on the FRLL-Morphs and corrected MAD22 landmark cells of `bench_s`.

Kill and pass numbers:
- Dead for landmark morphs at 224 if, in arm ii or iii, softened warp-only against softened two-person
  morph is below 0.90, or the excess over the best simple statistic has a lower bound at or below 0.
  Then the signal in these features is softness; go to recipe 2, where softness at a fixed size is
  evidence.
- The loss is dropped (the data protocol stays) if arm iii neither halves the paired shift of arm ii
  nor adds 0.02 AUC on softened pairs.
- Pass: arm iii keeps warp-only against morph at 0.95 or more native and 0.90 or more softened, shift
  at most 0.3 standard deviations, false alarms at most 10% on every history-matched pool, and EER at
  most 5% on FRLL-Morphs FaceMorpher and OpenCV against history-matched genuine photos.

### 3.13 Three days on many A100 cards

One fit is one GPU; waves are Slurm arrays. GPU-hours include scoring.

| Wave | When | Runs | GPU-hours | Decided afterwards |
|---|---|---|---|---|
| 0 inputs and first tests | night 11 to 12 Nov | crops of all pools (6); features at 224 and at five smaller sizes (4); diffusion ladder generation, about 8,700 encodes and 30,000 decodes (18); GAN ladder (15); reference row B0, 5 ViT-L/14 and 5 ViT-B/16 fits (24); the three frozen first tests (5) | about 75 | keep or drop the loss; is there a usable small size (recipe 2); does mixing transfer between pools |
| 1 screening on ViT-B/16 | 12 Nov, day | 24 configurations × 3 seeds: protocol (SMDD-Ladder, camera photos) × size (224, small) × loss (label only, + equality, + equality and order) × policy (A, O) | about 86 | which configurations pass the marks of 3.10 on development pools; loss weights; policy |
| 2 confirmation on ViT-L/14 | night 12 to 13 Nov | 6 configurations × 5 seeds (105); 336-pixel arm, 5 seeds (40) | about 145 | ONE configuration is frozen and written into the registration before any benchmark score is read |
| 3 ablations and controls | 13 Nov | rows B1 to B7, B6A and C1 to C6, 14 rows × 5 seeds (about 245); D1 to D3 (53); F1 to F3 (53); E1, E3 (35); the row of the other protocol (18) | about 405 | the ablation table; which cells are marked solvable without morphs |
| 4 final | 14 Nov | frozen configuration, 10 seeds (35); benchmark scoring of all rows, once (30); released detectors through their own pipelines (5); reserve for reruns (50) | about 120 | tables frozen |

Total about 830 A100-hours; with slack 1,500 of 30,000. Peak 72 cards in wave 1. If Athena stays
closed: two rented A100 machines run wave 1 with 8 configurations × 2 seeds on ViT-B/16 (about 20
hours) and wave 2 with 2 configurations × 3 seeds.

### 3.14 Risks

- The loss needs a group sampler and a pair term in the training script (about 150 lines behind a
  flag). It must be tested on 8 images first. If it slips, rows B0 to B3 and B5 still give a network.
- The equality term may collapse the score range. Guard: the order term and the label term; watch the
  development AUC, not only the shift.
- Only two registered storage strengths exist for camera photos. Invariance may hold only at those.
  Row D1 measures it; recipe 2 removes the question.
- JPEG is not covered. No allowed operation equalises it. The existing JPEG variants give the false
  alarm number; if it is high, that is a stated limit.

---

## 4. Recipe 2 (rank 2): the canonical-band network

### 4.1 Idea

Train and test the same network at one fixed, small input size S, chosen so that a face crop reaches
the network at about the inter-eye distance of the smallest benchmark files and of SMDD (about 63
pixels). With the estimate of section 2.2 that is S near 150: 154 (11 patches) or 140 (10 patches). The loader
reduces every larger crop to S with its existing bilinear resize, which averages when it shrinks.
Storage history above that size is then not in the input. No image is treated differently from any
other: one size for all, no measurement of the image, no gate.

Two forms, both from existing code: (a) the loader's size flag set to S and CLIP's position
embeddings interpolated by the model library; (b) the loader resize applied twice, to S and back to
224, to keep the pretrained token grid. The first test compares them.

### 4.2 What changes in the claims

- "No reaction to storage history" holds by construction for every history of about 63 pixels or
  more, including strengths and resampling kernels never used in training. It becomes a property of
  the input, shown with a probe that tries to read history and fails.
- Softness changes its meaning. At a fixed size every admissible genuine image has the same
  sharpness. A loss of mid-band detail can then come only from blending, or from real blur in the
  photo. So the softness floor of round 2 stops being a confound and becomes part of the evidence.
  The false alarm to measure is real blur: the existing blur variants of the FRLL genuine photos.
- SMDD is used at its native size (2.1). No enlargement in training.
- The three small-storage cells are scored at their own size. Larger morph files lose the detail
  between about 63 and 95 pixels. That is the price, and the first test measures it.
- Images stored below about 60 pixels between the eyes look soft and may be flagged. No benchmark
  family is below that; the 80-pixel SMDD copies are (about 20 pixels). This limit is stated.

### 4.3 What is new

Round 1 had "one network at the common Nyquist" from the physics lens, with the stated obstacle that a
downscale step collides with the rule against new resampling code. Here the step is the existing
loader resize at another fixed size; the size is tied to a measured fact (SMDD and the small-storage
families at 61 to 65 pixels); and the softness argument is turned around.

### 4.4 Recipe

Backbone, data, loss, schedule and evaluation as in recipe 1, with the size S in place of 224 at
training and test. Storage crossing stays in training (it is cheap and covers the 61 to 65 pixel pools,
which sit at the edge of the band). One extra arm has no storage crossing at all: if photo against
stored photo is at chance there too, the guarantee comes from the input alone.

### 4.5 First test, one day, existing crops, about 0.5 GPU-hour

- Data: existing crops only. The landmark ladder's crops (`/mnt/t7/smad_next/AR1/crops/main`, 18,239);
  the own-crop re-score's crops of FRLL photos, of every history-matched pool, of the JPEG, blur and
  half-size variants, and of the earlier corrective crops of the benchmark morphs
  (`/mnt/t7/smad_next/RS1/crops/`, `/mnt/t7/smad_heldout/a46_corrective_20261108/rgb_clip/`).
- Features: frozen CLIP ViT-L/14, mean-pooled tokens, at S = 224, 182, 154, 140, 126, 112, forms (a)
  and (b).
- Head 1, history probe: logistic regression that tries to tell a photo from its stored copy, per
  pool, five folds by person. Head 2, morph head: warp-only against two-person morph, trained on one
  tool and tested on the other, as the clean-negative test (CN0).
- Read per S: probe AUC per pool; morph-head AUC on the held-out tool; the morph head's EER on MAD22
  FaceMorpher, MorDIFF and FRLL-Morphs OpenCV against history-matched genuine photos; its flag rate on
  blurred genuine photos.

Kill and pass numbers:
- Dead if no S has probe AUC at most 0.60 on every pool together with morph-head AUC at least 0.95.
- Dead as the main network if, at the best S, the morph-head AUC is more than 0.03 below its value at
  224, or more than 20% of blurred genuine photos are flagged.
- Pass: such an S exists. S* is the largest one. Then the ViT-B/16 screening of wave 1 carries the
  size as a factor.

### 4.6 Expected numbers, ladder marks, ablations, compute

- Expected against recipe 1: equal on MAD22 FaceMorpher, MorDIFF and DiM; 0 to 2 points worse on
  FRLL-Morphs FaceMorpher, OpenCV and WebMorph; 1 to 3 points worse on MAD22 OpenCV and Webmorph (say
  2 to 6 and 8 to 13); AMSL unchanged at 8 to 15. False alarms on history-matched pools at the nominal
  5% without relying on training.
- Ladder marks: as 3.10, with mark 1 required also for the arm without storage crossing and for the
  history probe (at most 0.60).
- Ablation rows on top of recipe 1's table: size S against 224; with and without storage crossing;
  form (a) against (b).
- Compute: a ViT-L/14 fit at 154 pixels has about half the tokens, so about 1.7 GPU-hours. First
  test 0.5; size sweep on ViT-B/16, 5 sizes × 3 seeds, 12; inside waves 1 and 2 it is one factor (no
  extra wave); full ablation rows about 60. Total about 75 beyond recipe 1.

### 4.7 Risks

- CLIP at 154 pixels is off its pretraining size; accuracy may drop more than the lost band explains.
  Form (b) is the hedge.
- The 61 to 65 pixel pools sit at the edge of the band; a double resize can leave a small trace. The
  probe measures it; S = 126 or 112 is the fallback.
- "Softness is evidence at a fixed size" will be attacked with beauty filters and defocus. Print the
  blur false-alarm rate and say what it means.
- Needs the author's word that another value of the existing size flag is inside the image rules.

---

## 5. Recipe 3 (rank 3): the SMDD-Ladder protocol

### 5.1 Idea

Train the network of recipe 1 only on images derived from the SMDD training split and public
generators. Item 1 of the brief rebuilds SMDD's landmark morphs. This recipe extends the rebuild to a
full three-family ladder, so that the SMDD-only network also gets one-person rungs and generator rungs,
and it makes the result a training set we can release.

### 5.2 The set (all hosts are SMDD training-split renders)

| Family | L0 | L1 | L2 | L3 |
|---|---|---|---|---|
| Landmark (approved engine at 256 pixels) | render; warped halves; mirror warp-only | — | mirror self-morph | rebuilt morph, balanced partners |
| Diffusion autoencoder (pinned, unchanged; it was trained at this size and framing) | render | reconstruction | mix with the mirror image | two-render mix |
| GAN (existing StyleGAN2 inversion and MIPGAN-style code, unchanged) | render | inversion output | mix with the mirror code | latent-mean and optimised morph |

Storage states: native and the registered shrunk copy. Counts: 25,000 hosts for the landmark family;
6,000 to 25,000 for the generator families. SMDD has one image per identity, so the one-person rung
is the mirror image. Unreviewed lead behind that choice: in the diffusion autoencoder's semantic code a
mirrored photo is as far from the photo as a second photo of the same person (0.776 against 0.773;
another person 1.744; four persons; identical-and-mirrored-inputs check (AD1b)).

### 5.3 What it gives the paper

- The comparable row. Every published row trained on SMDD. A reviewer of the field will ask for ours
  on the same source. SelfMAD is the precedent for building one's own attacks from SMDD renders.
- A clean test bed. No camera photo is ever trained on, so every camera-photo ladder (all 536
  landmark-ladder hosts, FRLL, FEI) and every benchmark is an unseen source. The objection "you
  trained on the ladder and passed the ladder" loses most of its force.
- A released set. SMDD's terms ask that derived morphs are published and shared; the author accepted.
- A natural fit with recipe 2: at the small size SMDD is used without enlargement.

### 5.4 Expected numbers (expectations)

Policy O at 224, in brackets policy A: FRLL-Morphs FaceMorpher and OpenCV 0.5 to 2; WebMorph 5 to 9;
AMSL 10 to 16; MAD22 FaceMorpher 0.3 to 1, OpenCV 5 to 9, Webmorph 12 to 17; MorDIFF 1 to 5 [3 to
10]; GAN cells 2 to 8 [25 to 45]. So: at or above the published MADation level on most cells with the
storage control passed, but not the best number on MAD22 OpenCV (2.23) or FRLL-Morphs WebMorph (3.42).
The camera-photo protocol of recipe 1 is the row for the best numbers; this is the row for
comparability. If the two rows are within 2 points on the clean cells, this one becomes the headline.

### 5.5 First test, one day

The landmark half of this recipe is already under test: the rebuild arms of the SMDD audit (SM1,
part 3) on frozen features. The new half is the generator rungs. Its decisive question: does a mixing
head trained on renders transfer to camera photos?

- Zero-generation proxy on existing data: train a head on the existing diffusion blocks of colorFERET
  and FRGC persons (`/mnt/t7/smad_research/diffae-expanded123-v1/run/`, 102 complete blocks:
  reconstructions, same-person mixes, two-person morphs) and test it on the FRLL arms of the earlier
  MorDIFF controls (features in `/mnt/t7/smad_next/FZ1/`): two-person morph against reconstruction at
  20 steps, and published MorDIFF against reconstructions. This tests transfer between pools.
- The render-to-photo test needs about 1 GPU-hour of new generation from existing renders: the
  diffusion autoencoder on 600 SMDD renders (reconstruction, mirror mix, 300 two-render mixes, 20
  steps), then a head on frozen CLIP ViT-L/14 features, tested on the same FRLL arms.
- Metric: AUC of two-person morph against reconstruction on FRLL at 20 steps, person bootstrap; AUC of
  reconstruction against camera photo for the same head.

Kill and pass numbers: the generator rungs are dropped from this protocol if the render-trained head
is below 0.80 on FRLL (the in-pool probe is at 0.987, unreviewed), or if the proxy is below 0.85. Under
policy A the head must also leave reconstruction against camera photo at or below 0.65. Pass: 0.90 or
more; then generate the full set.

### 5.6 Ladder marks, ablations, compute

- Ladder marks as 3.10, all on unseen sources.
- Ablation rows: B0 to B4 of recipe 1 are this protocol's landmark rows; add "+ diffusion rungs",
  "+ GAN rungs", "mirror rung removed".
- Compute: generation 40 to 60 GPU-hours (encodes of 6,000 to 25,000 renders at an estimated 5 seconds
  each on an A100, to be measured; decodes; GAN ladder); five-seed rows at two sizes 35; extra ablation
  rows about 55. Total about 150. Crops and morph builds stay on CPU machines, not on Athena.

### 5.7 Risks

- Renders to camera photos is a real domain step; the mixing head may not carry over.
- The mirror rung is a symmetric face. It must never be the only one-person rung a head can separate
  by symmetry; the warped halves and reconstructions keep it honest.
- 256-pixel sources hold no fine detail; MAD22 OpenCV and Webmorph will lag the camera-photo protocol.
- The origin of the SMDD morph-source folders on disk is not recorded (SM1 README); use the 25,000
  genuine renders as hosts unless that is cleared.

---

## 6. How the three combine, and the decision tree

The recipes are three switches on one training script: loss (ladder terms on or off), size (224 or
S*), protocol (SMDD-Ladder or with camera photos). Wave 1 screens the grid on ViT-B/16.

1. After the frozen first tests: if the loss adds nothing, keep the data protocol and drop the loss.
   If softened pairs fall below 0.90 at 224, recipe 2 becomes the main line.
2. After wave 1, development pools only: among configurations that pass the marks of 3.10, take the
   one with the lowest family-mean miss at the threshold. Ties go to the SMDD-Ladder protocol, then to
   224.
3. After wave 2: freeze one configuration. The other protocol is trained once more as a labelled row.
4. If no LoRA configuration passes the storage marks: the paper's network is the frozen encoder with
   the ladder-trained head from the first tests, like the frozen-encoder MADation variant. Its numbers
   will be lower on WebMorph and AMSL; its controls can be exhaustive because heads train in minutes.

---

## 7. Alternatives I rejected, and why

- **DINOv3 ViT-L/16 at 512 with a dense blend map as the main network.** At 512 the 112 to 254 pixel
  storage histories become visible again, and so do JPEG and chroma differences in the high-resolution
  cells, which no allowed operation can equalise. The first pass of the alpha-field probe (AF0) fails
  its warp-only limit (0.73 against 0.3 standard deviations). Keep the map as an optional auxiliary
  head, only if its controls pass.
- **A dense target in feature space** (token displacement between a morph and its own half, zero for
  any one-capture image in the same storage state). I like it as the next upgrade of the map, because
  crossing storage makes softness useless for predicting it. Three days are too short to make it the
  headline. One optional row in wave 3.
- **Two declared outputs** (morph evidence, re-synthesis evidence). The record says a second head hurt
  the first; taking the larger of two outputs reads as fusion. Policy O gives one ordered score.
- **Training one-photo generator output as an attack.** It makes a generated-image detector and
  contradicts SMDD, whose genuine class is renders.
- **Projection of history directions out of the features.** Linear only; the record found the cue
  still decodable after normalisation. The equality term does the same job inside the fit.
- **Storage normalisation by the registered shrink call with a per-image scale.** It needs the
  inter-eye distance of every test image and enlarges images below the target. A fixed loader size
  needs neither.
- **Identity shrinkage and left-right asymmetry as signals.** Measured weak: 0.725 on exact landmark
  shapes (identity-shrinkage triage (ID0)); mirror distance 0.60 to 0.71 for photo or warp-only
  against two-person morph on the landmark ladder and 0.50 to 0.59 (folded) on FRLL
  (`experiments/AF0/mirror_clip224.json`, first block, unreviewed).
- **MambaVision or the earlier Mamba network as the backbone.** No evidence of an advantage; the
  earlier from-scratch networks learned border and frequency cues. One arm in wave 3 if cards idle.
- **JPEG augmentation, flip averaging at test, checkpoint or seed selection.** Outside the rules.

---

## 8. Decisions needed from the author

1. Class ruling for one-photo generator output: is a single ordered score (policy O) acceptable, with
   flags on such images printed in their own table? Otherwise policy A is the headline.
2. Is another fixed value of the existing loader size flag, the same for every image, inside the
   image rules (recipe 2)?
3. May the approved Poisson build script be run unchanged on new colorFERET and FRGC pairs (splice
   morphs for the WebMorph and AMSL cells)?
4. Which row is the headline if both pass: SMDD-Ladder only (comparable) or with camera photos (best
   numbers)?

---

## 9. Observations for the lead

1. SMDD's median inter-eye distance is 63.65 pixels (my measurement, 2.1). The small-storage families
   are at 61 to 65. This may explain why exactly those histories move SMDD-trained detectors. A
   reviewer should check the point indices.
2. The robust recipe is at 0.3% on FRLL-Morphs OpenCV and at 8.6% on MAD22 OpenCV, same tool, same
   persons. History matching leaves our aligner's border in place. "CLIP rows hold on landmark cells"
   needs the own-crop re-score (RS1) before it is printed.
3. History matching does not equalise compression. AMSL is separated perfectly by JPEG quality, and no
   allowed operation can test the morph side. The genuine-side JPEG variants are the only control.
4. The Athena diffusion set B (DG1) is built on the landmark ladder's 536 hosts. If it is used for
   training, the landmark ladder is no longer person-held-out for our network. Decide now which is
   training and which is test.
5. The clean-negative test (CN0) has no simple-statistic floor (empty cue list), so its "mixed"
   verdict comes from a missing number, not from a result.
6. Our SMDD-only ViT-L/14 retrains reach 0.8% on MAD22 MIPGAN-I where the release publishes 20.32%.
   GAN-cell numbers depend heavily on the pipeline; no control explains the gap yet.
7. The morph-free networks experiment (AD4) scores with flip averaging; the releases are read without
   it. Under "no fusion of scores" the headline should be without it, for every row.
8. The softened evaluation copies of the landmark ladder cover photos and warp-only images, not the
   two-person morphs. Without softened morphs the softness control has only one side.

---

## 10. Not verified

- The inter-eye distance at 224 after the face crop (about 95 pixels is an estimate), and the crop
  width of SMDD renders (about 146 pixels is an estimate).
- That points 38 and 88 of the 106-point layout are the eye centres.
- That the training script accepts other sizes for CLIP, and that the Poisson script runs on new
  pairs; that the StyleGAN2 inversion code runs on Athena; A100 timings of every generator.
- The fit time of ViT-L/14 on an A100 (3 hours is the task folders' estimate).
- The 90-pixel passport minimum (quoted by a reviewer in our record, clause not read).
- That the AMSL files in FRLL-Morphs keep the strong compression of the original AMSL set (memory).
- FD-MAD's per-cell values; only its averages are in our record.
- Prior-work statements in 3.2 are from memory.
- Every expected number in sections 3.9, 4.6 and 5.4 is my estimate.
- All numbers marked unreviewed: CN0, paired differences (PD1), frozen features (FZ1), AD1b, the
  mirror distance, and my SMDD measurement.
