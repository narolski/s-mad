# Signal isolation by paired differences (PD1), cross-family transfer: result

Owner's page, 11 Nov 2026, finished 21:20 CET (machine clock). Facts first, readings as registered. Not reviewed.
Registration: `prereg.md` (first saved 21:05; amendment 1 at 21:07 before any number; amendment 2 at 21:16, post hoc,
after the full CLIP results). Full record: `README.md`. Tables: `cosines.csv`, `lofo.csv`, `infamily.csv`,
`sensitivity.csv`, `probes.csv`, `pairwise_posthoc.csv`, `readings.json`. Raw outputs:
`/mnt/t7/smad_next/PD1/transfer/res/{clip_pool,clip_patch,dino_pool}{,_posthoc}.json`.

Terms. Host photo **x0**; pass-through **x1** (landmark: warp-only image; diffusion autoencoder (DiffAE) and GAN:
one-photo reconstruction); mirror self-morph **xm** (landmark only); same-person morph or mix **x2**; two-person morph
**x3**. Steps: pipeline trace (x0 to x1), one-person mixing (x1 to x2), whole morph (x1 to x3). One-person head =
linear head with the families' within-host paired loss, trained only on one-person images (landmark x2 and xm, the
others x2, against x1). Two-person head = the same on x3 against x1. Leave one family out (LOFO) = fit on two families,
score the third. AUC = area under the ROC curve (0.5 chance), intervals = 95% two-way person bootstrap over the
held-out family (2,000 draws) unless stated. Floor = best single simple image statistic on the held-out family's x1
vs x3 (landmark 0.886 band power; diffusion 0.773 PNG size; GAN 0.601 mirror asymmetry; the families' registered
floors). Features, all in one space: CLIP ViT-L/14 pooled (primary), CLIP mean patch token, DINOv3 ViT-L/16 pooled,
written below as **CLIP pooled / CLIP patch / DINOv3** in that order.

## Answer

1. **There is no shared mixing direction.** The one-person mixing direction of each family points elsewhere in the
   other two. Cross-fitted cosines (the registered statistic): landmark with diffusion 0.44 / 0.37 / 0.15, landmark
   with GAN -0.04 / -0.15 / -0.13, diffusion with GAN -0.27 / -0.37 / -0.45. Each direction is stable within its
   family (split-half reliability 0.94 to 0.99; GAN 0.67 to 0.83). All 9 pairs read "not shared". The whole-morph
   step reads the same way. Registered reading in all three features: **no shared mixing direction**.
2. **Leave one family out fails for every held-out family on every feature (9 of 9 cells "fails").** The one-person
   head trained on two families ranks the third family's two-person morphs above its pass-through images at AUC
   0.43 / 0.68 / 0.52 (landmark held out), 0.56 / 0.56 / 0.51 (diffusion) and 0.38 / 0.30 / 0.33 (GAN). That is below
   every floor and often below chance. The same heads fitted inside each family reach 1.00 / 0.99 / 0.95,
   0.95 / 0.88 / 0.91 and 0.81 / 0.78 / 0.79, so the gap is the change of family, not the code or the features. Heads
   trained on two-person morphs of two families fail as well (0.48 / 0.69 / 0.56; 0.59 / 0.68 / 0.59;
   0.44 / 0.41 / 0.38). So the failure is not specific to one-person training. Flag rates on softened genuine photos
   stay at 3.9 to 8.8%, so softness is not what goes wrong.
3. **Plain answer: no.** With these frozen features, a detector trained on one-person morphs of several pipelines
   would not be expected to detect two-person morphs of a pipeline it has not seen. Registered rule: "no" if at least
   two held-out families fail; all three fail. Each family's one-person "signal" is specific to its pipeline:
   - landmark: double exposure, mostly in the surround;
   - diffusion: render texture;
   - GAN: the latent code pulled toward the mean.

   These signals do not share a direction, and the GAN signal is partly opposed to the other two.
   **Largest threat to this reading:** "family" here means pipeline plus frame, resolution and photo source:
   - landmark: 512 px aligned frames;
   - diffusion: 256 px DiffAE crops;
   - GAN: 1,024 px renders, with camera photos in a third frame.

   Each family's one-person signal was also found to be largely a pipeline artefact (by the verifiers for landmark and
   diffusion, by the owner's registered qualifier for GAN). So the negative shows that
   these artefacts do not transfer. It does not show that a blending signal confined to the face could not transfer
   once the pipelines are run on the same photos in one frame. A post hoc cell shows that some shared component
   exists: the unfitted mean mixing direction of diffusion transfers to landmark morphs at 0.976. But it reads the
   landmark surround (surround only 0.95, face only 0.54).

