# Round 3 vetting, lens "Paired differences as a training method"

11 Nov 2026, 18:25 CET. Reviewer role: hostile but constructive area chair with an image-forensics and
morph-detection background. Reviewed: `ideas/round3/paired_ideas.md` (three ideas).

What I did. I read the brief, `CONSOLIDATED_v2.md`, the class definitions, the cue table, and the records of
the paired-differences experiment (PD1), the alpha-field probe (AF0), the landmark ladder (AR1), the
frozen-features experiment (FZ1), the identical-and-mirrored-inputs check (AD1b), the identity-shrinkage
triage (ID0), the diffusion generation on Athena (DG1) and the SMDD rebuild (SM1). I listed data folders. I
searched the literature on the web. I ran nothing: no experiment, no GPU, no cluster, no git. No sealed file
was opened. No image was loaded.

Terms. S-MAD = single-image morphing attack detection. AUC = area under the ROC curve (0.5 = chance).
EER = equal error rate. Host = one photo of one person. Twin = the image that went through every step of a
blend except the mixing. Dose = how much the two mixed images disagree. LoRA = low-rank adaptation.
DiffAE = diffusion autoencoder; z_sem = its semantic code; x_T = its noise map. LDA = linear discriminant
analysis. "Unreviewed" = an owner's first number that no second agent has checked.

---

## 0. Verdicts

| Idea | Verdict | Impact | Feasible by 14 Nov | Shortcut-proof | Novelty |
|---|---|---|---|---|---|
| 1. Self-morph ladder training (pair term + noise term) | **revise** | 6 | 4 | 4 | 4 |
| 2. Noise-only mirror mix for diffusion morphs | **revise** (audit tool only; training use dropped for this deadline) | 5 | 4 | 3 | 5 |
| 3. Dose-matched second-identity test and optional head | **revise** (keep the test, drop the head) | 4 | 7 | 5 | 4 |

One sentence each:

1. The data design (exact twins, history crossing, no second identity) is worth one training arm. The mirror
   partner and the new loss are the weak parts, and two of the idea's own expectations are contradicted by
   numbers already in the record.
2. As a training method it cannot be built in time and its positive carries two cheap cues. As a small
   audit (which code makes a diffusion morph look like a morph, and is the reconstruction too easy a twin)
   it is cheap and may change how existing numbers are read.
3. A single matched point does not answer the question. A dose curve with a face-recognition validity check
   does. It protects the wording of the paper; it is not a method.

---

## 1. Facts I checked that bear on all three ideas

### 1.1 Data that exist (listed at 18:14 to 18:23 CET)

| Item named by the generator | Path | State |
|---|---|---|
| Landmark ladder rungs | `/mnt/t7/smad_next/AR1/img/frgcferet/{opencv,facemorpher}/{R2w,R2wm,R3,R3m,R4}` | exist, 536 files each |
| Graded FaceMorpher mixing | `/mnt/t7/smad_next/AR1/img/frgcferet/fm_graded/m000..m050` | exist, 300 files each |
| Softened zero-dose images | `/mnt/t7/smad_next/AF0/lists/ar1soft.csv`, images in `/mnt/t7/smad_next/AF0/img/soft/{amsl112,fm61}` | exist: 1,200 rows = photo and warp-only image of 200 hosts, two strengths |
| Softened blends | none | **do not exist** |
| AF0 zero-field, 0.25 and 0.5 blends, warped halves | `/mnt/t7/smad_next/AF0/img/{train,val}/{zero,u25,u50,halfA,halfB}` | exist (val: 200 each of zero, u25, u50) |
| Landmark features | `/mnt/t7/smad_next/PD1/landmark/feat/clip224/ar1.npz`, `.../dinov3_512/af0_ar1_mean.npz`, `af0_bench_s_mean.npz`; patch tokens in `/mnt/t7/smad_next/AF0/feat/{clip224,dinov3_512}` | exist for the ladder and the benchmark subsample |
| Features of the softened images | none in either cache | **missing** (queued in the AF0 CLIP queue) |
| Features of the graded set | none in either cache | **missing** (lists exist: `AF0/lists/ar1g.csv`) |
| Simple statistics, mirror distances | `/mnt/t7/smad_next/AF0/cues/ar1.npz`, `/mnt/t7/smad_next/AF0/feat/clip224/ar1.mirror.npy` | exist |
| Diffusion blocks, CLIP features | `/mnt/t7/smad_next/PD1/diffae/feat/clip/{tr,f256,fr512,ad1b}.npz` | exist |
| Codes of the mirrored-inputs check | `/mnt/t7/smad_next/AD1b/smoke_gen/codes_xT.npz` (4 persons) | exists |
| Codes of its full run | `/mnt/t7/smad_next/AD1b/gen/codes_xT.npz` | **not written**; the run was at 32 of 80 inversions after 5,108 s (`gen_attempt1.log`) |
| Diffusion generation set B (536 hosts) | `/mnt/t7/smad_next/DG1/` | inputs aligned; **no image generated** (`experiments/DG1_diffusion-generation-athena/result.md`, 17:40) |

### 1.2 Resources

