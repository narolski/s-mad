# Diffusion-autoencoder generation on Athena (DG1): pre-registration

Written 11 Nov 2026, before any code of this experiment ran, before any image was generated and before any
number below was measured. Owner run. No detector is scored in this experiment; other experiments read the images.

- **Purpose (plain words):** the diffusion controls are stuck on the shared DGX (about 157 s per DiffAE inversion while
  other jobs run). This experiment moves the exact MorDIFF-controls generator (A43) to Athena (A100, x86) and builds two
  image sets: a benchmark-linked FRLL set (set A) and a larger twin set outside FRLL (set B).
- **Generator (unchanged in every part that touches an image):** the A43 path (`mambamorph-code-a44/smadcvpr/a43_gen.py`
  sha fc862ec6…): pinned DiffAE commit 00c57d3f…, FFHQ256 autoencoder checkpoint 9bd2ba9e…, `torch.load(weights_only=True)`,
  `LitModel.encode` (z_sem), `encode_stochastic` T = 250 (x_T), `render` T = 20 or 100, the A43 `interp()` verbatim
  (z lerp, x_T slerp; α = 0.5 unless the dose rung sets it), the official fp16 autocast, batch 16,
  `torchvision.utils.save_image` (256-px PNG). Inputs are read with DiffAE's `ImageDataset`. The only new operations are
  the ones the identical-and-mirrored-inputs check (AD1b) already used: a lossless left-right flip of a loaded input
  tensor (`torch.flip` along width), and the identical-input case handled as its mathematical limit (the A43 slerp is
  0/0 for identical inputs, AD1b; the limit is `render(x_T(A), z(A))`, the A43 reconstruction path, which is used).
- **Seeds:** as A43: `LitModel` seeds with `conf.seed = 0` at start; DDIM with η = 0 in both directions, so no random
  number affects a pixel. Recorded per image as seed 0.
- **Storage:** every rung of both sets, including the genuine photos, is a 256 × 256 RGB PNG written by the same
  `save_image` call in the same job (the genuine rung G is the loaded input tensor written back; it must be
  pixel-identical to its DiffAE-aligned input, checked per image). No resize, blur or compression code of our own.

## Equivalence gate (before any production job)

On Athena, regenerate 8 images that already exist from the DGX path: the A43 20-step reconstructions D20 of 001_03,
002_03, 003_03, 004_03 and the A43 20-step two-person morphs B20 of the first four neutral draws of `A43_pairs.csv`
(draws 0–3). Compare with the stored files `/mnt/t7/smad_heldout/a43/gen/{D20,B20}/png256/`.

- Printed: per image and pooled, mean and maximum absolute pixel difference (grey levels, 0–255, all channels), share
  of differing pixels; face-recognition cosine (glintr100, the A43 route) between the Athena and the DGX file; mean,
  standard deviation, Laplacian variance and left-right asymmetry of both files.
- No detector scoring path is at hand on the DGX for new images without the A43 storage step, so "would a detector
  score move" is answered by the face-recognition cosine and the simple statistics, against the spread between
  different images of the same rung.
- **Fixed reading:** "equivalent" if the mean absolute difference of every one of the 8 images is at most 2 grey
  levels. Otherwise the cause is reported (library versions, kernel order, random number stream) and Athena images are
  treated as a new generation run that is never mixed with DGX images inside one contrast. Either way every manifest row
  carries `gen_run = athena_DG1`.

## Set A (benchmark-linked, FRLL, 102 persons, neutral photos only)

Inputs: the X3 a256 FRLL images (DiffAE `align.py` output, X3 data root SHA256SUMS c2c06f4a…). Host A = `<p>_03`.

| Rung (pool) | Image | Steps | n |
|---|---|---|---|
| genuine photo, same storage (G) | the DiffAE-aligned neutral photo written by the same writer | — | 102 |
| one-photo reconstruction (R2; REC) | render(x_T(A), z(A)) | 20, 100 | 102 + 102 |
| photo mixed with its mirror image (R3m; MIR) | render(interp(A, flip A)) | 20, 100 | 102 + 102 |
| two-person morph (R4; X) | render(interp(A, B)) for the 100 neutral pairs of the A43 pair list (`A43_pairs.csv`, expr 03, sha 5cce5fcb…) | 20, 100 | 100 + 100 |
| same-person neutral + smiling mix (R3, **confounded**; CONF) | render(interp(p_03, p_08)), the A43 C / C20 rebuild for continuity; confounded by expression and by the capture-detail difference of the smiling FRLL files (C1b review) | 20, 100 | 102 + 102 |

