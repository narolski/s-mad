# AD1b: what a DiffAE morph of identical photos, and of a photo with its mirror image, is

Written 11 Nov 2026 before any code, image or score of this experiment was computed. Lead's request
(author questions): (1) does a diffusion morph of two identical photos reduce to the one-photo
reconstruction in our pipeline; (2) does a horizontal flip change anything for this diffusion morphing
method.

- **Pipeline:** the A43 generator unchanged in every part that touches an image
  (`mambamorph-code-a44/smadcvpr/a43_gen.py` sha fc862ec6…: pinned DiffAE commit 00c57d3f…, FFHQ256
  autoencoder checkpoint 9bd2ba9e…, `LitModel.encode` (z_sem), `encode_stochastic` T = 250 (x_T),
  `render` T = 20, the A43 `interp()` verbatim: z by lerp, x_T by slerp, α = 0.5, fp16 autocast,
  batch 16). Inputs: the X3 `a256` FRLL images (DiffAE `align.py` output) read with DiffAE's
  `ImageDataset`; flip = `torch.flip` of the loaded input tensor along width (lossless). Second pool:
  200 FRGC/colorFERET hosts from `/mnt/t7/smad_next/AR1/pool.csv` (first 200 by sha1 of `pid`; images
  H, S, B), aligned with the same unchanged DiffAE `align.py` runner the X3 a256 set used
  (`a41_diffae/data/scripts/run_align_unchanged.py`); no other image operation.
- **Part 1 (codes):** z_sem of A, flip(A), A′ (FRLL smiling; pool: S), B (FRLL: neutral photo of the
  next person in sorted order; pool: B). x_T (T = 250) for the same four on the first 30 FRLL persons.
  Medians [IQR] of Euclidean and cosine distance for (A, flip A), (A, A′), (A, B); per-person ratio
  dist(A, flip A) / dist(A, A′).
- **Part 2 (images, FRLL 102, 20 steps):** P_AA = render(interp(A, A)); P_AF = render(interp(A, flip A));
  D20′ = render(x_T(A), z(A)) re-run in this job (the D20 path) beside the stored A43 D20, C20, B20.
  (a) max / mean |P_AA − D20| (grey levels, 256-px PNG) and where the paths differ; (b) per-person
  median mean |·| of P_AF − P_AA, C20 − P_AA, B20 − D20(host); (c) left-right asymmetry = mean
  |img − mirror(img)| in a fixed central face box of the 256 frame (rows 70–220, cols 64–192) for A,
  D20, P_AF, C20, B20; (d) glintr100 cosine of P_AF to the raw photo A by the A43 route
  (prep_eval.kps → norm_crop → a2f_common.embed_crops 'glint'), beside the same for D20 and C20.
- **Part 3 (detectors):** only if the A43 scoring path runs unchanged on this machine.

## Fixed readings

- "**flip is close to a no-op for this diffusion pipeline, so a mirror self-morph is not a useful
  diffusion control**" if the median code ratio dist(A, flip A) / dist(A, A′) is below 0.25 AND the
  pixel difference of P_AF from P_AA is below 0.25 of that of C20 from P_AA;
  "**flip yields a genuinely different second image**" if both ratios are at least 0.5;
  otherwise "**partial**". Code ratio = z_sem Euclidean (primary); the others are printed beside it.
- "**Identical inputs reduce to the reconstruction**" if P_AA equals D20 within a mean absolute
  difference of 1 grey level; otherwise the difference and its cause are reported.

## Budget and guards

GB10 shared with other jobs: batch 16, one process; about 270 stochastic encodings (≈ 1 GPU-h) and 204
20-step renders. Outputs in `/mnt/t7/smad_next/AD1b/`; code in `src/AD1b/`. FRLL images evaluation
only. Tested on 8 images with the real command line before the full run.
