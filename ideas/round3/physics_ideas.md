# Round 3, physics lens: what averaging two faces forces in ONE image, apart from softness

11 Nov 2026, about 18:30 CET. Idea generator, physics lens. Nothing below was run. I read records and
listed folders only. "Measured" always names a file. "Expected" is my estimate. Numbers taken from the
brief's "New today" list are unreviewed leads and are marked "(lead)".

Terms. S-MAD = single-image morphing attack detection. AUC = area under the ROC curve (0.5 = chance);
"folded" = max(AUC, 1 − AUC). Ladder rungs as in the brief: R0 camera photo, R1 photo with the morphs'
storage history (the existing shrink-and-enlarge copies, called E7 in the record), R2w warp only, R3m
photo blended with its own mirror, R3 same-person morph, R4 two-person morph. IED = inter-eye distance in
pixels (132 px in our 512 frame, `mambamorph-code/smadcvpr/cue_floor.py` line 61). LSI channel = a linear,
shift-invariant operation (resize, defocus, mild blur; compression only roughly).

## 0. The two ideas, ranked

1. **Layer-count evidence.** A pixel-blend morph is two texture layers added. One softened photo is one
   layer. The count of independent layers is readable from amplitude-normalised fourth-order statistics,
   which a gain or a compact blur does not change. Make "number of independent layers" the dense training
   target (a scale-free replacement of the measured-disagreement map) and prove the read with a bracketing
   test: the score must rank a morph above negatives that are sharper AND above negatives that are softer.
2. **Left-right parity ratio.** Split the face into its mirror-even and mirror-odd parts. Every symmetric
   channel filters both parts alike, so their energy ratio per band is unchanged by storage history. Mixing
   two persons averages two independent odd parts while the even parts (shared anatomy) add coherently, so
   the ratio falls in the mid bands. Unlike superposition, it should also hold for GAN and diffusion morphs,
   and unlike identity shrinkage it should not weaken when the attacker picks look-alikes.

I propose no third idea. Section 5 lists what I considered and dropped.

## 1. What the record says that these ideas rest on

Measured and reviewed (brief, "Established"; `ideas/CONSOLIDATED_v2.md` section 1):
- A two-person landmark morph has 0.52 times the Laplacian variance of its own warped halves. That single
  number separates morph from halves at AUC 0.76 (512 px) to 0.87 (224 px).
- A photo blended with its own mirror carries 40 to 76% of the two-person value of the blend-disagreement
  target.

