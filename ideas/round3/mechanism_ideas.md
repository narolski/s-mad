# Round 3 ideas, lens: mechanism and transfer in frozen foundation features

11 Nov 2026, written by one idea generator of round 3. Nothing here was run. I read records and
listings only. No GPU, no cluster, no image opened, no sealed file opened.

Terms used below. S-MAD = single-image morphing attack detection. AUC = area under the ROC curve
(0.5 = chance; below 0.5 = reversed). CLIP and DINOv3 = pretrained image encoders (vision
transformers). LoRA = low-rank adapters added to a frozen encoder. DiffAE = diffusion autoencoder
(the generator behind MorDIFF-type morphs). z_sem = DiffAE's 512-number semantic code of an image.
x_T = DiffAE's inverted noise map of an image (the stochastic code). slerp = spherical interpolation.
W+ = the StyleGAN latent code (16 layers of 512 numbers). FR = face recognition. E7 = the existing,
approved shrink-and-enlarge history control. Rungs: x0 camera photo, x1 pipeline run on one photo
(warp-only image for landmark tools, reconstruction for generators), x2 same-person mix, xm mix of a
photo with its mirror image, x3 two-person morph.

"Measured" means a number in a record file, which I cite. "Unreviewed" means it is an owner's first
number with no independent review yet. "I expect" marks my own prediction.

## 0. The page in twelve lines

1. The frozen-feature probe on diffusion-autoencoder morphs most likely reads that the noise code was
   mixed, not that a second person is present. Reason: it separates same-person mixes from
   reconstructions as well as two-person morphs (measured, unreviewed), and any two images have
   near-orthogonal noise codes, also a photo and its mirror (measured on 4 persons, unreviewed).
2. On StyleGAN3 it reads where the code lies (latent averageness). Most of it disappears against
   spread-matched renders (measured, unreviewed; agrees with the reviewed re-read).
3. On landmark morphs frozen mean features read mostly the loss of fine detail. The excess over one
   band-power statistic is 0.02 to 0.07 (measured, one fold, unreviewed).
4. One physical picture covers all three: mixing combines two detail fields. What happens to detail
   power depends on the mixing rule: halved by pixel averaging (measured 0.52), kept by slerp of noise
   maps (diffusion morphs are sharper than reconstructions, measured, unreviewed), shrunk like
   truncation for a code midpoint. The sign differs between families.
5. So I expect no shared "mixing operation" direction. Earlier small heads already showed
   below-chance transfer from GAN to diffusion (0.26 to 0.32, measured by the Codex loop, not reviewed).
6. What can be shared is second-person evidence (the face is more average). Every measurement of it so
   far sits near 0.65 to 0.75, in every family and feature space.
7. Section 3 gives the test that decides this on cached features: a step-transfer matrix with a sign
   test and a softness control.
8. Idea 1 (ranked first): one score with three ordered levels, genuine below one-person manipulation
   below two-person morph, trained on trace-matched twins. The gap between the upper two levels is the
   measured second-person reading. One network serves both class policies.
9. Idea 2: one-person twins for generator morphs made by mixing only the noise code or only the
   semantic code. It isolates what the probe reads and gives the missing matched control.
10. Idea 3: choose layer and token type by ladder selectivity, freeze below, erase measured nuisance
    directions at the junction, adapt above. Lowest confidence of the three.
11. A missing control: all simple-statistic floors are first or second order. A scale-free
    fourth-order statistic (kurtosis of band-pass coefficients) separates a mixture from a blur in
    principle and should join the floors.
12. If the transfer matrix comes out as I expect, the honest claim is: detectors read the trace of each
    family's mixing operation; nothing family-independent beyond weak averageness exists in one image.

## 1. What the records say (with status)

