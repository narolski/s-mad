# GAN morphs in training with one-person renders as genuine (GX1): full record

Owner: AG1 owner (Opus agent). Registration: `prereg.md` (commit b6d2dce). Follows DOCUMENTATION.md.

## 1. Question and current answer

Can the protocol network learn something morph-specific about MIPGAN-style two-person morphs when one-person renders
of the same pipeline are genuine examples (rendering carries no class information)? Status 13 Nov 20:30: registered,
pre-run check running, input prep running on the DGX; nothing generated or trained. Development of the next method
version (the current candidate was frozen by the author at 18:28; MAD22 is a seen benchmark for anything built on GX1).

## 2. Timeline (13 Nov 2026, machine clock; git commit times are the record)

- Before 18:37 Lead's messages: new arm GX1 (author's go); first count (36 usable existing morphs, uninterpretable);
  feasibility (202 training, 109 development persons; 404 + 109 morphs; about 6.7 H100-h + 3.7 MIPGAN-II); go. Time
  note (added about 18:55): the lead's messages gave 18:50 / 19:15 / 19:35; by the machine clock these fall between
  about 18:32 and 18:46 (NOTEBOOK "CORRECTION OF TIMES").
- 18:37:16 `build_gx1.py select` (seed 20261113): 202 training, 109 development persons.
- 18:37-18:47 `build_gx1.py prep` (AG1 input path unchanged, onnxruntime capped at 2 threads, nice 10): 311 persons,
  0 photos dropped.
- About 18:38 WCSS: weight packs verified (`packs/AG1/gan_weights.tar` e06f19af..., `gan_sg1.tar` 1571c1a3...).
- 18:40:15 Registration committed (b6d2dce). Pre-run check (experiment-reviewer, opus) started; returned about 18:47:
  GO WITH FIXES (`PRERUN_GX1_20261113.md`).
- 18:40-18:41 Generation scripts written. 18:47:21 pairs; shard plans (22 shards incl. 2 smoke).
- About 18:55 Amendment 1 (review fixes F1-F8, time note, generation pins).

## 3. Data

- Persons: `/mnt/t7/smad_next/GX1/inputs/select.json` (from the PN1 split files only).
- Inputs (in progress): `/mnt/t7/smad_next/GX1/inputs/pack/{photos.json, crops/}`.

## 4. Code

`src/GX1/build_gx1.py` (select | prep | pair | shards; reuses `src/AG1/build_inputs.py` unchanged);
`src/GX1/wcss/gx1_gen_task.sh` (one shard on WCSS H100, `~/dmenv` read-only); `gx1_gen.sbatch` (array over a list);
`gx1_gen_smoke.sbatch` (two 3-image smoke shards). Generator: `src/AG1/ag1_gen.py` + vendored gan1 code.

## 5. Results

None yet.

## 6. Checks

Weight-pack hashes on WCSS verified (19:50). Others pending.

## 7. Dead ends and failures

- The first plan (existing AG1 images only) gave 36 usable morphs: uninterpretable; replaced by new generation.

## 8. Observations and ideas

- MIPGAN-II images exist only for FRLL in AG1; GX1 generates MIPGAN-II for FERET / FRGC as separate shards.

## 9. Open items and next steps

Pre-run check; finish prep; pairs and shards; packs to WCSS; smoke + generation arrays into the dispatcher queue
(behind the second-engine arm); then image checks, pins, training overlay, training smoke, 10 fits, read.

## 10. Handover state

DGX: `build_gx1.py prep` (background, log above). No cluster job yet. Compute spent: 0.

## 11. Reproduce from scratch

`python build_gx1.py select && python build_gx1.py prep && python build_gx1.py pair && python build_gx1.py shards`
(DGX venv, thread caps), then the WCSS steps (to be written).
