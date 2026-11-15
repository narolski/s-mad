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
  note (added with amendment 1): the lead's messages gave 18:50 / 19:15 / 19:35; by the machine clock these fall between
  about 18:32 and 18:46 (NOTEBOOK "CORRECTION OF TIMES").
- 18:37:16 `build_gx1.py select` (seed 20261113): 202 training, 109 development persons.
- 18:37-18:47 `build_gx1.py prep` (AG1 input path unchanged, onnxruntime capped at 2 threads, nice 10): 311 persons,
  0 photos dropped.
- About 18:38 WCSS: weight packs verified (`packs/AG1/gan_weights.tar` e06f19af..., `gan_sg1.tar` 1571c1a3...).
- 18:40:15 Registration committed (b6d2dce). Pre-run check (experiment-reviewer, opus) started; returned about 18:47:
  GO WITH FIXES (`PRERUN_GX1_20261113.md`).
- 18:40-18:41 Generation scripts written. 18:47:21 pairs; shard plans (22 shards incl. 2 smoke).
- 18:48:45 Amendment 1 committed (eabdcc4: review fixes F1-F8, time note, generation pins). 18:49 pack uploaded to WCSS packs/GX1 (GX1SUMS checked there; ~/dmenv torch 2.11.0+cu128); submission files in the dispatcher queue: wcss_gx1_gensmoke.cmd, wcss_gx1_gen_mip1.cmd and wcss_gx1_gen_mip2.cmd (both gated on the smoke).
- 18:51:09 Amendment 1b committed (748f4e2): lead's answers (FFHQ-Morphs is the development comparison set; seeds
  408-412 accepted; ~/dmenv in the WCSS home, job IO on $TMPDIR) and the registered sensitivity print without the four
  pairs of cosine > 0.4.
- About 18:52 Dispatcher submitted all three on WCSS (Nice 2, priority 677, behind AB1's second-engine arm): smoke
  **6315653**, MIPGAN-I array **6315654_[0-11]**, MIPGAN-II array **6315655_[0-7]**. The arrays went in beside the smoke
  (lead's standing rule of 13 Nov 09:05: arrays age in the queue with their smokes), not after it; the gate holds: no
  shard output counts unless 6315653 COMPLETES with GX1_SMOKE_OK in its log, and the dispatcher cancels 6315654 and
  6315655 at once if it fails. Owner: AG1 owner. Expected start: unknown (WCSS saturated at submission); expected
  run: smoke about 10 min, MIPGAN-I tasks 30-150 min each, MIPGAN-II 30-65 min each.
- Later (dispatcher, on the lead's order): `--dependency=afterok:6315653` added to arrays 6315654 and 6315655 (Slurm
  accepted; priority 672); no shard task can start before the smoke completes successfully; the dispatcher cancels both
  arrays if it fails. Five standing roles (OWNER_BRIEF, 6e42c86): reports end with a CLAIMS block; ADVERSARY publishes a
  shortcut-only floor before the read (no read while it is pending).
- Read hold (lead, via the dispatcher): GX contrast numbers stay closed until the lead announces that the next-version
  selection rule (experiments/NEXT_method-selection-rule/prereg_draft_v2.md, 3c2b9d5) binds or the author rules
  otherwise; generation, fits, fetching, verification and gates continue.
- 14 Nov 00:57:19-00:59:52 (dispatcher) smoke 6315653 on WCSS H100, exit 0, GX1_SMOKE_OK; arrays' afterok fulfilled,
  pending on priority. Fetched to `/mnt/t7/smad_next/GX1/smoke/`: both tars match their .sha256; 3 / 3 images per
  generator, every PNG sha256 equal to its log line, 1024 x 1024 RGB; NVIDIA H100, torch 2.11.0+cu128 (~/dmenv); peak
  GPU memory 1.9 GB (MIPGAN-I) / 6.3 GB (MIPGAN-II). Per image: MIPGAN-I 24.7-27.4 s including one 500-step inversion
  (so about 5 s per MIPGAN run, 20 s per inversion); MIPGAN-II about 18 s (twice the A28 estimate; shards of 260 jobs
  about 80 min, inside the 3 h limit). Final loss MIPGAN-I R2 0.780, R3 3.360, R4 5.736; MIPGAN-II 1.207, 3.581, 6.018.
  e4e loads under forced weights_only on torch 2.11.

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

WCSS: 6315653 (smoke), 6315654_[0-11], 6315655_[0-7] pending (see timeline). Owner checks each at its expected end. Compute spent so far: 0.

## 11. Reproduce from scratch

`python build_gx1.py select && python build_gx1.py prep && python build_gx1.py pair && python build_gx1.py shards`
(DGX venv, thread caps), then the WCSS steps (to be written).
