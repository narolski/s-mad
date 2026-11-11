# Signal isolation by paired differences (PD1), landmark family: pre-registration

Written 11 Nov 2026, 17:05 CET, by the owner of the landmark family, before any number of this experiment was
computed. Template: `prereg/TEMPLATE.md`. Results go to `result.md` beside this file.

**Read before writing (all numbers seen so far, none computed by me):** the alpha-field probe (AF0) `result.md`
first pass (its DINOv3 ridge head on the landmark ladder (AR1): warp-only vs two-person morph 0.995, same-person vs
two-person 0.83 to 0.85, mirror self-morph vs two-person 0.73 to 0.75, genuine-photo shifts); the landmark ladder
(AR1) `variants_check.json` (face-recognition cosines of each rung to its host) and `pool_summary.json`; the
reviewer's Laplacian-variance floor (0.76 at 512 px, 0.87 at 224 px) in `ideas/CONSOLIDATED_v2.md`. No feature,
head, projection or image statistic of this experiment has been computed. No detector score file of the landmark
ladder (AR1) was opened.

## The idea under test (author, 11 Nov)

"By making morphs of the same input image (and of the same person) we can learn something useful for detection: we
can clearly catch the signal." For one host photo A and one landmark pipeline P, the images below differ by one step
each; within one host everything constant (person, source, camera, frame, expression of A) cancels in a paired
difference.

## Terms (every abbreviation defined)

- **Host photo (x0)** = the landmark ladder rung R0: the aligned 512 x 512 frame of host photo H.
- **Warp-only image (x1)** = rung R2w: H warped by the tool's own warp routine to the mean shape of H and the same
  person's second photo S; texture from H only, no blending. (For landmark tools "the tool on A alone" returns A
  itself, so the warp-only image is the pass-through.)
- **Mirror warp-only image (x1m)** = rung R2wm: H warped to the mean of its own and its mirrored landmarks, H file
  only. It is the geometric match of the mirror self-morph and is used only in the "matched" mirror rows.
- **Mirror self-morph (xm)** = rung R3m: the unchanged tool on H and its lossless left-right mirror (mirrored
  landmark file with left and right indices swapped).
- **Same-person morph (x2)** = rung R3: the unchanged tool on H and S (two sessions of one person).
- **Two-person morph (x3)** = rung R4: the unchanged tool on H and B, where B is the second photo S of another
  person of the same database (the landmark ladder's look-alike permutation; every person is host once and partner
  once).
- **Engines.** The OpenCV-style engine (`scripts/78_tool_morph.py`, which loads `68_hires_morph.py`) decides.
  FaceMorpher (`scripts/96_facemorpher_tool.py`) is descriptive only: its two-person morph pastes the blended face
  onto a double-exposed surround.