| Fact | Value | Source | Status |
|---|---|---|---|
| Probe on frozen features, diffusion two-person morph vs reconstruction, 20 steps (B20 vs D20) | 0.987 to 1.000 on four feature sets | `experiments/FZ1/result.md`, P2 | unreviewed |
| Same probe recipe, same-person mix vs reconstruction (C20 vs D20) | 0.991 to 1.000 | same | unreviewed |
| Two-person vs same-person mix (B20 vs C20) | 0.945 to 0.982 | same | unreviewed; C20 mixes a neutral and a smiling FRLL file, so it is confounded |
| Simple statistics, B20 vs D20 | best 0.66 (Laplacian variance, centre crop, morph higher), 7-statistic logistic 0.695 | `experiments/FZ1/result.md`, P4 | unreviewed |
| Simple statistics, 100 steps (B vs D) | Laplacian variance 0.966, morph higher | same | unreviewed |
| StyleGAN3 morph vs one-identity render (a third person) | 0.886 to 0.936 | `experiments/FZ1/result.md`, P2 | unreviewed |
| StyleGAN3 morph vs spread-matched render | 0.583 to 0.632 | same | unreviewed |
| No released or retrained network separates StyleGAN3 morphs from renders | best 0.61 of 55 networks | `experiments/AG5/README.md` | reviewed |
| GAN ladder, CLIP pooled, one fold: x1 to x2 0.67, x2 to x3 0.65, x1 to x3 0.73; one-person head on x3 vs x1 0.78; two-person head 0.77; x1 vs x0 0.51 | | `experiments/PD1_signal-isolation-paired-differences/gan/first_pass_clip_pool_fold0.json` | unreviewed, 13 test blocks, no intervals |
| Landmark ladder, DINOv3 mean patch token, OpenCV engine, one fold: one-person head x1 vs x3 0.933, floor 0.912 (band power), excess 0.021 [-0.037, 0.081]; two-person head 0.980, excess 0.068; x2 vs x3 0.652 / 0.759; xm vs x3 0.486 / 0.694 | | `experiments/PD1_signal-isolation-paired-differences/landmark/first_pass_dino_opencv_fold0.json` | unreviewed |
| Landmark morph has 0.52 times the Laplacian variance of its own warped halves | | `ideas/CONSOLIDATED_v2.md`, section 1 | reviewed |
| Per-patch ridge head: same-person vs two-person 0.853 / 0.830, mirror vs two-person 0.747 / 0.726; warp-only genuine shift 0.73 / 0.30 standard deviations | | `experiments/AF0/result.md` | unreviewed |
| DiffAE: z_sem distance to own mirror 0.776, to another photo of the person 0.773, to another person 1.744; x_T cosine distance 0.98 / 0.97 / 0.99; slerp angle with the mirror about 89 degrees | | `experiments/AD1b/README.md` | unreviewed, 4 persons |
| Averageness score fitted on genuine photos only, in z_sem space: landmark warp-only vs two-person 0.692; diffusion reconstruction vs two-person 0.688; photo vs reconstruction 0.497; reconstruction vs same-person mix 0.445; StyleGAN3 render vs morph 0.597, spread-matched vs morph 0.503; but stored-small control 0.000 | | `experiments/ID0_identity-shrinkage-triage/README.md`, section 5 | unreviewed |
| Same score in CLIP space: landmark warp-only vs two-person 0.364 (reversed); diffusion reconstruction vs two-person 0.698; reconstruction vs same-person mix 0.756 | | same | unreviewed |
| Small heads trained on GAN twins score diffusion twins at 0.26 to 0.32; diffusion-trained heads score GAN twins at 0.41 to 0.52 | | `12_STATE_AT_HANDOVER.md`, results table | Codex loop, 16 to 90 pairs, not reviewed |

## 2. Question 1: what could the probe be reading, and which tests tell the candidates apart

### 2.1 Diffusion autoencoder

How the morph is made (from the generation code as described in the PD1 diffusion pre-registration):
z_sem is averaged linearly, x_T is interpolated by slerp at 0.5, then 20 or 100 decoding steps.

Candidates and what each predicts.

| Candidate | Same-person mix scores like | Mirror mix scores like | Score rises with z_sem distance of the two inputs | Works on background patches |
|---|---|---|---|---|
| A. Noise-code mixing trace: the image is no longer decoded from its own inverted noise map | a morph | a morph | no | yes |
| B. Semantic averageness: the midpoint z_sem lies nearer the mean code | weakly a morph (distance 0.77 against 1.74) | weakly | yes | partly |
| C. Identity typicality: only identity directions shrink | a reconstruction | a reconstruction | yes, with FR dissimilarity | no |
| D. Texture superposition in pixels | not applicable: no pixel blending happens | | | |

What is measured already. Same-person mixes separate from reconstructions at 0.991 to 1.000
(unreviewed). The smile cannot explain this with a linear probe: a half smile lies between the
neutral and the smiling reconstructions on any smile axis, and both are in the negative class. The
z_sem averageness score does not rank same-person mixes above reconstructions (0.445, unreviewed).
The noise codes of any two images are near-orthogonal (unreviewed, 4 persons), so every mix,
also with the mirror or with another photo of the same person, replaces the noise map by a
0.707 / 0.707 blend of two maps. All of this points to candidate A. I expect A to carry almost all
of the 0.99, and C to be worth about 0.65 to 0.70 underneath.

Tests on existing features (CPU, cached pooled features of four encoders in
`/mnt/t7/smad_next/FZ1/feats/{clip_mad,clip_native,dinov3,dinov2}/a43.npz`, probe code
`src/FZ1/fz1_probe.py`):

- T-D1 cross-application. Train the probe on B20 vs D20 (folds by person). Score C20 with it. Report
  AUC of C20 vs D20 on held-out persons. Then the reverse. A predicts at least 0.90 both ways. B and C
  predict at most 0.70.
- T-D2 mirror mixes. Same probe on the mirror mixes of identical and mirrored inputs for diffusion
  (AD1b) against the same persons' reconstructions. Only the 4 smoke persons exist as of 18:00
  (`/mnt/t7/smad_next/AD1b/` has no `gen/` folder yet). Mirror mixes are almost symmetric
  (asymmetry 2.1 against 18.3), so print the probe score against the asymmetry number too.
- T-D3 dose inside the morph class. Spearman correlation between the out-of-fold probe score of the
  200 B20 morphs and (i) the z_sem distance of the two source photos
  (`/mnt/t7/smad_next/ID0/feat/diffae.npz`), (ii) one minus the FR cosine (A43 manifest). A predicts
  a correlation inside plus or minus 0.15. B and C predict at least 0.3.
- T-D4 step count. Train at 20 steps, test at 100 (B vs D), and the reverse. The Laplacian statistic
  has the same sign at both step counts, so I expect transfer of at least 0.85.
- T-D5 published files. The B-trained probe on the 200 published MorDIFF morphs (arm A) against D and
  D20. If this is high, the published cell can be solved by the noise-code trace alone.
- T-D6 second pool. The same four numbers on the 129 FERET and FRGC blocks of the PD1 diffusion
  family (`/mnt/t7/smad_next/PD1/diffae/feat/clip/tr.npz`). These hosts do not have the FRLL
  smiling-file problem.
