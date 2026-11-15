# IDEAS v1: how to get a shortcut-free detector that is also state of the art

Research strategist's note, 11 Nov 2026 (evening). Thinking only: nothing was run, scored or generated
for this page. Read-only on everything except this folder. No sealed file was opened.

How to read this page

- S-MAD = single-image morphing attack detection (one face image in, "morph or genuine" out).
- AUC = area under the ROC curve (0.5 is chance). EER = equal error rate in percent (50 is chance).
- BPCER = share of genuine images wrongly rejected. APCER = share of morphs wrongly accepted.
- FR = face recognition. CLIP and DINOv3 = large pretrained image encoders. LoRA = low-rank adaptation,
  a light way to fine-tune them. SMDD = the standard synthetic training set (25,000 genuine renders,
  15,000 landmark morphs). MAD22 = SYN-MAD 2022 benchmark (corrected copy only). FRLL = Face Research
  Lab London photos (102 persons), the genuine class of every benchmark we use.
- Rungs (from `11_AUDIT_PLAN.md`): R0 camera photo, R1 camera photo with matched history (E7 = the
  approved shrink-and-enlarge control), R2 the tool run on one photo, R3 the tool run on two photos of
  one person, R4 the tool run on photos of two persons.
- Citation marks. "Checked (helper)" = a literature helper I ran opened the arXiv or abstract page
  in this session; it read abstracts, not full PDFs. "Checked in the literature file" = marked checked
  in `03_LITERATURE_AND_METHODS.md`, not re-opened today. "Snippet" = seen only in search-result text.
  "Memory" = cited from memory. Everything except the first kind must be verified before it goes into
  the paper. I opened no paper page myself.
- "Not verified" = I could not confirm it in the record.
- New words used here. Pass-through = the morphing tool run on one photo with itself (this is R2).
  Mirror self-morph = the tool run on a photo and its own left-right mirror image. Genuine orbit = all
  processed copies of one genuine photo (R0, R1, pass-through, mirror self-morph and similar).
  Pooled-genuine error = error when every member of the genuine orbit counts as genuine under one
  threshold.

