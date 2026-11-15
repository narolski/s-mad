# Round 3 vetting, lens "state of the art": review of the three recipes

11 Nov 2026, evening. Reviewer role: hostile but constructive area chair with an image-forensics and
morph-detection background. Reviewed file: `ideas/round3/sota_ideas.md`. I only read files and thought.
Nothing was trained, scored or generated. No sealed file was opened. No image was loaded.

How to read this page

- S-MAD = single-image morphing attack detection. EER = equal error rate in percent. AUC = area under
  the ROC curve (0.5 is chance). FA = share of genuine images flagged.
- LoRA = low-rank adaptation of a pretrained encoder. CLIP ViT-L/14 = the large OpenAI CLIP vision
  transformer. SMDD = the standard synthetic training set (25,000 StyleGAN2 renders, 15,000 morphs).
- IED = inter-eye distance in pixels.
- "Measured" = a number in our record, with its file. "Unreviewed" = an owner's first number from today.
  "Expected" = my estimate.
- Literature: ten web searches succeeded, then the session's search budget ran out. After that I opened
  five arXiv abstract pages directly. Anything I could not open is marked "not verified".

---

## 0. Verdicts in one table

| Recipe | Verdict | Impact | Feasible by 14 Nov | Shortcut-proof | Novelty |
|---|---|---|---|---|---|
| 1. Ladder-ordered CLIP ViT-L/14 LoRA network | revise | 6 | 5 | 4 | 3 |
| 2. Canonical-band network at one small size | revise (demote to a measurement and one ablation row) | 3 | 6 | 3 | 4 |
| 3. SMDD-Ladder (SMDD renders only) | revise | 5 | 5 | 4 | 3 |

Short version. Recipe 1 is the right skeleton, but three parts must go: the ordered policy for
one-photo generator output, the order term of the loss, and the first test as written. Recipe 2 does not
deliver its main promise at the only band that matters, and it turns softness into evidence. Recipe 3 is
needed as the comparable row, without its GAN family and without the mirror rung in the loss.

---

## 1. Points that affect all three recipes

### 1.1 "Tops the published tables" cannot be claimed as written

The generator says this itself for AMSL, the GAN cells and MorDIFF at 0.00. I add four points.

1. Published MAD22 numbers were computed on the SYN-MAD 2022 release. We score the corrected copy.
   Equivalence is not verified (measured caveat: `experiments/RS1_own-crop-rescore/prereg.md`, amendment 1,
   item 4). No released detector has a score on the corrected MAD22 yet
   (`experiments/EV1_fixed-threshold-reread/result.md`, "What could not be verified").
2. Scores depend on the platform. The same MADation ViT-B/16 release gives FaceMorpher 0.49 or 0.86 and
   WebMorph 1.51 or 1.88 on two machines, and DiM EERs move by up to 1.5 points
   (measured: `experiments/RS1_own-crop-rescore/README.md`, 17:48). One genuine photo of 204 is 0.49 points.
   So "0.3 to 1.0 against 0.00, 0.74 and 0.99" is a tie, not a win.
3. The generator's own expected ranges for the two clean cells straddle the published values: MAD22 OpenCV
   1.5 to 4 against 2.23, Webmorph 6 to 11 against 10.80. A win there is about a coin flip on present
   evidence.
4. The recipe trains on camera photos morphed with the benchmark's own tools. Every published row trained
   on SMDD only. The comparison is fair only with a baseline retrained on the same data.

Consequence. The honest headline is: best fixed-threshold miss rate among detectors that pass the
storage and softness controls; published-table EERs within platform noise on the easy landmark cells; a
win or a loss on the two clean MAD22 cells, whichever is measured. The paper should say so.

### 1.2 The ordered policy (policy O) trains the cue the paper attacks

Policy O ranks a one-photo reconstruction 2 logits above its host photo. That is a trained response to
generator output. The brief lists generator fingerprint among the cues the network must not rely on. Our
own class page says of the releases: they "place one-photo reconstructions with the morphs, so those
benchmark cells measure generated-image detection" (`14_CLASS_DEFINITIONS.md`, section 3). The author's
position of 16:00 is that this is a different task and the treatment must be the same for every detector
(`07_DECISIONS_NEEDED.md`). A reviewer will quote our audit against our method.

The expected GAN-cell numbers under policy O (1 to 6%) would come from that step, not from mixing.
Unreviewed lead: camera photo to reconstruction is separable at 0.98, mixing at 0.73
(`experiments/PD1_signal-isolation-paired-differences/gan/result.md`).

Consequence. Policy A (reconstruction tied to its host as genuine) is the only headline. Policy O may be
one labelled extra row, never the network of the paper.

### 1.3 Today's leads contradict the order the loss imposes

All unreviewed. They still decide the design, because the order term costs code and time.

- Diffusion autoencoder: a head trained on mixing ranks same-person mixes above two-person morphs (AUC
  0.25 for two-person against same-person) and reconstructions below photos (0.26)
  (`experiments/PD1_signal-isolation-paired-differences/diffae/result.md`).