- T-D7 where in the image (needs patch tokens for 2,024 A43 images, one short extraction pass). Fit
  the probe on the mean of face-interior patches only, and on background-and-hair patches only.
  A predicts both work. C predicts the face only.
- T-D8 the decisive one, new renders with the unchanged generator: the code factorial of Idea 2.

### 2.2 StyleGAN3

StyleGAN3 has no per-pixel noise input (from the published design; not re-checked in our code). The
image is a function of the W+ code alone. So an image can only show where the code lies. A midpoint of
two codes lies nearer the mean code. A same-person midpoint shrinks the capture-specific part only. A
two-person midpoint shrinks the identity part too. A spread-matched render scales every part by one
factor.

Candidates: (A) scalar spread, the distance from the mean code; (B) uneven shrink, for example the
16 layers agree more after averaging, or identity directions shrink while shared pose directions do
not; (C) nothing else is possible.

Note on the comparison set. The "one-identity render" of the existing StyleGAN3 set (H3) shows a third
person, not a contributor. Only the spread-matched render shows contributor A. So the 0.89 to 0.94 is
not a paired contrast.

Tests on existing data:

- T-G1 dose in spread on one identity. Score the truncated one-person renders with the probe trained
  on morph vs render. Manifests exist:
  `/mnt/t7/smad_heldout/a37_sg3ctl/data/manifests/{a37trunc50,a37trunc70,a37spread,a37redec,a37h3copy}.csv`.
  Features for the truncated pools are not cached (about 850 images, minutes). A predicts the order
  plain render below morph, spread-matched and 0.7-truncated about equal, 0.5-truncated highest.
- T-G2 the code as ceiling. The W+ codes of the 64 GAN blocks are in
  `/mnt/t7/smad_next/PD1/gan/latents.npz`. Compute per image: distance from the mean code (all layers,
  coarse layers, fine layers) and the variance across layers. Report the AUC of each number and of a
  linear probe on the PCA-reduced code for x3 vs x1, x2 vs x1, x3 vs x2. No image probe can beat the
  best reader of the code, because the image is a function of the code. Then regress the image probe's
  score on the code numbers inside folds and report the AUC of the residual. A predicts a residual at
  most 0.55.
- T-G3 second identity at equal spread. Inside x2 and x3 together, bin by distance from the mean code.
  Report x3 vs x2 inside bins. If it falls to 0.55 or less, the second-identity step of the GAN ladder
  (0.65, unreviewed) is only extra shrink.

### 2.3 Landmark tools

Measured and reviewed: the morph has 0.52 times the Laplacian variance of its own halves. Two
independent detail fields averaged with weights one half each give exactly 0.5. So the fine detail of
two warped faces is almost uncorrelated, and "softness" is the second-order face of superposition. It
cannot be separated from blur by any variance or band-power number.

A scale-free fourth-order number can separate them in principle. The sum of two independent
heavy-tailed fields is closer to Gaussian: the excess kurtosis halves, whatever the mixing weights.
A blur or a shrink-and-enlarge rescales the coefficients of the bands it lets through and leaves their
kurtosis about unchanged. I expect, inside one host: kurtosis of band-pass coefficients in the face
box of a two-person morph at 0.5 to 0.7 times that of the warp-only image; a same-person morph nearer
to 1 where structures line up; an E7 copy near 1 in the bands below its cut-off. This is a prediction,
not a measurement. JPEG quantisation and aligned contours will weaken it.

Tests on existing images and tokens:

- T-L1 mixture or blur. Add the excess kurtosis of the Haar detail coefficients (levels 1 to 3, face
  box) to the statistics already computed by `smadcvpr/cue_floor.stats`. Images: the landmark ladder
  (AR1) rungs under `/mnt/t7/smad_next/AR1/img/frgcferet/`, and genuine photos native and E7 of
  FRLL-Morphs and the corrected MAD22. Report within-host ratios and the AUC for warp-only vs
  two-person, same-person vs two-person, native vs E7. Use: a new floor statistic and a control. It is
  not proposed as a detector, because absolute kurtosis depends on hair and skin content.
- T-L2 where in the image. On the cached patch tokens (section 5), per-position AUC maps for the
  mixing step, the warp step and the history step.
- T-L3 one person to two persons. Already in the PD1 landmark pre-registration.

### 2.4 One picture for all three families

| Family | Mixing rule | Fine-detail power of the mix, relative to the one-photo output | Measured |
|---|---|---|---|
| Landmark | pixel average of two detail fields | 0.5 if the fields are independent | 0.52 (reviewed) |
| Diffusion autoencoder | slerp of two near-orthogonal noise maps, weights about 0.707 each | about 1; the detail is fresh, no longer the photo's own | morphs sharper than reconstructions: Laplacian AUC 0.966 at 100 steps, 0.661 at 20 (unreviewed) |
| StyleGAN3 | midpoint of two codes; deviations from the mean code shrink to about 0.707 | set by the generator; looks like truncation | probe drops from 0.89 to 0.94 down to 0.58 to 0.63 against spread-matched renders (unreviewed) |

The change of detail has a different size and a different sign in each family. A head trained on GAN
twins where "smoother means morph" will rank diffusion morphs, which are sharper, below
reconstructions. The Codex heads did exactly that (0.26 to 0.32). Nobody has tested this reading
directly. Section 3 does.

## 3. Question 2: is there one shared mixing direction? The step-transfer matrix

### 3.1 Data that exist