Disclosure. I wrote my list before opening `ideas/SEEDS_main.md` (the lead's own seeds). I read it
afterwards. Where my ideas overlap with it I say so, and section C ends with a critique of its main
idea (alpha-field supervision), because the two sets fit together.

---

## 0. The argument of this page in ten lines

1. A morph differs from a processed genuine photo in three ways only. (a) Superposition: two different
   photographs are present at half contrast each. (b) Averaging of photo-specific detail: noise, pores,
   lighting and pose detail lose half their power. (c) Averaging of identity: the face moves toward the
   mean face by a factor of about 0.71 for unrelated persons and 0.87 for look-alikes.
2. Landmark morphs have all three. Same-person morphs (R3) have (a) and (b) but not (c). Morphs made
   by a generator from an averaged code have only (c), because the generator renders one coherent
   image from one code.
3. (b) can be imitated by any smoothing of one photo. This is why every detector trained on "untouched
   photo against morph" turned into a detector of processing history.
4. The current plan's genuine class (the tool run on one photo with itself) is an identity operation.
   It has none of (a), (b), (c) and none of the smoothing either. So the planned contrast still lets a
   network solve the task with (b), and (b) is the imitable one. This is the strongest objection (B1).
5. For generator morphs the image depends on the two contributors only through the averaged code. By
   the data-processing inequality no detector can find a second identity beyond "this face is more
   average". Where the interpolation keeps the code's length (re-normalised embeddings), even that is
   gone. The record already agrees: the re-normalised set H2 sits at 0.47 to 0.53 for every scored
   network (with the caveat that its morphs have low attack potency), and the linear StyleGAN3 set is
   readable at 0.91 by a probe that turns out to read averageness only. The Arc2Face set is the second
   test of this; its scores and whether its mixed embedding was re-normalised are not verified.
6. So the paper should claim what is true: a detector of superposition for landmark morphs that does
   not react to one-photo processing, a measured ceiling for generator morphs, and an audit that shows
   released detectors read neither.
7. To get there: put hard one-photo negatives in the genuine class (mirror self-morph, pass-through,
   history-matched copies), rebuild the standard training set so that both classes pass the tool, use a
   score that cancels mirror-symmetric cues by construction (left-right asymmetry), and report one
   pooled-genuine operating point for every detector.
8. All first tests run on frozen features of images that already exist under `/mnt/t7/smad_next/AR1`
   and `/mnt/t7/smad_heldout`. Each takes minutes.
9. The lead's alpha-field idea and these negatives are complements: the field blocks image-constant
   cues during training, the one-photo negatives block local smoothing cues that the field itself
   creates.
10. What to stop: large generator twin sets, the two-identity embedding head, SelfMAD retrains, the
    three-backbone matrix.

---

## A. What "state of the art and shortcut-free" should mean

### A.1 One table, three columns per cell

For every detector and every benchmark cell, print three numbers side by side. Same morphs in all
three; only the genuine class changes.

| Column | Genuine class | What it answers |
|---|---|---|
| Native | the benchmark's own camera photos (R0) | the number everyone publishes |
| Equalised | the same photos given the morphs' history: existing E7 output, then pass-through; the morphs also get the pass-through (idea E4) | what is left when both classes share the last processing steps |
| Pooled genuine | all genuine constructions of the same persons under one threshold: R0, R1, pass-through, mirror self-morph, plus one construction never used in anyone's training | what an operator gets with one threshold and photos of mixed history |

Headline metric: pooled-genuine EER, and BPCER at APCER 5% and 10%, with a 95% bootstrap over persons
(the `a41_read.py` two-way method). With 102 FRLL persons an interval is about plus or minus 0.08 AUC,
so add FEI (200 persons, never used in any training, 14 photos each; usable frontal pairs not
verified) as a second test pool and report both.

### A.2 What would convince a sceptical reviewer

"State of the art" claim, landmark family (the only family where it can be earned honestly):

1. Pooled-genuine EER of our single network (five seeds, mean and range, last checkpoint) is lower
   than that of every released comparator, paired over persons, lower bound of the difference above
   zero, on both test pools and on at least one tool never used in training. Comparators: MADation
   ViT-B/16 and ViT-L/14 releases, SelfMAD release, MixFaceNet-MAD release (RGB path), SPL-MAD if
   downloaded, zero-shot MADPromptS, and the control that matters most: the same backbone and recipe
   trained on unmodified SMDD (the five M3L networks exist on disk). Methods without public weights
   appear "as reported", native column only: FD-MAD (arXiv 2601.20656: FRLL-Morphs 1.85%, MAD22 6.12%
   average EER, MorDIFF 0.00%; checked by the helper from the abstract and quoted tables), R-FLoRA,
   SRL-MAD, and the encoder study of Shahreza et al. (arXiv 2608.29802: CLIP ViT-L/14 with LoRA at
   3.7% overall error against 11.3% for SelfMAD; checked, helper). A reviewer will expect these rows;
   the pooled column cannot be filled for them and the table must say so.
2. Native EER on the seven landmark cells (corrected MAD22 FaceMorpher, OpenCV, Webmorph; FRLL AMSL,
   FaceMorpher, OpenCV, WebMorph) within 3 points of the best released detector in at least five of
   seven, or better. If this fails, the claim becomes "best under equal conditions, not best natively",
   and A.3 says how to print it.
3. On published benchmark morphs, not only on our own: equalised and pooled columns use the published
   morph files; the bridge AUC between published and our same-tool morphs must be 0.40 to 0.60.

"Shortcut-free" claim, by the same audit we apply to others:

4. Genuine-against-genuine silence. For every pair of genuine constructions of the same persons (R0
   vs R1, R0 vs pass-through, R1 vs pass-through, pass-through vs mirror self-morph, R0 vs the unseen
   construction) the detector's score separates them at folded AUC at most 0.60, upper bound at most
   0.65. Released detectors are printed beside it (today's AD1 re-read: R0 vs R2 at 0.88 to 0.996 for
   the three releases on MorDIFF).
5. Threshold transfer. With the threshold fixed at BPCER 5% on R0, BPCER on every other genuine
   construction stays at or below 10%. Today's first data point for comparison: at the benchmark
   threshold the releases flag 51% to 98% of history-matched photos.
6. Ladder shares: R0 to R2 share of the benchmark separation at most 0.2 (upper bound at most 0.3).
7. Content baselines: beats the best single low-level cue (the 26 measures of `cue_floor.stats()`),
   the 32-pixel model and the file-attribute model on the pooled column, paired lower bound above zero.
8. Dose: score rises monotonically with the mixing fraction on `fm_graded` (Page trend test), and the
   response at mixing 0 equals the response to the pass-through.
9. Leave-one-construction-out: criteria 4 and 5 hold for a genuine construction that was left out of
   training (idea E1). Without this the audit is circular (objection B3).

Generator families (GAN, diffusion): no superiority claim. Print native, equalised and pooled numbers
for every detector, the R2 vs R4 AUC, and the ceiling of idea E3. The convincing statement is: "every
released detector and ours sit within X of 0.5 on R2 vs R4; the ceiling analysis says why; the native
numbers of all detectors are explained by the construction share". State before scoring that this is
the expected result.

### A.3 How to report when the honest detector scores worse natively

- Put the morph-free network (AD4) in the table as a row. Next to each native cell print the
  "morph-attributable margin": EER of the morph-free network minus EER of the detector. A cell where
  the morph-free network is already below 10% EER is marked "solvable without morphs" and is left out
  of every average. Fix this rule before AD4 is read.
- Print the "price of honesty": native EER of ours minus native EER of the same backbone trained on
  unmodified SMDD, per cell, next to the same difference on the equalised column. The claim is that
  the first is positive and the second is zero or negative. If both are positive, we simply have a
  worse detector and must say so.
- One figure: native rank against pooled-genuine rank over all detectors (rank correlation). If it is
  near zero or negative, the figure itself is the paper's message.
- Never average native cells across families into one headline number.

---

## B. The three strongest objections to the current plan (TwinMAD)

### B1. The genuine class is too clean, so the easiest solvable signal is still "was smoothed"

The plan trains "tool on one photo" (R2) against "tool on two persons" (R4). In both landmark tools
`tool(H, H)` warps by zero displacement and averages two identical images. It returns the photo,
re-stored. (Checked in the code path of `scripts/78_tool_morph.py`; pixel identity of the R2 files to
their source not verified, a one-minute check.) R4 differs from it by real warp interpolation and by
averaging of two misaligned textures, which lowers fine detail. The record shows what networks do with
that: SMDD classes separate by one high-frequency scalar at AUC 0.99 or more (A8); the detector trained
on self-blends (SelfMAD) is the one that collapses hardest when genuine photos get a resampling
history (8.4 to 90.7); the earlier same-person arm R8 failed its guard. A twin-trained network can
pass every R2 vs R4 test and still call a denoised, resized or beautified photo a morph.

What would answer it:
- Single-cue floors on our own set: the 26 `cue_floor.stats()` measures and the 32-pixel model on
  `/mnt/t7/smad_next/AR1/img/frgcferet/{opencv,facemorpher}/{R2,R4}`. Pass: no single cue above 0.65.
- Clean-negative test (the first experiment, section D): a head trained on R2 vs R4, scored on genuine
  images it never saw as negatives. Pass: BPCER on untouched sources and on FRLL E7 photos at most
  twice the nominal 10%.
- If it fails: genuine orbit negatives (ideas D2, D3).

### B2. For GAN and diffusion morphs the plan has no mechanism, and theory says none exists beyond averageness

A generator renders one coherent image from one code. The image depends on the two contributors only
through the mixed code, so R2 vs R4 on a generator is "how average is the code", nothing more
(section C.iii). The record agrees at every point: probes read StyleGAN3 morphs at 0.91 and fall to
0.45 to 0.49 against one-person renders matched in spread (A38, A39); twin-trained heads do not
transfer between generators (0.26 to 0.63); re-normalised embedding morphs are at 0.47 to 0.53 for
every network (H2). The plan still budgets about 150 GPU-hours and two rental leases for generator
twins at scale. The best case of that spend is a per-generator averageness detector that an attacker
defeats by re-scaling the code.

What would answer it:
- The ceiling analysis (E3) run before any generator data is made. It costs CPU minutes.
- One cross-family test: does an averageness read-out fitted without any generator image (M2) score
  the existing StyleGAN3 and DiffAE morphs above their one-person renders? If yes, there is a generator
  method worth scaling. If no, the null is the result and the generation budget is freed.
- An author ruling on whether a re-synthesised genuine photo is a valid genuine image (question F1).

### B3. Scale and circularity

About 430 training persons, two tools of one family (both Delaunay warps), sources shared between
training and validation, and the audit rungs built by the same scripts as the training data. A
reviewer will say: you defined "shortcut" as what your ladder controls, trained on the ladder and
passed the ladder. Comparators were trained on 40,000 images. And 102 test persons give intervals that
turn most cells into "mixed".

What would answer it:
- The same construction on the standard training set at its full size and fixed count (D1). That
  makes "the data, not the loss" a controlled comparison against the same backbone on unmodified SMDD.
- Leave-one-construction-out for the genuine class and published benchmark morphs (AMSL, WebMorph,
  MAD22) and the Poisson set H1 as tools that share no code with ours.
- A second test pool (FEI) and a mediation analysis: the detector's R2 vs R4 AUC after its score is
  regressed on the 26 low-level cues (pass: residual AUC within 0.05 of the raw AUC).

A fourth point, smaller: under the author's ruling R3 is a morph, so the main contrast never tests
identity reading. The paper must therefore not say "reads identity blending" on the strength of the
main table; that sentence belongs to the R3 vs R4 side study only.

---

## C. Ideas

Each entry: mechanism; why it should be shortcut-free; cheapest decisive test with existing assets;
falsifier; compute; risk; closest prior work.

Shared feature cache for most tests ("F-mirror"): frozen CLIP ViT-L/14, DINOv3-L and glintr100 features
of each image and of its left-right mirror image, for: the AR1 rungs
(`/mnt/t7/smad_next/AR1/img/frgcferet/{opencv,facemorpher}/{R2,R3,R4,NC}`, 536 each, and `fm_graded`),
their sources (`AR1/src`), FRLL native and E7 photos (`eval.csv` sets with variant `resmatch`), the A43
arms (`/mnt/t7/smad_heldout/a43/data/a43/stored/{A,B20,C20,D20,E}`), `h3_sg3` and `a37_sg3ctl`,
`h1_poisson`, `arc2face`, `h2_embmid`. About 15,000 images, two views, three encoders: under one hour
on the DGX. A lossless mirror flip is not new resampling code, but see question F4.

### (i) Training-data constructions

#### D1. PM-SMDD: rebuild the standard training set with pipeline-matched genuine images

- Mechanism. Keep SMDD's 25,000 genuine renders and its pair logic, but pass every genuine image
  through the same unchanged tool that makes the morphs, and make the morphs with that tool too. Train
  the comparator's own recipe (CLIP ViT-L/14 with LoRA, the M3L recipe) on three arms of equal size:
  (a) unmodified SMDD, (b) PM-SMDD with pass-through genuine images, (c) PM-SMDD with the genuine
  orbit of D2 and D3. Nothing changes but the data construction.
- Why shortcut-free. In (b) and (c) the last processing steps are identical in both classes, and the
  renderer is the same in both classes already. It is the fixed-count test that the record lacks
  (`09_DATASET_EXTENSION_ANALYSIS.md`, section 2.4 item 6).
- Cheapest test. Landmarks, embeddings and look-alike pairs for the 25,000 renders already exist
  (`/mnt/t7/Datasety/downloads/SMDD/smdd_bona_landmarks_if106.npz`, `smdd_bona_arcface.npz`,
  `smdd_bona_lookalikes.npz`; images in `smadcvpr_data/train/smdd/os25k_bf_t`). Build on CPU with
  `78_tool_morph.py` and `96_facemorpher_tool.py`, cache CLIP features, fit a head per arm, read the
  ladder on AR1 and FRLL and the E7 rise on the FRLL cells. Whether the tools run unchanged on 256-pixel
  SMDD frames: not verified.
- Falsifier. Arm (c) fails if its E7 rise on the seven diffusion cells is not at most half of arm
  (a)'s, or if its native EER on the MAD22 landmark cells is more than 10 points worse than arm (a)'s,
  or if its R0 to R2 share stays above 0.2.
- Compute. CPU build about 1 to 2 hours (OpenCV tool measured at 2,000 images per minute in AR1).
  Features 30 minutes. Heads minutes. LoRA confirmation: 3 arms x 5 seeds, about 2 H100-hours each
  (A12BR M3L timing), 30 H100-hours on WCSS slots.
- Risk. SMDD renders carry StyleGAN2 texture in both classes, so camera photos are out of distribution
  for both arms alike; the tool pass may behave differently at 256 pixels.
- Prior work. B-Free (Guillaro et al., CVPR 2025, arXiv 2412.17671), Aligned Datasets (Rajan et al.,
  ICLR 2025, arXiv 2410.11835), Dual Data Alignment (Chen et al., NeurIPS 2025, arXiv 2505.14359) do
  this for generated-image detection (all checked, helper). Closest in MAD: Zhang, Ramachandra, Raja
  and Busch (CVPRW 2024, arXiv 2501.09817, checked, helper) replace the genuine images of their
  GAN-morph sets by GAN reconstructions "to reduce the bias between bona fide and morph"; they do not
  run a landmark tool on one image. SMDD itself (Damer et al., CVPRW 2022, arXiv 2203.06691, checked,
  helper) never passes its genuine images through the morpher. FD-MAD (arXiv 2601.20656, checked,
  helper) remarks that SMDD-trained models depend on the training set's texture statistics. No paper
  was found that rebuilds SMDD this way or that criticises it for the mismatch. Difference: the tool
  on one image for landmark morphs, the label "two photographs blended", and a comparison at fixed
  count inside the benchmark's own training protocol.

#### D2. Mirror self-morph: a one-photo twin for every family

- Mechanism. Morph a photo with its own left-right mirror image, using the unchanged tool and the
  mirrored landmark file. The result has a real warp (faces are not symmetric), real averaging of
  fine texture (pores do not match their mirror) and ghosting of one-sided features, but only one
  photograph and one person. For generators: mix the code of the photo with the code of its mirror.
- Why shortcut-free. It is the hardest genuine image we can build without a second photo: everything
  a morph does to pixels, minus the second photograph. As a negative it removes "was warped and
  averaged" as a solvable cue. As an audit rung it needs one photo per person, so it exists for FRLL,
  SMDD and FFHQ, and it has no expression confound (the A43 same-person set mixes neutral with
  smiling; the expression-matched set was never built).
- Cheapest test. CPU: mirror self-morphs for the 536 AR1 hosts and the 102 FRLL persons, both tools
  (minutes). Validity gate before any score: FR cosine to the source at least as high as for R3
  (median 0.87 on FRGC and colorFERET per `pool_summary.json`). Then score the four releases: do they
  flag mirror self-morphs like R4? GPU: DiffAE mirror mixes for the 102 FRLL persons at 20 steps (one
  extra encode and one decode per person, about 25 minutes on the DGX from the A43 timings) to replace
  the confounded C20 arm in AD1.
- Falsifier. Useless as a control if the FR oracle cannot separate it from R4 (AUC below 0.90) or if
  its FR cosine to the source falls below 0.6 (then mirroring changed the identity). Useless as a
  training negative if adding it lowers held-out-tool R2 vs R4 AUC by more than 0.05 without lowering
  the BPCER drift of B1.
- Compute. CPU minutes; 0.5 GPU-hour for the DiffAE part.
- Risk. Under the wording "the method is used" the author may rule it a morph (question F3). A mirror
  self-morph is perfectly symmetric, so it is trivially separable from everything by symmetry itself;
  it must be one negative among several, not the only one.
- Prior work. The label choice is not new: Pimenta, Medvedev and Goncalves ("Impact of Image Context
  for Single Deep Learning Face MAD", arXiv 2309.00549, checked, helper) blend two images of the same
  person with the attack generators and label these "selfmorphs" genuine, so that the detector does
  not rely on merging artefacts; they give no separate ablation. That is our R3 used as a negative,
  which the author's ruling now forbids as the main label. Kashiani et al. (IJCB 2023, arXiv
  2308.10392, checked, helper) use a "self-morphing" augmentation; its label is not stated in the
  abstract. Self-blended images (Shiohara and Yamasaki, CVPR 2022, arXiv 2204.08376, snippet) and
  SelfMAD (FG 2025, arXiv 2504.05504, checked, helper) label the one-image blend an attack.
  Symmetrised faces are standard stimuli in face perception (Rhodes, Sumich and Byatt 1999, snippet).
  A mirror-based one-photo version was not found. Difference: one photograph only, so it stays a
  negative under the ruling, and it exists for every person with a single photo.

#### D3. Warp-matched one-photo negatives and the genuine orbit as the class definition

- Mechanism. Two more one-photo constructions from unchanged library functions. Jitter self-blend:
  the photo warped by plus and minus half of a displacement field taken from a real pair, the two
  copies averaged (ghosting and smoothing, same mean shape). Displacement transplant: the photo warped
  by a real pair's half-displacement (same warp size as a morph, no averaging). The genuine class in
  training is then the whole orbit: untouched, E7 copy where one exists, pass-through, mirror
  self-morph, jitter, transplant. The attack class is R4 and R3.
- Why shortcut-free. Every pixel operation of the morph appears in the genuine class applied to one
  photo. What only the attack class has is a second photograph.
- Cheapest test. CPU build for AR1 hosts; then repeat the clean-negative test of B1 with and without
  the orbit.
- Falsifier. The orbit is not worth its cost if BPCER drift on a left-out construction does not fall
  by at least half compared with pass-through-only training, or if held-out-tool AUC against R4 falls
  below 0.75.
- Compute. CPU minutes, heads minutes.
- Risk. Needs the author's yes for calling the tools' internal warp functions with altered landmark
  inputs (precedent: `src/AR1/graded_fm.py` calls FaceMorpher's own functions). Jitter ghosts are
  stronger than real morph ghosts and may make the task too easy in the other direction.
- Prior work. Hard-negative reconstructions in DRCT (Chen et al., ICML 2024, memory). In MAD,
  one-image blends are positives in SelfMAD, and two-photo same-person blends are negatives in
  Pimenta et al. (see D2). Difference: negatives from one photograph that reproduce each pixel
  operation of the morph, with the label following the author's ruling.

#### D4. Factor-separated morph components (shape-only, texture-only)

- Mechanism. With the tools' own warp function build, for each pair: a shape-only morph (the host's
  texture in the averaged geometry), a texture-only morph (both textures averaged in the host's
  geometry) and the full morph. They give a 2 x 2 design: shape averaged or not, second texture present
  or not.
- Why shortcut-free. As training labels they let one network carry two outputs with known meaning
  (superposition present; shape averaged). As an analysis they say which factor each released detector
  answers to.
- Cheapest test. 300 hosts from AR1, CPU; score the releases and the F-mirror probes.
- Falsifier. If no detector or probe separates shape-only morphs from displacement-transplant
  negatives above 0.60, geometric averaging is not readable from pixels and M6 is closed with it.
- Compute. CPU minutes.
- Risk. Whether a shape-only morph is a morph is a ruling (F3). Low priority unless M6 passes.
- Prior work. Splicing morphs and component analysis of morph artefacts exist (Neubert, Makrushin
  et al., memory); a factorial attribution of detector response I have not seen.

### (ii) Models and objectives

#### M1. Asymmetry shrink: score what a mirror cannot cancel

- Mechanism. Every face has its own left-right asymmetry, and every photo has its own (light, pose).
  Averaging two photos halves the photo part; averaging two persons also halves the identity part.
  Score an image by the distance between the features of the image and of its mirror image
  (token-wise, with mirrored token positions), or train a small head that sees only that difference.
  One network, two views with shared weights, like the flip averaging `score.py` already does.
- Why shortcut-free. Resolution history, compression, sharpness, colour, format and symmetric borders
  act the same on the left and the right half. A reader of the mirror difference is blind to them by
  construction, including cues nobody listed. It is self-referenced: no population model, no second
  image.
- Cheapest test. On F-mirror, no training: AUC of the raw mirror distance for R2 vs R4, R3 vs R4 and
  R2 vs R3 on AR1, per tool; trend over `fm_graded`; R0 vs R1 on FRLL as the silence check. Then a
  linear head on the absolute mirror difference, leave-one-tool-out, 5-fold by person. Generator
  families for free: `h3_sg3` morphs vs renders, A43 B20 vs D20.
- Falsifier. Dead for landmark morphs if the raw distance gives R2 vs R4 below 0.60 and the head stays
  below 0.70 on the held-out tool. Not history-blind if R0 vs R1 exceeds 0.60. No cross-family value
  if `h3_sg3` is below 0.55.
- Compute. Minutes.
- Risk. Pose and lighting asymmetry may dominate identity asymmetry; alignment rotation makes borders
  asymmetric (blank them with the approved constant-colour mask); encoders are not exactly
  mirror-equivariant, which adds a constant offset. The mirror self-morph of D2 has zero asymmetry
  and scores as an extreme "morph" on this axis, so M1 must be read together with a superposition cue.
- Prior work. Averaged composite faces are highly symmetric (Rhodes, Sumich and Byatt, Psychological
  Science 1999; Langlois and Roggman 1990; snippets). In deepfake detection: Li, Cao and Zhao,
  "Exploiting Facial Symmetry to Expose Deepfakes" (ICIP 2021, snippet, abstract not retrieved)
  compare the two face halves; there the forgery is expected to break symmetry, the opposite
  direction. In MAD no symmetry or flip-consistency score was found; the closest is qualitative: a
  multimodal language model's explanations mention facial symmetry (Ivanovska and Struc, arXiv
  2602.15461, checked, helper). Our own protocol lists "more symmetric geometry" once as an attack
  property of landmark morphs (PROTOCOL.md line 7744) and never used it. Verdict of the sweep: exists
  in neighbouring fields only.

