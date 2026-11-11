# Signal isolation by paired differences (PD1), cross-family transfer: pre-registration

Written 11 Nov 2026, 21:00 to 21:05 CET (machine clock; file first saved 21:05), before any cross-family number was computed. What I had seen before writing:
the three family results and the independent verifications of the landmark and diffusion families (summaries handed
over by the workflow; files under `experiments/PD1_signal-isolation-paired-differences/{landmark,diffae,gan}/`), the
feature caches' metadata (model, loader, shapes), the image lists, and the person overlap counts below. No feature of a
landmark image in the common feature space existed, and no cosine, head or score across families had been computed.

## Question (plain words)

Is there ONE mixing direction shared by the three morph families (landmark tools, diffusion autoencoder, GAN latent
morphs)? Concretely: (1) do the step directions (pipeline trace, one-person mixing, whole morph) point the same way
in the three families; (2) does a head trained on one-person images of two families detect two-person morphs of the
third family, whose persons it never saw; (3) would a detector trained on one-person morphs of several pipelines be
expected to detect two-person morphs of an unseen pipeline, and what is the largest threat to that reading.

## Terms

Host photo **x0**; pass-through **x1** (landmark: warp-only image, rung R2w; diffusion: one-photo DiffAE
reconstruction at 20 steps; GAN: one-photo StyleGAN3 reconstruction); mirror self-morph **xm** (landmark only, rung
R3m); same-person morph or mix **x2**; two-person morph **x3**. Steps: pipeline trace P = x0 to x1; one-person mixing
M = x1 to x2 (landmark also Mm = x1 to xm); whole morph W = x1 to x3; second identity I = x2 to x3 (descriptive).
AUC = area under the ROC curve, 0.5 = chance. Floor = best single simple image statistic (folded AUC) on the same
images. E7 = the existing shrink-and-enlarge history control. FR = face recognition. LOFO = leave one family out.
One-person head = linear head trained only on one-person images; two-person (whole-morph) head = the same trained on
x3 against x1. Families are abbreviated L (landmark), D (diffusion), G (GAN) only inside tables.

## Verified family verdicts used (task rule: the verified verdict where it differs from the owner's)

| Family | Registered (owner) | Verified | Main reason given by the verifier |
|---|---|---|---|
| Landmark (OpenCV-style engine) | idea works | **mixed** | separation sits mainly in the double-exposed surround (face-only 0.62 to 0.71, below the floor); CLIP class-token head flags 27.5% of the hosts' own softened photos; margin over a 27-statistic head small |
| Diffusion autoencoder (DiffAE) | idea works | **mixed** | a 26-statistic head trained the same way reaches 0.947 (no excess); reacts to decoding steps without mixing; same-person and mirror mixes score above two-person morphs |
| GAN (StyleGAN3-T, set GAN32) | idea works, latent-averageness qualifier fired | **no verification delivered** (a partial sceptic run exists in `/mnt/t7/smad_next/PD1/gan/verify/`, no verdict) | owner's own qualifier: spread-matched one-identity renders score like morphs (0.46 to 0.48); the latent distance-to-mean statistic alone gives 1.00 |

These verdicts are quoted, not re-decided here. This experiment asks only the cross-family question.

## Data (all images exist; nothing is generated, resized or written as an image)

Primary pools, identical to the family analyses:

| Family | Pool | Hosts | Persons | Images used |
|---|---|---|---|---|
| Landmark | landmark ladder (AR1), FRGC + colorFERET, OpenCV-style engine; `/mnt/t7/smad_next/PD1/landmark/lists/ar1.csv` | 536 | 536 (partner = another host) | x0 R0, x1 R2w, xm R3m, x2 R3, x3 R4: 2,680 |
| Diffusion | DiffAE blocks (expanded123 + confirmation64), `/mnt/t7/smad_next/PD1/diffae/lists/items.csv` set `tr` | 516 | 258 | x0 516, x1 516, x2 258, x3 258 |
| GAN | GAN32 set G, `/mnt/t7/smad_next/PD1/gan/items.csv`, `hosts.csv` | 256 | 128 | x0 256, x1 256, x2 128, x3 128 |