Common feature space today: CLIP ViT-L/14 at 224, mean patch token (1,024 numbers) and pooled
embedding (768 numbers; for the landmark cache apply the model's fixed projection to the class token).

| Family | Hosts | Rungs | Cache |
|---|---|---|---|
| Landmark, OpenCV-style engine | 536 FRGC and colorFERET hosts | x0, x1 (warp-only), xm, x2, x3 | `/mnt/t7/smad_next/PD1/landmark/feat/clip224/ar1.part*.npz` (being written at 17:56) |
| StyleGAN3 | 256 hosts in 64 blocks (32 FERET, 32 FRGC) | x0, x1, x2, x3 | `/mnt/t7/smad_next/PD1/gan/feats/clip/G.npz` |
| Diffusion autoencoder | 516 hosts in 129 FERET and FRGC blocks | x0, x1, x2, x3 | `/mnt/t7/smad_next/PD1/diffae/feat/clip/tr.npz` |
| Softening pairs | 2,000 SMDD renders with their E7 copies; FRLL and MAD22 genuine native and E7 | | `/mnt/t7/smad_next/PD1/gan/feats/clip/{S,Fe,Fm}.npz` |

All three families use FERET and FRGC persons. That removes the photo pool as an explanation. Check
person overlap between families before folding; fold by person across all three.

Caveat: the landmark cache was made with a bicubic antialiased resize and bf16, the other two with PIL
bilinear and fp32, from 512, raw 1024 and 256 frames. Within-host differences cancel constants of a
family, but a softness axis may project differently. The final table needs one loader for all
(about 12,000 images, minutes on an A100).

### 3.2 Steps

Within one host and one family: P pipeline (x0 to x1), M same-person mixing (x1 to x2), I second
identity (x2 to x3), W whole morph (x1 to x3). Nuisance steps: S softening (render to E7 copy),
E expression or capture change (camera photo a0 to a1 of the same FERET person in the GAN blocks).

### 3.3 Parts

- Part A, geometry. Cosine between the mean step directions of two families, for M, I and W. Beside
  each: the split-half reliability of both directions, and a null from random sign flips of the host
  differences.
- Part B, leave one family out. A paired logistic head without intercept on the W differences of two
  families, each family weighted equally, features z-scored on the training images only. Score the
  third family. Report the signed AUC of x3 vs x1, x3 vs x2, x2 vs x1, x1 vs x0, and the share of hosts
  with s(x3) above s(x1).
- Part C, one person to two persons across families. The same head trained only on M differences
  (x2 against x1) of two families, scored on x3 vs x1 of the third.
- Part D, the second-identity step. A head trained on I differences (x3 against x2) of one family,
  scored on x3 vs x2 of each other family: a 3 by 3 matrix. Both rungs carry the full mixing
  operation, so the operation trace and the generator fingerprint cancel.
- Part E, softness and pipeline removed. Project out the softening direction (and the top four
  principal components of the softening differences) and the pipeline direction of each training
  family. Repeat B to D.
- Part F, the sign test. Project each family's W differences on the softening direction. Report the
  share of hosts that move toward "softer". I expect above one half for landmark and GAN, below one
  half for diffusion.
- Flag rate: for every head, the share of E7 genuine photos (FRLL, corrected MAD22) flagged at the
  threshold that flags 5% of the native photos.

### 3.4 Fixed readings

- Shared operation direction: Part B reaches at least 0.65 on x3 vs x1 with lower bound above 0.60 in
  all three held-out families, x1 vs x0 stays at or below 0.60, the flag rate is at most 15%, and
  Part E lowers it by at most 0.05.
- Shared only through softness: Part B passes, but Part E drops it below 0.58 or the flag rate
  exceeds 15%.
- Opposite signs: a held-out signed AUC of 0.40 or less. Then the families share an axis that mixing
  moves in opposite directions. Such an axis cannot be evidence of mixing.
- Shared second-person direction: every off-diagonal cell of Part D at least 0.58 with lower bound
  above 0.50, mean at least 0.60.
- Otherwise: no shared direction at this layer and token.

Power: the in-family value on GAN is only 0.73 to 0.78, with intervals of about plus or minus 0.07.
A pass mark of 0.65 there is close to the in-family value. Say this beside the table.

### 3.5 What I expect

Part B: landmark and GAN help each other a little (0.55 to 0.65, both "smoother"); diffusion as the
held-out family lands below 0.5; diffusion as a training family pushes the others below 0.5. Part E:
everything near 0.5. Part D: 0.52 to 0.60 off the diagonal. In words: no shared operation direction,
a weak or absent second-person direction in generic features. The identity-shrinkage triage (ID0)
already shows the sign reversal in CLIP space for an averageness score (landmark 0.364, diffusion
0.698, unreviewed).

## 4. Question 3: from the result to one network, or to an honest claim

### 4.1 If a shared direction or subspace U exists (rank at most 8)

- Backbone and token: the one where it was found. Start with CLIP ViT-L/14, because the published
  comparison (MADation) uses it.
- Keep it: freeze the blocks up to the block where U is read. Feed the head two things: the frozen
  read-out U applied to that block's token after the nuisance projection, and the adapted final token.
  The shared evidence is then wired in and training cannot unlearn it. It is still one network, one
  forward pass, one score.
- Discard pipeline directions: (i) the fixed projection of Idea 3 at the junction; (ii) tie terms in
  the loss for pairs that differ only by a nuisance step; (iii) history-crossed training data, as in
  the round-2 protocol.
- Objective: the ordinal loss of Idea 1 on the ladders of all families plus the SMDD rebuild.
- Proof for the paper: leave one family out for the trained network, with trace-matched negatives.

### 4.2 If none exists (what I expect)

The honest method claim, in the paper's words:

"We found no family-independent mixing signal in foundation features. Each morphing family leaves the
trace of its own mixing operation, and the change of fine detail even has opposite signs between
families. Our network is trained on matched ladders to read these traces and to stay silent on
admissible processing. Its reading of a second person, measured against one-person twins made by the
same operation, is X for landmark tools, Y for diffusion autoencoders and Z for GAN code averages. We
do not claim detection of an unseen morphing family. Cross-family numbers of earlier detectors are
explained by the benchmark cues of our audit."

This claim is strong for part (a) of the paper and it fixes what part (b) may say. Idea 1 is built to
deliver X, Y and Z from the same single score that produces the benchmark tables.

## 5. Question 4: which layer and token type, and a cheap check

### 5.1 What the record suggests

- CLIP final class token: semantic. The frozen-encoder MADation ViT-L/14 release reads it and does not
  move with storage history on the MorDIFF photo pool (34.8% to 29.9% flagged, `experiments/FZ1/result.md`
  P1), but the ViT-B/16 version does (39.7% to 69.6%). So the token type alone does not protect.
- DINOv3 final patch tokens at 512: local. A per-patch head on them separates everything, including
  warp-only images (shift 0.73 standard deviations, unreviewed).
- Resolution matters for the landmark family. The softness floor is 0.76 at 512 and 0.87 at 224
  (reviewed). At 224 double contours merge into blur, so less is left above softness.
- Intermediate blocks: nothing in our record. The caches hold the final block only.

I expect local superposition evidence to be most selective in middle blocks of a 512-pixel encoder,
and averageness in the late class token. This is a guess until the profile exists.

### 5.2 Check today on the cached final-block patch tokens (CPU)

Caches: `/mnt/t7/smad_next/AF0/feat/dinov3_512/{ar1,bench_s}.tokens.npy` (32 by 32 patches) and
`/mnt/t7/smad_next/AF0/feat/clip224/{ar1,bench_s}.tokens.npy` (16 by 16), lists in
`/mnt/t7/smad_next/AF0/lists/`. `ar1` holds every rung of the landmark ladder; `bench_s` holds the
landmark benchmark cells with native and E7 genuine photos.

Read-outs to compare, all with the same paired linear head and the PD1 landmark folds:

1. mean of all patch tokens (what PD1 uses);
2. means over regions: inner face, skin, hair and outline, background, border (masks from the
   landmark files);
3. centred tokens: each token minus the image's own mean token, per-patch head, mean of the top tenth;
4. second-order: the standard deviation over patches of each token dimension;
5. mirror difference (the cached `*.mirror.npy` arrays);
6. CLIP class token (PD1 landmark cache).

For each read-out, on the OpenCV-style engine: (a) x1 vs x3 with the one-person head, minus the
simple-statistic floor; (b) x2 vs x3 and xm vs x3; (c) x0 vs x1; (d) the E7 flag rate on FRLL and
MAD22 genuine photos at the 5% threshold; (e) FaceMorpher and the Poisson set as descriptive transfer
(the Poisson set is not in the token cache yet). A read-out is selective if (a) is at least 0.05 with
lower bound above 0, (c) is at most 0.60 and (d) is at most 15%.

### 5.3 The layer profile (one extraction pass)

One forward pass with hooks on about 12,000 images (landmark ladder of one engine, the GAN and
diffusion ladders, softening pairs, benchmark genuine photos native and E7). Store for each of the 24
blocks: class token, mean patch token, five region means. About 350 KB per image in half precision.
Then the table of 5.2 per block and token type, plus the step-transfer matrix of section 3 per block.
Pick the earliest block that is selective by the rule above. If no block is, say so: frozen features
then offer no selective read-out, and protection must come from the training data alone.

## 6. The ideas, ranked

### Idea 1. Three-level ordinal score trained on trace-matched one-person twins

One line: one network, one score, ordered genuine below one-person manipulation below two-person
morph; the gap between the upper two levels is the second-person reading, measured per family.

Why it follows from the mechanism. Section 2 says the strong, easily read evidence in every family is
the trace of the mixing operation, and that a one-person image can carry the same trace (same-person
mix, mirror mix, noise-only mix, spread-matched render). A binary label "morph" lets the network stop
at the trace. The proposed class definitions (`14_CLASS_DEFINITIONS.md`) already have three
categories. This idea makes them the training target.

Signal. Level 1 reads the trace of each family's mixing operation (pixel superposition, noise-code
mixing, code shrink) and, for generators, re-synthesis. Level 2 reads only what a two-person morph has
beyond its own one-person twin made by the same operation.

