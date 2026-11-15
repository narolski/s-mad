# Round 3 vetting, lens "What frozen foundation features read, and a shared mixing direction"

11 Nov 2026. Reviewer role: CVPR area chair with an image-forensics and morph-detection background.
Reviewed file: `ideas/round3/mechanism_ideas.md`. I ran no experiment. I read records, listed folders and
printed existing JSON results. No GPU, no cluster, no image opened, no sealed file opened.

Terms. S-MAD = single-image morphing attack detection. AUC = area under the ROC curve (0.5 = chance).
EER = equal error rate. CLIP, DINOv3 = pretrained image encoders. LoRA = low-rank adapters on a frozen
encoder. E7 = the existing, approved shrink-and-enlarge history control. FR = face recognition.
Rungs: R0 camera photo, R2w warp-only image, R3m mirror self-morph, R3 same-person morph (two sessions),
R4 two-person morph. In the paired-differences records the same rungs are called x0, x1, xm, x2, x3.

"Measured" = a number in a record file, cited. "Unreviewed" = an owner's first number, no independent
review. "I expect" = my prediction.

## 0. Verdicts in ten lines

1. Idea 1 (three-level ordinal score): **revise**. Keep it as a three-arm labelling comparison on the
   landmark family. Drop the generator levels, the mirror twin in the upper contrast and the tie penalty
   as a mechanism.
2. Idea 2 (code-factorised twins): **revise**. Keep it as an audit instrument for diffusion morphs. Add a
   fresh-noise cell. Its registered first test is already answered by a record written at 18:12.
3. Idea 3 (layer selection with a fixed eraser): **drop** as a method. It re-proposes round-1 idea M3 inside
   the network, and the first measurement of the pooled version shows nothing to erase.
4. Three records written between 18:08 and 18:14 contradict or pre-answer parts of all three first tests.
   The generator could not have seen them. They are unreviewed.
5. The mirror self-morph is not a trace-matched twin for landmark tools. A 32-pixel thumbnail separates
   it from a two-person morph at 0.93; the background alone gives 0.90 (measured, unreviewed).
6. The "second-person" level is confounded with warp size and source disparity. The control rung is
   missing: a warp-only image toward the two-person mean shape.
7. On diffusion morphs the wanted order is violated in frozen features: same-person mixes score above
   two-person morphs (0.25 and 0.44, measured, unreviewed, one fold).
8. Twin evidence gives no route to state-of-the-art numbers on generator cells: twin-trained frozen heads
   reach 31 to 39% EER on the published GAN cells (measured, unreviewed).
9. None of the three ideas raises a number in the published tables. Their value is in what may be claimed.
10. My web search stopped after 14 searches (session budget used up). Novelty statements are bounded by that.

## 1. Facts from the record that the write-up missed

All from files written at about the same time as the ideas file. All unreviewed.

