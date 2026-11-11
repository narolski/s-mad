# Round 3, physics lens: vetting of "signatures that any averaging of two faces must leave"

11 Nov 2026, 18:25 to 19:00 CET. Reviewer: area-chair role (image forensics, morph detection). I read the brief,
`CONSOLIDATED_v2.md`, the generator's write-up (`physics_ideas.md`) and the experiment records it cites. I listed
folders and read small JSON and CSV files. I ran no experiment, no GPU job and no statistic on any image. No sealed
file was opened.

Terms. S-MAD = single-image morphing attack detection. AUC = area under the ROC curve (0.5 = chance); "folded" =
max(AUC, 1 - AUC). Ladder rungs as in the brief: R0 camera photo, R1 photo with the morphs' storage history, R2w
warp only, R3m blend with own mirror, R3 same-person morph, R4 two-person morph. IED = inter-eye distance in pixels
(about 130 px in our 512 frame). "Measured" always names a file. "Expected" is my estimate. Numbers from the
brief's "New today" list are unreviewed leads and are marked "(lead)".

Web search: 9 searches ran, then the session's shared search budget was used up. Three further searches (symmetry
in morph detection, the psychology of averaged faces, band-pass texture features in morph detection) did not run.
Novelty statements below say which references I opened and which I did not.

## 0. Verdicts

| Idea | Verdict | Impact | Feasible by 14 Nov | Shortcut-proof | Novelty |
|---|---|---|---|---|---|
| 1. Layer-count evidence (fourth-order statistics, layer-count map, bracketing test) | revise: keep the bracketing test as an evaluation instrument for every detector; the layer-count statistic gets one CPU test; the layer-count training target only if that test passes | 4 | 5 | 4 | 5 |
| 2. Left-right parity ratio | revise: reduce to one evidence row measured inside the running mirror-asymmetry test (AS0); drop the two-view trained form and the "works for every generator" claim until AS0 reports | 3 | 8 | 5 | 5 |

## 1. Idea 1: layer-count evidence

### 1.1 What the idea claims

A pixel-blend morph is two texture layers added. A softened photo is one layer at lower gain. The number of
independent layers can be read from amplitude-normalised fourth-order statistics (kurtosis of band-pass responses,
or mean |c| over root mean c squared). The generator says a gain or a compact blur does not move these numbers.
The idea then trains the network on a per-patch layer-count map and proves the read with a bracketing test: the
score must rank a morph above negatives that are sharper and above negatives that are softer.

### 1.2 Novelty (what I found)

- The "layer law" is the central-limit argument behind independent component analysis: a sum of independent sparse
  signals is less sparse than its parts. It was used to separate two superimposed images (a scene and a reflection)
  by Farid and Adelson, "Separating reflections from images by use of independent components analysis", JOSA A
  1999 (https://persci.mit.edu/pub_abstracts/farid_josa_99_abs.html; abstract page read, the Gaussianity wording
  only through a secondary page).