#### M2. Fisher identity typicality (FIT): a morph-free read-out of "how average is this face"

- Mechanism. From genuine photos only (FRGC, 568 persons with many sessions), estimate which feature
  directions vary between persons and which vary within a person. Add to the within-person part the
  differences between the rungs of one photo (R1 minus R0, pass-through minus R0). Score an image by
  its distance from the mean face along the between-person directions only. A morph of two persons is
  closer to the mean; a same-person morph is not.
- Why shortcut-free. No morph and no tool output with an attack label is ever seen in fitting, so
  attack-side construction cues cannot be learned. Known processing directions are in the denominator.
  The prediction is sharp and can fail: R2 = R3 above R4.
- Cheapest test. On F-mirror: fit on FRGC and colorFERET persons, 5-fold by person. Read R3 vs R4 and
  R2 vs R3 on AR1; trend on `fm_graded`; bins of contributor similarity (`cos_HB` in `pool.csv`). Then
  the five existing generator sets as a predict-then-verify figure: linear-average sets (`h3_sg3`, A43
  B20 vs D20) should be above 0.5, spread-matched renders (`a37_sg3ctl`) and re-normalised sets
  (`arc2face`, `h2_embmid`) at 0.5.
- Falsifier. Dead if R3 vs R4 on AR1 is below 0.65 (lower bound below 0.60), or if R2 vs R3 exceeds
  0.60 folded (then it reads photo averaging, not identity), or if the trend over mixing is not
  monotone.