## Verified family verdicts this rests on

Landmark **mixed** (registered: "idea works"; the verifier: the separation sits in the double-exposed surround).
Diffusion **mixed** (registered: "idea works"; the verifier: matched by a 26-statistic head, reacts to decoding steps).
GAN: **no independent verification was delivered** (a partial sceptic run exists in `/mnt/t7/smad_next/PD1/gan/verify/`).
The owner's registered "idea works" therefore stands, with its own latent-averageness qualifier fired. The transfer
result is consistent with the two verified "mixed" readings and with the GAN qualifier. If the one-person signals were
morph signals, some shared direction would be expected; none is found.

## (1) Cosines between step directions (z-space, cross-fitted over 200 person-half splits; `cosines.csv`)

Raw cross-fitted cosine (disattenuated in brackets). The split range is narrow (at most ±0.14) and is not a confidence
interval. CLIP pooled / CLIP patch / DINOv3:

| Step | landmark vs diffusion | landmark vs GAN | diffusion vs GAN | Registered reading |
|---|---|---|---|---|
| one-person mixing x1 to x2 | 0.44 (0.45) / 0.37 (0.39) / 0.15 (0.16) | -0.04 / -0.15 / -0.13 | -0.27 / -0.37 / -0.45 | no shared direction (all 3 features) |
| whole morph x1 to x3 | 0.38 / 0.37 / 0.23 | -0.16 / -0.11 / -0.13 | -0.16 / -0.09 / -0.25 | no shared direction |
| pipeline x0 to x1 | 0.08 / -0.18 / -0.03 | 0.02 / 0.08 / 0.09 | **0.59** / 0.30 / 0.30 | no shared direction (diffusion-GAN "shared" in CLIP pooled only) |

- Reliabilities (split-half): landmark and diffusion mixing 0.94 to 0.99; GAN mixing 0.67 / 0.70 / 0.83. Whole morph:
  landmark 0.95 to 0.99, diffusion 0.79 to 0.89, GAN 0.65 to 0.69. The "not shared" readings are therefore not a
  noise ceiling.
- L2-normalised space (secondary) gives the same pattern. For the mixing step only landmark vs diffusion in CLIP
  pooled reaches 0.50 ("shared" for that pair), and the overall reading is still "no shared direction".
- Within each family, mixing and whole morph are aligned, as the families reported: 0.85 to 0.94 for landmark,
  0.68 to 0.79 for diffusion, 0.61 to 0.74 for GAN.
- References (one-person mixing against them):
  - SMDD softening: landmark -0.23 / -0.08 / 0.04, diffusion -0.18 / -0.14 / -0.16, GAN 0.18 / 0.23 / 0.22. None
    is above 0.5, so the mixing directions are not softness.
  - GAN latent spread (one identity, latent moved to the mean): GAN mixing 0.56 / 0.60 / 0.73, diffusion mixing
    -0.28 / -0.44 / -0.51, landmark -0.01 / -0.24 / -0.15.
  - Landmark host softening: landmark mixing 0.18 to 0.27. Diffusion decoding steps (FRLL, diagnostic): within ±0.24
    of all mixing directions.
- Notable cross-step alignment: the GAN pipeline step (camera photo to GAN render) aligns with landmark mixing at
  0.59 / 0.38 / 0.32 and with diffusion mixing at 0.32 / 0.44 / 0.45. "Rendered by a generator" resembles "blended"
  in these features.

## (2) Leave one family out (registered heads; `lofo.csv`)

Training hosts after removing every person of the held-out family:
- landmark held out: diffusion 124, GAN 40;
- diffusion held out: landmark 291, GAN 56;
- GAN held out: landmark 399, diffusion 316.

C was chosen by inner leave-one-family-out. Flag rate = the registered softened genuine set(s) of the held-out family
at the threshold that flags 5% of its untouched genuine frames (11 of 204). For landmark, the larger of the FRLL E7
OpenCV and corrected MAD22 E7 OpenCV rates counts.