Design.
- Level 0, genuine: camera photos, their softened copies made by the existing shrink-and-enlarge path,
  warp-only images (the brief asks that warp-only is not separated from the photo).
- Level 1, one-person manipulation: mirror self-morphs, same-person morphs, generator reconstructions,
  same-person and mirror mixes of generators, the twins of Idea 2, spread-matched renders.
- Level 2: two-person morphs. Every level-2 image has a level-1 twin of the same host and tool.
  Softened copies of level-1 and level-2 images keep their level.
- Sources: the SMDD rebuild (SM1) for the published protocol; the FRGC and colorFERET ladders; the
  diffusion and GAN ladders.
- Loss: cumulative-link ordinal loss with one score s and two thresholds; a tie penalty on pairs that
  differ only by softening or warping, (s(a) minus s(b)) squared; a within-host margin, s(level 2)
  above s(its twin).
- Architecture: the MADation recipe unchanged (CLIP ViT-L/14 with LoRA, one linear head). Only data
  and loss change, so the comparison with MADation is clean.
- Test time: one image in, s out. Benchmark error rates use s for genuine against morph. The
  single-subject table reports where level-1 images land.
- The class ruling becomes a threshold choice. If same-person morphs count as morphs, decide at the
  lower threshold. If only two persons count, decide at the upper one. No retraining.