- GAN latent morphs: two-person morph against spread-matched render 0.46 to 0.47, while latent averageness
  alone gives 0.9998 on morph against reconstruction (`.../gan/q3_heads.csv`). The "mixing" signal is the
  position in latent space. Transfer of the heads to the benchmark cells: FRLL-Morphs StyleGAN2 0.64 to
  0.75, MIPGAN-I 0.46 to 0.73, MIPGAN-II 0.38 to 0.64 (`.../gan/benchmarks.csv`). That is EER 31 to 58%,
  worse than the 25 to 45% the generator expects under policy A.
- Landmark: mirror self-morph against two-person morph 0.49 to 0.69; warp-only against mirror self-morph
  0.99 (`.../landmark/result.md`, `q1_clip_mean.json`).
- Mirror mixes are nearly symmetric faces: asymmetry 2.1 against 12.0 for a two-person morph and 19.6 for
  a photo (`experiments/AD1b/result.md`, four persons).

A margin "same-person or mirror mix must score below two-person morph" then forces the network to find
some separator. The cheapest ones are left-right symmetry (mirror rung) and the size of the outline ghost
(same-person photos share hair and shoulders; two persons do not). Neither is on the controls list. Our
own earlier note names the second one as the main risk of this design
(`03_LITERATURE_AND_METHODS.md`, design M1, "Main risk").

Consequence. Drop the order term. Mirror and same-person rungs are test-only rows of the single-subject
table.

### 1.4 The first tests read benchmark cells on frames that carry the border

The first test of recipe 1 reads EER on the list `bench_s`. I checked the list: its FRLL-Morphs rows are
our 512-pixel aligned frames (`/mnt/t7/smad_next/AF0/lists/bench_s.csv`, paths under
`smadcvpr_data/eval/frllm/`). On those frames the black border alone separates FRLL-Morphs FaceMorpher,
OpenCV and WebMorph at 0.99 to 1.00 (measured: EV1 result, Part B.1). The pass mark "EER at most 5% on
FRLL-Morphs FaceMorpher and OpenCV against history-matched photos" can be met by the border. The generator
states the border problem in its section 2.3 and then uses these cells as a gate.

Usable gates on existing features: corrected MAD22 OpenCV and Webmorph (best aligned-frame cue 0.76 and
0.75) and the approved Poisson set (H1: both classes from the same source, size and border; features in
`/mnt/t7/smad_next/AF0/feat/clip224/h1.*`). The bar on H1 is measured: MADation-recipe ViT-L/14 retrains
reach 0.833, file size 0.620 (`docs/sources/methods_table/gather_regular.md`, lines 233 and 240).

### 1.5 The softness control has a stronger form that needs no new image

The generator compares softened warp-only images with softened morphs and needs 800 new images for it.
Softening both sides does not remove the cue: a morph stays softer than its halves in any storage state.
The decisive contrast is crossed: a genuine image softened to the 61 pixel history against a native
two-person morph of the same host. A network that reads softness ranks the softened genuine image higher,
so its AUC falls below 0.5. Both sides exist as features now (`ar1soft` and `ar1` in
`/mnt/t7/smad_next/AF0/feat/clip224/`; 200 hosts, two tools).

### 1.6 Which registered softening strengths do anything