Measured, unreviewed (owners' first numbers):
- Paired differences on the landmark ladder (PD1, landmark family; one fold, 107 hosts;
  `experiments/PD1_signal-isolation-paired-differences/landmark/result.md`): a head trained only on
  one-person mixes ranks two-person morphs above warp-only images at 0.933, but one band-power statistic
  reaches 0.912 on the same images. Excess 0.021 [−0.037, 0.081].
- Blend-evidence probe (AF0, first pass; `experiments/AF0/result.md`): the head shifts warp-only genuine
  images by 0.73 standard deviations (FaceMorpher) and 0.30 (OpenCV).
- Mirror distance, CLIP ViT-L/14 at 224, no training (`experiments/AF0/mirror_clip224.json`, called
  preliminary in the AF0 README). Two definitions are in that file. "Position-aligned" compares the left
  half with the mirrored right half: that is facial asymmetry. On the FRGC and colorFERET pool it gives
  photo against two-person morph 0.675 folded (OpenCV, AUC 0.325, so morphs are LESS asymmetric) and 0.571
  folded (FaceMorpher); same-person against two-person morph 0.608 and 0.553 folded; mirror self-morph
  against two-person morph 1.000; native against history-matched frames 0.48 to 0.49 on FRLL and 0.46 to
  0.50 on the corrected MAD22 (folded at most 0.536). "Content-aligned"
  (0.715 and 0.608) measures how much the encoder's features change when a patch is mirrored. It is not
  facial asymmetry.
- DiffAE (diffusion autoencoder) asymmetry in the face box, 4 persons (AD1b;
  `experiments/AD1b/README.md` section 5): input photo 19.6, one-photo reconstruction 18.3, same-person
  mix 18.7, two-person morph 12.0, mix with own mirror 2.1 (lead).
- Frozen features on diffusion morphs (FZ1; `experiments/FZ1/result.md`, P2 and P4): probes read two-person
  morph against one-photo reconstruction at 0.987 to 1.000 at the matched 20 steps; seven simple statistics
  reach 0.63 to 0.70 there. One of the seven is mean |image − mirror image|: 0.52 to 0.59 folded, morph lower.
- Exact landmark shapes (ID0; `experiments/ID0_identity-shrinkage-triage/result.md`): photo shape against
  two-person mean shape 0.725 [0.689, 0.758]; the fit has 10 identity directions.

Checked by listing (11 Nov, 18:06 CET): the 26 registered simple statistics (`cue_floor.stats`, lines 74 to
108) are band powers, spectral slope, Laplacian variance, Haar energies, blockiness, a noise residual,
intensity, saturation and zero fraction. **None is of fourth order and none is a left-right ratio.** A text
search of all idea files and experiment records finds no kurtosis or sparsity statistic.

## 2. Reasoning

### 2.1 Four things averaging does, and which of them one image can show

| Consequence of averaging two faces | Exists for | Can a benign channel imitate it? | Same-person morph | Status in our record |
|---|---|---|---|---|
| Loss of fine-detail energy (about one half where the two textures are unrelated) | pixel blends | yes: any resize or blur | same loss | the softness floor; excluded by the brief |
| Two independent texture layers where the faces disagree | pixel blends; perhaps DiffAE (two noise maps are mixed) | no compact channel adds a second layer; a double exposure or a shifted self-blend does | yes at fine scale (pores and hairs of two captures never coincide); less at mid scale | read so far only through disagreement magnitude, which softness and tone mismatch also move |
| Mirror-odd part shrinks, mirror-even part does not | every family that averages two faces, in pixels or in a code | no symmetric channel changes the ratio | photo-bound asymmetry shrinks, person-bound asymmetry stays | raw, untrained read 0.57 to 0.68; never normalised, never fitted |
| Position moves toward the average face | every family | no | no | identity shrinkage (ID0): weak, and reads storage history in image features |

The second and third rows are what this lens can add.

### 2.2 The principle: use quantities that the genuine class cannot move

The class proposal defines a genuine image as one capture plus admissible processing (crop, alignment,
resize, compression, colour management). Apart from quantisation, these are gains and compact, symmetric
blurs. Two families of image statistics are untouched by them, by algebra and not by training:

- **Amplitude-normalised higher-order statistics inside a band.** A compact blur multiplies a narrow band
  by nearly one number. Dividing the band's fourth moment by its squared second moment removes that number.
- **The odd-to-even energy ratio per frequency.** A kernel that is its own mirror image commutes with the
  flip. So it filters the odd part and the even part of the image with the same gain, and the ratio at each
  frequency stays exactly as it was.

Morphing moves both. That is the whole argument. The tests below ask whether the movement is large
enough in real images.

### 2.3 The two laws

**Layer law.** Let u and v be the band-pass responses of the two warped source images and m = (1−a)u + av
the morph's. If u and v are unrelated, fourth cumulants add, so the excess kurtosis of m is that of one
layer divided by

  N_eff = ((1−a)² + a²)² / ((1−a)⁴ + a⁴)    (equal layer energies; 1 for one layer, 2 at a = 0.5).

In words: natural band-pass responses are sparse (a few strong edges, much empty space). Two sparse layers
added fill each other's gaps. The local-energy field becomes more even. Where the two layers coincide
(landmark-aligned anatomy), nothing changes: one layer. Where only one layer has structure, nothing changes:
the result is that layer at lower contrast, which is exactly what cannot be told from softening.

The law gives a dose curve that differs in shape from the softness curve. At mixing fraction a = 0.1, 0.25,
0.3 the energy loss has reached 36%, 75%, 84% of its value at a = 0.5. The kurtosis change has reached only
5%, 36%, 52%. A reader of softness saturates early; a reader of layers rises late. Three dose points decide.

**Parity law.** Write the frame as even part plus odd part about the face midline. For a 50% blend of two
warped faces, odd energy becomes E_odd·(1+ρ_odd)/2 and even energy E_even·(1+ρ_even)/2, where ρ is the
correlation of the two faces' parts in that band. So

  ratio(morph) = ratio(single) · (1 + ρ_odd) / (1 + ρ_even).

Even parts of two aligned faces are strongly correlated at coarse and mid scale (eyes, brows, nostrils and
mouth sit at the same places). Odd parts of two persons are unrelated (ρ_odd near 0). So the ratio falls
toward one half in the mid bands and is unchanged at the finest scale, where neither part is correlated.
For two photos of one person, ρ_odd is positive for whatever is bound to the person (nose deviation, brow
height, moles, usual hair parting) and near 0 for what is bound to the photo (yaw, light). For a mirror
self-blend ρ_odd = −1 and the ratio is 0 (measured: 2.1 against 18.3 in AD1b; 1.000 separation in AF0).

## 3. Idea 1: layer-count evidence (two superposed textures against one softened texture)

### What exactly is read
The number of independent texture layers per band and per region. Image side: the fourth moment of
band-pass responses divided by the squared second moment (and the plainer ratio mean |c| / root mean c²),
inside the face box. Training side: N_eff − 1 computed from the two warped layers the engine already holds.

### Why averaging forces it, and what differs for the look-alikes of a morph
- Two-person morph: two layers wherever the faces differ in structure. At fine scale almost everywhere
  inside the face. At mid scale at brows, lids, folds, moles, hairline.
- Softened or resized photo (R1): one layer at lower gain. No change, as long as the band still holds
  image content and not only noise.
- Warp-only image (R2w): one layer, locally stretched. No change expected.
- Same-person morph (R3) and mirror self-blend (R3m): two layers at fine scale (two captures never share
  pores), fewer at mid scale (the same folds and moles coincide after the warp). So this signal reads
  "two captures", and its band profile reads "two persons": expected R3 against R4 near 0.5 in the fine
  bands and rising in the mid bands (1/32 to 1/4 cycles per pixel, the bands that survive every registered
  storage history: the smallest native IED is 61 px against 132 px in the frame).
- GAN latent morphs: one render from one code with one fresh noise draw. No second layer. Expected silent.
- DiffAE morphs: the two inverted noise maps are nearly orthogonal (AD1b, `README.md` section 5: slerp
  angle about 89 degrees), so the mixed map is close to (x_A + x_B)/√2. Each map carries its photo's
  residual detail. I expect two detail layers at 0.71 amplitude each: no energy loss, but a layer count of 2.
  This would fit FZ1: energy statistics reach only 0.63 to 0.70 while probes reach 0.99, and same-person
  mixes are read as well as two-person morphs. The decoder is non-linear, so this is a guess to be tested,
  not a derivation.

### How one network learns it
- Target. For each training morph the engine wrapper of the blend-evidence probe (AF0, `af_morph.py`)
  already records the two float warped layers W_A and W_B. Per patch and band: split W_B's response into the
  part explained by W_A and the rest; e1 and e2 are the two energies after mixing with a(x);
  t = (e1 + e2)² / (e1² + e2²) − 1, between 0 and 1. Set t = 0 where the morph's own band energy is below a
  fixed noise floor. The patch target is the largest t over the three mid bands.
- Properties, by construction: zero for every one-capture image; zero where the two sources agree; zero
  where the partner is flat; unchanged when both layers are scaled or softened alike. The registered
  disagreement targets fail two of these (highest on flat skin; 74% tone mismatch, AF0 `result.md` wave 3).
- Negatives with all-zero maps: both warped halves, photos, zero-field images, and the existing softened
  copies. Positives: morphs and their softened copies with the same map.
- Loss: the dense regression plus a within-host ranking term built from brackets (below). One backbone
  (the chosen recipe, CLIP ViT-L/14 with LoRA, or frozen DINOv3 tokens for the first pass), one dense head,
  one fixed pooling (mean of the top tenth of patches in the face box). One score. No band logic at test.
- Bracketed ranking. Every morph M is paired with its unsoftened half (sharper than M) and with a softened
  half (softer than M); every softened morph is paired with an unsoftened half. A score that is any
  monotone function of sharpness wins one pair and loses the other. Only a non-sharpness signal lowers
  this loss. Pooled binary training with softened examples does not give this guarantee per image.

### Controls
| Confound | Control (existing images) | Pass |
|---|---|---|
| Softness | bracket: morph against own halves; morph against softened halves; softened morph against unsoftened halves. Laplacian variance printed beside it must flip sign between the first and the third | the same sign on all three, weakest AUC at least 0.75 |
| Storage history | FRLL and corrected MAD22 native against history-matched frames (R0 against R1), per band | 0.45 to 0.55 |
| Warp | R0 against R2w; AF0 photo against zero-field | at most 0.60 |
| Border | everything inside the registered face box (`cue_floor._face`); no band outside it | by construction |
| Capture detail and noise | FRLL neutral against smiling photo of the same person (the smiling files are larger and noisier, C1c) | at most 0.60 |
| Generator fingerprint | camera photo against one-photo reconstruction (GAN x0 against x1; DiffAE photo against 20-step reconstruction) reported; only same-generator contrasts are judged | reported |
| Softness law against layer law | dose: zero field, uniform 0.25, uniform 0.5 (AF0, OpenCV-style engine) and graded mixing 0 to 0.5 (AR2, FaceMorpher, descriptive) | share of the total change reached at a = 0.25 below 50% (layer law predicts 36%, energy law 75%) |
| Same-person twins | R3 against R4 and R3m against R4 per band | reported in the single-subject table, not a pass mark |

The dose-shape row is also an audit tool: the same three points, read on any released detector's scores,
say which law that detector follows.

### First test (CPU only, existing images, half a day)
- Images. AF0: `/mnt/t7/smad_next/AF0/img/{train,val}/{zero,u25,u50,halfA,halfB}` (listed 18:06: 800 + 200
  uniform-0.5 morphs, 1,160 + 1,280 training halves, 320 validation halfA) and the softened copies
  `/mnt/t7/smad_next/AF0/img/soft/{amsl112,fm61}` (about 600 each so far). Landmark ladder (AR1):
  `/mnt/t7/smad_next/AR1/img/frgcferet/{opencv,facemorpher}/{R2w,R3,R3m,R4}`, photos in `AR1/src`, graded set
  `fm_graded/m000..m050`, softened R0 and R2w of 200 hosts (`AF0/lists/ar1soft.csv`). FRLL native and
  history-matched frames (`smadcvpr_data/manifests/eval.csv`, set frllm, variants orig and resmatch).
  DiffAE: `/mnt/t7/smad_heldout/a43/gen/{D20,C20,B20}/png256` (204, 102, 200 files). GAN ladder:
  `/mnt/t7/smad_next/PD1/gan/items.csv`, roles x1, x2, x3.
- Features. No new filter: fourth moments of the responses the registered statistics already compute
  (Laplacian, one-level Haar HH and LH/HL, the noise residual) inside the face box, plus the same two ratios
  for the seven registered FFT bands (inverse transform of each registered band mask; an array, no image is
  written). About 22 numbers per image. Second line, no pixels at all: per feature dimension, the spread of
  squared token activations over the face tokens, from the cached DINOv3 tokens
  (`/mnt/t7/smad_next/AF0/feat/dinov3_512/`).
- Reads. (1) Each statistic alone, no fit. (2) A logistic head on the 22 numbers, 5 folds by person, fitted
  on uniform-0.5 morphs against their halves, then scored unchanged on the ladder. (3) The law itself: per
  pair, log(kurtosis of halves / kurtosis of morph) against log N_eff computed from the stored halves.
- Metric. The weakest of the three bracket AUCs; R0 against R1; the dose share at a = 0.25; excess over the
  existing energy floor on the PD1 fold (0.912 for warp-only against two-person morph).

### Kill and pass
- Kill: weakest bracket AUC below 0.65 for the fold head; or every statistic that passes the bracket has
  R0 against R1 outside 0.40 to 0.60; or the law check has rank correlation below 0.2.
- Pass: weakest bracket AUC at least 0.75 (lower bound above 0.70), R0 against R1 inside 0.45 to 0.55,
  R0 against R2w at most 0.60, neutral against smiling at most 0.60, dose share at a = 0.25 below 50%.
- Secondary, not a kill: DiffAE two-person morph against 20-step reconstruction at least 0.75 where the
  energy floor is 0.63 to 0.70; GAN x3 against x1 within 0.45 to 0.55 (predicted silence).
- My expectation: 0.70 to 0.85 for the weakest bracket; about even odds that it clears 0.75. Fine bands
  will look best on untouched images and will fail the noise control; the mid bands decide.

### How it reaches the published tables
It changes the target, not the recipe. The round-2 chain stays: MADation recipe, pipeline-matched and
history-crossed SMDD rebuild, warped halves as genuine images. The layer map replaces the
measured-disagreement map in the five-arm ablation that is already registered. The state-of-the-art claim
is on the landmark cells, which are pixel blends and hold the evidence in the mid bands at every stored
size. If the DiffAE prediction holds, the MorDIFF cell gets a read that is not a rendering cue. GAN cells
are reported as a measured limit.

### Compute
First test: 0 GPU-hours, 1 to 3 hours of wall time on the loaded DGX (about 15,000 images, FFT at 512).
Full version: targets for the stored pairs (CPU, 30 minutes), dense heads on cached tokens (about 1
GPU-hour), five-arm ablation (about 2 GPU-hours), LoRA fits 5 seeds x 2 training sets at about 3 A100-hours
each (30 A100-hours, one day on Athena).

### Risks
- Sensor noise is dense. A noisy genuine photo has low kurtosis in fine bands and would look layered. The
  neutral-against-smiling control tests exactly this.
- Inside the inner face much mid-band energy is aligned anatomy, so the layer count may stay near 1 there
  and the evidence may sit in brows, hairline and periphery, which splice morphs remove.
- The invariance is exact only for a pure gain. It is approximate for a blur inside a band, and it does not
  hold for extended kernels (a double exposure or long motion blur IS two layers). JPEG blocks add a weak
  grid layer.
- The FFT band responses and a filter-free feature variant need the author's word that an analysis which
  writes no image is not "new blur code" (question 1).

### Closest prior work (from memory; nothing was opened or searched this session)
Sparsity of derivative histograms falls when two natural images are added: used to separate reflections
(Levin, Zomet and Weiss, 2004; Levin and Weiss, 2007). Band-pass kurtosis of clean natural images is roughly
constant across scales, and noise changes it (Zoran and Weiss, ICCV 2009; used for splicing detection by
Pan, Zhang and Lyu, 2012). Texture descriptors in early morph detection (BSIF, LBP) capture such statistics
implicitly. I know of no morph detection work that states the layer law, uses a layer-count target or a
bracketing test. Not verified.

## 4. Idea 2: left-right parity ratio (asymmetry shrinks when two faces are averaged)

### What exactly is read
The ratio of mirror-odd to mirror-even energy of the face, per band, about the face midline; and, in feature
space, the odd part of the tokens (left token minus mirrored right token), scored against statistics of
genuine photos only.

### Why averaging forces it
The parity law of section 2.3. Two extra points make it worth a slot although its raw form is weak:
- **Exact history invariance.** Resize, blur and the shrink-and-enlarge path use kernels that are their own
  mirror image. They cannot change the ratio in any band that still holds content. Measured in CLIP space,
  unreviewed: native against history-matched 0.46 to 0.50, folded at most 0.536 (`mirror_clip224.json`,
  position-aligned). The identity-shrinkage read in the
  same feature spaces failed this control (0.582 in CLIP, 0.000 in DiffAE; ID0 `README.md` section 5).
- **No pool offset and no look-alike discount.** The reference point is zero for every photo pool, by
  symmetry; the identity-shrinkage estimator broke on pool offsets (ID0 `README.md` section 7). And
  fluctuating asymmetry is developmental noise: I expect the odd parts of two look-alikes to be as
  unrelated as those of two strangers, while their even parts are more alike. So the attacker's pair
  selection should not weaken this signal. Expected, not measured.

### How it differs along the ladder (predictions)
| Step | Photo-bound odd part (yaw, light, hair of the day) | Person-bound odd part |
|---|---|---|
| R0 to R1 (history) | unchanged | unchanged |
| R0 to R2w (warp only) | unchanged, apart from shape | unchanged |
| R2w to R3 (second photo, same person, other session) | halved in energy | unchanged |
| R3 to R4 (second person) | halved | halved |
| R3m (own mirror) | zero | zero |
| GAN: x1 to x2, then x2 to x3 | first step | second step |
| DiffAE: reconstruction to same-session mix, then to two-person morph | unchanged in the first step (same session: 18.3 to 18.7, lead), both parts in the second (to 12.0, lead) | |

The two columns are separable with genuine photos only: the within-person, between-session covariance of
the odd features spans the photo-bound part; the between-person covariance spans the person-bound part. This
gives the paired-difference steps of PD1 (same-person mixing 0.67, second identity 0.65, lead) a physical
coordinate each, and a dissociation that can fail.

### How one network learns it
- Morph-free form (reference row). Frozen backbone. Odd tokens of genuine photos from pools with two
  sessions per person (the 536 ladder hosts have a host photo and a second-session photo; fit and test by
  person folds). Whiten; score = minus the squared length along person-bound odd directions. No morph, no
  tool output and no softened image is ever seen in fitting.
- Trained form. One network applied to the image and to its lossless flip with shared weights (the scoring
  code already averages over the flip). The head sees the even feature part and the odd part separately.
  (`IDEAS_v1.md`, M1, says the scoring code already averages over the flip; I did not open that code.) The
  head sees the even feature part and the odd part separately.
  Even part: everything the standard recipe has, so table numbers are kept. Odd part alone: a declared
  read-out that no symmetric cue can feed. One image in, one score out; question 2 asks whether two views
  of one image by a lossless flip are within "one network on ONE image".
- The mirror self-morph and the warp toward the own mirror shape must not be training negatives or
  positives for this read: they are symmetric by construction.

### Controls
Softness and storage history: R0 against R1 per band, expected 0.50 by algebra (a miss means asymmetric
aliasing or border). Border and watermark: face box only, an odd-width crop centred on the eye midline
(column 256), lossless flip; the corrected MAD22 FaceMorpher files carry a one-sided watermark below the
face (AF0 `README.md` section 8). Expression: neutral-only genuine class (a crooked smile is asymmetric, and
half of the FRLL genuine class smiles). Capture detail: neutral against smiling of one person, at most
0.60. Warp: R0 against R2w at most 0.55. Twins: R3 against R4 is the identity read; R3m is reported as the
extreme of the scale. Generator fingerprint: camera photo against one-photo reconstruction, expected near
0.5 (measured lead: 19.6 against 18.3).

### First test (CPU only, existing files, one day at most)
1. Exact shapes, seconds. Split each Procrustes-aligned 106-point shape into symmetric and asymmetric part
   with the existing mirror permutation (`experiments/AR1/mirror_perm106.json`). Rerun the landmark arm of
   the identity-shrinkage triage (`src/ID0/iss.py`, `analyse.py --arm landmark`) on the asymmetric part only:
   R0 against R4, R3 against R4, dose, and the rank correlation of the score with contributor similarity
   (`cos_HB` in `experiments/AR1/pool.csv`).
2. Pixels, about one hour. Odd and even energy in the seven registered bands inside the face box, for the
   landmark ladder rungs, the AF0 halves, morphs and softened copies (the bracket of idea 1), FRLL native
   and history-matched frames, the DiffAE sets (`a43/gen/{D20,C20,B20}/png256`) and the GAN ladder roles
   x1, x2, x3. Read the mid-band ratio alone, then a logistic head on the seven log-ratios by person folds.
3. Tokens, about one hour. Odd tokens from the cached, unflipped tokens (left token minus mirrored right
   token, centred by the genuine mean; `/mnt/t7/smad_next/AF0/feat/{clip224,dinov3_512}/ar1.tokens.npy`),
   whitened on genuine photos only; same contrasts.

### Kill and pass
- Kill for the method: on the landmark ladder, OpenCV-style engine, warp-only against two-person morph
  below 0.65 for both the pixel ratio and the whitened token score. The raw untrained read is already 0.66
  to 0.675, so a fitted read that does not beat it adds nothing.
- Kill for the generator claim: DiffAE 20-step reconstruction against two-person morph below 0.60 on the
  200 and 204 native frames (the 4-person lead is then refuted); GAN x1 against x3 below 0.55.
- Kill for the look-alike claim: rank correlation of the shape-asymmetry score with contributor similarity
  outside ±0.15, or a drop above 0.05 AUC from the least to the most similar third of pairs.
- Pass: 0.75 or more on warp-only against two-person morph with R0 against R1 inside 0.45 to 0.55 and R0
  against R2w at most 0.55; DiffAE at least 0.70; same-person against two-person at least 0.65.
- My expectation: landmark 0.70 to 0.80, DiffAE 0.60 to 0.70, exact shapes 0.62 to 0.70 (about five
  asymmetric identity directions at zero similarity give about 0.72 by the ID0 closed form, before noise).
  This is a modest detector with unusually clean controls, not a headline number.

### How it serves the published tables
It does not reach state of the art alone, and I do not claim it will. It gives three things the paper
lacks: a morph-free read with a physical basis that passes the history control where morph-free networks
today succeed through history; one evidence row that exists for landmark, GAN and diffusion cells alike;
and, in the two-view form, a part of the main network's evidence that provably cannot come from any
symmetric benchmark cue. Table numbers stay those of the main recipe.

### Compute
First test: 0 GPU-hours; step 1 minutes, steps 2 and 3 about 2 hours of wall time on the loaded DGX. Full
version: flipped-view tokens for the ladders (about 1 GPU-hour), two-view LoRA fits 5 seeds at about 5
A100-hours each (25 A100-hours, one day).

### Risks
- Small effect against large natural spread: hair parting, yaw and light differ more between photos than a
  factor of two in odd energy. The raw numbers (0.57 to 0.68) may already be near the ceiling.
- It flags naturally symmetric faces and strictly frontal, evenly lit captures. False alarms by group must
  be reported.
- An attacker can add asymmetry. A mirror self-morph scores as the most extreme "morph".
- The within-person covariance must come from different sessions; a same-session fit understates photo-bound
  asymmetry (ID0 had only 47 persons with two sessions in its fit set).

### Closest prior work (from memory and from `IDEAS_v1.md`, M1; not searched this session)
Averaged faces are more symmetric (Langlois and Roggman, 1990; Rhodes, Sumich and Byatt, 1999). Symmetric
and asymmetric shape components by reflection and relabelling (Mardia, Bookstein and Moreton, 2000;
Klingenberg, Barluenga and Meyer, 2002). Face symmetry in deepfake detection reads the opposite direction
(Li, Cao and Zhao, ICIP 2021). The round-1 strategist proposed the raw mirror distance (M1); the lead ran
it as a free rider in AF0. New here: the odd-to-even ratio with its exact channel invariance, the split
into photo-bound and person-bound parts fitted on genuine photos, the look-alike prediction, and the
dissociation table.

## 5. Considered and dropped

| Candidate | Why dropped |
|---|---|
| Typicality in a face-recognition space fitted on genuine photos | The triage (ID0) is running; image-feature arms read storage history and the closed form overshoots. In a normalised embedding the midpoint of two unrelated directions is again a typical direction; the length before normalisation is a quality measure. Nothing new to add before the face-recognition arm reports |
| Identity consistency between face parts | For a uniform blend every part is the same mixture: no first-order signal (round-1 identity idea 4 gives the algebra). Only splice morphs could show it |
| Half-contrast moles and scars | Halving is not identifiable without a reference (a faint mole is a faint mole). Only doubling is, and that is idea 1 |
| Doubled catchlights in the eyes | Two lamps give two catchlights in a genuine photo; one studio rig gives coinciding catchlights across persons (FRLL). Capture-bound, not person-bound |
| Double iris edge, lip line and brow outline as hand-made tests | Real and classical, but region rules; a network trained on the layer target covers them |
| Noise-level function (sensor noise against brightness) | Averaging two captures halves noise variance, but camera gain is unknown and denoising, resizing and JPEG erase it |
| Phase coherence across scales | Used in the literature as a sharpness measure, so blur moves it. The invariance I would need does not hold as usually computed |
| Detail loss as a function of distance to the nearest landmark | A within-image energy contrast; cancels global softness, but skin texture differs between people by far more than the 3 dB at stake (its round-1 author scored it 4 of 10). The fourth-order version is inside idea 1's map |
| Triangle-mesh pattern of interpolation softness | A trace of warping, present in warp-only genuine images; fails R0 against R2w by design |
| Shading under two lights | Image formation is linear in lighting: the mean of two lightings is a valid lighting. No first-order signal |
| Colour direction of fine detail (two skins, two detail colours) | JPEG chroma subsampling removes it; colour statistics are already a benchmark confound (cue matrix row 13c) |

## 6. Observations for the lead

1. The brief's "mirror distance" numbers mix two definitions. The 0.715 and 0.608 values are the
   content-aligned distance (encoder flip sensitivity). Facial asymmetry is the position-aligned one: 0.571
   to 0.675 folded on the primary pool, morphs less asymmetric (`experiments/AF0/mirror_clip224.json`).
2. The 4-person asymmetry lead (19.6, 18.3, 18.7, 12.0, 2.1) is not confirmed at scale: FZ1's mean
   |image − mirror| gives 0.52 to 0.59 on about 200 against 204 images. That statistic is taken on stored
   frames about the frame axis, not in the face box, so the lead is untested rather than refuted.
3. The simple-statistic floor holds only energy-type statistics and file size. "Excess over the floor"
   therefore cannot tell superposition from softness in either direction.
4. Mirror self-morphs and the warp toward the own mirror shape are symmetric by construction (separation
   from two-person morphs 1.000 with no training). The paired-difference landmark head is trained on
   "mirror self-morph against warp-only" pairs and may learn symmetry; its mirror-against-two-person value of
   0.486 is consistent with that.
5. On the corrected MAD22 FaceMorpher cell the mirror reads (0.94 and a reversed 0.73) are probably the
   one-sided watermark noted in the AF0 README. Any frame-level statistic there needs the face box.
6. On FRLL cells the genuine class is half smiling. "Morph less asymmetric" (0.60 to 0.68) is confounded by
   expression until read against neutral photos only.
7. The AD1b same-person mix is a same-session pair (neutral and smiling). "A same-person mix keeps its
   asymmetry" is forced by shared pose, light and hair. The cross-session case exists only on the landmark
   ladder (R3) and the GAN ladder (x2).
8. Genuine-only fits whose within-person covariance is mostly within-session (ID0: 47 of 471 persons with
   two sessions) understate photo variation and overstate every predicted ceiling. The ladder's own
   two-session pairs (536 persons) are the better source.

## 7. Questions for the author

1. Does an analysis that writes no image (fourth moments of the registered Laplacian, Haar and FFT-band
   responses; a per-band normalisation layer inside the network) count as new blur or resampling code?
2. Is one network applied to an image and to its lossless flip, with one head and one score, within
   "one network at test time on ONE image"? (The scoring code already averages over the flip.)
3. Under the class proposal a double exposure or a shifted self-blend of one photo is a single-subject
   manipulation. Idea 1 will flag it. Is that accepted?

## 8. Not verified

- Every expectation in sections 3 and 4. No statistic of either idea has been computed on any image.
- That fourth-order statistics of face images vary little enough between persons for an unpaired read.
- That DiffAE noise-map mixing leaves two detail layers in the decoded image.
- That odd parts of look-alike pairs are unrelated.
- The prior-work statements: from memory, no paper opened, no search run.
- That the softened copies under `AF0/img/soft/` include softened morphs as well as softened halves (the AF0
  record says both are planned; I counted files, I did not read the list).
- That the canonical eye midline is exactly column 256 in every ladder frame (taken from the comment in
  `cue_floor.py`; the ladder frames come from another aligner).
