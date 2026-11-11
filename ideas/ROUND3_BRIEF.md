# Ideation round 3: brief for idea generators and vetters

11 Nov 2026, 18:00 CET. Written by the lead. The author asked to use the wait for the cluster to work on
new ideas. Rounds 1 and 2 are in `IDEAS_v1.md`, `CONSOLIDATED_v1.md` and `CONSOLIDATED_v2.md` (read
`CONSOLIDATED_v2.md` first; it says what did not survive vetting).

## Goal

A CVPR paper (deadline 16 Nov; experiments end 14 Nov) on single-image face morphing attack detection
(S-MAD: one image in, "morph or genuine" out) with (a) clear evidence that released detectors rely on cues
of the benchmark data, and (b) one network that is state of the art on the published tables and
demonstrably does not rely on those cues.

## The ladder (our main instrument)

For one host photo and one morphing tool: R0 camera photo; R1 the same photo with the morphs' storage
history (the existing shrink-and-enlarge path); R2 the tool run on one photo; R2w warp only (geometry moved,
no blending); R3m the photo blended with its own mirror image; R3 a morph of two photos of the same person;
R4 a morph of two persons. A detector that reads "a second identity was mixed in" must separate R4 from R3
and must not separate R0 from R1 or R2w. Class proposal awaiting the author: genuine; morphing attack (two
or more persons); single-subject manipulation (reported separately, never inside error rates).

## Established (independently reviewed)

- SelfMAD release, at its own decision rule: flags 0% of unprocessed genuine photos, 45% after a 50%
  shrink-and-enlarge, 97% of photos stored small; genuine photos with a morph family's storage history are
  flagged more often than the morphs in six families.
- MADation ViT-B/16 release (on our frames): the 63 to 65 pixel storage history raises the score of nearly
  every photo on two photo pools. MADation ViT-L/14 release: no usable statement yet (scores saturated on
  our frames; our frames do not reproduce published numbers; an own-crop re-score is running).
- Benchmark construction: in all 17 benchmark cells a file attribute separates the classes perfectly; in 12
  of 17 the genuine class is half smiling against neutral morphs; smiling FRLL files are 1.43 times larger
  with a 4.8 times noisier backdrop (so "expression is used" cannot be claimed). Our own aligner leaves a
  black border around smaller morph files.
- Diffusion morphs (MorDIFF-type, diffusion autoencoder): three adapted releases do not separate a two-person
  morph from a one-photo reconstruction (AUC 0.40 to 0.49). One frozen-encoder release does (0.66 at 20
  sampling steps, 0.85 at 100).
- StyleGAN3 latent morphs: no released detector separates a morph from a one-person render (best 0.61).
- SMDD, the standard training set: all 15,000 training morphs share five second contributors; the genuine
  class is 25,000 StyleGAN2 renders; none of the genuine renders is a contributor.
- Softness floor: a two-person landmark morph has 0.52 times the Laplacian variance of its own warped
  halves; that number alone separates a morph from its halves at AUC 0.76 (512 px) to 0.87 (224 px). A photo
  blended with its own mirror already carries 40 to 76% of the two-person value of the blend-disagreement
  target.
- A frozen encoder is not protection: the frozen-encoder MADation ViT-B/16 release also moves with storage
  history.

## New today (owners' first numbers, NOT yet reviewed: leads, not facts)

- Paired differences, GAN latent morphs (the author's idea; experiment PD1; CLIP pooled features, one fold,
  no intervals). Rungs: x0 camera photo, x1 one-photo reconstruction G(w_a), x2 same-person mix
  G((w_a0+w_a1)/2), x3 two-person morph G((w_a0+w_b0)/2). Within-host steps: x0→x1 separable at 0.98
  (pipeline); x1→x2 0.67; x2→x3 0.65 (second identity); x1→x3 0.73. A head trained ONLY on one-person mixes
  (x2 vs x1) ranks two-person morphs above reconstructions at 0.78; a head trained on two-person morphs
  reaches 0.77. Neither separates x1 from x0 (0.51). So training on same-person mixes transfers fully, and
  the signal it carries is mostly "two codes were mixed", only weakly "a second identity".
- Frozen features on diffusion-autoencoder morphs (experiment FZ1). A cross-validated logistic probe on
  frozen features (CLIP ViT-L/14, DINOv3, DINOv2) separates two-person morph from one-photo reconstruction
  at 0.945 to 1.000, including the matched 20-step contrast; and StyleGAN3 morph from one-identity render at
  0.89 to 0.94 (but morph from spread-matched render only 0.58 to 0.63). Simple statistics: Laplacian
  variance alone gives 0.966 at 100 steps on the centre of the 512 frame (morphs are sharper than the
  reconstructions there); for the matched 20-step contrast simple statistics reach only 0.66 to 0.70. So
  the one release that "worked" does no better than a sharpness statistic, while a probe trained on the
  contrast reads something more at 20 steps. A head trained on SMDD only has not been run yet.