- Fourth-order statistics of band-pass responses are 20-year-old forensic features: Farid and Lyu, "Higher-order
  wavelet statistics and their application to digital forensics", CVPR Workshops 2003
  (https://mlanthology.org/cvprw/2003/farid2003cvprw-higherorder); Lyu and Farid, "How realistic is photorealistic?",
  IEEE Trans. Signal Processing 2005 (https://cse.buffalo.edu/~siweilyu/papers/sp05.pdf): mean, variance, skewness
  and kurtosis of wavelet sub-band coefficients per scale and orientation. Search snippets and abstracts read.
- Kurtosis of band-pass responses is a known noise meter: Zoran and Weiss, "Scale invariance and noise in natural
  images", ICCV 2009 (https://people.csail.mit.edu/danielzoran/zoranweiss09.pdf): kurtosis is about constant across
  scales in clean images and noise changes it. Abstract read.
- The second proposed statistic (mean |c| over root mean c squared) is, up to a constant, the normalised sparsity
  measure of Krishnan, Tay and Fergus, "Blind deconvolution using a normalized sparsity measure", CVPR 2011
  (https://mlanthology.org/cvpr/2011/krishnan2011cvpr-blind). That paper introduced it because blur raises it. The
  sentence "blur decreases both norms, the l2 norm more, so the ratio increases" I read only in a secondary source.
  **This contradicts the generator's invariance claim** (section 1.3).
- Morph detection, closest neighbours found: (a) noise-residual statistics across image cells: Debiasi, Rathgeb,
  Scherhag, Uhl and Busch, "PRNU variance analysis for morphed face image detection", BTAS 2018
  (https://christoph-busch.de/files/Debiasi-PRNU-variance-MAD-BTAS-2018.pdf; first three pages read). They claim
  robustness to scaling to 50% and 75%, sharpening and histogram equalisation, on their own data. (b) A morph
  treated as two superimposed faces that one network decomposes from the single image: Banerjee, Jaiswal and Ross,
  "Facial de-morphing: extracting component faces from a single morph", IJCB 2022 (https://arxiv.org/abs/2209.02933);
  Shukla and Ross, "Facial demorphing via identity preserving image decomposition", IJCB 2024
  (https://arxiv.org/abs/2408.10993). Search results read, papers not opened. (c) Texture descriptors (BSIF, LBP)
  of the early papers, cited through a review only.
- Not found in one search: a morph detection paper that states the layer law, uses a layer-count target, or uses a
  two-sided (sharper and softer) negative test. A second, targeted search could not run. The generator's own
  citations (Levin and Weiss; Pan, Zhang and Lyu) are not verified by me either.
- What remains new if it works: the bracketing test as a stated protocol in morph detection, and a dense target
  whose value does not scale with contrast. The statistic itself is textbook.

### 1.3 Strongest objection: the statistic is not blind to blur, and the window where the law can act is one octave

1. **A blur lowers these statistics by the same mechanism as a second layer.** A blur is a weighted sum of
   neighbouring samples of one layer. Summing partly independent sparse samples makes the result less sparse. This is
   why the l1/l2 ratio is used as a blur measure and why kurtosis is the classical criterion in blind deconvolution.
   The generator's argument (inside a narrow band a blur is one gain) holds only for a band so narrow that the
   kernel's response is flat inside it. The registered bands are one octave wide.
2. **The responses "the registered statistics already compute" are the wrong band.** Laplacian (ksize 1), one-level
   Haar and the 3x3 noise residual all live in the top octave (`mambamorph-code/smadcvpr/cue_floor.py`, lines 74 to
   108, read). The registered softening strengths keep frequencies only below about 0.43 cycles/pixel (target IED
   112.7 px) and 0.23 cycles/pixel (target 61.2 px) of a frame with IED 130 px (my arithmetic from
   `experiments/AS0_mirror-asymmetry/iod_nominal.json` and the strengths in `experiments/AF0/result.md`). After the
   stronger history the top octave holds interpolation residue only. Its kurtosis says nothing about layers. The
   seven FFT bands are computed on the whole frame with a window, not inside the face box, so the mid-band version
   needs new analysis code. Precedent: the mirror-asymmetry test (AS0) registered in-memory FFT band images as an
   allowed measurement (`experiments/AS0_mirror-asymmetry/prereg.md`, Guards).
3. **The usable window is about one octave.** One sanity photo in the mirror-asymmetry test shows mirror-odd energy
   over mirror-even energy of 0.82 at wavelengths 4 to 8 px, 0.52 at 8 to 16 px and 0.17 at 16 to 32 px
   (`experiments/AS0_mirror-asymmetry/check.json`, `real_photo_L_F0_Y`, exponentiated; one image, a code check, not a
   result). A ratio near 1 means texture, a ratio far below 1 means landmark-aligned anatomy. So two faces are
   unrelated layers only from about 8 px wavelength downward (0.125 cycles/pixel and above). The stronger history
   cuts at 0.23. The band 0.125 to 0.25 is the only one where layers are unrelated and content survives, and the
   stronger history reshapes it. This is my expectation from one image and arithmetic, to be measured.
4. **Pooled kurtosis in the face box is dominated by anatomy.** Local energy is high at eyes, brows and mouth and
   low on cheeks. This variance mixture is shared by both aligned faces and does not change when they are averaged.
   Only a per-block statistic (kurtosis inside small blocks, then a median over blocks) can show the law. The
   generator's first test pools over the face box.
5. **The training target inherits the two objections of round 2.** (a) t = (e1 + e2)^2 / (e1^2 + e2^2) - 1 is
   largest where the two energies are equal, at any size. On flat skin both are small and about equal, so t is near
   1 unless the noise floor zeroes it. The floor is a free number that decides where the map is non-zero. The
   registered target check (flat below busy; `CONSOLIDATED_v2.md` section 3) will catch this, but "by construction"
   is not true. (b) The map is still zero on every negative and positive on every morph, so "a global flag times an
   anatomy template" still fits it. The first dense pass had map quality 0.275 against a template baseline of 0.231
   and 0.228 after removing the template (`experiments/AF0/README.md` section 5, unreviewed). A fourth-order target
   is harder to see than the disagreement magnitude. I expect lower map quality, not higher.
6. **The dose-shape audit of released detectors is not identified.** A network score is a squashed function of
   whatever it reads. Any monotone squashing changes "the share of the change reached at a = 0.25". The dose shape
   is readable only on a statistic in log units. Drop the audit claim for detectors.

### 1.4 Cheapest confound and the control that excludes it

- **Spectral shape, read by two or three registered band powers.** Averaging lowers all bands above the alignment
  scale by a flat factor (measured 0.52 for the Laplacian). Shrink-and-enlarge removes everything above one cut-off
  and leaves lower bands alone. A logistic head on the registered band powers can therefore rank a morph above a
  sharper half and above a softened half without counting layers. The bracket excludes any monotone function of ONE
  sharpness number. It does not exclude a function of two. Control: run the 26 registered statistics through the
  same head and the same bracket (energy-only head). The fourth-order numbers count only by what they add to that
  head.
- **Noise and compression level of the photo pool.** Kurtosis reads noise (Zoran and Weiss) and quantisation. The
  smiling FRLL files are 1.43 times larger with a 4.8 times noisier backdrop (established). colorFERET is scanned
  film, FRGC is digital. Controls: genuine FRGC against genuine colorFERET (R0 by database) at most 0.60; neutral
  against smiling photo of one FRLL person at most 0.60; R0 against softened R0 at both strengths.
- **One softening family only.** The only allowed softening is the shrink-and-enlarge path at two strengths.
  "Does not react to softness" is then a statement about that family. Camera defocus, denoising and JPEG are not
  covered. Say so in the paper.

### 1.5 Where the write-up disagrees with the record

- "Softened copies exist, about 600 each" (first test): the 600 are the softened ladder copies (R0 and R2w of 200
  hosts, both engines). Of the AF0 training copies, 139 existed per strength at 18:24 (photos and uniform-0.5 morphs;
  no softened half yet). The source list (`/mnt/t7/smad_next/AF0/lists/soft_src.csv`) covers the training split only
  and alternates the strength per image. So "morph against its own softened half" on AF0 pairs cannot be read
  tonight, and a morph and its half may have different strengths. Softened R4 of the ladder does not exist.
- The softer copy at target 112.7 px may not be softer than the morph. A morph keeps 0.52 of the Laplacian
  variance. A copy at scale 0.86 loses a similar share of the top octave (expected, not measured). That makes it the
  sharpness-matched negative round 2 asked for, which is useful, but the bracket's "softer" leg must use the
  61.2 px copies, with the Laplacian variance printed per pair.
- Two of the three bracket legs are already registered in wave 4 of the alpha-field probe (held-out-tool AUC against
  warped halves and against softened halves, softened positives in training; `experiments/AF0/result.md`). New here:
  the third leg (softened morph against unsoftened half), the within-host ranking loss, and using the weakest leg as
  one number.
- The diffusion prediction (two detail layers because two noise maps are mixed at 89 degrees) fits the record
  loosely: morphs are not softer than reconstructions (Laplacian variance 0.661 and 0.966, morph higher, centre of
  the frame; `experiments/FZ1/result.md`, P4, lead), and a head trained on same-person mixes ranks them above
  two-person morphs (0.249; `experiments/PD1_signal-isolation-paired-differences/diffae/result.md`, lead). A cheaper
  reading is a rendering cue of an off-distribution noise map. The secondary read decides; nothing rests on it.

### 1.6 Feasibility by 14 Nov, and data check (listed 11 Nov, 18:15 to 18:25 CET)

| Path | Found |
|---|---|
| `/mnt/t7/smad_next/AF0/img/train/{zero,u25,u50,halfA,halfB}` | 800, 800, 800, 1,160, 1,280 files |
| `/mnt/t7/smad_next/AF0/img/val/{zero,u25,u50,halfA,halfB}` | 200, 200, 200, 320, 360 |
| `/mnt/t7/smad_next/AF0/img/soft/{amsl112,fm61}` | about 600 ladder copies each (complete); AF0 copies being written (139 per strength, no halves) |
| `/mnt/t7/smad_next/AR1/img/frgcferet/{opencv,facemorpher}/{R2w,R3,R3m,R4}` | 536 each; `fm_graded/m000..m050` present; photos under `AR1/src/{feret,frgc}` |
| `/mnt/t7/smad_next/AF0/lists/ar1soft.csv` | 1,200 rows: R0 and R2w (both engines) of 200 hosts at two strengths |
| `/mnt/t7/smad_next/AF0/ghost_targets.npz`, `feat/{clip224,dinov3_512}/ar1.tokens.npy` | present |
| `/mnt/t7/smad_heldout/a43/gen/{D20,C20,B20}/png256` | 204, 102, 200 |
| `/mnt/t7/smad_next/PD1/gan/items.csv` | present; roles x1 1,102, x2 128, x3 974, x0 256 |
| `/home/narolski/mambamorph-code/smadcvpr_data/manifests/eval.csv` | present (not opened) |

First test: feasible, CPU, half a day. Full version (targets, heads, five-arm ablation, 30 A100-hours of LoRA fits)
is feasible only if Athena opens by 12 Nov and nothing else slips; it competes with the round-2 chain for the same
three days. I would not start the training version before the first test passes.

### 1.7 Revised design

1. Split the idea into three parts that stand or fall alone: (A) the bracketing test as an evaluation instrument,
   (B) the layer-count statistic as a measurement, (C) the layer-count map as a training target.
2. (A) Bracketing test, for every detector including the released ones and ours. Three legs within host on the
   OpenCV-style engine: two-person morph against its warp-only image (negative sharper); two-person morph against the
   warp-only image softened at 61.2 px (negative softer, checked per pair by face-box Laplacian variance); softened
   morph against unsoftened warp-only image. The copy at 112.7 px is the sharpness-matched negative and is reported
   beside them. One number: the weakest leg. It is reported beside the same number for the energy-only head.
3. (A) needs 400 new files: the ladder's R4 of the 200 hosts through the approved, unchanged shrink-and-enlarge path
   at both strengths (wave 4 approval names "our own morphs"; confirm).
4. (B) Fourth-order numbers per block, not pooled: kurtosis and the l1/l2 ratio inside 32-px blocks of the face box,
   median over blocks, for the bands 0.0625 to 0.125 and 0.125 to 0.25 cycles/pixel (in-memory band images as in
   the mirror-asymmetry test) and, for reference, the registered Laplacian, Haar and noise-residual responses.
5. (B) is judged by what it adds to the 26 registered statistics, not alone.
6. (C) only if (B) passes: the layer map becomes a sixth arm of the registered five-arm ablation, with the noise
   floor fixed beforehand and the registered target check (flat below busy, contrast correlation below 0.3). The
   test-time rule stays one forward pass, mean of the top tenth of patch predictions in the face box.
7. The dose shape is reported for the statistic only. No claim that it tells which law a released detector follows.
8. Same-person morphs and mirror self-blends will be flagged (two layers). They go to the single-subject table.
9. Diffusion and GAN reads are secondary and descriptive.

### 1.8 First test (CPU, 3 to 5 hours of wall time on the loaded machine, about 6,000 images)

- Fit data: `/mnt/t7/smad_next/AF0/img/train/u50` against `train/{halfA,halfB}` (no softened image in the fit). AF0
  persons are disjoint from the ladder persons (`experiments/AF0/result.md`, Counts).
- Test data: ladder, OpenCV-style engine, the 200 hosts of `AF0/lists/ar1soft.csv`: R0 (`AR1/src`), R2w, R4
  (`AR1/img/frgcferet/opencv/`), softened R0 and R2w (`AF0/img/soft/{amsl112,fm61}`), softened R4 (to be built,
  400 files). FRLL native and history-matched frames of the four landmark families (204 each, set frllm, variants
  orig and resmatch in `smadcvpr_data/manifests/eval.csv`). Law check: `AF0/img/val/u50` with `val/{halfA,halfB}`.
  Secondary: `a43/gen/{D20,B20}/png256`.
- Features: E = the 26 registered statistics (`cue_floor.stats`, unchanged). K = per-block kurtosis and l1/l2 ratio
  for two bands and three registered responses (10 numbers).
- Heads: logistic, three versions (E, K, E+K). Regime 1: fitted on AF0 morphs against halves, scored unchanged.
  Regime 2: 5 folds by person on the ladder with the softened copies of the training folds added to both classes.
- Metrics, all with the person bootstrap of the record: (m1) weakest of the three bracket legs, head K, regime 1;
  (m2) R0 against softened R0 at both strengths and FRLL native against history-matched, head K, regime 1;
  (m3) weakest leg of E+K minus weakest leg of E, regime 2, paired; (m4) the weakest leg of E alone, regime 2 (does
  the bracket stop band energies at all?); (m5) genuine FRGC against genuine colorFERET, and FRLL neutral against
  smiling, head K; (m6) rank correlation over the 200 validation pairs between log(kurtosis of halves / kurtosis of
  morph) and log N_eff from the stored halves.
- **Pass (all):** m1 at least 0.75 with lower bound above 0.70; m2 inside 0.45 to 0.55 everywhere; m3 at least
  +0.05 with lower bound above 0; m5 at most 0.60; m6 at least 0.3.
- **Kill (any):** m1 below 0.65; or the interval of m3 includes 0 (the fourth-order numbers add nothing to band
  energies); or m2 outside 0.40 to 0.60 at 61.2 px for every statistic whose weakest leg is 0.65 or more; or m6
  below 0.2.
- **Side result that matters for the whole programme:** if m4 is 0.70 or more, band energies alone pass the
  bracket. Then the bracket shows "not one sharpness number", not "not softness", and every bracket result must be
  printed as excess over m4.
- My expectation: m1 between 0.55 and 0.70 in regime 1 (the 61.2 px leg fails for top-octave responses); m3 between
  0 and +0.04. About one chance in five of a pass. The bracket instrument (A) survives either way.

### 1.9 Scores

Impact 4, feasibility 5, shortcut-proofness 4, novelty 5. The statistic is known to move with blur, noise and
compression, and the law can act in about one octave, so the method part is likely weak; the bracketing test is the
part worth keeping and costs little. It serves the landmark cells only, where the measured softness floor is 0.91
(lead) and the baselines are already strong.

## 2. Idea 2: left-right parity ratio

### 2.1 What the idea claims

Split the face into mirror-even and mirror-odd parts. A mirror-symmetric channel filters both alike, so the energy
ratio per band cannot move with storage history. Mixing two persons averages two unrelated odd parts while shared
anatomy adds, so the ratio falls. The write-up claims this for landmark, GAN and diffusion morphs, a morph-free
form fitted on genuine photos only, and a two-view trained form (image and its flip, even and odd feature parts).

### 2.2 Status in the repository

The lead opened the mirror-asymmetry test (AS0) at 18:10 with a full registration
(`experiments/AS0_mirror-asymmetry/prereg.md`): per-band log ratio of odd to even energy in a mirror-symmetric face
mask, shape asymmetry from the 106 points, covariates (yaw, lighting, softness), session strata, history controls on
five sets, GAN and diffusion contrasts, a dose curve with a stated law, and fixed pass and kill marks. Its item list
has 25,160 images, none missing (`lists_summary.json`). It is running on CPU; no contrast existed at 18:25.
**Steps 1 and 2 of the generator's first test are that experiment.** A second run would be a duplicate.

### 2.3 Novelty (what I found)

- Deepfake detection uses symmetry in the opposite direction (generated faces break it): Li, Cao and Zhao,
  "Exploiting facial symmetry to expose deepfakes", ICIP 2021, pages 3587 to 3591
  (https://dblp.org/rec/conf/icip/LiCZ21; a feature extractor maps a pair of symmetric patches to an angular
  distance; search result and listing read). A later journal paper, "Forensic symmetry for deepfakes" (IEEE TIFS
  2023), appeared in the search results; I could not open it and did not verify its authors.
- Morph detection: one search found no paper that uses left-right symmetry of the image. The landmark-geometry
  paper it returned (Autherith and Pasquini, "Detecting morphing attacks through face geometry features", J. Imaging
  2020, https://pmc.ncbi.nlm.nih.gov/articles/PMC8321196/, opened) is differential and uses no symmetry feature. A
  2026 preprint (Ivanovska and Struc, arXiv 2602.15461) was returned with a snippet saying that a language model's
  explanations mention symmetry; the abstract does not. A second search could not run, so "not used in morph
  detection" rests on one search.
- The psychology references of the write-up (averaged faces are more symmetric) are not verified by me.
- Inside our own record the raw idea is M1 of round 1 and the registered experiment AS0. New in the write-up: the
  split into photo-bound and person-bound odd parts fitted on genuine photos, the look-alike prediction, and the
  two-view trained form.

### 2.4 Strongest objection: the effect lives in the coarse bands, where it is small against pose and light, and it reads "two captures", not "two persons"

1. **Where the ratio can fall.** The ratio falls only where the even parts of two faces are strongly related and
   the odd parts are not. In texture bands both parts are unrelated, both halve, and the ratio does not move. The
   one sanity photo of AS0 has a ratio of 0.97, 0.82 and 0.52 at wavelengths below 16 px and 0.17, 0.10 and 0.05
   above (`check.json`). The record agrees for energy: the morph keeps 0.52 of the Laplacian variance (established),
   so fine-scale even parts are unrelated too. The fall is therefore confined to wavelengths above about 16 px.
   There the odd part is lighting direction, yaw and hair. AS0 registered this caveat itself.
2. **Size.** A fall of 2 to 3 dB against a between-photo spread of several dB gives an AUC of 0.6 to 0.7. The
   measured raw reads are in that range: position-aligned CLIP distance, photo against two-person morph 0.675 folded
   (OpenCV) and 0.571 (FaceMorpher); warp-only against two-person morph 0.662 and 0.589
   (`experiments/AF0/mirror_clip224.json`, called preliminary, unreviewed).
3. **Mostly not an identity read.** Same-person against two-person morph is 0.608 and 0.553 folded in the same
   file. Most of the change happens when a second capture is added, not a second person. This matches every other
   lead of today ("two codes were mixed"). The look-alike prediction is then true for a dull reason: the read hardly
   depends on the partner's identity.
4. **The morph-free score flags the photos a passport office wants.** A score that is low odd energy calls a
   strictly frontal, evenly lit, neutral photo a morph. Its threshold moves with the photo pool. "The reference
   point is zero for every pool by symmetry" is true of the mean of the odd part, not of its energy, which is the
   score. The closed form of the same kind overshot every image-feature arm of the identity-shrinkage triage by 0.24
   to 0.51 AUC (`experiments/ID0_identity-shrinkage-triage/result.md`, unreviewed).
5. **The invariance is algebra only for pixel band energies.** For encoder features there is no such algebra. An
   encoder is not flip-equivariant, and softness changes the size of the odd feature part. Measured: the CLIP
   position-aligned distance is slightly lower for history-matched copies in 5 of 7 cells, with intervals that
   exclude 0.5 (0.464 to 0.491; same file). The shift is small and inside 0.45 to 0.55, but it is not zero. So "a
   share of the network's evidence that provably cannot come from any symmetric benchmark cue" is false as written:
   a softer image has a smaller odd part, and morphs are softer.
6. **The two-view trained form buys nothing the paper needs.** Table numbers come from the even branch, which
   keeps every shortcut. The odd branch is a second read added inside the head, close to a fusion of two scores, and
   needs two forward passes. It costs 25 A100-hours in the three days the main chain needs.
7. **The generator claim has one number at scale, and it is weak.** Mean |image - mirror| reaches 0.52 to 0.59
   folded on about 200 against 204 diffusion images (`experiments/FZ1/result.md`, P4, frame axis, lead). The
   4-person lead (18.3 against 12.0) rests on 15 morph images. On FRLL-based cells both contributors come from one
   studio rig, so the lighting part of the odd energy is shared and does not halve.
8. **The kill number of the write-up cannot fire.** Kill is "below 0.65"; the untrained read is already 0.662 to
   0.675.

### 2.5 Cheapest confound and the control that excludes it

- **Capture conditions: yaw, lighting direction, hair, expression.** They set the coarse-band odd energy and differ
  by photo pool and by expression (the genuine class of 12 of 17 cells is half smiling). Controls: (a) the negative
  class is the warp-only image or the same-person morph of the same host, never the camera photo of another pool;
  (b) genuine against genuine across pools (R0 of FRGC against R0 of colorFERET; FRLL neutral against smiling of one
  person) at most 0.60; (c) AS0's registered partial-out of yaw, lighting and Laplacian variance, and its session
  strata; (d) neutral photos only on FRLL cells.
- **Softness, for any feature-space version.** Control: R0 against softened R0 at both strengths, paired shift at
  most 0.1 standard deviations (AS0's rule for bands below the cut-off).
- **Frame content.** The corrected MAD22 FaceMorpher files carry a one-sided watermark (measured mirror reads 0.94
  and a reversed 0.73 there, same file). Control: mirror-symmetric face mask only, as AS0 registers.

### 2.6 Feasibility by 14 Nov, and data check

Everything the first test names exists: `experiments/AR1/mirror_perm106.json`, `experiments/AR1/pool.csv` (column
`cos_HB` present), `src/ID0/iss.py` and `analyse.py`, the ladder folders (536 per rung and engine), the cached
tokens `/mnt/t7/smad_next/AF0/feat/{clip224,dinov3_512}/ar1.tokens.npy`, the diffusion sets (204, 102, 200) and the
GAN items. The measurement is already running as AS0 (expected end of measurement about 19:30, analysis after). No
new compute is needed for the revised form.

### 2.7 Revised design

1. One evidence row, not a method: "odd-to-even energy ratio in the coarse bands, no training", reported for
   landmark, GAN and diffusion ladders from the registered mirror-asymmetry test (AS0), with its history control.
2. No second run. Three reads are added to AS0, marked as additions made before its contrasts were opened if that is
   still true, otherwise as post hoc: (i) pool offset, genuine against genuine (FRGC against colorFERET R0; FRLL
   neutral against smiling); (ii) rank correlation of the R4 ratio with contributor similarity (`cos_HB`) and the
   main contrast by similarity third; (iii) one logistic head on the five band ratios, 5 folds by person, to see
   the ceiling of the pixel read.
3. The shape arm is AS0's registered shape asymmetry; it replaces step 1 of the write-up.
4. The token read (odd tokens whitened on genuine photos of the training folds, two-session covariance from the 536
   ladder hosts) is run only if AS0 ends "pass", and then as a reference row with the pool-offset control.
5. The two-view trained form is dropped. The claim "the same signal for every generator" is dropped until AS0's
   diffusion and GAN contrasts exist.
6. Mirror self-morphs and warps toward the own mirror shape stay out of any training set that feeds a symmetry
   read; the generator's warning about the paired-difference landmark head (trained on mirror self-morph against
   warp-only, 0.486 on mirror against two-person) should go to that experiment's owner tonight.
7. In the paper the row is worded as "two captures were averaged", and the single-subject table shows the mirror
   self-morph as the extreme.

### 2.8 First test (the registered AS0 run plus three reads; CPU, no extra images)

- Data: AS0's item list `/mnt/t7/smad_next/AS0/items.csv` (ladder 536 hosts, both engines; softened copies of 200
  hosts; FRLL and corrected MAD22 native and history-matched frames; GAN blocks; diffusion ladder).
- Features and head: AS0's per-band log ratio in the symmetric mask, luminance; no head for the verdict; the
  five-band logistic as a ceiling read.
- Metrics: AUC of two-person against same-person morph (identity read) and of two-person morph against warp-only
  image (evidence row), per band; paired history shift in standard deviations; pool offset; diffusion two-person
  morph against 20-step reconstruction; GAN two-person morph against one-photo reconstruction.
- **Pass for the evidence row:** two-person morph against warp-only at least 0.70 in a band below the history
  cut-off, history shift below 0.1 standard deviations in that band, pool offset at most 0.60, and AS0's positive
  control (mirror self-morph collapses). **Pass for an identity read:** AS0's own mark, two-person against
  same-person at least 0.70.
- **Kill:** AS0's kill (two-person against same-person below 0.60 in every band) together with two-person against
  warp-only below 0.70 in every band: the idea becomes one sentence in the limitations. Kill of the generator claim:
  diffusion below 0.60 or GAN below 0.55. Kill of the morph-free reference row: pool offset above 0.65.
- Hours: none beyond AS0, plus about one hour for the three reads.
- My expectation: evidence row 0.62 to 0.72 on the ladder, identity read 0.55 to 0.62 ("weak" under AS0's rule),
  diffusion 0.55 to 0.65.

### 2.9 Scores

Impact 3, feasibility 8, shortcut-proofness 5, novelty 5. It is cheap and its history control is the cleanest in
the programme, but the expected read is weak, mostly not about identity, and its morph-free form penalises the most
compliant photos.

## 3. Points for the whole programme

1. The two ideas assume opposite things about the same bands. Idea 1 needs the two faces to be unrelated layers in
   the mid bands; idea 2 needs their even parts to be strongly related there. The record (0.52 Laplacian ratio; band
   power 0.125 to 0.25 cycles/pixel alone at 0.912, lead) sides with "unrelated" from about 8 px wavelength down.
   That leaves idea 1 one octave and idea 2 only the coarse bands.
2. Everything measured today reads "two captures were averaged". Neither idea changes that. The paper should say it
   in these words and lean on the three-category class proposal, which still awaits the author.
3. The bracketing test is the most useful piece of this lens. It is an evaluation protocol, costs 400 softened
   files, and applies to the released detectors as well as ours. First check whether the 26-statistic head passes it.
4. "Softness" in this programme means one kernel family at two strengths. Claims must be worded for that family.
5. Softened copies of the AF0 halves did not exist at 18:24, and the softening list alternates strengths and covers
   the training split only. Any within-pair softened test must use the ladder copies or wait.
6. The mirror-asymmetry test (AS0) already covers idea 2's pixel and shape tests. Do not start a duplicate.
7. The dose-shape reading is valid for a statistic, not for a network score.
8. Web search stopped after 9 searches. The novelty of a symmetry read in morph detection rests on one search.

## 4. Questions for the author

1. May the approved shrink-and-enlarge path be run unchanged on the 200 ladder two-person morphs (400 files) for the
   third bracket leg? Wave 4 names "our own morphs"; I read that as yes.
2. In-memory band images for measurement are already used by the mirror-asymmetry test. Is the same accepted for
   per-block fourth-order statistics? (No image is written; nothing enters a network.)
3. Not needed if the two-view form is dropped: whether an image and its lossless flip count as one image.

## 5. Not verified

- Every expectation above. I computed nothing on any image.
- The band reasoning in 1.3 and 2.4 uses one sanity photo from `check.json` and my cut-off arithmetic.
- That a copy softened to 112.7 px is about as soft as a morph.
- Papers cited from search results only (not opened): Banerjee et al. 2022; Shukla and Ross 2024; Li, Cao and Zhao
  2021; Farid and Lyu 2003; Lyu and Farid 2005. Krishnan et al.: the direction of the blur effect comes from a
  secondary source.
- Absence claims (no layer-count target, no bracketing test, no symmetry read in morph detection) rest on one
  search each.

## Sources opened or returned by search

- Farid, Adelson 1999: https://persci.mit.edu/pub_abstracts/farid_josa_99_abs.html
- Farid, Lyu 2003: https://mlanthology.org/cvprw/2003/farid2003cvprw-higherorder
- Lyu, Farid 2005: https://cse.buffalo.edu/~siweilyu/papers/sp05.pdf
- Zoran, Weiss 2009: https://people.csail.mit.edu/danielzoran/zoranweiss09.pdf
- Krishnan, Tay, Fergus 2011: https://mlanthology.org/cvpr/2011/krishnan2011cvpr-blind
- Debiasi et al. 2018 (BTAS): https://christoph-busch.de/files/Debiasi-PRNU-variance-MAD-BTAS-2018.pdf
- Debiasi et al. 2018 (IWBF): https://www.christoph-busch.de/files/Debiasi-PRNUMorphDetection-IWBF-2018.pdf
- Banerjee, Jaiswal, Ross 2022: https://arxiv.org/abs/2209.02933
- Shukla, Ross 2024: https://arxiv.org/abs/2408.10993
- Li, Cao, Zhao 2021: https://dblp.org/rec/conf/icip/LiCZ21
- Autherith, Pasquini 2020: https://pmc.ncbi.nlm.nih.gov/articles/PMC8321196/
- Ivanovska, Struc 2026: https://arxiv.org/abs/2602.15461
