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
- 12 Nov 23:15: `build_pack.py` started (pack for part 2).

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

- FFHQ contains many second photos of development persons: 103 of 1,012 face-passing candidates had glintr100 cosine
  0.40 or more (median 0.565, up to 0.92) to an ffhqm genuine image or contributor. Any experiment that trains on FFHQ
  and reads ffhqm should check identity, not only keys.
- FFHQ photos are in-the-wild (sunglasses, open-mouth smiles, hands on the face); the aligner filters pose only. FRGC /
  colorFERET training photos are neutral frontal. FFHQ frames often carry a black border at the bottom of the 512 frame
  (tight 1024 crops), in both classes.

- FLUXSynID's live images: `live_0_a` 512 px with strong expression and tight crop (frontal filter failed in the one
  test), `live_0_e` near-copy of the document image, `live_0_p` a different scene; recorded only for the record.

## 9. Open items and next steps

Build FFHQ (prereg section 3); part 2 (training comparison) registration; pre-run review.

## 10. Handover state

none running yet. Compute spent: 0.

## 11. Reproduce from scratch

to be filled.