- Compute. Minutes on CPU after features.
- Risk. The honest size of the effect: with k well-measured identity directions the separation grows
  like 0.48 times the square root of k for unrelated pairs and 0.2 times the square root of k for
  look-alikes (cosine 0.5), before measurement noise. Frozen encoders may offer few clean directions.
  It false-alarms on naturally average faces, so report BPCER by demographic group. An attacker can
  re-scale (section C.iii).
- Prior work. The plan's T3 lists norm and distance-to-mean features. "When Morphs Look Better" (Peng
  et al., arXiv 2611.00074, checked, helper) uses 17 face-quality scores as training-free MAD: best
  mean error 11.42% on FRLL sets and 39.75% on FEI sets, which is itself a sign that quality follows
  the dataset. Fu and Damer (IET Biometrics, arXiv 2208.05864, checked, helper) report over 70%
  accuracy for unsupervised detection from MagFace and quality scores. The average-image prior of
  muFlow (Pontorno et al., ECCV 2026, memory, from the literature repository) is real-only detection
  of generated faces. Difference: the between/within split with ladder differences as nuisance, a
  prediction that same-person morphs score as genuine, and the cross-family prediction pattern.

#### M3. Host-orbit paired head with interventional nulling (ladder rungs as environments)

- Mechanism. Two steps on frozen features. First, collect feature differences between rungs of the
  same genuine photo (R1 minus R0, pass-through minus R0, mirror minus R0) on training persons and
  remove their leading directions from the features. Second, fit the head on within-host differences
  (morph of host H minus pass-through of H), which is conditional logistic regression with one
  stratum per host. A variance-of-risk penalty across genuine constructions (V-REx) can be added, with
  the constructions as environments.