Persons are the real FERET / FRGC subject IDs (GAN: the `subject` field of each host's camera photo). Overlap between
the pools (counted before writing): landmark and diffusion 152 persons, landmark and GAN 80, diffusion and GAN 100, all
three 65.

**Person rule for LOFO (primary).** The test set is the whole held-out family (so its numbers are comparable with the
family's own). A training host of the other two families is dropped if any image of its contrast involves a person who
appears in any image of the held-out family (host, second photo, or two-person partner); the same purged host set is
used for the one-person and the two-person head. Resulting training hosts (counted, not scored):

| Held-out family | Training hosts kept |
|---|---|
| landmark (536 test hosts) | diffusion 124 of 516, GAN 40 of 256 |
| diffusion (516 test hosts) | landmark 291 of 536, GAN 56 of 256 |
| GAN (256 test hosts) | landmark 399 of 536, diffusion 316 of 516 |

Sensitivity (descriptive): no purge (persons may overlap; full training families).

Reference sets (scoring or direction estimation only):
- SMDD softening: GAN set S, 2,000 SMDD genuine renders and their existing E7 copies (`a47/data47/i3`); part `S_fit`
  (1,000 pairs) estimates the softening direction, part `S_test` (1,000 pairs) gives a common flag rate.
- Landmark host softening: the existing shrink-and-enlarge copies of 200 hosts' photos at two strengths
  (`landmark/lists/ar1soft.csv`, rungs `R0_soft_amsl112`, `R0_soft_fm61`), against the hosts' untouched x0.
- GAN set H (CASIA, 423 pairs, raw 1024 frame `Hr`): x1 reconstruction, x1s spread-matched one-identity render, x3.
- Diffusion FRLL renders (diagnostic, FRLL persons never in a fit): 204 reconstructions at 20 steps (`f256` D20) and at
  100 steps (`f256` rec100); FRLL two-person morphs at 20 steps (`f256` B20).
- Landmark blanked copies (existing constant-grey blanking, `AR1/blank/bg` = face only, `AR1/blank/face` = surround
  only) of x1 and x3, and the matched-geometry warp-only image x1g (rung R2w4), OpenCV-style engine.
- Diffusion blanked features: the diffusion verifier's CLIP features of face-box-only and face-blanked training images
  (`/mnt/t7/smad_next/PD1/diffusion/verify/blank_clip.npz`; CLIP only).
- Registered softened-genuine sets of each family (flag rates):
  landmark (i) FRLL E7 OpenCV and (ii) corrected MAD22 E7 OpenCV, each against its 204 native genuine frames
  (`landmark/lists/bench.csv`); diffusion FRLL E7 for MorDIFF (`ev` `mordiff|resmatch`) against native
  (`ev` `mordiff_bona|orig`); GAN corrected MAD22 E7 FaceMorpher history (`Fm` `e7_FaceMorpher`) against native
  (`Fm` `native`).

## Features (frozen; one common space)

The three families' registered features are not in one space (landmark: timm bicubic transform, CLIP class token
before projection, DINOv3 at 512 px; diffusion and GAN: the existing loader `smadcvpr/common.ImageItems(res=224)`,
CLIP projected embedding, DINOv3 at 224). The cross-family analysis uses the diffusion/GAN space for all three:

- F1 **CLIP ViT-L/14 pooled** (768, projected embedding) — primary;
- F2 CLIP ViT-L/14 mean patch token (1,024);
- F3 DINOv3 ViT-L/16 pooled at 224 (1,024; equal to its mean patch token).

Model, weights and loader: `build()` and `extract()` of `src/PD1/gan/pd1_feats.py`, imported unchanged (the same timm
model and OpenAI checkpoint as the frozen-features experiment (FZ1) and the diffusion family; the loader's PIL bilinear
resize to 224 is the only resize). Diffusion and GAN caches are reused read-only; before use I re-extract 8 images of
each with the same code and require max |difference| below 1e-3 (TF32 differs between the two caches). Landmark images
(and the landmark reference sets above) are extracted new with the same code; GPU under 12 GB, `nice -n 10`, 2 loader
workers, 2 threads. Every vector is L2-normalised before any use.

Consequence stated in advance: in-family landmark numbers in this space will not equal the landmark family's own
(different features); I recompute in-family references in the common space (below) so that transfer is compared with
in-family on the same features.

## (1) Cosine matrix of step directions

Directions: unit mean paired difference over hosts. Steps per family: P, M, W (and I); landmark also Mm and the pooled
one-person step M+ = (x2 - x1 and xm - x1 pooled). References: SMDD softening (E7 copy minus render, `S_fit`), landmark
host softening (softened x0 minus x0, both strengths pooled), GAN H latent spread (x1s minus x1), GAN H whole morph (x3
minus x1), diffusion FRLL decoding steps (100-step minus 20-step reconstruction; diagnostic).

Space: primary = z-space (L2-normalised, then each dimension standardised with a common mean and SD over the ladder
images of the three primary pools, each family weighted equally); secondary = L2-normalised space without
standardisation (the diffusion and GAN families' Q2 space).

Cross-fitting: 200 random splits of the union of persons into two halves (SMDD and CASIA references split by their own
clusters). In each half a family-step direction uses only hosts whose step persons all lie in that half (one-person
steps: the host; W and I: host and partner). Cross-family cosine = mean over splits of the mean of cos(A in half 1,
B in half 2) and cos(A in half 2, B in half 1). Within-step reliability rel = mean cos(A in half 1, A in half 2).
Range = 2.5 to 97.5 percentiles over splits (a split range, not a confidence interval). Disattenuated cosine =
raw / sqrt(rel_A rel_B), descriptive and used only in the reading rule below. Also reported: the full-data cosine
(no split, descriptive).

**Fixed reading (per feature, per family pair, for the one-person mixing step M = x1 to x2):**
- **shared**: raw cross-fitted cosine >= 0.5;
- **not shared**: raw < 0.5 and disattenuated < 0.5, with both reliabilities >= 0.5;
- **attenuated**: raw < 0.5 but disattenuated >= 0.5;
- **underpowered**: raw < 0.5 and a reliability below 0.5.

Per feature: "one shared mixing direction" if all three pairs read "shared"; "no shared mixing direction" if at least
two pairs read "not shared"; otherwise "partly shared" (pairs named). Across features: the reading of at least 2 of the
3 features; otherwise "mixed". The same rule is applied descriptively to P and W. Also descriptive: cosine of each
family's M with SMDD softening (above 0.5 = "the shared signal is softness"), with GAN latent spread, with diffusion
decoding steps, with landmark host softening.

## (2) Leave one family out

For each held-out family T, training families A and B (person-purged as above).

- **One-person head O**: positives = the registered one-person images of each training family (landmark x2 and xm;
  diffusion x2; GAN x2), negative = x1 of the same host; within-host paired logistic loss, linear, no intercept, both
  signs fed (the families' recipe). Standardisation: mean and SD of the training images (positives and negatives),
  each training family weighted equally; sample weights give each training family equal total weight.
- **Two-person (whole-morph) head T2**: the same with x3 as positive.
- C from {0.001, 0.01, 0.1, 1, 10} by inner leave-one-family-out over A and B (fit on A, score B; fit on B, score A;
  criterion = mean share of B's (or A's) hosts with s(positive) > s(x1) on the head's own training contrast; O never
  sees a two-person morph, also not for selection); ties to the smaller C. All five C values are reported as a range.
- **Mean-direction head** (descriptive, no fitting choice): score = z(x) times the unit family-balanced mean of the
  training one-person differences.

Scored on all hosts of T, no refit:
- main: AUC x1 vs x3 (x3 positive), with a 95% two-way person bootstrap (pigeonhole draw of the record's `a41_read`
  method: an image weighs its person's count, a two-person image the product of both; B = 2,000, seed 20261111);
  paired share of hosts with s(x3) > s(x1);
- floor: best single statistic, folded, on T's x1 vs x3, from T's existing statistics (landmark: the 27 statistics of
  the alpha-field probe (AF0) cache; diffusion: the owner's 7 and the verifier's 26; GAN: the owner's 7); excess = AUC
  minus floor with the statistic and its sign fixed at the point and re-evaluated on each bootstrap draw;
- flag rate on T's registered softened genuine set(s) (listed above) at the threshold that flags 5% of T's untouched
  genuine frames: threshold = the k-th highest untouched score, k = ceil(0.05 n) (11 of 204); flag = share of softened
  frames at or above it, Clopper-Pearson interval. Landmark: the larger of (i) and (ii) counts;
- also: x0 vs x3, x2 vs x3, x1 vs x2 (T's own one-person mix), x1 vs x3 of the whole-morph head T2 and the difference
  O minus T2 (bootstrap), the common SMDD flag rate (`S_test`, threshold at 5% of its renders).

**Fixed reading (per feature, per held-out family), the families' rule applied to transfer:**
- **transfers**: AUC x1 vs x3 >= 0.75 AND excess over the floor >= 0.05 AND flag rate <= 15%;
- **fails**: AUC x1 vs x3 < 0.60, OR excess <= 0;
- **mixed**: anything else. Point estimates decide.
Per held-out family: the reading shared by at least 2 of the 3 features, otherwise "mixed".

**In-family reference (descriptive)**: the same O and T2 heads fitted inside T, out-of-fold (5 folds; landmark: the
landmark family's partner-run groups `groups_and_folds`, imported unchanged, partners of test hosts purged from
training; diffusion: blocks; GAN: blocks), on the same features. Transfer gap = LOFO minus in-family AUC (bootstrap).

## (3) Plain answer, fixed rule

"A detector trained on one-person morphs of several pipelines would be expected to detect two-person morphs of an
unseen pipeline" is stated as **yes** if all three held-out families read "transfers"; **no** if at least two read
"fails"; otherwise **partly**, naming the families. The answer is qualified, never upgraded, by the threat probes.

**Threat probes (descriptive, fixed wording):** with the LOFO one-person head on the held-out family:
- landmark held out: xm vs x3 (mirror self-morph, one photograph) in 0.40 to 0.60 while x1 vs x3 >= 0.75 is worded
  "reads blending of captures, not a second identity"; face-only and surround-only blanked x1 vs x3 (the verifier's
  test of where the signal sits); matched-geometry x1g vs x3;
- diffusion held out: x3 vs x2 below 0.5 is worded "same-person mixes score above two-person morphs"; share of FRLL
  100-step reconstructions flagged at the threshold that flags 5% of the 20-step reconstructions (above 15% is worded
  "reacts to decoding steps without mixing"); face-box-only and face-blanked x1 vs x3 (CLIP only);
- GAN held out: set H x1s vs x3 in 0.40 to 0.60 while x1 vs x3 >= 0.75 is worded "the transferred signal is latent
  averageness, not a second identity"; x1 vs x1s; set H x1 vs x3.
- all: flag rate on the landmark hosts' own softened photos (landmark held out) and on SMDD `S_test`.

Sensitivity (descriptive): no person purge; landmark positives x2 only; unweighted families; all five C values; the
L2-normalised space for the cosines.

## Guards and rules

- FRLL persons never enter a fit: heads, scalers, C choice and directions use only FERET/FRGC hosts (and SMDD
  `S_fit` for the softening reference); asserted in code. FRLL images are scored only; directions estimated on FRLL
  images are labelled diagnostics. No conclusion from an FRLL neutral-plus-smiling pair.
- No new image is made; no file whose name contains a sealed token is opened (asserted on every path).
- One network per result; no ensemble, fusion or seed picking.
- Every command is tested on 8 images with its real command line before the full run.
- Compute: one GPU process (under 12 GB, expected under 4 GB, under 30 minutes), at most 2 CPU processes, `nice -n 10`,
  2 threads each. No cluster, no spending, no git.

## Not done

No new generation, no retraining of any backbone, no mirror self-morphs for diffusion or GAN hosts (none exist), no
graded mixing across families, no FaceMorpher engine in the transfer (descriptive engine), no benchmark-cell scoring
(the question is transfer between ladders).

## Amendment 1 (11 Nov 2026, 21:07 CET by the machine clock; after the 8-image cache check, before any cosine, head or score)

The registered cache check (max |difference| below 1e-3) passes for the GAN caches (CLIP pooled 1e-5, mean patch 0.0,
DINOv3 4e-4) and for the diffusion DINOv3 cache (8e-4), but **fails for the diffusion CLIP cache**: pooled 0.0031,
mean patch 0.0016 (minimum cosine 0.9999996). The diffusion owner extracted with TF32 off, the GAN owner and this code
with TF32 on. So that every feature comes from one extraction setting, the diffusion images used here (set `tr`, 1,548;
the registered flag set `ev` MorDIFF native and E7, 408; the FRLL decoding-step diagnostic `f256` D20, rec100, B20,
608) are re-extracted with the common code for both backbones, under the same ids; the diffusion caches are then not
used. Exception, descriptive only: the diffusion verifier's face-box-only and face-blanked CLIP features
(`blank_clip.npz`, TF32 off) are scored as they are; the difference (cosine at least 0.9999996) is far below any
reading. Check outputs: `/mnt/t7/smad_next/PD1/transfer/feats/check_common_space_{clip,dinov3}.json`.
