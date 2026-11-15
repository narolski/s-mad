# Lead's own ideas, written before reading any generator output

11 Nov 2026, about 15:00 CET. These are the lead's ideas; the seven independent generators of the
ideation workflow did not see them. Terms: alpha = mixing fraction of the second face (0 = none,
0.5 = equal blend). Rungs R0 to R4 as in `11_AUDIT_PLAN.md`.

## The diagnosis in one sentence

Every failure so far has the same shape: the label is one number per image, so any property that is
constant within an image and differs between the classes (resolution history, compression, format,
frame, colour, source, expression, renderer) can carry the label. Matching the classes removes only
the properties we thought of.

## S1. Alpha-field supervision (main idea)

Make the training target vary inside each image. Build landmark morphs whose texture mixing fraction is
a smooth spatial field alpha(x) between 0 and 0.5 (for example a gradient across the face, or a bump on
one facial part), with the geometric warp applied everywhere. Train a per-patch head to regress
alpha(x). The image score at test time is the mean predicted alpha over the face.

Why it should be shortcut-free: within one training image the blended and unblended regions share
every global property. A cue that is constant over the image cannot predict a target that varies over
it. This holds for cues we have not listed. Images with alpha = 0 everywhere that went through the same
pipeline stop "pipeline output" from becoming evidence for a non-zero mean.

What it reads: superposition of two textures (double contours, half-contrast details, averaged fine
texture relative to the rest of the same image). That is the pixel-level definition of landmark
morphing, and same-person morphs have it too, in line with the author's ruling.

Cheapest test (AF0): frozen DINOv3 and CLIP patch tokens, a per-patch linear or small MLP head, a few
thousand alpha-field morphs built on CPU from FRGC and colorFERET persons not used in the audit sets.
Falsifiers are fixed in `experiments/AF0/prereg.md`.

Stress test that would make the paper: train the dense head and an ordinary image-level head on a
deliberately confounded set (all mixed images from one photo source, all unmixed from another), then
test on the crossed set. Prediction: the image-level head collapses, the dense head does not.

Closest prior work to check: PW-MAD (pixel-wise supervision with a constant map per image, which our
record shows follows processing history), Face X-ray and self-blended images (blending boundary of
face swaps, image-level labels), morph localisation by feature-wise supervision (Qin et al.), LAA-Net.
The claimed difference is the within-image varying target used as a shortcut blocker. Not verified.

## S2. Synthesis-field supervision for GAN and diffusion morphs

Same principle for generated morphs: composite a generator's output (reconstruction or morph) into the
aligner-only copy of the photo through an analytic smooth mask, regress the mask. A second dense head
on the same backbone. It reads "this region was rendered", which is not specific to two identities.
Needs the author's ruling on whether a one-photo reconstruction is a processed genuine image.

## S3. What one image can and cannot show (analysis for the paper)

- Landmark morph: superposition evidence (local, legitimate), reduced texture variance (only relative
  to unblended regions), warp interpolation traces (fragile), splice boundary, identity typicality.
- GAN or diffusion morph: the render trace (shared with any one-person render), and typicality. A
  perfectly rendered blend of two latents is a realistic face of a person who does not exist; nothing
  else marks it. So "two-identity" detection of generator morphs from one image is bounded by
  typicality, and our measured R2 versus R4 results near 0.5 for every detector agree.

## S4. Operational meaning of "state of the art and shortcut-free"

1. Detection error with the genuine class history-matched (R1 versus R4) on every benchmark cell.
2. False alarms on processed genuine photos at a threshold fixed on unprocessed ones (E7 photos, tool
   on one photo). First data point from the MorDIFF re-read: at the benchmark threshold the released
   detectors flag 51 to 98 percent of history-matched genuine photos.
3. Ladder shares: construction share at most 0.2.
4. Unseen photo source and unseen tool.
5. Native benchmark numbers beside these, with the morph-free network as the reason they cannot be
   read at face value.

## S5. Other ideas, lower priority

- Paired-difference nulling: estimate the "benign channel" subspace from pairs of the same photo with
  different histories (not FRLL), project it out of frozen features, fit a linear head in the rest.
  Provable for linear readers, minutes to run. A baseline for S1.
- Identity typicality with a stated ceiling (norm shrinkage of the mean of two identity vectors).
- Protocol-compliant arm: alpha-field morphs built from SMDD faces only, so the comparison with
  MADation changes nothing but the supervision.
- Dense backbones as a side quest: the frequency stream of our Mamba design becomes safe to use once
  the target varies within the image.
- Expression-balanced and frame-matched benchmark variants as a contribution (expression alone
  separates 11 of 17 cells at up to 0.75 according to today's cue check).

## What I would drop

Two-identity embedding head, stand-alone mixing-fraction regression (absorbed by S1), SelfMAD
retrains, the morph-free GAN network, the large generator twin set, pipeline-count ablation.