| Fact | Value | Source |
|---|---|---|
| Landmark: mirror self-morph vs two-person morph, logistic probe on a 32 x 32 block-mean thumbnail | 0.935 (OpenCV-style engine), 0.927 (FaceMorpher) | `experiments/AR1/baselines.json`, keys `frgcferet|*|R4vsR3m|thumb32` |
| Same contrast, face blanked (background only) | 0.901 / 0.889 | same, `...|background` |
| Landmark: same-person vs two-person morph, thumbnail / background / PNG size | folded 0.62 to 0.65 / 0.54 to 0.59 / 0.51 to 0.52 | same, `...|R4vsR3|*` |
| Landmark: probe trained directly on same-person vs two-person morph, frozen features of released nets | 0.909 and 0.931 (SelfMAD features), 0.889 and 0.878 (a MADation-recipe retrain) | `experiments/AR1/README.md`, section 5, gate G-c |
| Landmark: mean-difference direction for the second-identity step, 536 hosts | CLIP mean token 0.821 [0.786, 0.853]; CLIP class token 0.825; DINOv3 mean token 0.699 | `experiments/PD1_signal-isolation-paired-differences/landmark/q1_*.json` |
| Landmark: photo vs warp-only image, mean-difference direction | DINOv3 at 512: 0.715 to 0.737; CLIP mean token at 224: 0.548 to 0.570 | same files, step `pipeline` |
| Diffusion, FERET and FRGC hosts: two-person morph vs same-person mix under the head trained on same-person mixes / on two-person morphs | 0.249 [0.149, 0.358] / 0.438 [0.278, 0.606] | `.../diffae/result.md` and `first_pass.json` (one fold) |
| Diffusion: head trained on two-person morphs, same-person mix vs reconstruction | 0.991 | same |
| Diffusion: reconstruction vs camera photo under the mix-trained head | 0.260 (photos score above reconstructions) | same |
| Diffusion: two-person morph vs camera photo, mix-trained head / PNG size | 0.876 / 0.877; excess -0.001 [-0.17, 0.18] | same |
| Diffusion: dedicated second-identity direction | 0.793 [0.700, 0.883], reading "not consistent" | same |
| GAN, full run, 256 hosts: two-person morph vs same-person mix | 0.611 [0.572, 0.655] (one-person head), 0.661 [0.617, 0.711] (two-person head); floor 0.515 | `.../gan/res_clip_pool.json`, Q3 |
| GAN: twin-trained heads on published cells (FRLL-Morphs StyleGAN, MAD22 MIPGAN-I, MIPGAN-II) | AUC 0.72 / 0.73 / 0.64 and 0.75 / 0.70 / 0.64; EER 31 to 39% | same, `benchmarks` |
| GAN: E7 flag rate of the twin-trained binary heads at the 5% threshold | 4.4 to 8.3% | same, `flag_rates` |
| GAN: removing the softening direction from the features | AUC 0.8016 to 0.8024; flag rate 4.4% to 3.9% | same, Q4 (a) |
| Landmark ladder partners are look-alikes | median FR cosine 0.234; benchmarks 0.04 to 0.12 | `experiments/ID0_identity-shrinkage-triage/result.md` |
| The inverted noise codes of the diffusion material (A43) are not on disk; one inversion costs 143 to 157 s on the shared DGX | | listing of `/mnt/t7/smad_heldout/a43`; `experiments/AD1b/result.md`; `experiments/DG1_diffusion-generation-athena/README.md` |
| Athena accepted no job at 17:40; nothing generated | | `experiments/DG1_diffusion-generation-athena/result.md` |
| An earlier consistency loss gave no gain | | `NOTEBOOK.md`, line 15 (A49; not re-verified by the lead; small data) |

## 2. Idea 1: three-level ordinal score trained on trace-matched one-person twins

### 2.1 Novelty (what I found)