- Athena does not accept our jobs yet (notebook entry 11 Nov 17:35; entry 18:10 says "while Athena is not
  usable"). Notebook entries stamped 20:30 to 00:20 carry times later than the machine clock (18:23); I treat
  the entries written last in the file as the newest.
- The DGX runs one DiffAE inversion in about 160 s (measured in the AD1b log), against 13 s when idle.
- One measured hint on fit time: the first network of the morph-free experiment (AD4) on a rented A100 took
  "about 70 minutes" (notebook 18:05; not read by me, model not checked). The generator's 8 A100-hours per
  fit is an estimate.

### 1.3 Numbers in the record that the write-up does not use

All unreviewed unless marked.

- **The mirror step is the easiest step and has the lowest dose.** Projection AUC of the within-host step,
  OpenCV-style engine, three features: mirror mix 0.98 to 0.99; same-person mix 0.82 to 0.92; whole
  two-person morph 0.89 to 0.98 (`experiments/PD1_signal-isolation-paired-differences/landmark/q1_clip_cls.json`,
  `q1_clip_mean.json`, `q1_dino_mean.json`). The matched mirror twin gives the same 0.99. Median pixel
  difference to the host: mirror 9.6, same-person 15.1, two-person 18.8 grey levels
  (`experiments/AR1/README.md`, section 5). So separability does not follow dose. Something else separates
  mirror blends. The training-free mirror distance separates them from two-person morphs at 1.0
  (`experiments/AF0/mirror_clip224.json`, position-aligned rows).
- **A plain two-class head on frozen CLIP at 224 px does not show the history failure.** Trained on photo
  against two-person morph on one engine and tested on the other, it flags 3 to 6% of history-matched FRLL
  genuine photos at the threshold that flags 10% of untouched photos (`experiments/AF0/cn0.json`).
- **A training change already removed the history effect in our own networks, at a cost.** The same random
  resample, JPEG and blur chain on both classes (A22: +14.5 to -0.2 points, 5.1-point cost; A30 amendment 6:
  19 to 40% flagged down to 4 to 8%) (`02_REVIEW_AND_SHORTCOMINGS.md`, line 20).
- **History crossing with twins is already registered** as arm (e) of the SMDD rebuild (SM1): renders, shrunk
  renders, warped halves, shrunk halves against morphs and shrunk morphs, two-person morphs, normal
  two-class loss (`experiments/SM1_smdd-partner-audit-and-rebuild/prereg.md`, lines 258 to 268).
- **Diffusion first pass.** The one-person head ranks two-person morphs above reconstructions at 0.955, but
  it ranks morphs against camera photos at 0.876 where PNG size alone gives 0.877. It scores reconstructions
  below photos (0.26). It scores same-person mixes above two-person morphs (0.25)
  (`experiments/PD1_signal-isolation-paired-differences/diffae/result.md`).
- **GAN first pass.** The one-person head reads its own training contrast on held-out hosts at only 0.70
  (`.../gan/first_pass_clip_pool_fold0.json`).

---

## 2. Idea 1: self-morph ladder training (pair term + noise term)

### 2.1 Novelty

Closest work I found:

- **SelfMAD** (Ivanovska, Todorov, Damer, Jain, Peer, Struc, FG 2025, arXiv 2504.05504,
  https://arxiv.org/abs/2504.05504). Positives are made from genuine images only: an image is blended with
  a geometrically transformed copy of itself. Label 1 for the blend, 0 for the genuine image. This is the
  same premise as Idea 1: no second identity in training. (Pipeline details from a third-party summary of
  the paper; I did not read the full text today.)
- **Self-blended images** (Shiohara and Yamasaki, CVPR 2022, arXiv 2204.08376,
  https://arxiv.org/abs/2204.08376). The source of that premise in deepfake detection. I read the abstract
  only. Whether a mirrored copy is ever the partner, and whether unblended transformed copies are used as
  negatives, is **not verified**.
- **Selfmorphs as genuine images** (MorDeephy, Medvedev et al., ICPRAM 2023, arXiv 2208.03110,
  https://arxiv.org/abs/2208.03110; MorphGuard, arXiv 2505.10497, https://arxiv.org/abs/2505.10497). Same
  images as our same-person blends, opposite label. From search summaries.
- **Single-center loss** (Li et al., CVPR 2021,
  https://openaccess.thecvf.com/content/CVPR2021/html/Li_Frequency-Aware_Discriminative_Feature_Learning_Supervised_by_Single-Center_Loss_for_Face_CVPR_2021_paper.html).
  Pulls genuine faces to one centre and pushes manipulated faces away. This is the "noise term" in feature
  space. In linear form the noise term is LDA with the genuine covariance, which is textbook.
- **Aligned real and fake pairs as the training set** (Rajan et al., ICLR 2025, arXiv 2410.11835,
  https://arxiv.org/abs/2410.11835; Guillaro et al., CVPR 2025, arXiv 2412.17671,
  https://arxiv.org/abs/2412.17671). Each fake is a reconstruction of a real image, so content, size and
  format cancel. This is the "exact twin" principle in generated-image detection.
- "The Alpha Blending Hypothesis" (arXiv 2605.10334, https://arxiv.org/abs/2605.10334) argues that deepfake
  detectors mainly find compositing traces and trains on real images plus self-blends. The arXiv page marks
  the current version as withdrawn (4 Nov 2026). Not a citable result; a sign the topic is crowded.
- In our own round 1: the within-host paired head with a variance penalty across genuine constructions
  (`ideas/IDEAS_v1.md`, M3), and the mirror self-morph as a **negative** (D2).

What remains new: (a) the mirror image as blending partner (one search in morph detection and forgery
detection found nothing; absence not proven); (b) exact warp-only twins crossed with storage history as the
negatives of self-made positives; (c) a controlled comparison with SelfMAD on the same 25,000 renders.
The loss is not new. I did not find a within-host dose-ranking loss in morph detection (one search; not
verified beyond that).

### 2.2 Strongest objection

**The idea rebuilds SelfMAD and inherits its measured weakness, and the two fixes it relies on are not
shown to work.** SelfMAD is the release that fails hardest in our audit (0%, 45%, 97% of genuine photos
flagged by processing; established). Idea 1 says the cause is missing twins and missing history crossing. That is a
reasonable guess. It is not measured. Two numbers in the record point the other way:

1. In the landmark first pass the one-person head beats one band-power statistic by 0.021, interval
   [-0.037, 0.081] (unreviewed). By the registered reading of PD1 (excess at least 0.05) this fold is
   "mixed", not "works". What a one-person blend teaches these features may be softness.
2. The ablation meant to tie audit and method ("no twins reproduces the SelfMAD failure") may show nothing
   in the chosen recipe. A plain head on frozen CLIP at 224 px flags only 3 to 6% of history-matched FRLL
   photos (`experiments/AF0/cn0.json`, unreviewed). The history failure is established for SelfMAD (HRNet,
   own crop) and MADation ViT-B/16. For the ViT-L/14 recipe the brief says "no usable statement yet". If the
   no-twin arm does not fail, the method has nothing to remove.

### 2.3 Cheapest confounds and the controls that exclude them

| Cue | Why it would give the same numbers | Is it controlled in the write-up? | Control that excludes it |
|---|---|---|---|
| **Softness** (cheapest) | A blend has about half the Laplacian variance of its halves (established). One statistic reaches 0.912 where the head reaches 0.933 | One-sided. Softened copies exist only for zero-dose images. A head that says "soft and came through the warp" passes the crossed contrast as written if softened morphs are never tested | Full 2 x 2: {native, softened} x {twin, blend} on the same hosts. Both off-diagonal contrasts and the softened-against-softened cell are read. Needs 1,200 softened blends built with the verified call |
| **Left-right symmetry** | A mirror blend at fraction a has its left-right asymmetry cut by the factor (1 - 2a) against its twin, in every variant. Uneven fields and fractions below 0.5 change the amount, not the fact: the mixed-in content is always the face's own other half. Inside a host this is a perfect dose proxy with no doubled structure | Partly (decoy, mirror-difference statistic at most 0.65). The measured step AUC of 0.98 to 0.99 at the lowest dose says the by-product is already what features read | Train a head on mirror pairs only and one on same-person pairs only. Read the rank correlation of each score with the training-free mirror distance among untouched photos, and whether mirror blends score below two-person morphs (half the dose). If not: no mirror partner |
| **Storage history** | Crossing uses the registered strengths only. For SMDD renders one strength exists (256 to 80 px, scale 0.3125). A network can learn those strengths and stay sensitive to others | No | Leave one strength out in training and test on it; test on the SMDD 80-px copies when training on FRGC and colorFERET |
| **Warp trace** | Zero-dose twins are warped, photos in the pool are not; a head can still read "warped" if most positives' twins are warped and most pool photos are not | Yes (photo against warp-only shift at most 0.3 standard deviations) | Keep. Add the AF0 number as the bar: the dense head shifted warp-only images by 0.73 (FaceMorpher) and 0.30 (OpenCV) |
| **Border** | Uncovered regions | Yes (constant-colour blanking in all classes) | Keep |
| **Generator fingerprint, SMDD variant** | All training images are StyleGAN2 renders at 256 px. FRLL photos are camera photos. The threshold comes from a development pool of renders | No | Take the threshold from a camera-photo development pool (FRGC, colorFERET outside sealed persons) and print the flag rate of FRLL photos at it |
| **Five SMDD partners, file attributes** | Not in play: no SMDD morph is used, all images are written by one writer | n/a | none needed |
| **Capture detail and expression** | Not in training. FRLL smiling files differ in detail | Reported without claim | Keep; score neutral-only genuine photos beside the full class |

### 2.4 Where the write-up contradicts measured facts

1. "The same thing at growing dose in mirror blends, same-person blends and two-person morphs." Measured:
   the mirror step is the most separable (0.98 to 0.99) at the lowest dose (9.6 against 15.1 and 18.8). The
   one-person head scores mirror blends like two-person morphs (0.486) and same-person blends below them
   (0.652). The order is not the dose order. In the diffusion family the one-person head puts same-person
   mixes above two-person morphs (0.25). All unreviewed.
2. "No term compares a blend of one host with a genuine image of another, so a file or source property has
   no term to enter through." The two terms together do compare them: all genuine images sit at one
   constant and every blend sits a margin above its twin, hence above every genuine image. Protection comes
   from what is in the genuine pool (twins, softened copies), not from the form of the loss. A normal
   two-class loss on the same pool has the same protection.
3. "The no-twin ablation is expected to reproduce the SelfMAD failure." See 2.2, point 2.
4. "The noise term carries pairs over to one image" rests on a Gaussian model of one GAN fold (paired 0.92,
   unpaired 0.78). It is an expectation. The comparison it proposes, (B) against (A), compares LDA with a
   paired logistic head. The fair comparator is an ordinary unpaired logistic head, which also sees host
   variance.
5. "Softened images ... 200 of its hosts" is right, but the softened features are not cached and softened
   blends do not exist. The write-up says so; the kill rule nevertheless uses a contrast that only softened
   zero-dose images can serve.

### 2.5 Feasibility by 14 Nov

- First test: feasible in half a day. Needs 1,200 new softened blends (CPU; the same call built 1,200
  softened copies in about an hour under load) and features for 2,400 images.
- Full version: at risk. It needs a ladder build of about 125,000 images plus shrunk copies on CPU cores
  that we do not have today (WCSS closed, DGX load 80 to 146), a new training loop (host batches, two-term
  loss) with a pre-run review, and Athena, which does not accept jobs yet. Other owners queue for the same
  cards. Three days leave no slack for a failed first fit.
- The registered history-crossed SMDD arm (SM1, arm e) covers twins and crossing with two-person morphs. Idea 1 should be added
  to that experiment as arms, not run as a second pipeline.

### 2.6 Revised design

Name: one-person positives with exact twins and crossed history, as arms of the SMDD rebuild (SM1).

1. Recipe and loss stay the MADation recipe (CLIP ViT-L/14, LoRA, linear header, its two-class loss). Only
   the training images change. This keeps "data changed, nothing else" true against MADation and against
   SM1 arm (e).
2. Arms, equal counts, one pre-declared seed, extra seeds only for spread and all printed:
   (N) one-person blends against plain renders; (TW) blends against their exact twins and plain renders;
   (TX) as TW with every image also at the registered shrink strength; (TX2) as TX with two-person morphs
   in place of one-person blends, which is SM1 arm (e) and serves as the reference.
3. The pair term and the noise term become one optional fifth arm (TX-L). It earns a place only if it
   lowers the flag rate of an unseen genuine source at the development threshold; AUC alone does not count.
4. Partner. Same-person second photo where a database has one (FRGC, colorFERET). For one-photo sources
   (SMDD, FFHQ) the mirror partner is allowed only if it passes the symmetry test in 2.7. If it fails, the
   SMDD-only variant needs a shifted-copy partner built with the approved warp path (needs the lead's yes
   and verification against the unchanged tool), and the write-up must say that this is SelfMAD's
   construction with twins.
5. A symmetric decoy as a zero-dose image is added only with a yes, and only if the mirror partner is used.
6. History: leave one registered strength out of training and test on it.
7. Tie to the audit on the architecture where the failure is established. If arm (N) on CLIP ViT-L/14 flags
   at most 10% of history-matched genuine photos, the sentence "twins and crossing remove the failure" is
   void for this recipe. Then the same four image sets are fitted on the SelfMAD backbone (HRNet-W18, its
   own crop, code staged by the retrains experiment, AD5), or the claim is dropped.
8. Claim: "two face images were mixed". Mirror and same-person blends go into the single-subject table
   under both rulings. The author must say which ruling holds before tables are laid out.
9. Test time: one image, one forward pass, one threshold from a camera-photo development pool. No twin, no
   gate.

### 2.7 First test (frozen features, linear heads, half a day)

Data, checked to exist: `/mnt/t7/smad_next/AR1/img/frgcferet/opencv/{R2w,R2wm,R3,R3m,R4}` (536 each);
`/mnt/t7/smad_next/AF0/lists/ar1soft.csv` (photo and warp-only image of 200 hosts at the 112-px and 61-px
strengths); features `/mnt/t7/smad_next/PD1/landmark/feat/clip224/ar1.npz` (CLIP ViT-L/14 class and mean
patch token, 224 px) and `/mnt/t7/smad_next/PD1/landmark/feat/dinov3_512/af0_ar1_mean.npz` (DINOv3 ViT-L/16
mean patch token, 512 px); benchmark features `af0_bench_s_mean.npz` and
`/mnt/t7/smad_next/AF0/feat/clip224/bench_s.tokens.npy`; statistics `/mnt/t7/smad_next/AF0/cues/ar1.npz`;
mirror distances `/mnt/t7/smad_next/AF0/feat/clip224/ar1.mirror.npy`.
To build (approved kind, verified call `src/AF0/soften.py`): same-person blend, mirror blend and two-person
morph of the same 200 hosts, OpenCV-style engine, two strengths: 1,200 images. Then features of 2,400
softened images.

Heads, 5 folds by person (the PD1 folds), linear:
- S: paired logistic on (same-person blend, its twin).
- M: paired logistic on (mirror blend, its matched twin R2wm).
- S+: S plus crossed pairs from the softened training hosts (native blend with softened twin, softened blend
  with native twin), with softened and native twins tied to one score.
- T: two-person paired head (reference). N: unpaired logistic, one-person blends against plain photos.

Metrics on held-out hosts, person bootstrap, each beside the best of the 27 simple statistics (signed) and
Laplacian variance at the backbone's input size:
(a) native twin against native two-person morph; (b) softened twin (61 px) against native morph;
(c) native twin against softened morph (61 px); (d) softened twin against softened morph (112 px);
(e) rank correlation of the score with the mirror distance among untouched photos, and mirror blend against
two-person morph; (f) share of history-matched FRLL and corrected MAD22 genuine photos flagged at the native
5% threshold; (g) EER per benchmark cell against history-matched genuine photos, beside the frozen-encoder
MADation ViT-L/14 header on our frames (AMSL 21.6, WebMorph 9.8, OpenCV 4.4, FaceMorpher 3.9%;
`experiments/FZ1/result.md`, table P1).

Note (my expectation, not measured): at a 224 px input the 112-px strength may be invisible, so cells (b)
to (d) are informative mainly for DINOv3 at 512 px and for the 61-px strength.

### 2.8 Pass and kill

- **Pass** (go to the fits): head S+ has the minimum of (a), (b), (c) at 0.85 or more with every lower
  bound above 0.75; (d) at least 0.70; (f) at most 10% on both sets; S+ within 0.03 of T on (a); on the
  FRLL-Morphs OpenCV and FaceMorpher cells S+ is at most 10 EER points worse than the frozen MADation
  header.
- **Kill**: head S+ has the minimum of (a), (b), (c) below 0.75 on both feature sets. Then what one-person
  blends teach these features is softness and the line stops before any fit.
- **Mirror partner kill**: head M has a rank correlation with the mirror distance above 0.35 in size among
  untouched photos, or scores mirror blends at or above two-person morphs (AUC 0.50 or less). Then no
  mirror partner, and the SMDD-only variant depends on point 4 of 2.6.
- **Loss arm kill**: the LDA head (genuine covariance, shrinkage by inner cross-validation) does not beat
  the ordinary unpaired logistic head by 0.03 unpaired AUC in at least two of the three families (landmark;
  GAN `/mnt/t7/smad_next/PD1/gan/feats/clip/G.npz`; diffusion `/mnt/t7/smad_next/PD1/diffae/feat/clip/tr.npz`).
  Then arm TX-L is not fitted.

### 2.9 Scores

Impact 6, feasibility 4, shortcut-proofness 4, novelty 4. If it passes it joins audit and method on one
architecture and removes the need for a second identity in training. But the data design overlaps a
registered arm and SelfMAD, the softness and symmetry controls are open, and the fits depend on a cluster
that is not available today.

---

## 3. Idea 2: noise-only mirror mix for diffusion morphs

### 3.1 Novelty

- **Diffusion autoencoders** (Preechakul et al., CVPR 2022, arXiv 2111.15640,
  https://arxiv.org/abs/2111.15640). The paper already reports what the write-up lists as "not measured by
  anyone": with z_sem fixed, changing x_T "only affects minor details, such as the hair and skin details,
  the eyes, or the mouth"; encoded maps "show some residual details and do not look normally distributed".
  Interpolation is linear for z_sem and spherical for x_T. (Quotes as returned by a page-reading tool on
  the ar5iv copy; I did not read the PDF myself.)
- **Inverted noise maps are not white noise**: Parmar et al., "Zero-shot Image-to-Image Translation"
  (arXiv 2302.03027, https://arxiv.org/abs/2302.03027) add a regulariser because DDIM-inverted maps stray
  from white noise; Huberman-Spiegelglas et al. (arXiv 2304.06140, https://arxiv.org/abs/2304.06140) make
  the same point for their noise space. From search summaries.
- **MorDIFF** (Damer et al., arXiv 2302.01843, https://arxiv.org/abs/2302.01843) mixes both codes. I found
  no ablation there that mixes one code only.
- **DiM** (Blasingame and Liu, arXiv 2301.04218, https://arxiv.org/html/2301.04218v4). Variants change only
  the noise path: A = lerp of z, slerp of x_T; B = lerp of x_T; **C (their default) = the two images are
  averaged pixel-wise and that "pre-morph" is given to the stochastic encoder**; D = an OpenCV morph as
  pre-morph. No variant mixes one code only, and none is about what a detector reads. (From the tool's
  reading of the HTML version.)

What remains new: single-code mixes and a fresh-noise render used to attribute a detector's response, and a
one-photo positive for diffusion morphs. I found no prior work on either in morph detection (two searches;
absence not proven).

### 3.2 Strongest objection

**It cannot be built in time as a method, and nothing shows it is needed.** No image of the design exists.
The 32-person codes are not written yet. The 536-host set has not started because Athena takes no jobs.
On the DGX one inversion takes about 160 s. Meanwhile the diffusion first pass (unreviewed) already shows
that a head trained on same-person mixes of two real photos transfers to two-person morphs at 0.955. So
for databases with two sessions the one-photo positive is not needed. It is needed only to scale to
one-photo sources (FFHQ, SMDD), which is the 40 GPU-hour part that will not happen by 14 Nov.

Second objection, on the state-of-the-art path. "Leads on the column that matters" names a column that is
in no published table. On the published contrast (morph against camera photo) the same one-person head
reaches 0.876, PNG size alone 0.877, and reconstructions score below photos (0.26; unreviewed). A network
pinned so that a reconstruction scores like a photo gives up the generator fingerprint that carries the
published numbers. That is honest, but it is not state of the art on the published MorDIFF and DiM cells.

### 3.3 Cheapest confounds and the controls that exclude them

| Cue | Why it would give the same numbers | Control |
|---|---|---|
| **"Not this photo's own inversion"** (cheapest) | A reconstruction uses the exact inverted map of its own photo. Any other map (mixed, or fresh random noise) breaks that fit. A head may read the misfit, not mixing | The fresh-noise render. The write-up has it as a reading rule; it must be the first thing measured, because it also bears on every existing "morph against reconstruction" number |
| **Symmetry of the fine-detail layer** | If the encoder is close to flip-equivariant, x_T(mirror) is close to the mirror of x_T, and the spherical mix of a map with its own mirror is a left-right symmetric map. The layout stays the host's, but skin and hair detail become symmetric. "No symmetric face" then holds for layout only. Not measured | CPU check on saved codes: cosine between x_T(flipped photo) and the flipped x_T(photo). Replace the mirror by a second photo or by another person's noise map with the host's z_sem |
| **Detail energy** | A spherical mix of two nearly orthogonal maps (cosine distance 0.98) keeps the norm but carries each photo's residual detail at about 0.71. Sharpness of the render changes. FZ1 found Laplacian variance alone at 0.966 for one contrast | Simple-statistic floor per arm at the backbone's input size and on the centre crop; equal step count |
| **Step count, writer, size** | Known cue for this generator | Controlled (20 steps, one writer) |
| **Generator fingerprint** | Reconstruction against photo | Controlled by the 0.45 to 0.55 rule, at the price named in 3.2 |
| **Storage history** | Detail may not survive the published storage size | Named, not built. Score arms at the stored size too |
| **Expression and capture detail** | Only if FRLL smiling files are partners | Use neutral partners only |

### 3.4 Where the write-up contradicts the record or the literature

1. "NOT measured by anyone: that the noise map carries capture detail." The generator's own paper says so
   (3.1).
2. "No symmetric face." True of layout by design; open for fine detail (3.3).
3. "The DiM samplers serve as a held-out generator." In DiM variant C, the default, the noise map comes
   from a pixel-averaged pre-morph, not from a spherical mix of two maps. The trace a noise-only mix teaches
   may not be the trace in those cells, and we cannot build twins for them.
4. "Existing images can only kill it." The first kill test (the PD1 one-person head on two-person morph
   against reconstruction) has already been run: 0.955 (unreviewed). It tests same-person mixes of both
   codes, so it says nothing about the noise map.

### 3.5 Feasibility by 14 Nov

- Tonight: a CPU check on 4 persons' saved codes; a small render batch on the 32 persons once their codes
  exist (the run is 40% through its inversions).
- Decisive 536-host part: only if Athena opens by 12 Nov and the generation job (DG1) keeps its plan. The
  extra renders are cheap; the inversions are the cost and are already planned.
- Training use at 5,000 hosts: not feasible in this sprint.

### 3.6 Revised design

Name: which input makes a diffusion morph look like a morph (audit of the two codes, with a fresh-noise
twin).

1. Purpose is the audit, not a training method. The training use is parked until the audit passes and the
   cluster is open.
2. Arms per host, unchanged encoder, mixing and render functions, 20 steps, one writer:
   REC (host codes), FRESH (host z_sem, new random noise, two draws), NOISE-B (host z_sem, noise map mixed
   with another person's), SEM-B (z_sem mixed with another person's, host noise map), FULL-B (the published
   recipe), NOISE-M (noise map mixed with the mirror's; kept only as a symmetry probe).
3. Scoring first with heads that already exist: the one-person and two-person heads of the diffusion arm of
   PD1 (fitted on 516 FRGC and colorFERET hosts). FRLL persons are scored only.
4. Every "morph against reconstruction" number in the paper is printed beside "morph against fresh-noise
   render" from then on, if FRESH turns out to be flagged.
5. Face-recognition check per arm: does NOISE-B verify against the partner? If not, it is a one-identity
   image under every definition.
6. Calling the unchanged functions with one code swapped adds no image operation but needs the lead's yes.

### 3.7 First test

Step 0, CPU, minutes, file that exists: `/mnt/t7/smad_next/AD1b/smoke_gen/codes_xT.npz` (4 persons; later
`/mnt/t7/smad_next/AD1b/gen/codes_xT.npz`, 32 persons, when written). Compute (i) the cosine between the
noise map of the flipped photo and the flipped noise map of the photo; (ii) lag-1 autocorrelation of a map
and its correlation with the photo's Laplacian.

Step 1, GPU, small, needs the yes of 3.6 point 6: for the persons with saved codes (32 with photo and
mirror, 16 with a second photo and another person), render the arms of 3.6 at 20 steps: about 200 renders,
between 5 minutes and 1 hour of the shared GPU.

Step 2, CPU: CLIP pooled features as in PD1 (`/mnt/t7/smad_next/PD1/diffae/feat/clip/` holds the training
features), score with the existing PD1 heads. Metric: share of persons whose arm scores above their own
reconstruction, exact binomial interval; the seven simple statistics beside it.

### 3.8 Pass and kill

With 16 to 32 persons only clear outcomes count.

- **Kill of the training idea**: FRESH scores above the reconstruction in 90% or more of persons under both
  heads. Then heads read the misfit to the photo's own inversion. A noise-only positive cannot be told from
  any re-noised render. The audit finding stays and the twin changes.
- **Kill of the noise arm**: NOISE-B at 60% or less while SEM-B is at 90% or more. Then the readable part is
  the semantic mix, and a one-photo positive would have to mix z_sem with the mirror, which gives a
  symmetric face (asymmetry 2.1 against 18.3; `experiments/AD1b/result.md`).
- **Pass to the 536-host run**: FRESH at 60% or less and NOISE-B at 90% or more. Decisive bar there: a head
  trained on noise-only mixes against reconstructions and fresh-noise renders reaches at least 0.85 on full
  two-person morphs, within 0.05 of the two-person head and 0.05 above the statistic floor.
- **Mirror partner**: dropped for the noise arm if the cosine of step 0 (i) is 0.5 or more.
- Anything between the bars: no decision before the 536-host set exists.

### 3.9 Scores

Impact 5, feasibility 4, shortcut-proofness 3, novelty 5. The fresh-noise twin may change how the
established diffusion contrast and the FZ1 probes are read, which matters for the audit. As a method it
has two cheap cues in its positive, no path to the published columns, and no data before the cluster opens.

---

## 4. Idea 3: dose-matched test and optional head for the second-identity step

### 4.1 Novelty

- **Ferrara, Franco, Maltoni**, "Decoupling texture blending and shape warping in face morphing", BIOSIG
  2019 (https://dl.gi.de/handle/20.500.12116/34232). Separate factors for shape and texture, studied for
  attack success. Bibliographic record only; content not read.
- **Selfmorphs** as genuine or as attack (MorDeephy, MorphGuard, Kashiani et al.; see
  `14_CLASS_DEFINITIONS.md`). Nobody there compares a same-person and a two-person blend at equal blend
  strength.
- **Face X-ray** type targets (already in `CONSOLIDATED_v2.md`): disagreement times mask is the known
  definition of blend evidence.

What remains new: the dose-matched contrast itself. I found none (one targeted search; not proven absent).
It is a control, small in scope.

### 4.2 Strongest objection

**One matched scalar does not isolate identity, and the matched morph may stop being an attack.**

- Matching the mean disagreement inside the face leaves everything else free: where the disagreement sits
  (contours and brows for two persons, lighting for two sessions), the mixing fraction itself (0.5 against
  a lower value, so different warp distance), and averaged shape (0.687 on exact shapes; ID0). A probe that
  passes may read any of these. A probe that fails on 300 hosts with mean-pooled frozen features may simply
  lack power.
- The generator expects a small effect. The unmatched numbers are not small: 0.88 to 0.93 on detector
  features (`experiments/AR1/README.md`, gate G-c), 0.82 to 0.83 as a CLIP projection, 0.76 for the
  two-person head (unreviewed). The whole-frame dose differs by only 25% (15.1 against 18.8). Either the
  dose response is steep or something else is read. The prior should be "open".
- The whole-frame number includes clothing and background of two sessions. Inside the face a same-person
  blend may disagree far less. The matched two-person fraction may then be 0.2 or lower. Such a blend may no
  longer verify against the partner. Then it is not a morphing attack by the definitions in
  `14_CLASS_DEFINITIONS.md`, and the comparison says nothing about attacks. This must be checked with the
  face-recognition gate before any probe is read.

### 4.3 Cheapest confounds and the controls that exclude them

| Cue | Why | Control |
|---|---|---|
| **Residual dose** (cheapest) | Graded levels are 0.1 apart; the proxy "pixel difference to the warp-only image" includes warp displacement, because the warp-only image is the exact twin of the same-person blend only | Measure dose as the disagreement of the two warped images inside the face while building (the AF0 path does this); print the dose statistic's own AUC on the matched pairs; require it near 0.5 |
| **Softness** | Follows dose | The 27 statistics on the matched pairs; excess over the best |
| **Shape averaging** | 0.687 on exact shapes | Print the shape score beside the probe; second geometry version (both in the host's shape) only if the modified target is verified against the unchanged tool |
| **Ghosted clothing and background** | Two sessions | Constant-colour blanking outside the face in all images |
| **FaceMorpher surround** | Pastes onto a double-exposed surround | OpenCV-style engine decides |
| **Session and capture detail** | Second photo from another session in both blends | Holds by the ladder's composition rule; state it |
| **Storage history, border, file attributes** | Same writer, same frame | none needed |

### 4.4 Where the write-up contradicts the record

1. "Cached CLIP ViT-L/14 and DINOv3 mean features": true for the same-person blends, not for the graded
   set (no feature file at 18:14; lists exist).
2. The FaceMorpher warp-only image is the exact twin of the same-person blend, not of any graded two-person
   level. The proxy is therefore biased against the two-person side.
3. The head "rides on Idea 1's fits": Idea 1 is not certain to be fitted. A second output trained on 536
   hosts of one tool family is not a result the paper can carry.

### 4.5 Feasibility by 14 Nov

Good. Existing-image version: CPU plus features for 1,800 graded images (queued). Deciding version: about
3,200 new images of an approved kind (uniform fractions through the verified AF0 path), under an hour of
CPU when idle, 0.3 to 0.5 shared-GPU hours of features, face-recognition embeddings for the graded levels.

### 4.6 Revised design

Name: second-identity step at equal measured disagreement (reporting control; no head).

1. Build, OpenCV-style engine through the verified AF0 path, the 536 ladder hosts: same-person blend at 0.5
   and two-person blends at 0.1, 0.2, 0.3, 0.4, 0.5, each in its own mean shape. Record the measured
   disagreement of the two warped images inside the face for every blend at build time.
2. Blank everything outside the face with one constant colour in all images.
3. Validity gate first: per two-person level, the share of blends that verify against both contributors
   (the ladder's face-recognition route). Only levels at 70% or more count as attacks.
4. Read a curve, not a point: probe score against measured disagreement for both partner types. The
   deciding statistic is the within-host comparison at the two-person level whose disagreement is closest
   to the host's same-person blend, restricted to valid levels.
5. Probe: logistic head on CLIP and DINOv3 mean features, 5 folds by person, trained on that matched
   contrast. Power check: the same recipe on the unmatched same-person against two-person contrast.
6. Printed beside it: the dose statistic's own AUC on the matched pairs, the best of the 27 statistics, the
   exact-shape score.
7. No second output is trained. The paper gets one sentence and one small figure. The result fixes the
   wording ("mixing" or "mixing and a second person") and the reading of the single-subject table.
8. A host-shape (texture-only) version is added only if the modified target shape is verified against the
   unchanged tool.

### 4.7 First test

Existing images, to decide whether the build is worth it: `/mnt/t7/smad_next/AR1/img/frgcferet/fm_graded/m000..m050`
(300 hosts) and `/mnt/t7/smad_next/AR1/img/frgcferet/facemorpher/R3` (536). CPU: mean absolute pixel
difference to the host's `m000` image inside the landmark hull for graded levels and for the same-person
blend (same reference for both sides, which removes the bias of 4.4 point 2); the level at which the doses
cross; statistics from `/mnt/t7/smad_next/AF0/cues/`. Features of the graded set when extracted. FaceMorpher
is descriptive. Then the build of 4.6. About 2 hours of CPU for the existing-image part; half a day for the
deciding version.

### 4.8 Pass and kill

- **Void**: at the dose-matched level fewer than 70% of two-person blends verify against both
  contributors. Reported as a finding: at equal in-face disagreement a two-person blend is no longer an
  attack, so dose and second identity cannot be separated on landmark morphs.
- **Kill** (no identity claim): matched AUC below 0.60 with upper bound below 0.65 on both feature sets,
  while the same recipe reaches 0.85 or more on the unmatched contrast.
- **Pass** (identity-specific trace readable): matched AUC at least 0.75, lower bound above 0.65, at least
  0.05 above the largest of the dose statistic, the 27 statistics and the shape score.
- Between: reported as open, wording stays "mixing".

### 4.9 Scores

Impact 4, feasibility 7, shortcut-proofness 5, novelty 4. Cheap and it protects the central wording of the
paper. It moves no benchmark number and its answer depends on how dose is defined.

---

## 5. Points that affect the whole programme

1. **The mirror partner carries a measured by-product in every family.** Landmark: the mirror step is the
   most separable at the lowest dose, and a training-free symmetry score isolates mirror blends at 1.0.
   Diffusion: asymmetry 2.1 against 18.3 (4 persons). The mirror rungs planned at fraction 0.5 in the
   diffusion and MIPGAN generation jobs (DG1, AG1) inherit this. A mirror blend is safe as an audit rung only
   with a symmetric decoy beside it, and as a training positive only after the test in 2.7.
2. **The softness control is one-sided today.** Softened copies exist for zero-dose images only. Until
   softened blends exist, no head can be shown to read blending and not sharpness.
3. **History may be invisible at a 224 px input.** The failure is established for SelfMAD and MADation
   ViT-B/16. A plain frozen CLIP head at 224 px does not show it (unreviewed). The method arm uses ViT-L/14
   at 224 px. The chain "failure, then a protocol that removes it" needs the failure shown on the recipe
   that is being fixed. This waits for the own-crop re-score (RS1) or needs an HRNet arm.
4. **The reconstruction may be too easy a twin for diffusion morphs.** A fresh-noise render belongs beside
   it in the audit before more weight is put on "morph against reconstruction" numbers.
5. **The honest diffusion column is not a published column.** On morph against camera photo the paired
   heads do not beat PNG size. The state-of-the-art claim on diffusion cells cannot come from this lens.
6. **Pair statistics overstate.** Print the unpaired number beside every paired one, and compare any new
   loss with an ordinary unpaired head, not only with the paired head.
7. **Rulings disagree** on same-person blends (morph; side study; third category). Idea 1 trains them as
   positives. The author's yes or no is needed before any table is laid out.
8. **Only frozen-feature tests are safe before 14 Nov.** Athena takes no jobs yet and a new training loop
   is the riskiest element in this lens.

---

## 6. Not verified

- Every number marked unreviewed, including all first-pass files of PD1, `experiments/AF0/cn0.json` and the
  Q1 projection files.
- The full texts of SelfMAD, self-blended images, MorDeephy, MorphGuard, single-center loss, the aligned
  dataset papers and Ferrara et al. I worked from abstracts, search summaries and a page-reading tool.
- That no morph detection or forgery detection paper uses a mirrored copy as blending partner, a within-host
  dose-ranking loss, single-code mixes of a diffusion autoencoder, or a dose-matched same-person control.
  These rest on a few searches.
- The native inter-eye distance of the ladder frames, hence at which input size each registered strength is
  visible.
- That the diffusion encoder is close to flip-equivariant (step 0 of 3.7 measures it).
- The fit time per network on an A100.
- Whether partner B in the mirrored-inputs check (AD1b) is a neutral photo.

## Sources

- SelfMAD: https://arxiv.org/abs/2504.05504
- Self-blended images: https://arxiv.org/abs/2204.08376
- MorDeephy: https://arxiv.org/abs/2208.03110
- MorphGuard: https://arxiv.org/abs/2505.10497
- Single-center loss: https://openaccess.thecvf.com/content/CVPR2021/html/Li_Frequency-Aware_Discriminative_Feature_Learning_Supervised_by_Single-Center_Loss_for_Face_CVPR_2021_paper.html
- Aligned datasets: https://arxiv.org/abs/2410.11835
- Bias-free training paradigm: https://arxiv.org/abs/2412.17671
- The Alpha Blending Hypothesis (listed as withdrawn): https://arxiv.org/abs/2605.10334
- Diffusion autoencoders: https://arxiv.org/abs/2111.15640
- MorDIFF: https://arxiv.org/abs/2302.01843
- DiM: https://arxiv.org/html/2301.04218v4
- Zero-shot image-to-image translation: https://arxiv.org/abs/2302.03027
- Edit-friendly noise space: https://arxiv.org/abs/2304.06140
- Decoupling texture blending and shape warping: https://dl.gi.de/handle/20.500.12116/34232