- **Features (frozen backbones, no fine-tuning, standard preprocessing of each backbone):**
  - *CLIP class token*: OpenAI CLIP ViT-L/14 (timm `vit_large_patch14_clip_224.openai`) at 224 px, the class token
    after the final norm (the pooled, pre-projection 1,024-d feature).
  - *CLIP mean patch token*: the same forward pass, mean of the 256 patch tokens after the final norm.
  - *DINOv3 mean patch token*: DINOv3 ViT-L/16 (timm `vit_large_patch16_dinov3.lvd1689m`) at 512 px, mean of the
    1,024 patch tokens after the final norm (prefix tokens dropped).
  The alpha-field probe (AF0) caches hold patch tokens only, with the same model, transform and bf16 autocast.
  DINOv3 means are taken from its cache where it exists. The CLIP class token is in no complete cache, so the CLIP
  forward pass is run once here (AF0's `build()` imported unchanged) and gives both CLIP features; the mean patch
  token is checked against AF0's cached tokens on shared images.
- **AUC** = area under the ROC curve, rank-based, the later rung positive (higher score = more morph-like), 0.5 is
  chance. **Folded AUC** = max(AUC, 1 - AUC).
- **Simple-statistic floor** = the highest folded AUC, on the same images and contrast, among 27 simple statistics:
  the 26 statistics of `smadcvpr/cue_floor.stats` (imported unchanged; band powers, spectral slope, Laplacian
  variance of frame, face box and border, noise residuals, intensity, saturation, zero fraction) plus PNG file size.
  The statistic is picked on the full data (optimistic floor, so conservative for the idea). **Excess** = head AUC
  minus floor AUC, interval from the same bootstrap draws. Laplacian variance alone is printed beside it.
- **Person bootstrap** = the pigeonhole (two-way) person bootstrap of the record (`a41_read.Draw`, re-implemented
  identically: persons ~ Multinomial(n, 1/n); a one-person image weighs its host's count, a two-person morph the
  product of its two contributors' counts), B = 2,000, seed 20261111, the same draw for every head, feature, engine
  and contrast of a table (paired).

## Data

- **Primary pool (fits and held-out tests):** the landmark ladder (AR1) FRGC 2.0 and colorFERET pool,
  536 hosts (FRGC 427, colorFERET 109), `experiments/AR1/pool.csv`, images under `/mnt/t7/smad_next/AR1/img` (read
  only). Per host and engine: x0, x1, x1m, xm, x2, x3 (536 each; counts checked in the manifest). All rungs were
  built by the landmark ladder owner with the unchanged tools and their own warp routines, so nothing is built here.
- **Graded mixing (Q5):** the landmark dose set (AR2) in AR1's manifest: 300 hosts, FaceMorpher library, mixing
  m = 0, 0.1, ..., 0.5 on (H, B) (FaceMorpher, hence descriptive).
- **Alpha-field probe images (AF0), OpenCV-style engine, 663 FRGC and colorFERET persons disjoint from the 536
  hosts:** unprocessed photos (715), zero-field images (the host warped to the pair's mean shape, no partner texture;
  1,000), uniform 0.25 blends (1,000), uniform 0.5 blends (1,000; identical to the unchanged engine's two-person morph,
  verified by AF0). Never in a fit here; used as an unseen-person test with matched geometry and as an OpenCV dose.
- **Softening direction:** SMDD bona fide renders (256 px, `smadcvpr_data/train/smdd/os25k_bf_t`) and their existing
  stored-small copies (80 px, `/mnt/t7/smad_heldout/a47/data47/i3/train/smdd_a47e7`), the pairs of
  `data47/i3/manifests/train.csv`. 1,500 pairs drawn with seed 20261111: 1,000 "fit" pairs estimate the direction,
  500 "test" pairs give a descriptive flag rate. No shrink-and-enlarge or stored-small copy exists for the 536 hosts.
  The images enter only through each backbone's standard preprocessing (its own resize to 224 or 512); no image is
  written. Diagnostic only: the FRLL native-to-E7 direction (FRLL persons, never used to fit a reported head).
- **Softened genuine photos for the flag rate:** FRLL-Morphs genuine frames native (204: `frll_bona/*_orig.png`)
  and their existing E7 frames (shrink-and-enlarge history, 204 per family); corrected MAD22 native BonaFide (204,
  `mad22_canonical_E7_inputs_v3_20261109T113746Z/native`) and its E7 frames (204 per family, `.../e7`). Primary sets:
  (i) FRLL native against FRLL E7 of the OpenCV family; (ii) corrected MAD22 native against MAD22 E7 OpenCV. Native
  and E7 are the same photos, so neutral and smiling are balanced between them.
- **Unseen tool and source:** the approved Poisson set (H1) `/mnt/t7/smad_heldout/h1_poisson`, orig variant,
  598 morphs and 598 genuine photos of a third CASIA person.
- **Benchmark cells (descriptive, no refit):** FRLL-Morphs amsl, facemorpher, opencv, webmorph; corrected MAD22
  FaceMorpher, OpenCV, Webmorph. Morphs: AF0's subsample list `lists/bench_s.csv` (600 per cell; MAD22 Webmorph 500);
  genuine native and E7 as above.
- **FRLL ladder pool (102 persons), scored only and labelled "diagnostic":** every FRLL rung beyond x0 involves a
  smiling photo (S is smiling, B is smiling), and the FRLL smiling photos differ from the neutral ones in capture
  detail, so no conclusion is drawn from it.

## Folds (5, by person)

The partner permutation has 88 cycles (largest 163). Groups = consecutive runs of at most 22 persons along each
cycle, so a host and its partner are almost always in one group; groups go to 5 folds by a seeded greedy size
balance (seed 20261111). For each fold the training hosts exclude every person who is the partner of a test host, and
the two-person head drops training rows whose partner is a test person, so no held-out image contains the face of a
person whose images trained the head. Out-of-fold scores of the 5 folds are pooled.

## Questions, methods and fixed readings

### Q1 Direction consistency

Steps (a to b): pipeline trace x0 to x1; mirror mixing x1 to xm (and matched x1m to xm); same-person mixing x1 to
x2; second identity x2 to x3; whole morph x1 to x3; photo to morph x0 to x3 (descriptive). Per feature, engine and
fold: z-scores with mean and standard deviation from the training hosts' images; direction d = unit vector of the
mean of (z_b - z_a) over training hosts. On held-out hosts: (1) the share of hosts with d . (z_b - z_a) > 0
(person-bootstrap weights); (2) the AUC of the single projection d . z, rung b against rung a, unpaired.
**Consistent** = share at least 0.75 with lower bound above 0.65.

### Q2 Geometry

z-scores from all primary-pool images of the engine (no labels). 20 seeded split-halves of the groups. Cosine of step
A estimated on one half with step B estimated on the other half, averaged over both assignments and the 20 splits
(2.5 to 97.5 percentiles over splits printed), and the split-half reliability cos(A on half 1, A on half 2) as the
ceiling. Softening direction (stored-small minus render, SMDD fit pairs) in the same z space; FRLL native-to-E7
(OpenCV family) as a labelled diagnostic. Also the cosine between the weight vectors of the heads of Q3.
Fixed readings: cos(same-person mixing x1 to x2, whole morph x1 to x3) at least 0.5 means "the signal learned from
same-person morphs is the signal of real morphs" (the same reading for mirror mixing). A cosine above 0.5 between a
mixing direction and the softening direction means "the signal is softness". The cosine with the pipeline direction
is reported. Because x1 to x3 contains x1 to x2 as a part, cos(x1 to x2, x2 to x3) (mixing against second
identity) is printed beside it.

### Q3 The author's test: learn from one person, detect two

- **One-person head:** linear, within-host paired logistic loss: for each training host the pairs (x2, x1) and
  (xm, x1); s(x) = w . z(x); fitted as L2 logistic regression without intercept on the differences z_pos - z_neg
  (label 1) and their negatives (label 0); z-scores from the head's training images; C chosen from
  {0.001, 0.01, 0.1, 1} by inner 3-fold (by group) AUC of positives against negatives on inner held-out hosts. Only
  one-person images enter fitting and selection; no two-person morph is seen.
- **Two-person head (comparison):** the same with the pairs (x3, x1).
- Per engine and feature. OpenCV-style engine decides; FaceMorpher and cross-engine scoring are descriptive.
- **Held-out contrasts (out-of-fold):** x1 vs x3 (main), x0 vs x3, x2 vs x3, xm vs x3, x0 vs x1, x1 vs x2, x1 vs xm;
  person-bootstrap intervals; the difference one-person minus two-person head on x1 vs x3 (paired).
- **Floor and excess** on the main contrast and on x0 vs x3 (all 536 hosts).
- **Final heads** for every external set: one head per (engine, feature, head type, projection) fitted on all 536
  hosts with the same rule (one head per result; no averaging of fold heads).
- **Flag rate on softened genuine photos:** threshold t = the score flagging 5% of the untouched set (the
  ceil(0.05 n)-th highest native score; flagged = score at least t); flag rate of the softened set with a
  Clopper-Pearson 95% interval. Primary: sets (i) and (ii) above, both must pass. Other families' E7 sets and the SMDD
  test pairs descriptive.
- **Fixed reading, per feature, OpenCV-style engine, one-person head:** *works* if AUC(x1 vs x3) is at least 0.75
  AND the excess over the floor is at least 0.05 AND the flag rate is at most 15% on (i) and on (ii); *fails* if
  AUC(x1 vs x3) is below 0.60 OR the excess is at most 0 (does not exceed the floor); *mixed* otherwise. Point
  estimates decide, intervals are printed beside them.
- **Family verdict:** "idea works" if *works* holds for at least 2 of the 3 features; "idea fails" if *fails* holds
  for at least 2 of 3; "mixed" otherwise.

### Q4 Trace subtraction

Per fold, in the fold's z space, estimated without held-out hosts: (a) the softening direction (SMDD fit pairs,
stored-small minus render); (b) the pipeline direction (training hosts' mean of z(x1) - z(x0)); (c) both
(orthonormalised). The direction(s) are projected out of every z (training, held-out and external) and the Q3 heads
are refitted with the same rule. Readings: "keeps its separation" = AUC(x1 vs x3) within 0.05 of the unprojected
head; "loses its reaction to softened genuine photos" = flag rate at most 15% on (i) and (ii); the change in flag
rate is printed.

### Q5 Dose and second identity

(a) Graded FaceMorpher set (descriptive engine): out-of-fold scores of the FaceMorpher heads (OpenCV heads
cross-engine) per host and level; Page trend test with hosts as blocks and the predicted order m = 0 < 0.1 < ... <
0.5; "rises" = Page p < 0.05 and mean score at 0.5 above that at 0. (b) OpenCV-style engine dose from the AF0 images
(zero field, uniform 0.25, uniform 0.5; different pairs per level, unseen persons): final OpenCV heads; Spearman of
score with a; AUC 0.25 vs 0 and 0.5 vs 0; pair bootstrap; "rises" = Spearman lower bound above 0. (c) Contributor
dissimilarity: Spearman between the out-of-fold s(x3) - s(x1) (and s(x3)) and 1 - cos(H, B), the glintr100 cosine of
the two source photos in `pool.csv`; "rises with dissimilarity" = lower bound above 0.

### Benchmark cells, H1 and AF0 (descriptive, no refit)

Final heads of Q3 and Q4, every feature, OpenCV-trained (and FaceMorpher-trained, descriptive): AUC morph vs genuine
native, morph vs genuine E7 of the same family, morph vs neutral-only native genuine; native equal error rate; E7
flag rate at the native 5% threshold. H1: AUC morph vs genuine. AF0: AUC zero field vs uniform 0.5 blend (matched
geometry, unseen persons), photos vs zero field.

## Guards

- No FRLL person in any fit (asserted on person IDs in code). FRLL cross-validated analyses are not run.
- No image is written; no resize, blur or compression code; images enter only through the backbones' standard
  preprocessing and `cue_floor.stats` (imported unchanged; SMDD and H1 images are not given statistics).
- Feature check: CLIP mean patch tokens equal to AF0's cached tokens on shared images (max abs difference reported).
- Every command tested on 8 images with its real command line before the full run.
- The AR1 warp-only image x1 is warped toward the same person's shape, the two-person morph toward the mean with
  another person's shape (a larger warp). The AF0 zero field vs uniform 0.5 contrast has matched geometry and is
  printed beside the main contrast.

## Stop rule and budget

DGX only. GPU memory under 12 GB per process (nvidia-smi checked first), one extraction process at a time, at most
4 CPU processes with `nice -n 10`. About 1.5 GPU-hours of extraction (CLIP about 25k images, DINOv3 about 4k
images not cached elsewhere). No WCSS, no spending.

## Commands

`src/PD1/landmark/{lists,feat,cues,analyse}.py`, each tested on 8 images first.

## Pre-run review

Not run (the task gives the design and the fixed readings; flagged to the lead).

## Result

`result.md` beside this file.