| Held out | Head | CLIP pooled | CLIP patch | DINOv3 | Floor | Reading (3 features) |
|---|---|---|---|---|---|---|
| landmark (536 hosts) | one-person | 0.432 [0.386, 0.482] | 0.676 [0.632, 0.718] | 0.522 [0.481, 0.563] | 0.886 | fails / fails / fails |
| | two-person | 0.481 [0.440, 0.521] | 0.685 [0.645, 0.723] | 0.561 [0.522, 0.599] | | |
| | flag (one-person) | 4.4% | 5.4% | 5.4% | | |
| diffusion (516 hosts) | one-person | 0.555 [0.499, 0.613] | 0.559 [0.500, 0.624] | 0.506 [0.444, 0.568] | 0.773 | fails / fails / fails |
| | two-person | 0.589 [0.528, 0.650] | 0.683 [0.619, 0.742] | 0.586 [0.522, 0.648] | | |
| | flag (one-person) | 8.3% | 8.3% | 5.9% | | |
| GAN (256 hosts) | one-person | 0.383 [0.298, 0.475] | 0.300 [0.218, 0.390] | 0.325 [0.251, 0.408] | 0.601 | fails / fails / fails |
| | two-person | 0.439 [0.350, 0.527] | 0.414 [0.336, 0.492] | 0.383 [0.301, 0.476] | | |
| | flag (one-person) | 3.9% | 4.4% | 5.4% | | |

- Excess over the floor (one-person head): -0.45 to -0.21 (landmark), -0.27 to -0.21 (diffusion), -0.30 to -0.22 (GAN).
  All intervals lie below 0.
- One-person minus two-person head: -0.12 to -0.01.
- Paired share of held-out hosts with s(x3) > s(x1): 0.42 / 0.77 / 0.54 (landmark), 0.56 / 0.60 / 0.50 (diffusion),
  0.33 / 0.23 / 0.23 (GAN).
- **Every C value fails.** One-person head, x1 vs x3, over the five C values:
  - diffusion held out: 0.555 to 0.576 / 0.557 to 0.569 / 0.505 to 0.512;
  - GAN held out: 0.373 to 0.383 / 0.300 to 0.310 / 0.325 to 0.345;
  - landmark held out: 0.427 to 0.781 / 0.581 to 0.805 / 0.506 to 0.553. The smallest C does best here, still below
    the floor.
- Common SMDD flag rate (held-out renders against their E7 copies): 0.5 to 10.6%, with one exception: 38.1% for the
  CLIP pooled one-person head with diffusion held out (C = 10). Hosts' own softened photos (landmark held out): 4.0 to
  10.5%.
- Unfitted mean-direction head (registered, descriptive):
  - landmark held out: 0.975 [0.957, 0.988] (CLIP pooled; excess +0.090, flag 4.4%), 0.888 (CLIP patch, excess
    +0.002), 0.575 (DINOv3);
  - diffusion held out: 0.64 / 0.61 / 0.45;
  - GAN held out: 0.41 / 0.30 / 0.31.

**In-family reference on the same features** (out-of-fold, 5 folds, persons of test hosts removed from training;
`infamily.csv`). One-person head x1 vs x3:
- landmark 1.000 / 0.994 / 0.947;
- diffusion 0.949 / 0.877 / 0.913;
- GAN 0.814 / 0.784 / 0.785.

These are within 0.02 of the families' own numbers where the features coincide. Transfer gap (LOFO minus in-family,
paired bootstrap):
- landmark -0.57 [-0.61, -0.52] / -0.32 / -0.43;
- diffusion -0.39 [-0.45, -0.33] / -0.32 / -0.41;
- GAN -0.43 [-0.55, -0.31] / -0.48 / -0.46.

**Sensitivity** (`sensitivity.csv`): no person purge (full training families), landmark positives x2 only, unweighted
families. All 27 variant cells fail. One-person head range: landmark 0.43 to 0.77, diffusion 0.40 to 0.58, GAN 0.30
to 0.40. Without the purge, the two-person head reaches 0.77 / 0.72 / 0.65 on landmark, still below the floor.

**Threat probes** (registered, one-person head of the LOFO run; `probes.csv`):
- landmark held out: mirror self-morph vs x3 0.33 / 0.40 / 0.44. Blanked: face only 0.48 / 0.55 / 0.48, surround
  only 0.64 / 0.73 / 0.55. Matched-geometry warp-only vs x3 0.43 / 0.67 / 0.51. Nothing to qualify, since x1 vs x3
  is already below 0.75.