- Blend-evidence map (experiment AF0, first small pass, DINOv3 patch tokens, ridge head, 600 training
  morphs): image-level separation of morphs 0.999; map quality 0.275 (drop mark 0.2, pass mark 0.4); but
  the head shifts warp-only genuine images (R2w) by 0.73 standard deviations on FaceMorpher (limit 0.3) and
  0.30 on OpenCV. It reacts to warping or softness, as the round-2 forensics review predicted.
- Identity shrinkage (experiment ID0). Exact landmark shapes, no image: two-person mean shape against a
  real shape AUC 0.725 [0.689, 0.758], rising monotonically with the mixing fraction. In CLIP and
  diffusion-autoencoder feature spaces the statistic reads storage history (the control fails) and the
  closed form overshoots (predicted 0.99, observed at most 0.70).
- Identical and mirrored inputs, diffusion autoencoder (experiment AD1b, 4 persons): two identical inputs
  reduce mathematically to the one-photo reconstruction. A mirrored copy behaves like a second photo of the
  same person (semantic-code distance to own mirror 0.776, to another photo of the same person 0.773, to
  another person 1.744). Left-right asymmetry in the face box: input photo 19.6, one-photo reconstruction
  18.3, same-person mix 18.7, two-person morph 12.0, mix with own mirror 2.1.
- Expression-cue study corrections: one CNN recipe does reach 0.667 on the smiling-against-neutral split;
  a SelfMAD-style recipe ranks the smiling photo higher in every untied pair.

## Ideas already on the table (improve, replace or kill; do not re-propose unchanged)

1. Paper chain of round 2: fixed-threshold failure of released detectors under storage history; a training
   protocol that removes it (pipeline-matched, history-crossed rebuild of SMDD on the MADation recipe, CLIP
   with LoRA: balanced partners, warped halves as genuine images, softened examples through the existing
   shrink-and-enlarge path); the blend-evidence map only if it passes its controls.
2. Paired differences (the author's idea), in test on landmark, GAN and diffusion ladders.
3. Identity shrinkage: weak so far.
4. Morph-free networks and label-permuted fits as references (what a network reaches with no morph seen).

## Hard constraints (binding)

- One network. No ensembles, no fusion of scores or seeds, no seed picking, no gate on resolution, file
  size, format or source.
- Image operations allowed: the approved warp path and the unchanged OpenCV and FaceMorpher morphers
  (modified warp paths if verified against the unchanged tool), constant-colour blanking, lossless flip, the
  existing shrink-and-enlarge path run unchanged, existing processed files. No new blur, resize, resampling
  or JPEG code. Generators (StyleGAN inversion, diffusion autoencoder) may be run unchanged.
- Sealed files are never opened (`manifests/valx.csv`, anything named FST, A12SP).
- A genuine image that was only processed (crop, alignment, compression) and is called a morph is an error.

## Resources and time

- Three days of experiments. The DGX (one shared GPU, 20 cores) is saturated. Athena (A100 40 GB, 30,000
  GPU-hours granted) is expected within hours and may then be used heavily. WCSS is closed to us for now.
  Rented GPUs only for small, clearly justified runs.
- Data on disk: FRLL and FRLL-Morphs, FRGC 2.0, colorFERET, FEI, FFHQ, SMDD, the corrected MAD22, MorDIFF
  and DiM material, MIPGAN sets. Own ladders: landmark ladder (536 hosts, two engines, rungs R2w, R2wm, R3m,
  R3, R4, plus graded mixing at six levels for 300 hosts); 64 GAN blocks (256 captures, x0 to x3);
  diffusion-autoencoder ladder (A43 material; a larger run finishes tonight). Feature caches: DINOv3
  ViT-L/16 patch tokens at 512, CLIP ViT-L/14 patch tokens at 224.
- Released detectors on disk: MADation ViT-B/16 and ViT-L/14 (adapted and frozen-encoder variants), SelfMAD
  HRNet-W18, MixFaceNet-SMDD and others. Recipes we can retrain: MADation (CLIP with LoRA), SelfMAD-style.

## What a usable idea looks like

- Works at test time on ONE image.
- Names the signal it reads and the control that separates that signal from softness, storage history,
  border, capture detail, expression and generator fingerprint.
- Has a decisive first test of at most one day on data that exist, with a number that kills it.
- States how it reaches or keeps state-of-the-art numbers on the published tables.
- Records: experiment folders under `/home/narolski/smad-next/experiments/` each hold a `README.md`
  (full record) and `result.md`.
