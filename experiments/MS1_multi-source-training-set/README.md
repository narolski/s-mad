# Multi-source training set for threshold transfer (MS1)

## 1. Question and current answer

Do genuine photos, morphs and matched controls from a third capture source (FFHQ) in training make the decision
threshold of the protocol network (PN1 recipe, Sb manifest) carry over to genuine photos of unseen sources?
Status 12 Nov 2026 23:20 CET: build plan registered (`prereg.md`, 3d4411b); FFHQ source built (3,263 unique training
images, 1,500 hold-out images), exclusion proof passes, all pixel and path gates pass; multi-source manifest SbM3 written
(13,414 rows; FRGC / colorFERET rows equal train_Sb's). Multi-PIE unusable; FLUXSynID ruled out by the author.
Pack being built; part 2 (training comparison) to be drafted and reviewed. No fit, no score.

## 2. Timeline

- 12 Nov ~22:55 CET: author approved the build ("3. Please do build it ASAP."); 50 USD rental budget for the day.
  Owner's `date` at recording: Thu Nov 12 11:01:39 PM CET 2026.
- 12 Nov ~22:57: Multi-PIE inspected (zip listing; 3 crops through the unchanged aligner): 128 x 128 crops only, session
  01, 249 subjects, eye distance about 39 px -> unusable (prereg section 0). Lead agreed.
- 12 Nov ~22:58: FLUXSynID inventoried from the zip listing (14,889 identities; per identity one 1024 px document-style
  JPEG and three live JPEGs `live_0_{a,e,p}`; identity filter lists inside) and one identity's 4 images measured in the
  scratchpad. 23:05: author ruled "Do not use FluxSynID"; scratchpad copies deleted, zip untouched, nothing built.
- 12 Nov 23:03: plan (`prereg.md` part 1) committed at 3d4411b before any build step.
- 12 Nov 23:05-23:08: FFHQ person selection (`src/MS1/run_select.sh`: `ffhq_select.py refs`, then `select --n 900`):
  1,833 candidates attempted, 821 failed the aligner (no face or frontal filter), 112 dropped as identity duplicates
  (103 against the ffhqm references, median cosine 0.565, up to 0.92; 9 against earlier kept frames), 900 kept
  (450 af0, 150 ladder, 300 hold-out). In parallel `excl_sha.py`: sha256 of the 20,000 excluded raw files.
- 12 Nov 23:09: `gate.py path`: the MS1 wrappers reproduce 4 AF0 u50, 4 zero, 4 halves, 4 fm61 copies and 4 AR1 R4
  OpenCV files pixel for pixel (20 of 20; `gate_path.json`).
- 12 Nov 23:10: `proof.py`: exclusion proof passes (`exclusion_proof.json`): 0 overlaps by key and by raw sha256; largest
  cosine to the ffhqm references 0.396, among kept 0.391, hold-out vs training 0.374; no benchmark path in any list.
- 12 Nov 23:11: `ffhq_build.py plan` (`plan_summary.json`): 400 + 400 training pairs, 150 + 150 hold-out pairs, 1,100
  halves, 1,525 stored copies to build, 150 ladder hosts (look-alike partner cosine median 0.173).
- 12 Nov 23:12-23:14: `run_build.sh`: morph stage (1,100 pairs, 150 R4 through 78_tool_morph, 300 ladder halves, 150
  R2w4), stored copies (1,525 rows, 32 failed re-alignment and are dropped), `gate.py pixel` (8 u50, 8 zero, 8 R4: all
  equal to the unchanged engine; `gate_pixel.json`).
- 12 Nov 23:14: `mkmanifest.py` -> `/mnt/t7/smad_next/MS1/manifests/train_SbM3.csv` sha256 `885dff9d…`
  (`manifest_SbM3_summary.json`); FRGC / colorFERET rows equal train_Sb's as a multiset (asserted).
- 12 Nov 23:15-23:17: `build_pack.py` -> `/mnt/t7/smad_next/MS1/pn1_pack_ms1.tar` sha256 `dac228f5…` (14,508,625,920
  bytes, 51,272 files); evaluation manifest `d1fab6ad…` (42,366 rows: FS1 19,797, MS1 FFHQ hold-out 1,480, TT1
  21,089). Tree of symlinks `/mnt/t7/smad_next/MS1/pack_tree/`.
- 12 Nov 23:17: draft of part 2 (`prereg_comparison_draft.md`, commit cb1cf09) sent to the lead for pre-run review.
- 12 Nov 23:18-23:20: DGX smoke of `src/MS1/run.sh` (20 steps, 64 scoring rows, SbM3 seed 403, pinned pack):
  passed; result `/mnt/t7/smad_next/MS1/smoke/results/MS1smoke_SbM3_s403.tar`; work folder (14 GB, mine) deleted.
- 12 Nov 23:21: reader `src/MS1/ms1_read.py` written and tested on mock scores (`ms1_read_mock.json`); commit c1c4224.
- 12 Nov 23:21 (before commit 03198c5 at 23:22:09): inventory of new candidate sources (no build; lead's instruction), see section 8.
- 12 Nov ~23:22: pre-run review `experiments/reviews/PRERUN_MS1_COMPARISON_20261112.md`: GO WITH FIXES (B1 register,
  B2 reader before fetch, B3 sharp unseen source; M1-M5; minors). Lead rulings: CFD becomes a held-out evaluation
  source (never training), KDEF printed secondary, data-volume control arm SbV, owner may upload and submit on WCSS.
- 12 Nov 23:23-23:25: `heldout_pool.py cfd` (831 of 831 aligned, 827 persons) and `kdef` (140 of 140, 70 persons);
  `mkmanifest_vol.py` -> train_SbV (13,414 rows, `8920699f…`); run.sh: arm SbV and env.txt line; pack rebuilt with
  train_SbV.csv: `c11b16bc…` (the reviewed pack `dac228f5…` deleted after the rebuild; it differed only by that file).
- 12 Nov 23:26:12: part 2 registered in `prereg.md` at f748da4 (pins included).
- 12 Nov 23:27:54: upload of the pack and scripts to WCSS started (`/mnt/t7/smad_next/MS1/logs/upload.log`).
- 12 Nov 23:29: reader extended (P1-S, P1-T, SbV prints) and tested on mock scores incl. a supported path; commit
  de10419 (B2), sha256 `5e5ada46…`.
- 12 Nov 23:30: held-out scoring pack `ms1_heldout_pack.tar` (`06b64608…`, 971 rows: CFD 831, KDEF 140; manifest
  `b3fe4e77…`) and `wcss/ms1_heldout.sbatch`; tested locally on the smoke result (RESCORE_DONE 831 and 140).
- 12 Nov 23:27:54-~23:36: pack and scripts uploaded to WCSS; 23:43 held-out pack and job uploaded; 23:46 on WCSS:
  `sha256sum -c` OK for the pack, run.sh and the held-out pack; sbatch sha256 equal to the f748da4 pins.
- 12 Nov 23:46:29 and 23:48:05: `sbatch ms1_smoke.sbatch` refused twice ("Unable to contact slurm controller (connect
  failure)"); per the lead's rule no further retry; lead told. Nothing submitted.
- 12 Nov ~23:50: lead: do not retry; the lead pings the controller every 5 min. If WCSS does not accept jobs by 13 Nov
  01:00, MS1 switches to rented A100s: deviation MS1-D1 prepared and registered at 5eadc1b (three A100 PCIe 40 GB
  machines, whole seeds: m1 403+406, m2 404+407, m3 405; held-out step per machine; `src/MS1/rented/drive_ms1.sh`,
  `remote_ms1.sh`; remote queue tested on the DGX with stand-in tasks in `/mnt/t7/smad_next/MS1/smoke/rtest`).

## 3. Data

- FFHQ-1024 raw: `/mnt/t7/Datasety/downloads/FFHQ-1024/Part{1..7}/<key>.png` (70,000).
- Exclusion lists: FFHQ-Morphs `/mnt/t7/Datasety/downloads/FFHQ_Morphs/_docs/FFHQ-Morphs/{pairs,bonafide_only}.csv`;
  ffhqm `/mnt/t7/smad_heldout/ffhq_morphs/{manifests/ffhqm_meta.csv,protocol/*.txt}`.
- Outputs under `/mnt/t7/smad_next/MS1/ffhq/`: `src/<key>.png|.tem` (900 aligned frames + 106-point landmarks),
  `select_log.csv` (every attempted key, outcome, cosines, raw and frame sha256), `persons.csv`, `emb_ref.npz`,
  `emb_kept.npz`, `excluded_raw_sha256.csv`, `lists/{af0_pairs,halves,soft,ladder}.csv`, `img/{train,hold}/{zero,u50,
  halfA,halfB}/`, `img/ladder/opencv/{R4,half,R2w4}/`, `img/soft/{fm61,amsl112}/`, `soft_log.csv`.
  Manifest `/mnt/t7/smad_next/MS1/manifests/train_SbM3.csv` and `SbM3_files.csv` (pack path, source, sha256 of every
  FFHQ training image). Gate scratch `/mnt/t7/smad_next/MS1/gate/`.

FFHQ training images in SbM3 (unique): af0_photo 450, af0_photo61 216, af0_zero 400, af0_half 800, af0_half61 198,
af0_u50 400, af0_u5061 199, lad_R0 150, lad_R4 150, lad_half 300; total 3,263 (target 3,275; 12 stored copies failed
re-alignment). Not supplied by FFHQ: lad_R2w, lad_S0, lad_S3, lad_S4 (prereg 3.3). Hold-out (MS1 FFHQ, 300 persons):
photo 300, photo fm61 291, photo amsl112 290, u50 150 (+ fm61 150, amsl112 149), zero 150.

## 4. Code

`src/MS1/` (run order): `ms1common.py` (paths, exclusion keys); `ffhq_select.py refs|select` (via `run_select.sh`);
`excl_sha.py`; `gate.py path`; `proof.py`; `ffhq_build.py plan|morph|soft` (via `run_build.sh`, which ends with
`gate.py pixel`); `mkmanifest.py`; `build_pack.py`; `run.sh` (copy of `src/PN1/run.sh`, arm list Sb|SbM3, results
folder MS1); `wcss/ms1_smoke.sbatch`, `wcss/ms1_fit.sbatch` (drafts, not submitted). Python
`/home/narolski/mambamorph-code/.venv-spark/bin/python -I`, thread caps 2, nice 10, 2 workers. Unchanged code used,
with sha256 in `gate_path.json`: 73_delin_align (47eefed3…), 78_tool_morph, 68_hires_morph, prep_eval (374408ab…),
AF0 af_morph / soften / ghost, AR1 variants / fr, PN1 mkmanifests.

## 5. Results

none yet.

## 6. Checks

Path gate 20/20 pixel-identical (`gate_path.json`); pixel gate 24/24 (`gate_pixel.json`); exclusion proof passes
(`exclusion_proof.json`); FRGC / colorFERET rows of SbM3 equal train_Sb (asserted in `mkmanifest.py`); 8-image smoke of
every stage run before the full run. Not verified: re-alignment of an FRGC raw photo through 73_delin_align against its
recorded frame (the aligner's sha256 equals AR1's pin); duplicates of persons below glintr100 cosine 0.40.

## 7. Dead ends and failures

- Multi-PIE as held: 128 px crops, unusable (prereg section 0).
- FLUXSynID: ruled out by the author (23:05), not built.

## 8. Observations and ideas

- New candidate sources (inventory 12 Nov, before 23:22; eye distances measured with the unchanged detector on 2-8 images
  each, nothing built):
  - Chicago Face Database 3.0.1: 827 persons (CFD 597, CFD-INDIA 142, CFD-MR 88), exactly one neutral frontal photo
    each, 2444 x 1718 JPEG, eye distance 329-381 px (all 10 test images aligned); 154 CFD persons also have angry,
    fear, happy-closed and happy-open photos from the same session (CFD-INDIA 5 extra files). Same-person controls
    possible for about 154 hosts with the happy-closed photo as the second photo (the FRLL neutral + smiling
    precedent of AR1's secondary pool). Meets the resolution and count rules.
  - KDEF: 70 persons x 2 sessions (A, B), 35 photos each (7 expressions x 5 angles); neutral straight NES at
    562 x 762, eye distance about 150-153 px; two-session same-person controls for all 70, but 70 persons is below
    the minimum of 400. AKDEF holds 70 averaged faces (composites): not genuine photos, never usable as genuine.
  - MUCT: 276 persons, 5 cameras, 480 x 640 JPEG; camera a (frontal) 751 images (about 2.7 per person, lighting
    variants q-z of one session); eye distance 87-93 px (below 112.7, so frames are enlarged about 1.45x); below 400
    persons; licence forbids reproduction in public documents.
  - CelebA-HQ: downloading (11.0 of 33.9 GB at 23:18); the HQ-to-CelebA mapping file is not on disk
    (`CelebAMask-HQ/` empty). Note: CelebA-HQ images were made with JPEG-artefact removal and 4x super-resolution
    networks (Karras et al. 2018), i.e. network-processed texture.

- FFHQ contains many second photos of development persons: 103 of 1,012 face-passing candidates had glintr100 cosine
  0.40 or more (median 0.565, up to 0.92) to an ffhqm genuine image or contributor. Any experiment that trains on FFHQ
  and reads ffhqm should check identity, not only keys.
- FFHQ photos are in-the-wild (sunglasses, open-mouth smiles, hands on the face); the aligner filters pose only. FRGC /
  colorFERET training photos are neutral frontal. FFHQ frames often carry a black border at the bottom of the 512 frame
  (tight 1024 crops), in both classes.

- FLUXSynID's live images: `live_0_a` 512 px with strong expression and tight crop (frontal filter failed in the one
  test), `live_0_e` near-copy of the document image, `live_0_p` a different scene; recorded only for the record.

## 9. Open items and next steps

- Lead's pre-run review of `prereg_comparison_draft.md`; apply fixes; copy the final text into `prereg.md` part 2 and
  commit before any fit is submitted.
- Lead runs the upload, smoke and array commands (draft section 9); fetch tars; run `ms1_read.py`; post-result review.
- A fourth-source arm only after the lead confirms a source (section 8).

## 10. Handover state

State 12 Nov 23:48 CET: nothing submitted (WCSS slurm controller unreachable at 23:46 and 23:48). Staged and verified on
WCSS under `/lustre/pd03/hpc-narolski-1790461090/smad-next/packs/MS1/`: `pn1_pack_ms1.tar` (`c11b16bc…`), `run.sh`,
`ms1_smoke.sbatch`, `ms1_fit.sbatch` (array 0-14%6), `ms1_heldout_pack.tar` (`06b64608…`), `ms1_heldout.sbatch`.
Order: smoke -> fits (after MS1_SMOKE_DONE) -> held-out job (after all 15 tars exist) -> fetch results/MS1 and
results/MS1H to `/mnt/t7/smad_next/MS1/results/` (keep the WCSS copies) -> `ms1_read.py --results ... --heldout ...`.
No local process running. Compute spent: DGX CPU about 15 minutes, DGX GPU about 3 minutes; 0 USD.

## 11. Reproduce from scratch

```
P=/home/narolski/mambamorph-code/.venv-spark/bin/python; cd /home/narolski/smad-next/src/MS1
./run_select.sh; $P -I excl_sha.py; $P -I gate.py path; $P -I proof.py
$P -I ffhq_build.py plan; ./run_build.sh; $P -I mkmanifest.py; $P -I build_pack.py
# smoke: see /mnt/t7/smad_next/MS1/smoke/smoke_dgx.log for the env line; fits: src/MS1/wcss/*.sbatch
$P -I ms1_read.py --results /mnt/t7/smad_next/MS1/results --out ../../experiments/MS1_multi-source-training-set/ms1_read.json
```