- Both generator policies come from the same score: "reconstruction inadmissible" uses camera photos
  as genuine; "reconstruction counted as genuine" is the level 2 against level 1 reading.

Controls. Softness and storage history: x0 vs its E7 copy and the E7 flag rate at the 5% threshold.
Warp: x0 vs warp-only. Operation trace and generator fingerprint: level 2 against its own level-1
twin, where both cancel. Simple statistics: every contrast is printed as excess over the floor, with
the kurtosis number of T-L1 added. Expression and capture detail: neutral-only genuine column; no
conclusion from FRLL neutral-plus-smiling pairs. Border: the same region blanked in both classes.

First test (at most one day, existing caches, CPU). Data: landmark ladder tokens
`/mnt/t7/smad_next/AF0/feat/dinov3_512/ar1.tokens.npy` and CLIP
`/mnt/t7/smad_next/PD1/landmark/feat/clip224/`; benchmark genuine photos in `bench_s`. Features: mean
patch token and the centred top-tenth read-out of section 5.2. Heads: an ordinal head (linear, and a
two-layer version with 256 hidden units) with levels 0 = {x0, x1}, 1 = {xm, x2}, 2 = {x3}; a binary
head x3 against {x0, x1} as comparator; PD1 landmark folds by person. Metrics on held-out hosts,
OpenCV-style engine: x3 vs x2 and x3 vs xm, each with its floor; x0 vs x1; E7 flag rate; x3 vs x0.
Then Part D of section 3 with the top-level direction on the CLIP caches of all three families.

Kill and pass.
- Kill: ordinal head x3 vs x2 below 0.75, or less than 0.05 above the simple-statistic floor of that
  contrast, or the E7 flag rate above 15% while the binary head stays below it. Then the upper level
  is decoration; keep a binary operation detector and report the single-subject table descriptively.
- Pass: x3 vs x2 at least 0.80 and at least 0.05 above its floor; x3 vs xm at least 0.80; x0 vs x1 at
  most 0.60; E7 flag rate at most 15%; x3 vs x0 within 0.01 of the binary head.
- Cross-family reading of the upper level: section 3.4, "shared second-person direction".

State of the art. Under the proposed classes the published tables compare genuine photos with
morphs. Level-1 evidence counts there, so the score keeps what a binary network of the same recipe
uses, minus the history cues removed by ties and crossing. I expect table numbers equal to the round-2
protocol arm within seed spread. The ordinal target adds the second-person column that no published
detector reports.

Compute. First test: CPU, 2 to 3 hours on the loaded machine. Full: binary arm and ordinal arm, five
seeds each, about 3 A100-hours per fit (scaled from the 2 H100-hours of the MADation ViT-L/14 recipe
in the record), 30 A100-hours, under one day of wall time on Athena. A DINOv3 512 arm is optional,
about 60 A100-hours.

Risks. Level 1 may absorb everything, so level 2 against level 1 stays at the floor; that is then the
reported limit. The mirror twin is almost symmetric and can be told from a two-person morph by
symmetry alone; SMDD has one render per identity, so SMDD offers only mirror twins, and same-person
twins must come from FRGC and colorFERET. The single ordered axis may cost accuracy if trace and
identity evidence are not monotone together. The level of warp-only images and of reconstructions
needs the author's ruling.

Evidence. Same-person against two-person on frozen features with heads not trained for it: 0.652 /
0.759 (`.../PD1.../landmark/first_pass_dino_opencv_fold0.json`, unreviewed) and 0.853 / 0.830
(`experiments/AF0/result.md`, unreviewed). Same-person mixes carry the diffusion trace: 0.991 to 1.000
(`experiments/FZ1/result.md`, unreviewed). One-person head detects two-person GAN morphs at 0.78
(`.../PD1.../gan/first_pass_clip_pool_fold0.json`, unreviewed). Class proposal:
`14_CLASS_DEFINITIONS.md` (awaiting the author).

### Idea 2. Code-factorised one-person twins for diffusion and GAN morphs

One line: with the unchanged generator, mix only the noise code or only the semantic code, so the
one-person twin carries the full mixing trace and the two-person morph differs from it by identity
content only.

Signal. It isolates what the frozen probe reads: the trace of mixing the noise code (what I expect) or
the averaged semantic code. A network trained with these twins at level 1 can call an image a
two-person morph only from semantic or identity averaging.

Design.
- Diffusion autoencoder, per host A and partner B, same steps and storage for all:
  reconstruction render(z_A, x_A); noise-only mix render(z_A, slerp(x_A, x_B)); semantic-only mix
  render(mean of z_A and z_B, x_A); the morph. Optional: noise transplant render(z_A, x_B).
- Only the job list changes. Encode and render are called unchanged. The codes of the diffusion
  generation on Athena (DG1) are reused, so no new inversion is needed.
- Validity gate before any score: the noise-only mix must verify against A and not against B by FR;
  report what the semantic-only mix verifies against.