- diffusion held out: x2 vs x3 0.60 / 0.57 / 0.63. Photo vs reconstruction (pipeline) 0.75 / 0.67 / 0.65 against
  the own one-person mix 0.47 / 0.49 / 0.38, so the transferred head reads the DiffAE pipeline more than DiffAE
  mixing. FRLL 100-step reconstructions flagged at the 20-step threshold 0 to 2.5% ("reacts to decoding steps":
  no).
- GAN held out: set H x1 vs x3 0.38 / 0.24 / 0.25; x1s vs x3 (spread-matched one identity) 0.46 / 0.49 / 0.50;
  x1 vs x1s 0.43 / 0.25 / 0.26. Camera photo vs reconstruction 0.95 / 0.95 / 0.96. The head trained on landmark and
  diffusion reads GAN rendering (camera vs render) and the GAN latent pull with the opposite sign: renders whose
  latent sits nearer the mean score lower, whether they are morphs or not.

## Post hoc (amendment 2; descriptive, not part of any reading)

**Pairwise single-family transfer** (`pairwise_posthoc.csv`), one-person head x1 vs x3:
- diffusion to landmark: 0.811 / 0.906 / 0.605 (excess -0.075 / +0.021 / -0.281). The unfitted mean direction gives
  0.976 [0.957, 0.988] / 0.902 / 0.566. Read by the registered rule: "transfers" (CLIP pooled mean direction only),
  "mixed" (CLIP patch), otherwise "fails".
- GAN to landmark: 0.19 / 0.39 / 0.46 (mean direction 0.10 / 0.41 / 0.47): opposed.
- landmark to diffusion: 0.70 / 0.74 / 0.62. GAN to diffusion: 0.49 / 0.42 / 0.41.
- landmark to GAN: 0.45 / 0.39 / 0.42. Diffusion to GAN: 0.31 / 0.28 / 0.32.

Landmark and diffusion share part of a direction; GAN is opposed to both. The landmark result of the registered LOFO
fails partly because the 40 GAN hosts pull the head the other way.

**What the one transferring direction reads.** Probes of the mean direction of diffusion and GAN, scored on landmark:
- surround only (face grey) 0.948 [0.923, 0.967], face only (surround grey) 0.537 [0.501, 0.576] (CLIP pooled; CLIP
  patch 0.914 against 0.522);
- mirror self-morph vs x3 0.44 / 0.45;
- matched geometry 0.974.

It reads the double-exposed surround of the OpenCV-style engine, the same thing the landmark verifier found for the
in-family heads, and it does not separate one-photograph blends from two-person morphs.

## What failed, what is weak, what could not be verified

- The registered cache check failed for the diffusion CLIP cache (max difference 0.0031 against a bound of 1e-3;
  the cache was made with TF32 off). All diffusion images were re-extracted with the common code (amendment 1). The
  GAN caches passed (1e-5 / 0 / 4e-4) and are reused.
- The landmark features here are not the landmark family's registered ones. That family used the CLIP class token
  before projection with timm's bicubic transform, and DINOv3 at 512 px. The in-family reference recomputed here
  (1.000 / 0.994 / 0.947) is the comparison on equal features.
- The GAN family has no delivered independent verification.
- The analysis code-path test (`--quick`: 50 draws, 10 splits) produced the first cross-family numbers at 21:14,
  after the registration. Its head point estimates are identical to the full run's (only the number of draws and
  splits differs). The full run used the same code unchanged. Amendment 2 was written after the full CLIP results had been seen.
- Bootstrap intervals cover person sampling of the held-out family only. They do not cover the sampling of the
  training families or the head fit. The C range is reported instead.
- Training sizes after the person purge are small for GAN as a training family (40 and 56 hosts). The no-purge
  sensitivity (256 GAN hosts) gives the same readings.
- Only three families. "Unseen pipeline" is tested three times, each with a single held-out family.
- Frozen features and linear heads only. A fine-tuned network was not tested.
- The diffusion blanked probes use the diffusion verifier's CLIP features (TF32 off; cosine at least 0.9999996 to the
  common code). They are descriptive.
- Not done: FaceMorpher engine, benchmark cells, any new image, graded mixing.

## Compute

One GPU process, about 9 minutes in total (21:07:56 to 21:16:54; 9,140 images × 2 backbones, peak 1.72 GB). Analyses on the CPU: about
2 minutes in total, at most 2 processes, `nice -n 10`, 2 threads each. No cluster, no spending, no git operation.