- Why shortcut-free. Whatever moves when only the processing of one photo changes is removed by
  measurement, not by a label. The paired fit cancels host, source, session and camera.
- Cheapest test. F-mirror features of AR1; leave-one-tool-out; BPCER drift on FRLL E7 photos and on a
  left-out construction; history probe (R0 vs R1) on the projected features.
- Falsifier. Fails if a linear probe still reads R0 vs R1 above 0.60 after projection, or if R2 vs R4
  on the held-out tool drops by more than 0.05 against the plain head, or if drift is not halved.
- Compute. Minutes.
- Risk. Linear only; a LoRA fit can relearn the cue, so the projection must become a penalty there.
  The earlier consistency loss (A49) and group-robust weighting failed, but they had no interventional
  pairs and 16 to 90 pairs of data.
- Prior work. Overlaps with the lead's "paired-difference nulling" (SEEDS S5); same idea reached
  independently. LEACE (Belrose et al., NeurIPS 2023, memory), last-layer retraining (Kirichenko et
  al., ICLR 2023, checked in the literature file), V-REx (Krueger et al., ICML 2021, memory).
  Difference: the erased subspace comes from interventions on single photos, not from labels.

#### M4. Band-limited backbone: a face-recognition network at 112 pixels

- Mechanism. Use a pretrained FR network (glintr100 or AdaFace) at its native 112-pixel input and read
  its intermediate feature maps with a small head or LoRA.
- Why shortcut-free. Most construction cues live above what a 112-pixel input can carry: the E7
  shrink leaves faces far larger than 112 pixels. The guarantee comes from bandwidth, not from
  training. The record has the matching number: a probe on glintr100 embeddings read native vs E7 at
  0.506 and reconstruction vs aligner copy at 0.493, where CLIP ViT-L/14 read 0.597 (A46 d2).
- Cheapest test. glintr100 layer-3 and layer-4 maps for AR1 rungs and FRLL native and E7; heads for
  R2 vs R4 and R3 vs R4; history probe.
- Falsifier. Fails if R2 vs R4 on the held-out tool is below 0.70, or if R0 vs R1 exceeds 0.60.
- Compute. Minutes for heads; one hour for a LoRA fit.
- Risk. At 112 pixels superposition detail is mostly gone, so this reads averageness and coarse
  ghosting; the embedding-level probe reached only 0.68 on diffusion morphs vs reconstructions.
- Prior work. FR features are established for differential detection, not single-image: Scherhag et
  al. (TIFS 2020, arXiv 2001.01202, snippet), Kessler et al. on embeddings for pair selection and
  detection (arXiv 2305.18216, checked, helper). Attack-agnostic frozen features for S-MAD (Colbois
  and Marcel, IJCB 2024, arXiv 2410.16802, checked, helper) use DINOv2, CLIP and similar encoders, not
  FR networks. No S-MAD paper was found that uses a 112-pixel FR backbone and argues from what it
  cannot see. Difference: chosen for its blindness, with the history probe as a reported guarantee.

#### M5. Shrink-factor regression: one physical target for dose and look-alikes

- Mechanism. Replace the binary label by the identity shrink factor
  s = sqrt(a^2 + (1-a)^2 + 2a(1-a)c), where a is the mixing fraction and c the FR cosine between the
  two sources. It is 1 for every genuine rung, about 0.97 for a same-person morph, about 0.78 for a
  typical AR1 pair. Regress 1 minus s.
- Why shortcut-free. A pipeline cue predicts a step at "tool used"; the target is a surface over
  mixing and similarity. The network is rewarded only for tracking both.
- Cheapest test. Ridge regression on F-mirror features with `fm_graded` plus R2, R3, R4; held-out tool.
- Falsifier. Rank correlation with s on the held-out tool below 0.3, or, at mixing 0.5, partial
  correlation with c below 0.2 (then it tracks "morphed", not "how much identity was averaged").
- Compute. Minutes.
- Risk. It is the identity head; under the ruling R3 is an attack and this target calls it nearly
  genuine. Use as an auxiliary output next to the main label, never fused.
- Prior work. The plan's T6 regresses the mixing fraction alone. Morphing-factor estimation appears
  in demorphing work as an ill-posed nuisance (seen in search results, memory). Adding the similarity
  term is the difference.

#### M6. Landmark-shape typicality with an oracle kill test

- Mechanism. A landmark morph averages landmark positions exactly. After removing pose and scale
  (Procrustes) and within-person shape variation, the shape of a morph is closer to the mean shape by
  the factor s of M5. Score the shape norm; pixels are never seen.
- Why shortcut-free. The detector's input is 106 coordinates.
- Cheapest test. Oracle first: the morph's landmarks are known without detection (the mean of the two
  `.tem` files in `AR1/src`). Fit shape statistics on the 6,921 candidate frames of `pool.py`; read
  oracle shapes of R4 vs genuine shapes. Only if that passes, detect landmarks on the outputs.
- Falsifier. Stop if the oracle AUC is below 0.65.
- Compute. Seconds.
- Risk. High. Expression moves landmarks more than identity does, and landmark detectors are noisy.
  The oracle test exists to close this in seconds, not to sell it.
- Prior work. Scherhag et al., "Detecting morphed face images using facial landmarks" (ICISP 2018,
  snippet): per the sweep it is a differential method (probe against passport image), and its error
  rates could not be retrieved, so my recollection that they were high is not verified. A 2020 paper
  on face geometry features exists by title only (snippet). No single-image method on 3D shape
  coefficients was found. Difference: single image, an identity-subspace norm, a perfect-landmark
  upper bound.

#### M7. Pass-through canonicalisation at test time