- The two endpoints are published labelling habits. Same-person "selfmorphs" as genuine: MorDeephy
  (Medvedev, Shadmand, Goncalves, ICPRAM 2023, https://arxiv.org/abs/2208.03110). One image blended with a
  transformed copy of itself as attack: SelfMAD (Ivanovska et al., FG 2025, https://arxiv.org/abs/2504.05504).
- Reading two identities from one image exists: OrthoMAD (Neto et al., BIOSIG 2022,
  https://arxiv.org/abs/2208.07841) and IDistill (Caldeira et al., EUSIPCO 2023,
  https://arxiv.org/abs/2306.03002). Our own retrains of the OrthoMAD recipe do not separate StyleGAN3
  morphs from renders (0.57 to 0.58, `experiments/AG5/result.md`, reviewed).
- A three-class scheme exists only in the differential setting (criminal, accomplice, genuine; University
  of Bologna group, seen in a search result, paper not opened).
- Ordinal losses are standard (CORAL, CORN; survey https://arxiv.org/abs/2503.00952).
- Not found: a three-level ordered label (genuine, one-person manipulation, two-person morph) for
  single-image detection, or a three-arm comparison of the two habits against it. Round 1 already had two
  related targets (mixing-fraction regression T6, shrink-factor regression M5 in `ideas/IDEAS_v1.md`).
- Not verified by me: MorphGuard (arXiv 2505.10497), Kashiani et al. (IJCB 2023), Borghi et al. (2021).
  They are in `14_CLASS_DEFINITIONS.md`; my search budget ended before I could re-open them.

What remains new: the ordered label and the labelling comparison. It is modest.

### 2.2 Strongest objections

1. **The upper level is not shown to be a second-person reading.** Same-person and two-person morphs of
   the ladder differ in more than identity: the two-person warp is larger, and hair, glasses, collar and
   skin tone differ more. The record itself notes that a same-person morph already shows a ghosted
   background and clothing outline (`experiments/AR1/README.md`, section 8). So the level-2 margin may
   read "how different the two sources are". Attackers choose look-alikes to make that small.
2. **The first test is close to decided.** A direct probe already gives 0.88 to 0.93 for same-person vs
   two-person morph, and a plain mean-difference direction in CLIP gives 0.82. PNG size gives 0.51 and a
   thumbnail 0.62 to 0.65. The pass marks (0.80; 0.05 above the floor) will be met. A test whose
   outcome is known decides nothing.
3. **The mirror pass mark is void.** "Two-person vs mirror at least 0.80" is met by a 32-pixel thumbnail
   (0.93) and by the background alone (0.90). The mirror twin does not change the background and gives
   a symmetric face. If it sits at level 1 with a margin below level 2, the network learns "asymmetric
   face with ghosted surround". SMDD has one render per identity, so on the SMDD arm the mirror twin is
   the only twin. The upper level cannot be trained honestly on SMDD.
4. **Generator levels train a fingerprint split.** The design puts generator reconstructions at level 1.
   The SMDD genuine class is 25,000 StyleGAN2 renders at level 0. The network must then tell one kind of
   generator output from another. That is the cue the paper criticises.
5. **One ordered axis contradicts the diffusion record.** Under a head trained on the mixing trace,
   same-person mixes score above two-person morphs (0.25), and camera photos score above reconstructions
   (0.26). The order genuine < reconstruction < same-person mix < morph is not what the features show.
   The write-up lists this as a risk; the record shows it has happened (unreviewed, one fold).
6. **"The class ruling becomes a threshold choice" hides a cost.** EER does not depend on the threshold,
   so the tables do not show it. At the upper threshold only the level-2 margin is left. With an AUC of
   0.65 to 0.85 between the upper levels I expect well under half of the two-person morphs caught at the
   threshold that flags 5% of same-person twins. This number must be printed.
7. **No table number rises.** The write-up says so itself ("equal to the round-2 arm within seed spread").
   The "second-person column" can be printed for any detector without ordinal training.
8. **The comparator is confounded.** "Only data and loss differ from MADation" is two changes. The ordinal
   arm needs FRGC and colorFERET photos for same-person twins; a binary arm on the same images is missing.
9. **The tie penalty is unproven here.** One earlier consistency loss gave no gain (A49, small data, not
   re-verified). Softened copies at every level do the same job through data.
10. **Level-0 composition needs a ruling.** The class proposal lists warp-only images as single-subject
    manipulation; the brief asks that they are not separated from the photo. In DINOv3 tokens at 512 a
    mean direction separates photo from warp-only at 0.72 to 0.74 (unreviewed), so the tie is not free.

### 2.3 Cheapest confound and its control

Cheapest explanation of "two-person vs same-person at 0.80 or more": **warp size and source disparity**.
The two-person warp moves the host further, so interpolation softening and the ghosted surround are
stronger. Softness as file size is excluded already (PNG size 0.51). Warp size is not.

Controls, in order of cost:

- Print the floor for this contrast: best of the 27 cached simple statistics (`/mnt/t7/smad_next/AF0/cues/ar1.npz`),
  same-person vs two-person morph. It was computed only for the warp-only contrasts so far.
- Dose inside the two-person class: rank correlation of the upper-level score with the landmark shape
  distance of the two sources and with FR dissimilarity, and the partial correlation of each given the
  other. Same-person vs two-person AUC inside the overlapping band of shape distance.
- The missing rung: host warped toward the mean shape of host and **other person**, texture from the host
  only. The approved warp path builds it in CPU minutes (round-1 idea D4 proposed it). The upper-level
  read-out must not separate it from the existing warp-only image (toward the same person's shape).
  A zero-cost first look exists: the 1,000 "zero-field" images of the alpha-field probe (AF0) are exactly
  this warp, but on other persons and another database mix, so it is descriptive only.
- Mirror twins are evaluation-only.

### 2.4 Feasibility by 14 Nov

- Data named by the idea exist: `/mnt/t7/smad_next/AF0/feat/dinov3_512/ar1.tokens.npy` (17.4 GB),
  `/mnt/t7/smad_next/AF0/feat/{dinov3_512,clip224}/bench_s.tokens.npy`,
  `/mnt/t7/smad_next/PD1/landmark/feat/clip224/ar1.npz`, `/mnt/t7/smad_next/PD1/gan/feats/clip/G.npz`,
  `/mnt/t7/smad_next/PD1/diffae/feat/clip/tr.npz`. The landmark benchmark features of the paired-differences
  cache were still being written (three parts at 18:18).
- Frozen-feature test: feasible today on CPU. Use pooled features; do not re-read the 17 GB token file for
  a per-patch head on the loaded machine unless the pooled result asks for it.
- Full training: needs the SMDD rebuild (its cluster job was failing and is being re-staged, `NOTEBOOK.md`),
  Athena (no job accepted at 17:40), a new loss in the MADation code and a pre-run review. Same-person twins
  exist for 536 hosts only; a fixed held-out fifth leaves 107 hosts, whose interval is about plus or minus
  0.09 (see the one-fold intervals). Arm differences below 0.06 to 0.08 will not be resolved.
- I rate the full version as possible but tight: one landmark-only comparison, three arms, three seeds.

### 2.5 Revised design

Scope: landmark family only for any training claim. Generator families are report-only.

1. Three arms on the MADation recipe (CLIP ViT-L/14 with LoRA, one linear head), identical images and
   identical softening: (A) same-person twins labelled genuine; (B) same-person twins labelled attack;
   (C) ordinal, three levels.
2. Level 0: camera photos, their E7 copies, warp-only images of both warp sizes. Level 1: same-person,
   two-session morphs only. Level 2: two-person morphs. Softened copies keep their level.
3. Mirror self-morphs get no label. They are scored and reported.
4. Generator reconstructions and mixes get no label. SMDD renders stay genuine as in the published
   protocol. No generator-fingerprint split is trained.
5. The ordinal form is chosen on frozen features: shared-direction cumulative link if the trace direction
   and the second-identity direction agree (cosine at least 0.5), otherwise a two-step head (probability
   of "manipulated", then probability of "two persons" given manipulated). The two-step head is one network
   with two logits and a fixed product; the author must rule whether that counts as score fusion.
6. No tie penalty in the main arms. It is one optional ablation.
7. A fixed, person-disjoint set of 107 hosts is held out before any fit.
8. Reported for every arm and every released detector: benchmark error with the neutral-only genuine
   column; E7 flag rate at the 5% threshold; two-person vs same-person AUC with its floor and inside the
   overlap band of shape distance; share of two-person morphs caught at the threshold that flags 5% of
   same-person twins; where warp-only, mirror and reconstruction images land.
9. All seeds are reported. No seed is picked.

### 2.6 First test (frozen features, CPU)

- Data: pooled CLIP features of the landmark ladder (`/mnt/t7/smad_next/PD1/landmark/feat/clip224/ar1.npz`,
  mean patch token and class token), DINOv3 mean patch token (from `.../AF0/feat/dinov3_512/ar1.tokens.npy`,
  as the paired-differences run already does), genuine photos native and E7
  (`.../AF0/feat/clip224/bench_s.tokens.npy`), simple statistics (`.../AF0/cues/ar1.npz`), landmark files
  and FR embeddings of the ladder (`/mnt/t7/smad_next/AR1/`), zero-field images of the alpha-field probe
  (`.../PD1/landmark/feat/clip224/af0.npz`) as the descriptive warp control.
- Heads, linear, five person folds of the paired-differences landmark run: (A) two-person morph vs
  {photo, warp-only, same-person morph}; (B) {same-person, two-person} vs {photo, warp-only};
  (C1) cumulative link; (C2) two-step.
- Metrics on held-out hosts, OpenCV-style engine decides, FaceMorpher descriptive:
  M1 two-person vs same-person AUC and its excess over the simple-statistic floor;
  M2 the same inside the overlap band of shape distance, and warp toward a two-person shape vs warp toward
  a same-person shape under the upper-level read-out;
  M3 two-person vs {photo, warp-only};
  M4 E7 flag rate on FRLL and MAD22 genuine photos at the 5% threshold;
  M5 share of two-person morphs caught at the threshold that flags 5% of same-person twins;
  M6 cosine between the trace direction and the second-identity direction;
  M7 fit on one engine, score the other.
- Time: 2 to 3 CPU-hours. The clean warp rung adds CPU minutes and about ten GPU-minutes of features.

### 2.7 Pass and kill

- **Pass** (the ordinal arm earns GPU time): arm C is within 0.01 of the better binary arm on M3, within
  0.03 of arm A on M1, has M4 at most 10%, and the second-person reading survives M2 (AUC in the overlap
  band at least 0.65 with lower bound above 0.55; the two warp sizes at most 0.60 apart).
- **Kill 1** (label adds nothing): arm A matches arm B on M3 within 0.01 and on M4 within 3 points. Then
  "twins as genuine" is the simpler choice; the three-arm table is reported as a finding and no ordinal
  network is trained. I expect this outcome: in the one-fold record the two-person head beats the
  one-person head on both contrasts (0.980 vs 0.933; 0.759 vs 0.652).
- **Kill 2** (upper level reads warp size): M2 in the overlap band below 0.60, or the two warp sizes at
  0.65 or more. The column is then named "source disparity" and no second-person claim is made.
- **Kill 3**: M4 above 15% for arm C while a binary arm is at 10% or less.

### 2.8 Compute and scores

First test: 0 GPU-hours (ten GPU-minutes with the clean warp rung), 2 to 3 CPU-hours. Full, only after a
pass: three arms, three seeds, about 3 A100-hours per fit (the generator's estimate, not measured on
Athena), 27 A100-hours.

Impact 5, feasibility 5, shortcut-proofness 4, novelty 5.

## 3. Idea 2: code-factorised one-person twins for diffusion and GAN morphs

### 3.1 Novelty (what I found)

- The two-part code is the published design of the diffusion autoencoder: a semantic part and a
  stochastic part that "captures stochastic details" (Preechakul et al., CVPR 2022,
  https://arxiv.org/abs/2111.15640, abstract read).
- The morph rule (average of semantic codes, slerp of noise codes at 0.5) is stated in the Fast-DiM
  paper (Blasingame and Liu, https://arxiv.org/abs/2310.09484, read through a page fetch). That paper has
  one partial ablation: white noise in place of the encoded noise code, with the averaged semantic code.
  It measures attack strength, not detection. It reports no noise-only or semantic-only mix.
- MorDIFF (Damer et al., IWBF 2023, https://arxiv.org/abs/2302.01843) interpolates both codes; no
  one-person control.
- Matched reconstructions as hard negatives exist in generated-image detection: DRCT (Chen et al., ICML 2024,
  https://proceedings.mlr.press/v235/chen24ay.html) and Aligned Datasets (Rajan et al., ICLR 2025,
  https://arxiv.org/abs/2410.11835).
- Not found: partial-code mixes used as one-person controls or training negatives in morph detection.
  My search ended before a dedicated query on this; treat "not found" as weak.

### 3.2 Strongest objections

1. **The registered first test is already answered.** On the FERET and FRGC pool the head trained on
   two-person morphs scores same-person mixes against reconstructions at 0.991 (unreviewed, one fold).
   That is the "pass" branch of the cross-application test. Only the dose correlation is still open.
2. **"Noise-code mixing trace" is not yet separated from "detail was regenerated".** Under the mix-trained
   head camera photos score above reconstructions (0.26). So the direction points from the reconstruction
   toward the photo. Diffusion morphs are sharper than reconstructions (Laplacian variance 0.966 at 100
   steps, unreviewed). The plain reading: a 20-step reconstruction is smooth, and any render from a noise
   map that is not the image's own inversion gets detail back. A noise-only mix with another person's
   noise code cannot tell these two readings apart. A mix with fresh Gaussian noise can.
3. **The noise-only mix may carry the partner's layout.** An inverted noise map is not white noise; it
   holds spatial residue of its image (hairline, collar, background). The FR gate checks identity, not a
   ghosted surround.
4. **The audit gains little for the adapted releases.** They already fail to separate morph from
   reconstruction (0.40 to 0.49). A new one-person cell adds a figure, not a finding. Only the
   frozen-encoder ViT-L/14 release and our probe are informed by it.
5. **No route to the published cell.** On morph vs camera photo the mix-trained head equals PNG size
   (0.876 vs 0.877, unreviewed). "A network can still detect these morphs through the mixing trace" is
   not supported for the published contrast.
6. **Training use depends on idea 1**, which is cut back to the landmark family above.
7. **Feasibility of the renders.** The inverted codes of the existing diffusion material are not stored.
   Inversion on the shared DGX costs 143 to 157 s per image. The renders need Athena, the equivalence gate
   of the diffusion generation (DG1), and a job that saves the codes.

### 3.3 Cheapest confound and its control

**Detail level, with reversed sign** (the softness cue seen from the other side). Control on existing
features: score each camera photo and its E7 copy with the morph-vs-reconstruction probe, and correlate
the probe score with Laplacian variance inside each class. Control in the renders: the fresh-noise cell,
and the Laplacian variance and PNG size of every cell printed beside the probe score.

### 3.4 Revised design

1. Purpose: say what the probe and the one separating release read on diffusion morphs. No training use
   before 14 Nov.
2. Cells per host, same steps, storage and frame: reconstruction; noise mix with **fresh Gaussian noise**
   (no second image); noise mix with the host's mirror; noise mix with another person; semantic-only mix;
   the morph. The generator and the existing interpolation function run unchanged; only the job list
   changes.
3. Gates: FR (every noise mix verifies against the host and not the partner; the semantic-only mix is
   reported); no undefined slerp (identical inputs gave NaN in the identical-inputs test, AD1b).
4. Read-outs: the probe trained on morph vs reconstruction; the released detectors through their own
   crop path; Laplacian variance and PNG size per cell.
5. Hosts: the 102 neutral FRLL photos and the FERET and FRGC hosts of the paired-differences run. Twenty
   steps first; 100 steps for FRLL only.
6. The diffusion generation jobs on Athena (DG1) must save both codes, or the renders cost a second
   inversion.
7. StyleGAN3: only the code-statistics ceiling test on `/mnt/t7/smad_next/PD1/gan/latents.npz`. No new
   render. The full paired-differences run already shows the head falls to 0.47 against spread-matched
   renders (unreviewed).

### 3.5 First test (existing features, CPU, under one hour)

- T1 detail sign. Fit the probe on two-person morph vs reconstruction at 20 steps
  (`/mnt/t7/smad_next/FZ1/feats/clip_mad/a43.npz`, recipe `src/FZ1/fz1_probe.py`, folds by person). Score
  the 204 FRLL photos native and E7 (`/mnt/t7/smad_next/FZ1/feats/clip_mad/eval.npz`). Report the AUC of
  native vs E7 and the share of photos scored above their own E7 copy.
- T2 dose. Spearman correlation of the out-of-fold score of the 200 morphs with the semantic-code distance
  of their sources (`/mnt/t7/smad_next/ID0/feat/diffae.npz`) and with FR dissimilarity (columns of
  `/mnt/t7/smad_heldout/a43/data/manifests/a43.csv`).
- T3 floor inside classes. Spearman correlation of the probe score with centre-crop Laplacian variance
  inside the morphs and inside the reconstructions.
- T4 second pool. The same three numbers on `/mnt/t7/smad_next/PD1/diffae/feat/clip/tr.npz`.
- T5 GAN ceiling. AUC of code statistics against the image probe and the residual, as the generator
  defined it.
- All files exist (listed). Person bootstrap of the record.

### 3.6 Pass and kill

- **Kill** (no renders; the probe reads detail level): native vs E7 at 0.80 or more with the native photo
  scored higher, or a within-class correlation with Laplacian variance of 0.5 or more in absolute value.
  The finding is then "the probe reads regenerated detail", and the existing same-person mixes are enough.
- **Pass** (render the cells): native vs E7 at most 0.65 and within-class correlation at most 0.3 in
  absolute value. In between: render the 102 neutral FRLL hosts only.
- After the renders. "Mixing of two images" holds only if the other-person noise mix scores above the
  fresh-noise mix at 0.70 or more. If the fresh-noise mix scores like a morph (morph vs fresh-noise mix
  at most 0.60), the claim becomes "detail not from the image's own inversion". Semantic averaging is
  readable only if the semantic-only mix separates from the reconstruction at 0.65 or more.
- Dose: a correlation with semantic-code distance of 0.30 or more would be the first sign of a
  second-person reading on diffusion morphs. I expect it inside plus or minus 0.15.

### 3.7 Compute and scores

First test: 0 GPU-hours, under 1 CPU-hour. Renders: 1 to 2 A100-hours for three extra cells on about 640
hosts at 20 steps (scaled from the generator's estimate; not measured on Athena), 0.5 GPU-hours of
features. Drop the renders if Athena has not accepted a job by the morning of 13 Nov.

Impact 4, feasibility 6, shortcut-proofness 6, novelty 5.

## 4. Idea 3: ladder-selected layers and tokens with a fixed nuisance eraser

### 4.1 Novelty (what I found)

- Closed-form linear erasure: LEACE (Belrose et al., NeurIPS 2023,
  https://proceedings.neurips.cc/paper_files/paper/2023/hash/d066d21c619d0a78c5b557fa3291a8f4-Abstract.html).
  The guarantee is against linear readers only.
- Intermediate CLIP blocks with learned block weights for forensic detection: RINE (Koutlis and
  Papadopoulos, ECCV 2024, https://arxiv.org/abs/2402.19091).
- Freezing a principal subspace and adapting the rest: Effort (Yan et al., ICML 2025,
  https://arxiv.org/abs/2411.15633).
- In morph detection: MADation (Caldeira et al., WACV Workshops 2025, https://arxiv.org/abs/2501.03800).
  A search snippet also shows R-FLoRA (arXiv 2604.17321), a "residual-statistic-gated" LoRA on CLIP
  ViT-L/14 for S-MAD; I did not open it.
- Inside our own programme: round-1 idea M3 ("host-orbit paired head with interventional nulling",
  `ideas/IDEAS_v1.md`) is the same eraser on pooled features, and question Q4 of the paired-differences
  experiment (PD1) runs it. The brief says not to re-propose unchanged. Moving the projection inside the
  network is the only change.

What remains new: choosing the junction block by ladder selectivity. That is a tuning rule, not a method.

### 4.2 Strongest objections

1. **It contradicts an established fact.** "The frozen part cannot learn storage cues" is true and beside
   the point: frozen features already carry them. The frozen-encoder ViT-B/16 release moves from 39.7% to
   69.6% flagged under history. A statistic fitted on genuine photos alone fails the history control in
   CLIP (0.582), DINOv3 (0.356) and diffusion-autoencoder features (0.000)
   (`experiments/ID0_identity-shrinkage-triage/result.md`, unreviewed).
2. **A linear eraser at one block does not bind trainable blocks above it.** They can rebuild softness
   from second-order token statistics. The write-up's own read-out 4 (standard deviation over patches) is
   such a statistic. The write-up concedes this.
3. **Where it was measured, there was nothing to erase.** GAN family, pooled CLIP: removing the softening
   direction changes the AUC by 0.001 and the flag rate from 4.4% to 3.9% (unreviewed). Twin-paired
   training already gave flag rates of 4 to 8%.
4. **The eraser would be tested on the nuisance it was fitted to.** E7 has two registered strengths. An
   honest test needs an unseen history, and new resize or JPEG code is forbidden.
5. **Fitting the expression direction on FRLL pairs would fit on benchmark genuine photos**, and those
   pairs differ in capture detail (1.43 times file size). Only FERET or FRGC pairs could be used.
6. **Neither resolution is free.** CLIP at 224: softness floor 0.87, warp-only readable at 0.55 to 0.57.
   DINOv3 at 512: floor 0.76, warp-only readable at 0.72 to 0.74 by a mean direction (unreviewed).
7. **Cost.** A 24-block profile needs a hooked extraction on a saturated GPU, then an eraser in the training
   code, then 10 to 20 fits. It competes with the main chain for the same three days.

### 4.3 Cheapest confound

A "selective" block can be selected by chance: 24 blocks times two token types times six read-outs is
about 290 cells tested against three thresholds on 107 held-out hosts. Control: choose the block on the
OpenCV-style engine and four folds, confirm on the fifth fold and on the other engine. For the eraser:
the cheapest explanation of a low E7 flag rate is that the eraser saw the same E7 strengths; control is
an unseen strength from existing files (the 80-pixel SMDD copies).

### 4.4 Verdict and what to keep

Drop the method. Two measurements are worth keeping, both already owned elsewhere:

- The final-block read-out comparison belongs in the first test of idea 1 (which read-out feeds the heads).
- The pooled-feature projection is question Q4 of the paired-differences experiment (PD1). Its landmark
  result decides whether any eraser is worth a line in the paper.

### 4.5 The one test, if the lead wants a number

- Data: `/mnt/t7/smad_next/AF0/feat/{clip224,dinov3_512}/{ar1,bench_s}.tokens.npy` (exist),
  `/mnt/t7/smad_next/PD1/landmark/feat/clip224/smdd.npz` (1,500 SMDD renders with their 80-pixel copies).
- Read-outs: mean patch token, CLIP class token, per-dimension standard deviation over patches, inner-face
  mean. Head: paired linear one-person head, person folds of the paired-differences landmark run.
- Metrics, OpenCV-style engine: warp-only vs two-person morph minus the simple-statistic floor; photo vs
  warp-only; E7 flag rate at the 5% threshold on FRLL and MAD22; and the same flag rate after projecting
  out a softening direction fitted on the SMDD pairs only (an unseen strength and source for the photos).
- **Pass**: one read-out with excess at least 0.05 (lower bound above 0), photo vs warp-only at most 0.60,
  flag rate at most 15%, confirmed on the held-out fold and on FaceMorpher. **Kill**: no read-out meets
  all three; frozen final-block features then offer no selective read-out, and protection must come from
  the data protocol. For the projection: kept only if it halves a flag rate that is above 10% before
  projection; if the flag rate is already at most 10%, the eraser is redundant.
- Time: 2 to 3 CPU-hours, 0 GPU-hours.

Impact 3, feasibility 3, shortcut-proofness 3, novelty 3.

## 5. Points that affect the whole programme

1. **Stale first tests.** Three records from the last hour pre-answer or contradict parts of these ideas
   (table in section 1). Any idea of this round should be re-checked against the paired-differences
   results before it is given an owner.
2. **Mirror twins.** For landmark tools the mirror self-morph is separable from a two-person morph by a
   thumbnail and by the background. Use it for the lower (trace) contrast only, never as the negative of a
   second-person claim.
3. **"Second person" has no clean measurement yet.** It is measured on our look-alike pairs only and is
   confounded with warp size. The warp-only rung toward a two-person shape is the cheapest missing control.
4. **Generator cells.** Twin evidence reaches 31 to 39% EER on the published GAN cells and equals file size
   on diffusion morph vs photo (unreviewed). Table numbers there will come from re-synthesis evidence.
   The paper must say so under both class policies.
5. **Kurtosis floor.** Worth adding as a floor statistic. Prior art for kurtosis in band-pass domains is
   Pan, Zhang and Lyu (ICCP 2012) and Lyu, Pan and Zhang (IJCV 2014). Two cautions: use bands well below
   the E7 cut-off (Haar level 1 leaks), and expect less than the predicted halving, because the heavy
   tails come from eye, mouth and outline edges that the landmark warp aligns.
6. **Rulings needed from the author.** The level of warp-only images. Whether two logits of one network
   combined by a fixed rule count as score fusion. And one conflict in the record: the landmark-ladder
   record says "a same-person morph counts as a morph" while the class proposal makes it a single-subject
   manipulation.
7. **Power.** Same-person twins exist for 536 hosts. A held-out fifth resolves AUC differences of about
   0.06 to 0.08 and no less.

## 6. Not verified

- Every number marked unreviewed. I recomputed nothing.
- That the FRLL native and E7 rows are both in `FZ1/feats/clip_mad/eval.npz` (taken from the sources
  section of the record; I could not open the array on this machine's system Python).
- That the diffusion generation jobs (DG1) save the inverted codes.
- The per-fit and per-render A100 times.
- Papers named in section 2.1 as "not verified".
- R-FLoRA (seen in one search snippet).
- Absence claims ("not found") rest on 14 searches and two page fetches.

## Sources

- MorDeephy: https://arxiv.org/abs/2208.03110
- SelfMAD: https://arxiv.org/abs/2504.05504
- OrthoMAD: https://arxiv.org/abs/2208.07841
- IDistill: https://arxiv.org/abs/2306.03002
- Ordinal regression survey (CORAL, CORN): https://arxiv.org/abs/2503.00952
- Diffusion Autoencoders: https://arxiv.org/abs/2111.15640
- Fast-DiM / design space of diffusion autoencoders for face morphing: https://arxiv.org/abs/2310.09484
- MorDIFF: https://arxiv.org/abs/2302.01843
- DRCT: https://proceedings.mlr.press/v235/chen24ay.html
- Aligned Datasets: https://arxiv.org/abs/2410.11835
- Quality-agnostic deepfake detection (pair consistency across quality): https://arxiv.org/abs/2309.05911
- LEACE: https://proceedings.neurips.cc/paper_files/paper/2023/hash/d066d21c619d0a78c5b557fa3291a8f4-Abstract.html
- RINE: https://arxiv.org/abs/2402.19091
- Effort: https://arxiv.org/abs/2411.15633
- MADation: https://arxiv.org/abs/2501.03800
- Kurtosis in band-pass domains (Pan, Zhang, Lyu): https://cse.buffalo.edu/~siweilyu/papers/iccp12.pdf