- StyleGAN3: the spread-matched render already is the trace-matched one-person twin. New renders
  (midpoint on coarse layers only, on fine layers only) are made only if T-G2 shows the image probe is
  not explained by the code numbers.
- Use 1, mechanism: score all four cells with the probe trained on morph against reconstruction.
- Use 2, audit row: do the released detectors and the frozen-encoder release flag a one-person
  noise-only mix like a morph?
- Use 3, training: level-1 images for Idea 1.

Controls. Generator, step count, storage and host are identical in all four cells, so fingerprint,
sampler and history cancel exactly. The FR gate proves the twin shows one person. The Laplacian floor
is printed for every cell pair. The existing same-person mixes and mirror mixes test the same
hypothesis without a new render.

First test (existing features, CPU, under one hour). T-D1, T-D3, T-D4 and T-D5 of section 2.1 on
`/mnt/t7/smad_next/FZ1/feats/*/a43.npz` with the probe recipe of `src/FZ1/fz1_probe.py`; T-D6 on
`/mnt/t7/smad_next/PD1/diffae/feat/clip/tr.npz`; T-D2 when the mirror renders exist. Metric: AUC of
C20 vs D20 under the B20-trained probe, held-out persons, with the person bootstrap of the record;
Spearman correlation of the morph scores with the z_sem distance of the sources.

Kill and pass.
- Kill (twins not needed for diffusion): the B20-trained probe gives C20 vs D20 below 0.70 and the
  correlation with z_sem distance is at least 0.30. Then the probe reads semantic or identity
  averaging and the reconstruction already is the right control. That would be good news.
- Pass (trace confirmed, twins needed): C20 vs D20 at least 0.90 under the B20-trained probe and the
  correlation inside plus or minus 0.15.
- In between: run the factorial anyway; it is cheap.
- After the renders: the noise-code reading holds if the probe scores noise-only mixes like morphs
  (AUC against morphs at most 0.60) and semantic-only mixes like reconstructions (at most 0.60).

State of the art. No table number rises from this alone. It decides what may be claimed on
MorDIFF-type cells. If the trace is confirmed, a network can ignore the generator fingerprint and
still detect these morphs through the mixing trace, and the paper reports the second-person reading
against noise-only twins. It also gives the audit a clean figure: one person, flagged like a morph.

Compute. First test: CPU, under one hour. Full: two extra renders per host for the 536 FRGC and
colorFERET hosts and the 204 FRLL photos at 20 steps, the FRLL ones also at 100 steps, about
2 A100-hours from the A43 timings; features and probes 0.5 hours; StyleGAN3 decode-only renders, if
needed, about 2 A100-hours. Half a day of wall time once Athena accepts jobs.

Risks. The DG1 equivalence gate must cover the new job rows. The noise-only mix may change identity
more than expected; the FR gate catches that. The outcome may be that nothing identity-related is
readable in diffusion morphs; that is a finding for the audit, not a gain for the method.

Evidence. `experiments/FZ1/result.md` P2 and P4 (unreviewed); `experiments/AD1b/README.md`
(4 persons, unreviewed); `experiments/ID0_identity-shrinkage-triage/README.md` section 5 (unreviewed);
`experiments/AG5/README.md` (reviewed); `12_STATE_AT_HANDOVER.md` (Codex heads, not reviewed).

### Idea 3. Ladder-selected layers and tokens with a fixed nuisance eraser

One line: pick the block and token type where the mixing step is readable above the simple-statistic
floor while softening and warping are not; freeze everything below; remove the measured nuisance
directions there with a fixed projection; adapt only the blocks above.

Signal. Local superposition evidence in patch tokens of a 512-pixel encoder, in the blocks where it
exceeds the softness floor. The late class token is used for averageness only.

Design.
- Profile first (section 5): per block and token type, mixing excess, warp AUC, E7 flag rate.
- Junction: the earliest selective block.
- Eraser: a fixed linear projection on all tokens at the junction that removes the directions spanned
  by paired interventions: photo against its E7 copy, photo against warp-only image, generator
  reconstruction against photo if the ruling says reconstructions are genuine, expression pairs. Fitted
  by least-squares concept erasure on training persons. After it, no linear reader of the junction
  tokens separates those pairs on the fitting data.
- Above the junction: LoRA and an attention-pooling head over patch tokens, trained with the loss of
  Idea 1 or the binary loss of the round-2 protocol.
- Backbones: CLIP ViT-L/14 at 224 for the published comparison; DINOv3 ViT-L/16 at 512 if the profile
  shows that 224 leaves no excess over softness.
- Test time: one image, one forward pass, one score. The projection is a constant matrix, not a gate.

Controls. The selectivity rule itself is the softness, history and warp control. After training: a
fresh linear probe on the network's last features for photo against E7 copy must stay at or below
0.60 on held-out persons, and the E7 flag rate at or below 10%. Arm without the eraser, same data and
loss, as comparator. Region read-outs show whether evidence sits in the border or background.

First test (existing caches, CPU, about 3 hours). The read-out table of section 5.2 on the cached
final-block tokens. Then one extraction pass for the block profile (about 0.5 GPU-hours, the only GPU
use).

Kill and pass.
- Kill: no block and read-out with mixing excess at least 0.05 (lower bound above 0), warp AUC at most
  0.60 and E7 flag rate at most 15% on the OpenCV-style engine. Then frozen features offer no
  selective read-out and the idea ends; protection must come from the data protocol.
- Pass: at least one such block and read-out, holding on FaceMorpher and the Poisson set as
  descriptive checks.