- Mechanism. Before scoring, run every input through the unchanged tool with itself (and blank the
  frame outside the tool's mask with the approved constant colour). All inputs then share the tool's
  last-stage processing, support and storage. Train on images treated the same way.
- Why shortcut-free. Last-stage differences (borders, crop, final resampling, format trace) are
  equal by construction for any input. It is a fixed preprocessing step, not a gate.
- Cheapest test. Build it for the corrected MAD22 (4,687 images) and FRLL landmark cells; score the
  releases with and without (this is E4).
- Falsifier. Pointless for our detector if its own native and equalised numbers already differ by
  less than 2 points.
- Compute. CPU minutes.
- Risk. It does not equalise earlier history (that is what E7 is for). Needs the author's yes (F4).
- Prior work. JPEG-equalised benchmarks in generated-image detection (Grommelt et al., ECCVW 2024,
  arXiv 2403.17608, checked, helper); Stay-Positive (Rajan and Lee, ICML 2025, arXiv 2502.07778,
  checked, helper); training-side alignment in B-Free. In MAD, Zhang et al. (arXiv 2501.09817,
  checked, helper) apply the same print-scan and compression to both classes when building the
  dataset. A test-time step that equalises both classes was not found in either field.

Kept from the current plan, not new: the two-contributor embedding head (T5) and stand-alone
mixing-fraction regression (T6). See section E.

### (iii) What one image can and cannot show

Model. A genuine image is mean face + identity part I + photo part P (pose, expression, light,
sensor noise), then a processing history. I and P are independent across persons; P is independent
across photos of one person.

| Family | How the morph is made | Superposition | Photo part | Identity part | Detectable in one image | Not detectable |
|---|---|---|---|---|---|---|
| Landmark | pixel average of two warped photos | yes: each source's own structure at half contrast | halved in power | shrunk by s (0.71 unrelated, 0.87 look-alike) | superposition at fine and medium scale; averageness of shape and texture | superposition after strong downsizing, print and scan, or manual retouching; identity averaging when the pair is very similar |
| Landmark, same person (R3) | same, two photos of one person | yes, weaker (same structures nearly aligned) | halved | unchanged | superposition only | anything about a second person |
| GAN, linear code average (StyleGAN W+ mean, MIPGAN start point) | one render from the mean code | none | one fresh draw | shrunk in the code | averageness only | a second identity as such |
| Diffusion autoencoder (DiffAE, MorDIFF, DiM) | semantic code averaged linearly, noise map interpolated on the sphere | none | one draw | shrunk in the semantic code | averageness only | a second identity as such |
| Re-normalised embedding morphs (Arc2Face, IP-Adapter midpoint) | render from the re-normalised mean embedding | none | one draw | length restored | nothing in principle | everything |
| Optimised morphs (MIPGAN, Greedy-DiM) | search for a code close to both identities | none | one draw | shrunk unless the search restores it | averageness; possibly traces of the search | a second identity as such |

The arguments.

1. Superposition is real evidence and cannot be made from one photo by filtering: a filter cannot add
   a second eyebrow edge at another angle. It can be imitated only by blending a photo with a shifted
   or mirrored copy of itself, which is why those are the right hard negatives (D2, D3). It lives at
   the scale of the misalignment (pixels to tens of pixels at 512), so it fades with resolution.
2. The loss of photo detail equals what smoothing does to one photo, up to phase statistics. A
   detector that reads it is reading processing. This is the shortcut every earlier method fell into.
3. Identity averaging is real evidence with a ceiling. If identity coordinates are roughly Gaussian
   with k effective dimensions, the distance from the mean is concentrated near sqrt(k) with spread
   about 0.7, and a morph sits at s times that. The best possible separation is about
   (1 - s) sqrt(k) / 0.6: for k = 30, AUC about 0.97 for unrelated pairs and about 0.78 for cosine
   0.5; it falls to chance as the pair becomes more similar. Measurement noise lowers k.
4. For a generator the image is a function of the mixed code and fresh noise. Given the mixed code,
   the image is independent of the two contributors. By the data-processing inequality no image
   detector can beat the best test on the code itself, and that test can only ask how far the code is
   from the centre. A one-person render at the same distance is the same kind of image. So A37's
   chance result on spread-matched renders is the theoretical prediction, not a failure of power.
5. Re-normalised midpoints of independent directions are again typical directions. The length is
   restored, the signal is gone. The record's set of this kind (H2) is at chance for every scored
   network; the Arc2Face set should behave the same (not verified).
6. An attacker can restore the length at no cost: FR systems compare directions. Pushing the mixed
   code away from the centre by 1/s keeps both matches and removes averageness. So averageness is a
   detector of naive generator morphs only. This should be said in the paper, and can be shown with a
   decode-only experiment on the existing StyleGAN3 codes (about 1 GPU-hour on x86; optional).
7. Consequence for the ruling "R3 is a morph": it fits landmark morphs exactly (R3 and R4 share
   superposition). For generators a same-person mix is, in principle, a reconstruction with averaged
   nuisance; no detector can be asked to separate it from R2. AD1's values there (0.27 to 0.68) are
   artefacts of the comparison set, as its own verdict says.

### (iv) Evaluation and analysis ideas that are publishable on their own

#### E1. Pooled-genuine operating point with leave-one-construction-out

- Mechanism. One threshold, all genuine constructions in the genuine class (section A.1), and a
  protocol in which one genuine construction is never used in anyone's training.
- Why shortcut-free. It measures the thing operators fear: a genuine photo with another history
  being rejected. It needs no agreement on which cue is "the" shortcut.
- Cheapest test. Recompute from existing score files: AD1 already holds R0, R1, R2, R3, R4 scores of
  three releases on MorDIFF (`experiments/AD1/ad1_ladder.json`); AR1 scores are being produced.
- Falsifier. Uninformative if pooled-genuine EER ranks the detectors the same as native EER (rank
  correlation above 0.9) over all cells.
- Compute. CPU minutes. Risk: reviewers may want the pooled mix weights justified; print each
  construction separately as well.
- Prior work. Chameleon and "A Sanity Check" (Yan et al., arXiv 2406.19435, memory) and "Fake or
  JPEG?" (checked in the literature file) change the test set; MAD has cross-dataset protocols only.

#### E2. Morph-attributable margin from the morph-free network

- Mechanism. Report next to every native cell what a network that never saw a morph scores (AD4), and
  exclude cells it solves from averages (A.3).
- Cheapest test. AD4 is already queued (20 tasks). Only the reporting rule is new: fix it now.
- Falsifier. If the morph-free network is above 30% EER on every landmark cell at the fixed
  checkpoint, the margin adds nothing for that family.
- Compute. None beyond AD4. Risk: checkpoint sensitivity seen in A47 (last vs selected).
- Prior work. Hypothesis-only baselines in language inference (Poliak et al., Gururangan et al.,
  2018, snippet); face presentation-attack detection trained on vegetables reaching 92.70% AUC
  ("Tomatoes, Potatoes, and Onions", Ozgur, Boutros and Damer, arXiv 2608.21455, checked, helper);
  leading silence alone separating real from fake in audio-visual deepfake sets (Smeu et al., CVPR
  2025, arXiv 2412.00175, checked, helper). No MAD equivalent was found, and no 2025 to 2026 shortcut
  audit of MAD benchmarks.

#### E3. Identity ceiling curve

- Mechanism. Estimate the best possible AUC of any image detector for averaged-code morphs as a
  function of contributor similarity, in two ways. (a) In FR space: embeddings of many genuine
  identities (CASIA-WebFace, 10,572 persons) against midpoints of pairs binned by cosine, linear and
  re-normalised, best classifier on the embeddings. (b) In the generator's own code space where codes
  exist (`h3_sg3`, GAN32). Then print every detector's R2 vs R4 AUC as a fraction of the ceiling.
- Why it matters. It turns "nothing detects generator morphs" from an absence into a bound, and it
  predicts which existing sets must be at chance.
- Cheapest test. CPU, after one pass of glintr100 over a CASIA subsample (50,000 images, minutes).
- Falsifier. The account is wrong if the re-normalised ceiling is above 0.65 while all networks are
  at chance on `h2_embmid` and `arc2face`, or if any detector exceeds the code-space ceiling on a
  spread-matched set.
- Compute. Under 1 GPU-hour. Risk: the FR-space bound is a model, not a theorem about pixels; say so.
- Prior work. The norm-shrink remark in `03_LITERATURE_AND_METHODS.md`; vulnerability studies of
  pair similarity (memory). The sweep found no impossibility or limit argument for single-image
  morph detection, and no paper using single-image demorphing as a detector.

#### E4. Pass-through-equalised benchmarks for released detectors

- Mechanism. Apply the pass-through (M7) to both classes of each landmark cell of the corrected MAD22
  and FRLL, after the existing E7 step for the genuine side, and rescore every release.
- Why it matters. It is the missing landmark control: E7 leaves borders in place, and border
  fraction alone separates several cells at 0.99 to 1.00. It needs no new processing code.
- Cheapest test. CPU build (about 10,000 images), then the four releases.
- Falsifier. If no release moves by more than 3 EER points on any landmark cell, last-stage
  construction is not what they read there, and the four rows that held under E7 are confirmed.
- Compute. CPU minutes plus scoring. Risk: the pass-through adds one resampling to both classes,
  which may itself hide a morph trace; report the morph-only change as well.
- Prior work. As M7.

#### E5. Response surface over mixing fraction and contributor similarity, with factor attribution

- Mechanism. For every detector, the mean score over a grid of mixing fraction (0 to 0.5) and FR
  cosine of the pair, plus the D4 components. A superposition reader rises with mixing and is flat in
  similarity; an identity reader falls with similarity; a pipeline reader is a step at "tool used".
- Cheapest test. `fm_graded` and `pool.csv` cosines; scores from AR1.
- Falsifier. None; descriptive. Compute: CPU minutes. Risk: the AR1 pairs were chosen for high
  similarity, so the cosine range is narrow (median 0.23); add random pairs.
- Prior work. Dose ladders in this record (A44); AR2 and AR7 of the plan. The joint surface is new.

### A critique of the lead's alpha-field supervision (SEEDS S1), and how the two sets combine

The idea is good and I would keep it. Three risks to test before it becomes the main method:

1. The field creates a local version of the old cue. Inside one image the blended region has less
   fine detail than the unblended region. A dense head can learn "locally smoother than the rest".
   Genuine photos have that too: skin retouching, depth of field, hair against skin. Remedy: give
   one-photo negatives the same field (jitter self-blend or mirror self-morph weighted by the same
   field, target 0). Then only a second photograph makes the target non-zero.
2. Real morphs are uniform. At test time the mixing fraction is 0.5 everywhere, so there is no
   within-image reference, and the head must work from absolute local evidence. Whether it does is
   exactly the E7 question again. The training set must therefore contain uniform 0.5 and uniform 0
   images of varied history, and the first read must be the BPCER drift of B1 on the mean predicted
   field.
3. It cannot help with generator morphs (no superposition), which S3 already says.

The stress test proposed there (confounded source, crossed test) is the right first experiment for
it. Run it with and without the field-shaped one-photo negatives.

Note on prior-work status. A literature helper checked eight of the claims above by web search on
11 Nov. Its verdicts are folded into the entries and summarised in the appendix. "Not found" means
not found by that sweep (abstracts and search results, no full texts); it is not proof of absence.

---

## D. Ranked top five and the 72-hour order

Score = chance of a valid positive result x novelty (1 to 5) / cost (1 = hours on frozen features,
2 = needs a CPU build and a LoRA confirmation). My estimates.

| Rank | Idea | Chance | Novelty | Cost | Score | What a positive result gives the paper |
|---|---|---|---|---|---|---|
| 1 | D2 mirror self-morph (control and negative) | 0.7 | 3 | 1 | 2.1 | a one-photo twin for all families and for FRLL, closes the expression confound, the hard negative the plan lacks |
| 2 | E3 identity ceiling curve with the theory table | 0.7 | 4 | 1.5 | 1.9 | turns the generator null into a bound and predicts five existing results |
| 3 | M1 asymmetry shrink | 0.35 | 5 | 1 | 1.75 | a score that is blind to every mirror-symmetric cue by construction |
| 4 | E4 + M7 pass-through equalisation | 0.5 | 3 | 1 | 1.5 | the missing landmark control for released detectors, and a fixed test-time step for ours |
| 5 | D1 PM-SMDD with the genuine orbit (D3) and the paired head (M3) | 0.5 | 4 | 1.5 | 1.3 | the headline detector and the fixed-count proof that the data construction is the cause |

Rank 5 is lowest by the formula and is still the route to the detector. Ranks 1 to 4 feed it.
M2, M3 and M6 ride on the same feature cache at no extra cost and are read the same night.

### The single experiment to run first, tonight: the clean-negative test

Question: does a head trained the way the current plan trains (R2 against R4) reject genuine photos
it has not seen as negatives?

- Data: F-mirror features (CLIP ViT-L/14 first) of `AR1/img/frgcferet/{opencv,facemorpher}/{R2,R4}`,
  the untouched sources in `AR1/src`, and FRLL native and E7 photos. No new image.
- Fit: logistic head, train on one tool, test on the other, 5-fold by person.
- Read 1: BPCER on untouched sources of test persons and on FRLL E7 photos, at the threshold that
  gives 10% BPCER on test-person R2.
- Read 2: best single `cue_floor.stats()` measure for R2 vs R4.
- Verdict fixed now. The plan's class definition fails if BPCER in read 1 exceeds 20% on either
  genuine set, or if any single cue exceeds 0.80. It stands if both BPCER values are at most 15% and
  no cue exceeds 0.65. In between: mixed, add the orbit and repeat.
- Free riders in the same run: the raw mirror distance (M1), FIT (M2), the oracle shape test (M6).
- Time: about 1 to 2 hours on the DGX, mostly feature extraction.

### 72-hour order

Wednesday 11 Nov, evening (DGX and its CPU)
1. F-mirror cache. Clean-negative test with the three riders.
2. CPU in the background: mirror self-morphs and jitter negatives for AR1 hosts and FRLL persons;
   PM-SMDD build (pass-through, mirror, morphs, two tools).
3. DiffAE mirror mixes for the 102 FRLL persons (25 minutes of GPU).

Thursday 12 Nov
4. Morning: read the riders. Fix the class definition (pass-through only, or orbit).
5. E4: pass-through-equalised MAD22 and FRLL landmark cells, four releases scored.
6. E3 on CPU; theory table checked against `h3_sg3`, `a37_sg3ctl`, A43, `arc2face`, `h2_embmid`.
7. D1 on frozen features, three arms at equal count, with the M3 head. Gate at 16:00: arm (c) halves
   the E7 rise and keeps MAD22 landmark EER within 10 points of arm (a). If yes, stage 15 LoRA tasks
   (3 arms x 5 seeds) for the WCSS slots the same afternoon. If no, the paper is audit, ceiling and
   the M1/M2 read-outs, and the slots go to audit coverage.
8. If the lead runs the alpha-field test AF0: add the field-shaped one-photo negatives to it.

Friday 13 Nov
9. LoRA results as they arrive. Leave-one-construction-out and held-out tool. Pooled-genuine table
   for all comparators (E1). Response surface (E5).
10. Second backbone on the winning arm only (DINOv3-L or MambaVision), five seeds, if slots are free.

Saturday 14 Nov
11. FRLL and FEI test scored once. Corrected MAD22 native, equalised, pooled. AD4 margins (E2).
    Tables frozen.

---

## E. What to drop from the current plan to make room

1. Generator twin training sets at scale (D3 and D4 of the plan at 10,000 pairs, about 150
   GPU-hours) and rental lease V2. Theory and record both say the best case is per-generator
   averageness. Keep only what the audit's causal test needs (AG1 for the 102 benchmark persons).
2. T5, the two-contributor embedding head. For generators the contributors are not in the image
   beyond the mixed code; for landmark morphs it costs a day and its falsifier is likely to fire.
3. T6 as a stand-alone experiment. Fold into M5 on frozen features.
4. AD5 (SelfMAD retrains, 30 H100-hours), AG4 (morph-free GAN network, 12 H100-hours), AD2 (DiM
   ladder) and the plan's X3 (number of pipelines).
5. The three-backbone x five-seed matrix. One backbone with five seeds on three data arms answers the
   causal question; a second backbone only on the winning arm. The MADMamba arm goes; MambaVision only
   if slots are idle.
6. The FRGC and colorFERET "second pool" for E7: no approved E7 output exists there and our own
   networks trained on those persons. Use FEI for the second test pool and FFHQ for the E7 repeat.
7. Same-person latent twins as a verdict cell for generators (see C.iii point 7). Replace by the
   mirror mix as a validity control.

---

## F. Questions only the author can answer

1. Is a re-synthesised genuine photo (a GAN inversion or diffusion reconstruction of one person's
   photo) a valid genuine image, or already an inadmissible image? If it is genuine, generator-morph
   detection is bounded by averageness and the paper states a limit. If it is inadmissible, a second,
   openly named output "re-synthesised" is legitimate and the generator cells become winnable.
2. Does averageness count as morphing evidence? A one-person image pulled toward the mean face
   (truncated render, heavy beautification) is then the false alarm we accept, and the limit in C.iii
   point 6 is printed as a known evasion.
3. Is a mirror self-morph (one photo morphed with its own mirror image), and more generally any
   one-photo construction that calls the morphing tool's functions, a processed genuine image? Your
   ruling says same-person morphs are morphs "since the method is used"; here the method is used on
   one photograph. I recommend: genuine, as a hard negative, with the alternative labelling printed.
4. May agents (a) flip images left to right without loss, (b) call the unchanged tools with altered
   landmark inputs and the tools' own warp functions, as `graded_fm.py` already does, and (c) make
   the pass-through a fixed preprocessing step of our detector at test time?
5. Will you accept pooled-genuine and equalised numbers as the headline, native benchmark numbers
   second, and a stated negative result for generator morphs, if the native landmark numbers end up
   within a few points of the released detectors but not ahead?

---

## Not verified

- That the R2 files are pixel-identical (up to crop and mask) to their sources.
- Whether the plan's training negatives include R0 and R1 or only R2 (the plan says "pipeline-matched
  genuine images").
- That the two landmark tools run unchanged on 256-pixel SMDD frames, and FaceMorpher's speed there.
- That FEI offers two usable frontal photos for all 200 persons, and that no released detector was
  trained on FEI.
- That intermediate glintr100 feature maps can be read with the existing `src/AR1/fr.py` loader.
- The left-right index map of the 106-point landmark files (needed for mirrored landmarks; the
  alternative is to detect landmarks on the mirrored image with the existing aligner).
- Whether the Arc2Face set (A23) used a re-normalised mixed embedding, and what networks score on it.
- All compute figures are estimates from timings quoted in the record.
- Prior-work statements marked "memory" or "snippet". The helper read abstracts only.
- Every chance, novelty and effect-size figure in sections C and D is my estimate, not a measurement.

---

## Appendix: prior-art sweep of 11 Nov (literature helper, web search, abstracts only)

| Claim | Closest work found | Verdict |
|---|---|---|
| Facial asymmetry as a morph score (M1) | Deepfakes: Li, Cao, Zhao, ICIP 2021 (snippet). Psychology: Rhodes et al. 1999 (snippet). MAD: only qualitative mentions in language-model explanations, arXiv 2602.15461 (checked) | neighbouring fields only |
| Mirror self-morph as a control (D2) | Two-photo same-person "selfmorphs" labelled genuine: Pimenta et al., arXiv 2309.00549 (checked). No mirror version | same-person negatives exist in MAD; the mirror variant appears new |
| Pipeline-matched genuine images in training (D1) | GAN-reconstructed genuine images for GAN sets: Zhang et al., CVPRW 2024, arXiv 2501.09817 (checked). Aligned data in generated-image detection: B-Free, Aligned Datasets, Dual Data Alignment, Fake or JPEG (all checked) | partly exists in MAD (GAN reconstruction); the tool on one image for landmark morphs appears new |
| Averageness and limits (M2, E3) | Quality scores as MAD: arXiv 2611.00074 (checked); MagFace and quality, unsupervised: arXiv 2208.05864 (checked). No limit argument, no 3D-shape S-MAD | quality and feature magnitude exist; the limit argument appears new |
| FR backbone at 112 pixels (M4) | FR features for differential detection (TIFS 2020, snippet; arXiv 2305.18216, checked); frozen general encoders for S-MAD (arXiv 2410.16802, checked) | the blindness argument appears new |
| Test-time equalisation (M7, E4) | Dataset-level equal print-scan and compression (arXiv 2501.09817, checked); JPEG-bias work in generated-image detection (checked) | appears new as a test-time step |
| Reference row from a network that never saw the class (E2) | Vegetables-trained presentation-attack detector, arXiv 2608.21455 (checked); silence audit, arXiv 2412.00175 (checked) | neighbouring fields only |
| Recent comparators | FD-MAD arXiv 2601.20656 (checked), SRL-MAD arXiv 2603.15050 (checked, no numbers in abstract), R-FLoRA arXiv 2604.17321 (abstract checked), Shahreza et al. arXiv 2608.29802 (checked), MADation arXiv 2501.03800, SelfMAD arXiv 2504.05504, MADPromptS arXiv 2508.08939 (abstracts checked, no absolute numbers retrieved) | no 2025 to 2026 shortcut audit of MAD benchmarks found |

Not retrieved by the sweep: error rates of the 2018 landmark paper, absolute numbers of SelfMAD and
Greedy-DiM, the abstract of the ICIP 2021 symmetry paper, verified metadata of the psychology papers.