## Set B (twin set outside FRLL: FRGC 427 and colorFERET 109 hosts)

Inputs: `/mnt/t7/smad_next/AR1/pool.csv` (536 hosts; H = neutral host photo, S = neutral same-person photo of another
session, partner = another host of the same database whose S photo is the B photo; verified B = partner's S for 536 of
536). The 1,072 photos (H and S of every host) are aligned on the DGX CPU with DiffAE's `align.py` run unchanged
through the X3 runner `run_align_unchanged.py` (the AD1b procedure); photos without a detected face are dropped and
counted. Person-disjoint from FRLL by construction (other databases).

| Rung (pool) | Image | Steps | n (planned) |
|---|---|---|---|
| genuine photo, same storage (G) | the DiffAE-aligned H and S photos, written by the same writer | — | 1,072 |
| one-photo reconstruction (R2; REC) | render(x_T(H), z(H)) | 20 | 536 |
| photo mixed with its mirror image (R3m; MIR) | render(interp(H, flip H)) | 20 | 536 |
| same-person mix (R3; SAME) | render(interp(H, S)) | 20 | 536 |
| two-person morph (R4; X) | render(interp(H, partner S)) | 20 | 536 |
| dose (DOSE) | render(interp_α(H, partner S)), α = 0.1, 0.2, 0.3, 0.4 for the first 100 hosts by sha1 of the person id; α = 0.5 is X, α = 0 is REC | 20 | 400 |

Composition rule (`11_AUDIT_PLAN.md`): SAME and X use the same tool, the same host photo H and the same kind of
second photo (neutral, other session than H); every partner is itself a host.

## Validity numbers per rung (computed on the DGX after copy-back; descriptive, no detector)

- Face-recognition cosine to the host and to the partner: glintr100 by the A43 route (`prep_eval.kps` → insightface
  `norm_crop` → `a2f_common.embed_crops('glint')`); references: the raw FRLL JPEGs (as A43) for set A; the AR1 source
  frames of H and of the second photo for set B, and beside them the independent AR1 reference photo R.
- Share verifying at the A23 threshold for a false-match rate of 1 in 1,000 (0.239399): two-person morphs against both
  contributors (the plan's gate G-b asks ≥ 70%; printed against it), one-person rungs against the host.
- Left-right asymmetry: mean |img − mirror(img)| in the fixed central box of the 256 frame (rows 70–220, columns
  64–192), as AD1b.
- Laplacian variance: variance of `cv2.Laplacian` (CV_64F, default kernel) of the grey image in the same box; whole
  frame beside it.
- Medians with interquartile ranges per rung and step count; counts generated vs planned; non-finite or blank images.

## Budget, shards, stop rules

- Smoke job (environment build, the 8 equivalence images, an 8-image timing sample with 100-step renders): at most 1
  GPU-hour, one A100, `-c 8 --mem=64G`, `-C localfs`, all work in `$SCRATCH_LOCAL`.
- Production only after the smoke job passed and this file exists: up to 150 GPU-hours for sets A and B together, array
  tasks of at most 4 hours each, one result tar with a `.sha256` per shard. An honest estimate from the measured seconds
  per image on the A100 is written into `result.md` before submission.
- Environment: built inside a job under `smad-next/envs/DG1/`, starting from the DGX versions (Python 3.12.3, torch
  2.12.1 + torchvision 0.27.1, numpy 1.26.4, pillow 12.2.0, pytorch-lightning 2.5.5, torchmetrics 1.8.2, scipy 1.17.1,
  pandas 2.2.3, lmdb 1.7.3, lpips 0.1.4, pytorch-fid 0.3.0); where a version has no x86 wheel (or the CUDA build does not
  fit the driver), the nearest is taken and recorded.
- Stop: a shard fails on any non-finite image, a checkpoint or code hash mismatch, or a missing input.

## Command (tested on 8 images on the DGX with its real command line before the smoke job)

`python -I src/DG1/dg1_gen.py --repo R --ckpt C --inputs DIR --jobs CSV --out-root DIR [--bs 16]`, job lists from
`src/DG1/dg1_lists.py`; Athena wrappers `src/DG1/dg1_smoke.sbatch`, `src/DG1/dg1_prod.sbatch`.

## Pre-run review

Not run by a separate reviewer (generation only, no detector, no score); the equivalence gate is the binding check.