- Eraser kept only if it at least halves the E7 flag rate of the no-eraser arm at equal benchmark
  error within 0.5 points.

State of the art. It is the round-2 protocol with a principled choice of where to adapt. The frozen
part cannot learn storage cues, and the published comparison (MADation recipe) stays one change away.
The record hints at the price: the fully adapted ViT-L/14 release is 3 to 5 points better than the
frozen-encoder one on FRLL landmark cells on our frames, and moves with history.

Compute. Profile 0.5 GPU-hours and CPU probes. Full: eraser arm and plain arm, five seeds each, about
3 A100-hours per CLIP fit, 30 A100-hours; a DINOv3 512 arm about 60 A100-hours. One day.

Risks. Linear erasure does not stop the upper blocks from recomputing a nuisance from what is left.
Softening is not one direction in token space, so a low-rank eraser may remove little. The selective
block may not exist. This is the weakest of the three ideas; its first test is cheap and also answers
question 4 whatever happens.

Evidence. Softness floor 0.76 at 512 and 0.87 at 224 (`ideas/CONSOLIDATED_v2.md`, reviewed).
Frozen-encoder releases and history: `experiments/FZ1/result.md` P1. Per-patch head reacts to warping:
`experiments/AF0/result.md` (unreviewed). Trace subtraction on pooled features is registered in the
PD1 pre-registrations (Q4); no result yet.

## 7. Order of work and decision tree

1. Today, CPU: Idea 2 first test (T-D1, T-D3 to T-D6), the step-transfer matrix (section 3), the
   read-out table (5.2), T-G2, T-L1.
2. When Athena opens: the code factorial renders, the block profile, one loader for all families.
3. Decide:
   - Shared operation direction found: section 4.1 with Idea 1's loss.
   - Not found, but level 2 against level 1 passes on landmark: Idea 1 as the method, claim of 4.2.
   - Level 2 against level 1 fails everywhere: binary operation detector trained with the round-2
     protocol; the paper states that no second-person evidence was readable and gives the floors.

## 8. Alternatives I rejected, and why

- A universal mixing head on pooled frozen features, trained on all three families. Rejected as a
  method until the transfer matrix is in: the Codex heads show below-chance transfer and the detail
  sign differs between families, so I expect family-conditional rules, which is an internal source gate.
- Checking the noise code at test time by inverting the test image with the diffusion autoencoder.
  Rejected: it needs the attacker's generator and a second network, and many steps per image.
- Averageness as the main score, closed form or learned on feature midpoints of genuine photos.
  Rejected as a method: every measurement is near 0.69, and the z_sem version fails the stored-small
  control completely (0.000, unreviewed). The learned version would train on exact feature midpoints,
  where the closed form already reaches 0.965 to 0.982; the loss is in the step from a feature
  midpoint to a real morph image, which a better head does not close. Averageness stays as the
  definition of what level 2 may read.
- The DiffAE encoder as backbone, because its averageness score has the right ladder profile. Rejected:
  256-pixel input, specific to one generator, fails on stored-small files.
- Kurtosis as a detector. Rejected as a detector, kept as a floor statistic and a control.
- Mirror-difference tokens as a score. Already registered by the lead as a free rider of the
  alpha-field probe (AF0); not proposed again.
- A projection on pooled features only. Already in the PD1 pre-registrations; Idea 3 moves it inside
  the network.

## 9. Things the lead should know

1. The brief's range "0.945 to 1.000" includes two-person against same-person mix (0.945). That
   contrast uses FRLL neutral-plus-smiling files and is confounded. The clean statement is that
   same-person mixes separate from reconstructions as well as two-person morphs do. That argues against
   an identity reading.
2. The StyleGAN3 "one-identity render" shows a third person. Morph against render is not a paired
   contrast. Only the spread-matched render shows a contributor.
3. Signs disagree across families: landmark morphs lose detail, diffusion morphs are sharper than
   reconstructions, and GAN-trained heads scored diffusion twins below chance. No experiment tests
   this directly yet.
4. The z_sem averageness score of the identity-shrinkage triage (ID0) is the only statistic in the
   record with the wanted ladder profile on two families (0.69 and 0.69, pipeline step 0.50,
   same-person mix silent). It also fails one history control completely. It deserves a reviewer.
5. All simple-statistic floors are first or second order. A mixture and a blur can agree on all of
   them. A fourth-order number is missing.
6. The feature caches of the three families use different resize kernels, precisions and frame sizes.
   A cross-family test on them is a first look only.
7. The softness floor is higher at 224 than at 512. A 224-pixel network may be unable to separate
   superposition from softness. This bears on the choice of the MADation recipe for the method.
8. The GAN first pass is one fold with 13 test blocks. "Training on same-person mixes transfers fully"
   (0.78 against 0.77) cannot be ranked yet.
9. The mirror numbers of identical and mirrored inputs for diffusion (AD1b) come from 4 persons; the
   full render folder did not exist at 18:00.

## 10. Not verified

- That StyleGAN3-T as used in our runs has no noise input (taken from the published design).
- The decoding details of the diffusion morph path (taken from the pre-registration text, not from
  code).
- Person overlap between the landmark, GAN and diffusion ladders.
- Whether the landmark CLIP cache was complete when this was written (seven parts existed at 17:56).
- Every number marked unreviewed. I did not recompute anything.
- The kurtosis prediction and every "I expect" in this file.
- Compute estimates are scaled from timings in the record, not measured on Athena.
- A second file, `paired_ideas.md`, was already in this folder. I did not read it.