- The 112.7 pixel strength is probably invisible at a 224 input (the generator's own section 2.2). If so,
  half of every "softened" pool is a copy of the original and inflates pass rates. Check with one
  statistic before pooling. Not verified by me.
- The SMDD shrunk copy is 80 pixels wide, about 20 pixels between the eyes (scale 0.3125; measured call in
  `experiments/SM1_smdd-partner-audit-and-rebuild/result.md`, checks). Tying a render to that copy and
  asking a morph at that size to score 4 logits higher cannot be satisfied by reading blending.
- For SMDD renders (about 63 pixels between the eyes, unreviewed) the 61.2 pixel strength is a 4% shrink,
  close to nothing.

Consequence. Under the image rules the SMDD pool has no softening strength in the useful band. Only the
61.2 pixel strength on camera photos teaches "softness is not blending". Recipes 1 and 3 must say this;
recipe 3 cannot claim a storage control learned from SMDD alone.

### 1.7 A frozen head cannot clear a LoRA network

All three first tests use a logistic head on frozen CLIP features. Measured: frozen encoders do move with
storage history (brief), and the LoRA retrains of the MADation ViT-L/14 recipe flag 59 to 87% of the FRLL
photos with the MorDIFF history at their 5% threshold (EV1 result, Part A.1, "Other rows"). The frozen
head of the clean-negative test (CN0) flags 3 to 6% (unreviewed, `experiments/AF0/cn0.json`). So the
frozen head can pass and the trained network still fail. A decisive test must contain real LoRA fits. A
ViT-B/16 fit takes 0.87 hours on an A100 (measured: `experiments/AD4/README.md`, section 5.5). Athena
accepts jobs since 18:26 (`NOTEBOOK.md`).

### 1.8 Record disagreements the generator builds on

- "Robust recipe" row: AMSL 15.0% EER for the ViT-L/14 retrains (`gather_regular.md`, row 13). The
  fixed-threshold re-read (EV1) prints AUC 0.999 on AMSL for the same five networks at the last checkpoint
  (Part B.2) and a miss rate of 0.2% (Part A.2). Both cannot be the same score. Resolve before "honest
  AMSL is 8 to 14%" is used anywhere.
- "0.8% on MAD22 MIPGAN-I with no control that explains it": on our frames the border separates the
  corrected MIPGAN cells at 0.999 to 1.000 (EV1 result, Part B.1). That is the cheapest explanation. Not
  tested.
- The softened training list (`soft`) is not extracted yet. The softening chain logged "soften try 1
  failed" at 18:18 (`/mnt/t7/smad_next/AF0/chain_soft.log`); 1,819 of about 3,370 softened images exist.

---

## 2. Recipe 1: ladder-ordered training of one CLIP ViT-L/14 LoRA network

### 2.1 Novelty

Closest prior work I found:

- Heinze-Deml and Meinshausen, "Conditional variance penalties and domain shift robustness", Machine
  Learning 110, 2021, https://arxiv.org/abs/1710.11469 (abstract read). It penalises the variance of the
  prediction inside groups that share class and identity, to become invariant to style such as image
  quality. The equality term is this penalty with "host" as the group.
- Kashiani, Talemi, Saadabadi, Nasrabadi, "Towards Generalizable Morph Attack Detection with Consistency
  Regularization", IJCB 2023, https://arxiv.org/abs/2308.10392 (abstract read). Consistency at logit and
  embedding level across morph-wise augmented views. This is the precedent inside morph detection. Which
  augmentations it uses: not verified (abstract only).
- Ni et al., "CORE: Consistent Representation Learning for Face Forgery Detection", CVPR Workshops 2022,
  https://arxiv.org/abs/2206.02749 (found by search). Consistency between two augmented views.
- Le and Woo, "Quality-Agnostic Deepfake Detection with Intra-model Collaborative Learning", ICCV 2023,
  https://arxiv.org/abs/2309.05911 (found by search). One model sees the same image at several qualities
  and its representations are tied. This is the storage-crossing idea in the neighbouring field.
- Chen et al., "DRCT", ICML 2024, https://proceedings.mlr.press/v235/chen24ay.html (found by search).
  Reconstructions of real images as hard samples with a contrastive loss.
- Medvedev, Shadmand, Gonçalves, "MorDeephy", ICPRAM 2023, https://arxiv.org/abs/2208.03110 (found). Our
  class page credits this group with same-person "selfmorphs" as genuine; my search did not confirm that
  detail.
- A triplet-loss Siamese S-MAD paper ("Single Morphing Attack Detection using Siamese Network and Few-shot
  Learning"; title seen in search results, authors and venue not verified).
- Our own note already holds this design: per-image cross-entropy plus a within-pair margin ranking loss on
  CLIP ViT-L with LoRA (`03_LITERATURE_AND_METHODS.md`, design M1), and within-pair ordinal ranking (M4).
- Backbone and recipe: Caldeira et al., MADation, WACV Workshops 2025, https://arxiv.org/abs/2501.03800.

What remains new: the choice of tied views (the morph's own warped halves, warp-only images, storage
states crossed in both directions) and the fixed-threshold evaluation with every history-matched pool
protected. The loss itself is standard. I did not find a morph-detection paper that ties a morph's warped
halves to the genuine class; "not found" rests on ten searches.

### 2.2 Strongest objection

The path to "state of the art" on the MAD22 mean and on the generator cells goes through policy O, which
is a trained generated-image detector (1.2). Without it the recipe has no route to the published level on
5 to 7 of 17 cells, and on the cells it can reach, the gap to published values is inside platform noise
(1.1). What is left is a robustness claim. That claim is worth a paper only if the softness control is
passed by a LoRA network, which no test in the recipe shows before about 400 GPU-hours are spent.

### 2.3 Cheapest confound and the control

- Landmark numbers: softness. A single band-power statistic separates warp-only from two-person morph at
  0.912; the two-person head reaches 0.980; excess 0.068 [0.026, 0.114] (unreviewed, one fold, DINOv3 at
  512: `experiments/PD1_signal-isolation-paired-differences/landmark/result.md`). At 224 the Laplacian
  floor is higher than at 512 (0.87 against 0.76, measured, `ideas/CONSOLIDATED_v2.md`). Control: the
  crossed contrast of 1.5, and every AUC printed as excess over the best statistic on the same images.
- Benchmark numbers: the aligner border, if any cell is read on our frames (1.4). Control: raw files
  through the face-detector crop (0% black pixels on 8 files per source, measured, RS1 README 17:45).
- Generator cells: generator fingerprint under policy O (1.2). Control: policy A, and reconstruction
  against morph of the same generator.
- Loss rungs: symmetry and outline ghost (1.3). Control: remove the order term.

### 2.4 Where the recipe contradicts the record

- The first test gates on border-confounded cells (1.4).
- "Softened evaluation copies exist" is true for photos and warp-only images only; softened training
  features do not exist yet (1.8).
- The threshold rule protects "SMDD evaluation renders in all storage states". That includes the 20 pixel
  copy (1.6). One extreme pool then sets the threshold of the whole paper.
- The camera-photo pool is 530 persons, 490 of them colorFERET (measured: `experiments/AF0/result.md`,
  Counts). At 6,250 steps each host is seen several hundred times. The landmark ladder (AR1) holds 427 FRGC
  persons as test hosts (`experiments/AR1/pool_summary.json`), although FRGC morphs were the lever in the
  earlier draft. The split wastes the best training source.
- Go and no-go marks (section 3.10 of the recipe) are read on the landmark ladder, FRLL and FEI. After one
  revision those are no longer held out. The ladder has a person split file
  (`experiments/AR1/pool_person_split.csv`), but only 8 of 536 persons are marked validation.
- "The reported network is the mean over seeds" is not one network. Name one seed before training.

### 2.5 Feasibility by 14 Nov

Exists (listed): `/mnt/t7/smad_next/AF0/feat/clip224/` with `af0_w1`, `af0_w2`, `af0_h`, `ar1`, `ar1soft`,
`bench_s`, `h1`; statistics for `ar1`, `bench_s`, `h1`, `af0_w1` in `/mnt/t7/smad_next/AF0/cues/`;
`src/AF0/soften.py`; the SMDD rebuild images (`/mnt/t7/smad_next/SM1/img/armc` 45,000, `arme` 45,001,
`armcr` 15,000). Missing: the `soft` feature list; statistics for `ar1soft`; softened ladder morphs; every
generator ladder (diffusion generation on Athena (DG1) has produced nothing yet; the MIPGAN controls (AG1)
have submitted nothing); the host-group sampler and the pair loss; face-detector crops of all training
pools (0.4 images per second per process on the loaded DGX, so this must run on Athena).

The full plan (five waves, 23 table rows at five seeds, 830 GPU-hours, peak 72 cards on 12 Nov) needs all
of that by tomorrow morning plus a pre-run review. I do not believe it. A reduced plan fits: landmark
families only, policy A, data rows first with the unchanged training script, the equality term only if the
data rows fail.

### 2.6 Revised design

1. One CLIP ViT-L/14 LoRA network, the registered MADation recipe, last checkpoint, face-detector crop
   stored as PNG, loader resize to 224, no flip averaging. Seed 401 is named now as the network of the
   paper; seeds 402 to 405 give the spread.
2. Policy A only: a one-photo generator output is genuine and tied to its host. Policy O is one labelled
   row if time allows.
3. Training classes. Genuine: camera photos, SMDD renders, warp-only images, the morph's own warped
   halves, and their copies with the 61.2 pixel history. Morph: two-person morphs and their 61.2 pixel
   copies. The 112.7 pixel strength is used only if a statistic shows it is visible at 224. The 80 pixel
   SMDD copy is not a tied view.
4. No order term. Mirror and same-person rungs are never trained on; they fill the single-subject table.
5. Step 1 is data only, with the unchanged training script. The equality term (squared logit difference
   between genuine views of one host) is written only if step 1 fails the shift mark and passes the
   signal marks.
6. Camera-photo pool: move FRGC into training. Keep a fixed, seeded list of 200 landmark-ladder hosts as
   the test ladder and 100 more as the development ladder; all go and no-go decisions use the development
   ladder, the alpha-field probe's 133 validation persons and FFHQ development photos.
7. Threshold: 5% false alarms on every development genuine pool whose IED is 60 pixels or more. Pools
   below that are printed, not protected, and the scope limit is stated.
8. Diffusion rungs enter only after recipe 3's transfer test passes; GAN rungs do not enter.
9. Reported: fixed-threshold miss per family with every history-matched pool protected (headline);
   native, history-matched and neutral-only EER on raw files through the same crop; the crossed softness
   contrast; excess over the best statistic; the Poisson set (H1); both class policies for generator
   cells; released detectors through their own crop on the same files, including the corrected MAD22.
10. Reference rows with the same data: MADation recipe on released SMDD; the same recipe on our data
    without halves and softened copies; history-only and label-permuted networks.
11. Ablation table cut to eight rows at five seeds: released SMDD; rebuilt SMDD; + halves and warp-only;
    + 61 pixel copies in both classes; + camera photos; + equality term (if built); left-out engine;
    left-out strength is impossible with one useful strength and is replaced by the unseen-kernel pools
    (`e7bicubic`, `e7lanczos` in `/mnt/t7/smad_heldout/a46_corrective_20261108/rgb_clip/`).
12. Claim: best fixed-threshold miss among detectors that pass the storage and softness controls; table
    EERs reported with platform spread; no "state of the art" sentence for AMSL, GAN cells or MorDIFF.

### 2.7 First test

Tier 0, tonight, CPU, no new image.

- Data: `/mnt/t7/smad_next/AF0/feat/clip224/{af0_w1,af0_w2,af0_h,ar1,ar1soft,bench_s,h1}.tokens.npy` with
  lists in `/mnt/t7/smad_next/AF0/lists/`; statistics in `/mnt/t7/smad_next/AF0/cues/` (compute them for
  `ar1soft` with the existing `cues_all.py`).
- Features: mean-pooled CLIP ViT-L/14 patch tokens at 224. Head: logistic regression, C by inner
  cross-validation over persons, five seeds. Arms: (i) photos against uniform 0.5 morphs; (ii) photos,
  zero-field (warp-only) images and both halves against the same morphs. Trained on the 530 training
  persons of the alpha-field probe (AF0); threshold at 5% false alarms on its validation genuine images.
- Reads on the landmark ladder (AR1), OpenCV-style engine decides, FaceMorpher descriptive:
  (a) warp-only against two-person morph, AUC and excess over the best of the 27 statistics;
  (b) crossed: warp-only softened to 61 pixels against the native two-person morph of the same 200 hosts;
  (c) paired shift from photo to its 61 pixel copy in standard deviations of the photo scores, and the
  share flagged; the 112.7 pixel copies separately;
  (d) AUC on the Poisson set (H1);
  (e) EER on corrected MAD22 OpenCV and Webmorph, native and history-matched. FRLL-Morphs cells are
  printed, not gated.
- About 4 CPU-hours on the loaded machine.

Tier 1, decisive, Athena, about 5 A100-hours, within one day of the softened set being complete.

- Four ViT-B/16 LoRA fits with the unchanged training script (MADation recipe, 6,250 steps, last
  checkpoint, seeds 401 and 402). Manifest A: photos against morphs. Manifest B: photos, zero-field
  images, halves and their 61 pixel copies against morphs and their 61 pixel copies. Same images as tier
  0, same reads (a) to (e), no flip averaging.

### 2.8 Pass and kill

- Pass (tier 1, manifest B, both seeds): (a) at least 0.95 and excess at least 0.03 with a lower bound
  above 0; (b) at least 0.90; (c) shift at most 0.3 standard deviations and at most 10% flagged; (d) at
  least 0.85 (measured bar 0.833).
- Kill: (b) below 0.75, or the lower bound of the excess in (a) at or below 0, on both seeds. Then the
  network reads softness at 224 and the landmark claim stops.
- Loss rule: the equality term is written only if manifest B passes (a) and (b) and fails (c). It stays
  only if it halves the shift and costs at most 0.02 on (a) and (b).
- Tier 0 alone decides nothing in favour. It can kill: arm (ii) with (b) below 0.60 means the frozen
  features hold no softness-free signal, and tier 1 is then run with low expectations.

### 2.9 Compute

Tier 0: none. Tier 1: about 5 A100-hours. Revised full plan: about 270 A100-hours (ViT-B/16 screen of 8
configurations at 3 seeds, 26; frozen configuration at 5 seeds on ViT-L/14, 18; eight ablation rows, 140;
three reference rows, 53; scoring, 30). The ViT-L/14 fit time of 3.5 hours is still an estimate.

### 2.10 Scores

Impact 6, feasibility 5, shortcut-proofness 4, novelty 3. It is the natural network for the paper, but its
table claim shrinks to "within noise on easy cells, uncertain on clean cells". The loss is known work, and
whether a LoRA fit passes the crossed softness control is not shown by anything on disk.

---

## 3. Recipe 2: canonical-band network at the smallest benchmark storage size

### 3.1 Novelty

- Grommelt, Weiss, Pfreundt, Keuper, "Fake or JPEG? Revealing Common Biases in Generated Image Detection
  Datasets", ECCV Workshops 2024, https://arxiv.org/abs/2403.17608 (found by search). Size and JPEG biases
  in a detection benchmark; removing them changes robustness and cross-generator results. This is the
  closest statement of the problem.
- Damer et al., PW-MAD, https://arxiv.org/abs/2108.10291 (search summary): keeps only images with at least
  90 pixels between the eyes. A size rule at the data level.
- OrthoMAD, https://arxiv.org/abs/2208.07841 (search summary): includes a 64 by 64 low-resolution set.
- Singh and Ramachandra, IJCB 2022, https://arxiv.org/abs/2209.15474 (search summary): morph detection
  across camera resolutions and capture distances, in the differential setting.
- Spreeuwers, Schils, Veldhuis, "Towards robust evaluation of face morphing detection", EUSIPCO 2018
  (found; "sensitivity to simple morphing disguise techniques" confirmed, details not verified).
- Our own round 1: "one network at the common Nyquist" (`ideas/ROUND1_raw.json`, physics lens).

I found no morph-detection paper that trains and tests at one small fixed face scale to remove storage
history. The search budget ran out before I could look for it in generated-image detection, where
"resizing destroys forensic traces" is common knowledge. Novelty is unverified on that side.

### 3.2 Strongest objection

The promise is "storage history absent by construction". It fails at the only band that matters. By the
generator's own section 2.2, histories of 101 pixels and more are already invisible at 224. The histories
that move detectors are at 61 to 65 pixels. A size S near 150 puts the face at about 63 to 67 pixels,
the same band. A photo shrunk to 61 pixels with an area filter, enlarged, and resized again has passed
three filters; a photo resized once has passed one. Real filters are not brick walls, so the two differ
below the nominal cut-off. To hide a 61 pixel history the input must sit well below it, and then little is
left of the morph signal. So recipe 2 gives by-construction invariance where 224 already has it, and needs
learned invariance exactly where recipe 1 needs it.

Second objection: "softness is evidence at a fixed size" is the behaviour the paper measures in the
SelfMAD release (97% of photos stored small are flagged) and calls a failure. Admissible genuine images do
not have equal sharpness at a fixed size: defocus, denoising, JPEG, a different resize kernel or factor
all change it. SMDD renders arrive at native size; FRLL crops arrive after a threefold reduction.

### 3.3 Cheapest confound and the control

Softness at size S. Measured: the Laplacian floor for morph against halves rises as resolution falls (0.76
at 512, 0.87 at 224). At S near 150 I expect a single statistic at 0.9 or more (expected, not measured).
A morph head at 0.95 would then be a band-power reader. Controls: the best statistic computed on the
resized arrays at S, beside the history probe and beside the morph head; and the flag rate on blurred
genuine photos.

### 3.4 Where the recipe contradicts the record

- "The size flag with interpolated position embeddings, from existing code": the project's CLIP builder
  refuses any size other than 224 when weights are loaded (`mambamorph-code-a46/smadcvpr/archs_a12.py`,
  lines 36 to 37: "any other res is refused, since timm would resample the pretrained position
  embedding"). Form (a) needs a code change. Form (b), resize down and up again, is a blur made from two
  resizes; under "no new blur or resize code" it needs the author's explicit yes.
- "The loader's resize averages when it shrinks": true for the training loader (PIL bilinear,
  `smadcvpr/common.py` line 859). Verified by reading the line, not by a test.
- The first test names blur crops under `/mnt/t7/smad_next/RS1/crops/`. The manifest there has JPEG 50,
  JPEG 70 and the 50% shrink-and-enlarge pool, and no blur set (`/mnt/t7/smad_next/RS1/manifest.csv`, set
  counts). Crops of the existing blurred frames must be made first.
- The softened ladder copies exist only as aligned frames, not as face crops.

### 3.5 Feasibility by 14 Nov

The sweep is cheap and its data exist: `/mnt/t7/smad_next/AR1/crops/main` (18,245 files),
`/mnt/t7/smad_next/RS1/crops/main` and `amend`, `/mnt/t7/smad_heldout/a46_corrective_20261108/rgb_clip/`
with three kernels of the history pools (`e7area`, `e7bicubic`, `e7lanczos` for MorDIFF, DiM-A,
Greedy-DiM). As a second network family in the screening grid it doubles wave 1 and needs the code change.
Not worth it before the sweep says a usable size exists.

### 3.6 Revised design

1. Recipe 2 is no longer a candidate network. It becomes a measurement and, if it passes, one ablation
   arm of recipe 1.
2. Measurement: frozen CLIP ViT-L/14 through timm directly, sizes 224, 182, 154, 140, 126, 112, position
   embeddings resampled by timm; the double-resize form only with the author's yes.
3. At each size: a history probe (photo against its own stored copy, per pool and per kernel), the same
   contrast for the best single statistic on the resized arrays, a cross-tool morph head (warp-only
   against two-person morph) and its excess over the best statistic.
4. The figure "where storage history stops being readable, and what the morph head has lost by then" goes
   into the paper whatever the outcome. It explains why SMDD-trained detectors live in the 61 to 65 band.
5. Only if a size passes (3.8): one ViT-B/16 arm of recipe 1 at that size, with and without the 61 pixel
   copies, five seeds, as an ablation row. The claim is "an input-side alternative", not "by
   construction".
6. Softness is never called evidence. The flag rate on blurred genuine photos is printed for every arm.

### 3.7 First test

- Data: FRLL photos and their stored copies as crops: `G_raw`, `E7raw_mordiff`, `E7raw_dim_a`,
  `E7raw_greedy_dim`, `Gresample50_frll` (204 each, `/mnt/t7/smad_next/RS1/crops/`); the three-kernel
  pools in `/mnt/t7/smad_heldout/a46_corrective_20261108/rgb_clip/` (note: these are crops of SelfMAD
  crops, measured in the RS1 README at 16:45; label them so); ladder crops in
  `/mnt/t7/smad_next/AR1/crops/main`. Blur crops: make them from the existing blurred frames or drop that
  read.
- Features: as 3.6 item 2, mean-pooled tokens. Statistics: Laplacian variance and the band-power set on
  the same resized arrays.
- Head 1: logistic, photo against own stored copy, five folds by FRLL person (102), folded AUC with person
  bootstrap. Head 2: logistic, warp-only against two-person morph, trained on one engine, tested on the
  other.
- About 1 A100-hour and 2 CPU-hours; half a day.

### 3.8 Pass and kill

- Pass: a size exists where, on every 61 to 65 pixel pool and all three kernels, head 1 is at most 0.60
  (upper bound at most 0.65) and the best statistic is at most 0.60; and head 2 is at least 0.95 with an
  excess over the best statistic of at least 0.03 (lower bound above 0).
- Kill as a network: no such size; or at the largest size that passes head 1, the excess of head 2 has a
  lower bound at or below 0; or more than 20% of blurred genuine photos are flagged there.
- The measurement itself is kept in either case.

### 3.9 Compute

Sweep: about 1 A100-hour. If it passes: one ablation arm, 10 ViT-B/16 fits, about 11 A100-hours.

### 3.10 Scores

Impact 3, feasibility 6, shortcut-proofness 3, novelty 4. The cheap sweep is worth doing as a figure. As a
network the recipe gives invariance only where 224 already has it and makes softness its signal.

---

## 4. Recipe 3: SMDD-Ladder, a three-family ladder built only from SMDD renders

### 4.1 Novelty

- SMDD itself (Damer et al., arXiv 2203.06691; quoted and checked in
  `experiments/SM1_smdd-partner-audit-and-rebuild/result.md`).
- Huber et al., SYN-MAD 2022, IJCB 2022, https://arxiv.org/abs/2208.07337 (abstract read): training
  limited to the organisers' synthetic data. This is the protocol the row would be compared in.
- SelfMAD (Ivanovska et al., FG 2025, arXiv 2504.05504; in our record): builds its own attacks from
  genuine images. The precedent for deriving attacks from SMDD renders.
- Zhang, Ramachandra, Raja, Busch, "SynMorph: Generating Synthetic Face Morphing Dataset with Mated
  Samples", https://arxiv.org/abs/2409.05595 (abstract read): 2,450 identities, more than 100,000 morphs,
  several morphing algorithms, mated samples. Whether it has generator morphs and one-person rungs: not
  verified. This is the closest released set and must be read in full before any "new set" claim.
- Matched reconstructions as negatives in generated-image detection: Aligned Datasets (arXiv 2410.11835),
  B-Free (2412.17671), Dual Data Alignment (2505.14359). Marked "checked" in our own note
  (`03_LITERATURE_AND_METHODS.md`, A5); not reopened by me. DRCT (above) is the same idea with a
  contrastive loss.
- Same authors as SynMorph, https://arxiv.org/abs/2501.09817 (abstract read): our class page says this
  group adds GAN-reconstructed genuine images; the abstract I read does not confirm it. Not verified.

What remains new: one-render reconstructions as genuine images beside two-render mixes of the same
generator, built on the standard training source, with every camera-photo ladder held out. Incremental.

### 4.2 Strongest objection

Two of the three families teach a cue, and the third has no usable softness control.

- GAN family. All rungs are StyleGAN2 output: the SMDD render, its inversion, the mirror-code mix, the
  latent-mean morph. What separates them is the position in latent space and inversion artefacts.
  Unreviewed lead: latent averageness alone gives 0.9998, spread-matched renders score like morphs (0.46 to
  0.47), and transfer to MIPGAN-I and II is 0.38 to 0.73 (1.3). An SMDD-only network is also taught that
  StyleGAN2 output is genuine, so it cannot use generator output on the MIPGAN cells. The expected "2 to
  8%" on GAN cells has no support. The measured SMDD-trained retrains sit at AUC 0.376 on FRLL-Morphs
  StyleGAN2 (EV1 result, Part B.2).
- Mirror rung. It is the only one-person rung SMDD allows, and it is a symmetric face (asymmetry 2.1
  against 12 to 19.6; warp-only against mirror self-morph 0.99). Ranking it above the render teaches
  symmetry.
- Landmark family. No useful softening strength exists for SMDD under the image rules (1.6).

### 4.3 Cheapest confound and the control

- Diffusion rungs: sampler and noise statistics of the mixed latent, and PNG size. Measured (unreviewed):
  at 100 steps Laplacian variance alone separates two-person morphs from reconstructions at 0.966 on the
  centre of the frame, morphs being sharper; PNG size gives 0.73 to 0.80; at 20 steps statistics reach
  0.66 to 0.70 (`experiments/FZ1/result.md`, P4; PD1 diffusion result). A head can read "two noise maps
  were interpolated at this step count". Controls: train at 20 steps, test at 100 steps and on the
  published MorDIFF files against reconstructions; print the excess over PNG size.
- Landmark rungs: softness, and SMDD's StyleGAN2 texture (cue matrix row 19: one high-frequency number
  separates SMDD classes at 1.00). Control: every camera-photo ladder is unseen, read with the crossed
  softness contrast of 1.5.
- Benchmark cells: the border, if read on our frames (1.4).

### 4.4 Where the recipe contradicts the record

- "SMDD-trained MADation-recipe retrains hold under history matching on landmark cells" rests on frames
  with the border and on pools above 100 pixels. The same retrains flag 59 to 87% of photos with the
  MorDIFF history (1.7), and their AMSL number is disputed (1.8).
- The in-pool diffusion probe (0.987) is cross-validated inside FRLL with second contributors shared
  between folds (`experiments/FZ1/result.md`, P2 limitation). It is an upper bound for transfer.
- The diffusion blocks folder lists 130 entries, at least two of them files (`BLOCKS.json`,
  `events.jsonl`), and the diffusion part of paired differences (PD1) counts 129 blocks; the recipe says
  102 complete blocks. Minor, but the block list must be fixed before use.

### 4.5 Feasibility by 14 Nov

Landmark half: on disk (`/mnt/t7/smad_next/SM1/img/armc`, `arme`, `armcr`). Diffusion half: the generator
runs on Athena only after the equivalence gate of the diffusion generation experiment (DG1), which has not
run. Encoding takes 13 seconds per image on the unshared DGX; the A100 rate is not measured. 6,000 renders
are realistic, 25,000 are not. GAN half: nothing has run on Athena; drop it.

### 4.6 Revised design

1. Role: the comparable row (SMDD-only training) and a set to release. Not the headline.
2. Hosts: SMDD training-split genuine renders only.
3. Landmark family: rebuilt morphs with balanced partners; both warped halves and warp-only images as
   genuine. No mirror rung in training.
4. Diffusion family, only if the first test passes: the pinned diffusion autoencoder, unchanged, on 6,000
   renders; reconstruction is genuine and tied to nothing else (policy A); two-render mix is the morph; 20
   steps with a 100-step subset.
5. No GAN family.
6. Same backbone, crop, schedule, threshold rule and reports as the revised recipe 1; no order term.
7. The paper states that SMDD allows no softening strength in the 61 to 95 pixel band, and reads the
   storage and softness controls on camera-photo pools, all unseen.
8. Ablation rows: released SMDD; rebuilt, balanced partners; + halves and warp-only; + diffusion rungs.
9. Claim: at the level of the published SMDD-trained rows on landmark cells, with lower fixed-threshold
   miss; weaker than the camera-photo row on the clean MAD22 cells; no claim on GAN cells.
10. Release: pair lists, code and the derived images, shared with the SMDD authors as their terms ask.

### 4.7 First test

Part A, no generation.

- Train a mixing head on the existing diffusion blocks of colorFERET and FRGC persons
  (`/mnt/t7/smad_research/diffae-expanded123-v1/run/`; exists; features are those of the diffusion part
  of paired differences (PD1) under `/mnt/t7/smad_next/PD1/diffae/`, path to confirm with its owner).
  Frozen CLIP ViT-L/14, mean-pooled, logistic; two-person morph against reconstruction of the same host.
- Test on the FRLL arms of the earlier MorDIFF controls (features under
  `/mnt/t7/smad_next/FZ1/feats/clip_mad`; exists): two-person morph against reconstruction at 20 steps;
  the same at 100 steps; published MorDIFF against reconstructions; reconstruction against camera photo;
  same-person mix against two-person morph (printed only). Person bootstrap; PNG size and Laplacian
  variance as floors.

Part B, render to photo, about 1 to 2 A100-hours after the generation gate has passed.

- The diffusion autoencoder on 600 SMDD renders: 600 reconstructions and 300 two-render mixes at 20
  steps. Same head, trained on renders only, same FRLL reads.

### 4.8 Pass and kill

- Pass: two-person morph against reconstruction on FRLL at 20 steps at least 0.90 (lower bound at least
  0.85); published MorDIFF against reconstructions at least 0.85; the 100-step read at least 0.80; excess
  over PNG size at least 0.10; reconstruction against camera photo at most 0.65.
- Kill the diffusion rungs: render-trained head below 0.80 at 20 steps; or the proxy of part A below
  0.85; or the 100-step read below 0.70 (then the head reads the step count); or reconstruction against
  camera photo above 0.65.
- If killed, recipe 3 is the landmark rebuild row alone, which the SMDD audit (SM1) already builds.

### 4.9 Compute

Part A: none. Part B: 1 to 2 A100-hours. Full revised row: about 90 A100-hours (generation on 6,000
renders 25 to 40, to be measured; three rows at five seeds on ViT-L/14 about 53).

### 4.10 Scores

Impact 5, feasibility 5, shortcut-proofness 4, novelty 3. Reviewers will ask for the SMDD-only row, so it
is needed. Its GAN and mirror rungs teach cues and its landmark family has no softness control of its own.

---

## 5. What I could not verify

- Novelty beyond ten searches and five abstracts: the search budget of the session ran out. Not searched:
  fixed small face scale in generated-image detection; ordinal or ranking losses in face anti-spoofing;
  the full text of SynMorph, of Kashiani et al. and of MorDeephy.
- Whether the 112.7 pixel softening is visible at 224 (1.6), and the IED of the aligned frames.
- The SMDD inter-eye distance of 63.65 pixels (the generator's unreviewed measurement).
- Which of the two AMSL values for the ViT-L/14 retrains is right (1.8).
- The fit time of ViT-L/14 on an A100, and every generator rate on an A100.
- That timm's resampled position embeddings keep frozen CLIP features usable at 112 to 182 pixels.
- All numbers marked unreviewed: clean-negative test (CN0), paired differences (PD1), frozen features
  (FZ1), identical and mirrored inputs (AD1b).
