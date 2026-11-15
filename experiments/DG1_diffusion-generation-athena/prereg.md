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

---

## Amendment 1 (11 Nov 2026, 19:45 CET): reading registration

Written after the independent pre-run review (`experiments/reviews/PRERUN_DG1_20261111.md`, finding 1) and the lead's
instruction, **before any production image was looked at and before the validity table was computed on production
images**. Production array 3545841 was running; only the smoke images had been read (equivalence gate). These rules
bind every experiment that scores DG1 images and the DG1 validity table itself, because its per-rung statistics are
the simple baselines of every contrast.

- **Primary contrast:** two-person morph (X) against same-person mix (SAME), set B (FRGC and colorFERET), 20 steps.
- **Morph against reconstruction (X vs REC)** is printed only beside morph against the fresh-noise render (X vs FRESH,
  amendment 2): the reconstruction is the only rung rendered from its own photo's noise map, so X vs REC alone
  mixes "two persons" with "noise map not the photo's own".
- **Mirror mix (MIR)** is a trace contrast only (it tests the mixing operation on one photo; no identity reading).
- Set A (FRLL) contrasts are benchmark-linked and secondary; its neutral+smiling mix (CONF) stays labelled confounded.
- **Statistics:** AUC with the two-way person bootstrap (the `a41_read.py` pigeonhole method, host and partner as the
  two ways), B = 10,000; 95% intervals. Any learned probe or baseline is fitted out of fold with folds that hold out
  **whole partner cycles** (the landmark ladder's fold rule, `src/AR1/folds.py`), because a morph (H_p, S_q) and the
  twin (H_q, S_q) share the photo S_q.
- **Baselines:** every detector number is reported as its excess over the best of five simple baselines computed on
  the same images and the same contrast: PNG file bytes; Laplacian variance (face box, `dg1_validity.py`); left-right
  asymmetry (face box); 32-pixel thumbnail (32 × 32 × 3 block means, logistic; `src/AR1/baselines.py` `thumb32`);
  surround-only thumbnail (face blanked with constant colour, same block means; `src/AR1/baselines.py` `background`).
  The excess is paired by image, with the same bootstrap.
- **Flag rates:** at a camera-photo threshold (each detector's score at 5% false alarms on camera photos of a
  development pool fixed by the scoring experiment, never on DG1 images), the share flagged of every rung, under both
  class policies of the fixed-threshold re-read (EV1, A1): policy G counts one-person renders (REC, FRESH, MIR, SAME,
  noise-only and semantic-only mixes with the host's own photo) as genuine, so their flags are false alarms; policy X
  leaves them out as inadmissible and prints them as their own rows. Exact (Clopper-Pearson) intervals.
- **Path to the detectors:** the 256-px PNG files go to each released detector through that release's own
  preprocessing, as in the own-crop re-score (RS1), identical for every rung. The earlier A43 storage step (crop to the
  eye-relative extent of a published MorDIFF file, OpenCV PNG, `prep_eval.align`) is a secondary, benchmark-linked row
  only (set A).
- **No mixing of runs:** images from the DGX and from Athena are never combined inside one contrast, although the
  equivalence gate passed (finding 7: morphs differ more across machines than reconstructions, max 2–4 against 1). Within
  Athena, a contrast uses images of one process (one array task) where amendment 2 provides them.
- **Sensitivity and strata:** every set B contrast is printed with and without flagged items (black wedges in the input
  photo; greyscale input; the two probable twin pairs `frgc:04637`/`frgc:04638` and `frgc:04692`/`frgc:04856`; shared
  capture date of the two photos), and per database (FRGC, colorFERET). Input-pair pixel disagreement is a covariate
  of the dose readings.
- **Validity table (this experiment):** descriptive. Its cue columns (bytes, Laplacian variance, asymmetry) are printed
  per rung with intervals; no statement about a detector is drawn from them.

## Amendment 2 (11 Nov 2026, 19:45 CET): self-contained add-on array

Approved by the lead (review findings 2–4, about 4 A100-hours), registered before it is built or run.

- **What:** for all 536 set B hosts, in ONE process per host (8 array tasks cut along the partner cycles, so a host and
  every image it enters are produced together): encode H, S, flip(H) and the partner's S; **save** the semantic codes
  and noise maps of every source and the fresh-noise draws; render, with the unchanged generator and the unchanged A43
  mixing function:
  - re-renders at 20 steps: REC, SAME, X, MIR (so the primary and trace contrasts come from one run; the re-renders also
    give a run-to-run check against production);
  - fresh-noise renders FRESH1, FRESH2: render(ε_k, z(H)), ε_k ~ N(0, I) drawn on the CPU with seed
    int(sha256("DG1fresh|<host>|<k>")[:15], 16), k = 1, 2;
  - noise-only mixes (z(H) with the slerped noise map of the A43 mix) and semantic-only mixes (the lerped semantic
    code with x_T(H)), each with the partner's photo (NOISEX, SEMX) and with the host's own second photo (NOISES,
    SEMS); both halves come from the unchanged `interp()` output, only one half is used;
  - 100 steps: REC, SAME, X, FRESH1;
  - dose series at 20 steps, α = 0.1, 0.2, 0.3, 0.4: two-person (DOSEX) and same-person (DOSES), for the union of the
    100 production dose hosts and the 191 test-read hosts of the protocol-network split (PN1,
    `experiments/PN1_protocol-network-first-tests/split/ladder_split.csv`, `test_read = 1`).
- **Guards (finding 8):** the mixing angle θ is checked finite before rendering (a job with a non-finite θ is not
  rendered and is recorded); the result tar is written before the task fails on any non-finite item.
- **Environment:** the existing DG1 environment (same experiment); the same pack (checkpoint, inputs, repo) plus a small
  add-on pack (code and job lists).
- **Reading:** amendment 1 applies; the add-on images form their own generation run (`gen_run = athena_DG1_addon`)
  and are not mixed with production images inside one contrast.

## Deviations

- Production and smoke jobs ran in the job's RAM disk `$MEMFS` (`#SBATCH -C memfs`), not node-local scratch as written
  above ("all work in `$SCRATCH_LOCAL`"): Athena's `-C localfs` gives only 4 GB (measured by the lead, 11 Nov).
- `module load Python/3.12.3` needs `GCCcore/13.3.0` first on Athena; the environment pins numpy 1.26.4 and pillow
  12.2.0 as constraints (job 3544215 ended up with numpy 2.5.4, which DiffAE cannot import).

## Amendment 3 (11 Nov 2026, about 21:40 CET): add-on shards 2–7 on a rented machine

Registered before any image of this route exists or is read. The six add-on tasks still waiting on Athena (array
3545907, tasks 2–7) are forecast for after 02:30, and the frozen read of the new images (FZ2) waits for them; the author
approved rented machines within tonight's budget.

- **Platform:** one rented Docker machine (image `pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime`, root, one GPU with at
  least 24 GB, about 80 GB disk). The DG1 environment is rebuilt there with the same pins as on Athena (Python 3.12.3,
  torch 2.12.1 / torchvision 0.27.1 with cu130 if the driver is ≥ 580 else cu128 then cu126, numpy 1.26.4 and pillow
  12.2.0 as constraints, the other pins unchanged); the build actually used is recorded. Same packs (sha-checked), same
  code (`dg1_gen.py`, `dg1_addon.py`), batch 16.
- **Gate (binding, the registered reading of the equivalence gate unchanged):** the 8 equivalence images (`eq.csv`)
  are generated on the rented machine and compared with the stored DGX A43 files; the rented route is accepted only
  if the mean |difference| of every one of the 8 images is ≤ 2 grey levels. If not, no rented shard is produced or used.
- **One platform per shard:** shards 0 and 1 stay as produced on Athena. For shards 2–7, before starting a shard the
  driver asks Athena: if the Athena task is already running or finished, the shard is left to Athena and not run on
  the rented machine. Otherwise the shard is run on the rented machine; once its tar is copied back and verified
  (sha256), the Athena task is cancelled, and if it finished meanwhile its output is not used. Every shard folder
  carries a `PLATFORM.txt`. Each shard is self-contained (all its images, including the in-process reference renders
  REC / SAME / X / MIR, come from one process), so no contrast mixes platforms; rented images form generation run
  `rented_DG1_addon` and are never combined with Athena or DGX images inside one contrast.
- **Codes and fresh draws** of rented shards are copied back only if T7 keeps more than 55 GB free (lead's disk rule);
  otherwise they are not kept (they are reproducible: deterministic encoding up to GPU arithmetic, seeded fresh draws),
  and this is recorded.
