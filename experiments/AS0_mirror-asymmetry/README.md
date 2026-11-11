# Mirror-asymmetry test (AS0): full record

Owner: hypothesis-owner agent for the mirror-asymmetry test (AS0), phase 1 (CPU only, existing images only).
Machine: DGX (GB10, ARM), CPU only, at most 2 processes at nice 10. Registration: `prereg.md` (this folder, written
before any statistic). Short verdict: `result.md` (when phase 1 numbers exist). This README follows
`/home/narolski/smad-next/DOCUMENTATION.md`; dated lines are added, history is not rewritten.

Terms. AUC = area under the ROC curve (0.5 = chance). IOD = inter-ocular distance (pupil landmarks 38 and 92 of the
106-point insightface layout). E_A, E_S = energy of the mirror-asymmetric part A = (x - mirror x)/2 and of the
mirror-symmetric part S = (x + mirror x)/2 inside a symmetric face mask, per octave band. L = ln(E_A / E_S).
Rungs of the landmark ladder (AR1): camera photo (R0), the person's other-session photo (S0), tool run on one photo
(R2), warp-only image toward the mean shape of the two photos (R2w), warp-only toward the own mirrored shape (R2wm),
mirror self-morph (R3m), same-person morph (R3), two-person morph (R4). E7 = the existing shrink-and-enlarge
storage-history copy. FR = face recognition.

## 1. Question and current answer

Question (lead, 11 Nov): averaging two different persons averages two independent asymmetry patterns, so a
two-person morph should have a lower ratio of asymmetric to symmetric energy than a same-person morph, and the ratio
should not move with softness or storage history. Is this a single-image signal for a second identity?

Status 11 Nov 2026, 18:25 CET: **running** (landmark detection and per-image measurement on the DGX CPU). No
contrast computed yet. Answer: none yet.

## 2. Timeline (11 Nov 2026, CET)

- 18:02-18:08 Read OWNER_BRIEF, DOCUMENTATION, ideas/ROUND3_BRIEF, AR1 README, PD1 GAN prereg, AD1b README and
  result, ID0 README, NOTEBOOK, EXPERIMENTS, 10_ASSET_INVENTORY. Inventory (no statistic): AR1 pool (536 hosts; every
  same-person pair R3 is cross-session by construction), AR1 rungs (536 each, graded FaceMorpher 6 x 300), the
  106-point layout (mean host shape printed; contour 0-32, brows 43-51 / 97-105, pupils 38 / 92, nose tip 86, mouth
  52-71), alignment eye coordinates of 73_delin_align and prep_eval (both (190, 210), (322, 210) in 512 frames),
  MAD22 canonical E7 records (FaceMorpher E7 scale about 0.30), AF0 softened AR1 copies (1,200), r8 same-person
  landmark morphs with session information (2,500 pairs x 2 engines), GAN32 SOURCES (capture names), A43 and AD1b
  folders (AD1b full run at x_T 32 of 80 at 17:35), expanded123 DiffAE blocks (102 complete; include non-frontal
  FERET captures).
- 18:10 `as0_lists.py` written and run: 24,624 items (graded-folder filter bug fixed: a JSON file in the folder was
  read as a level). 18:16 rerun with the second photos S0 added: 25,160 items, 0 missing paths, 4,228 need landmark
  detection. sha256 of `items.csv` in `lists_summary.json`.
- 18:11-18:13 `as0_landmarks.py`: 8-image tests per set (about 0.6 s per image on the CPU); the A43 stored crops
  gave no face in 8 of 8 (tight crops), fixed by one retry on an in-memory copy padded with black (8 of 8 found;
  detector input only). Full detection launched 18:13 (PID 2241441, log `/mnt/t7/smad_next/AS0/logs/landmarks.log`).
- 18:10-18:17 `prereg.md` written (before any statistic). 18:18 experiment-reviewer agent asked for an independent
  read of the registration.
- 18:19 `as0_measure.py` written. Nominal IOD: ar1_512 130.51 px (1,072 genuine shapes). The SMDD landmark file
  stores coordinates divided by the image size (first IOD read 0.249); fixed by scaling with 256 (IOD 63.7 px).
  8-image tests of L, Lsoft, R8, S (0.19 s per 512 image). `as0_check.py`: implementation checks (section 6).
- 18:21 measurement of L, Lsoft, R8, S launched (PID 2250330, log `/mnt/t7/smad_next/AS0/logs/measure_a.log`).
  8-image smoke outputs `meas/smoke_*` deleted unread. Prereg time stamps corrected to the file times (18:21:55 save;
  only three time strings changed).
- 18:22-18:30 `as0_analyse.py` (contrasts, bootstrap, verdict) and `as0_tables.py` written; README first version;
  volatile inputs byte-copied to `/mnt/t7/smad_next/AS0/inputs/` (r8_pairs.csv sha256 e7bca16c...,
  smdd_bona_landmarks_if106.npz f167eaf8...; `COPY_SHA256.txt`).
- about 18:35 reviewer: GO WITH FIXES (no rule violation); 8 findings (geometry can produce the contrast; timeline;
  history cut-off scale and re-aligned copies; low-band leakage; numerical floor; dose/share bias; database mix in the
  strata; canon512 IOD). 18:38-18:45 registered as amendments A1-A8 (prereg section "Review result and amendments").
- 18:40 base landmark detection stopped by me before the secondary X set (PID 2241441; parts for G, Fm, D, M, Ds,
  Fe complete) to give the primary history control priority.
- about 18:40 lead message (review of the identity-shrinkage triage (ID0)): five additions, registered 18:45 as A9-A13
  (calculated shapes are arithmetic; detected landmarks on the built ladder images with ID0's typicality score and
  the shape asymmetry; external prediction 0.58-0.70 with dose slope < 0.7; drop the 8 validation-reserved persons from
  fits and report with and without; all R3 cross-session). prereg sha256 after A13: ee1ae0de...
- 18:41 `as0_lists.py` extended (appended rows only; existing ids unchanged): copies with own detected landmarks
  (FmO, FeO, LsoftO, 2,628) and Lsoft natives detected (LsoftN, 600); 18:40 detected-landmark ladder sets LD1 (R0,
  S0, R3, R4; 3,216), LD2 (R2w, R3m, R2wm; 3,216), LD3 (graded; 1,800). items.csv now 36,620 rows, 15,688 to detect.
- 18:41 compute chains started (one process each, nice 10): `src/AS0/chain_b.sh` (PID 2272290: detect FmO and X,
  merge, nominal IOD, measure Fm, FmO, G, D, M, Ds, Fe, X, detect LsoftN, LsoftO, FeO, measure them, blank run) and
  `src/AS0/chain_a.sh` (PID 2272291: waits for PID 2250330, then detects LD1, LD2, LD3). `as0_geom.py` (midline
  geometry, A1) and `as0_typ.py` (A10) written; `as0_analyse.py` patched for A1-A8 and A12 (pre-amendment copy
  `/mnt/t7/smad_next/AS0/logs/as0_analyse_pre_amend.py.txt`).

Amendments to the registration: A1-A13 (prereg.md), all registered before any contrast was computed.

## 3. Data

Item list `/mnt/t7/smad_next/AS0/items.csv` (25,160 rows; columns described in `src/AS0/as0_lists.py`), counts per
set and rung in `lists_summary.json` (this folder). Inputs are read in place, nothing is copied or written:

| Set | What | Path | n |
|---|---|---|---|
| L | landmark ladder (AR1) primary pool, FRGC + colorFERET | `/mnt/t7/smad_next/AR1/{src,img/frgcferet/{opencv,facemorpher}/{R2,R2w,R2wm,R3,R3m,R4},img/frgcferet/fm_graded/m000..m050,mirror/frgcferet}`, pool `/mnt/t7/smad_next/AR1/pool.csv` | 536 R0 + 536 S0 + 6 x 2 x 536 + 1,800 graded |
| Lsoft | AR1 R0 and R2w (200 hosts) through the existing shrink-and-enlarge path, strengths amsl112 / fm61 | `/mnt/t7/smad_next/AF0/img/soft/`, lists `/mnt/t7/smad_next/AF0/{lists/ar1soft_src.csv,soft_ar1soft_src.csv}` | 1,200 |
| R8 | record's landmark same-person morphs of two captures | images `/mnt/t7/smad_next/volatile_backup_20261111/r8_{cv,fm}/m*.png`, pairs `/dev/shm/smad_arms/r8_pairs.csv` (volatile; to be copied) | 2 x 2,500 |
| G | GAN latent blocks (PD1 set G) | `/mnt/t7/smad_next/PD1/gan/items.csv` (paths), anchors and raw1024 renders | 768 |
| D | A43 DiffAE-native 256 frames | `/mnt/t7/smad_heldout/a41_diffae/data/a41diffae/a256/png256`, `/mnt/t7/smad_heldout/a43/gen/{D20,C20,B20,B}/png256` | 910 |
| M | AD1b mirror mix and re-run reconstruction (smoke, 4 persons) | `/mnt/t7/smad_next/AD1b/smoke_gen/{PAF,D20r}/png256` | 8 |
| Ds | A43 stored crops and published MorDIFF | `/mnt/t7/smad_heldout/a43/data/a43/stored/{E,D20,C20,B20,A}` | 910 |
| Fm | corrected MAD22 canonical native genuine and E7 copies | `/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z/{native/BonaFide,e7/{FaceMorpher,OpenCV,Webmorph}}` | 204 + 3 x 204 |
| Fe | FRLL-Morphs evaluation frames native and resmatch | `/home/narolski/mambamorph-code/smadcvpr_data/eval/frllm/frll_bona/*_{orig,resmatch_*}.png` | 204 + 4 x 204 |
| S | SMDD genuine renders and E7 (80 px) | PD1 items set S; landmarks `/dev/shm/smad_arms/smdd_bona_landmarks_if106.npz` (volatile) | 2,000 + 2,000 |
| X | expanded123 DiffAE blocks (secondary) | `/mnt/t7/smad_research/diffae-expanded123-v1/run/<block>/` | 1,224 |

Produced (all under `/mnt/t7/smad_next/AS0/`): `items.csv`, `lists_summary.json`, `lm/part_*.npz` (detected
landmarks, merged to `lm/landmarks.npz`), `iod_nominal.json`, `meas/<set>_<k>.npz` (per-image energies and
covariates), `check.json`, logs in `logs/`.

## 4. Code (`/home/narolski/smad-next/src/AS0/`)

| Script | Job |
|---|---|
| `as0_common.py` | paths, sealed-name guard, `.tem` reader, mirrored shape, 106-point indices, face polygon |
| `as0_lists.py` | item list from existing files and metadata; FRGC session dates through AR1 `pool.frgc_meta` (imported unchanged) |
| `as0_landmarks.py` | insightface buffalo_l landmarks on the CPU (2 intra-op threads), padded retry, parts, `--merge` |
| `as0_measure.py` | `--iod` nominal IOD per frame; per-image band energies (7 bands, 4 channels, 2 flips), shape asymmetry, covariates; `--merge` |
| `as0_check.py` | implementation checks on synthetic arrays and mirror equivariance |
| `as0_analyse.py` | contrasts, bootstrap, verdict (to be written) |

Run order: `as0_lists.py` -> `as0_landmarks.py` (+ `--merge`) -> `as0_measure.py --iod` -> `as0_measure.py --sets ...`
-> `as0_measure.py --merge` -> `as0_analyse.py`. Environment: `/home/narolski/mambamorph-code/.venv-spark/bin/python`
(Python 3.12, numpy 1.26.4, scipy 1.17.1, OpenCV 4.11.0, insightface 1.0.1, onnxruntime 1.27.0 CPU only). Weights:
`~/.insightface/models/buffalo_l/{det_10g,2d106det}.onnx` (the pack of 73_delin_align / prep_eval). Seeds: bootstrap
[20261111, 61]; no other randomness (check script noise seed 1).

## 5. Results

None yet.

## 6. Checks

`as0_check.py` -> `check.json` (11 Nov 18:20): a symmetric image has E_A / E_S below 1e-7 in every band; a symmetric
image about a shifted axis (x = 250) has E_A / E_S below 2e-4 under the shifted flip F1; the squared band weights sum
to 1 within 1e-7; flipping a photo and its shape changes the energies by at most 1.2% (mask rasterisation at the
boundary); an exactly symmetric shape gives shape asymmetry ln = -72.9 (numerical zero). White noise gives
E_A / E_S = 0.52, 0.80, 0.89, 0.97, 1.00 in B1..B5 (0 in B0): in low bands the mask is only a few wavelengths wide and
pixels near the axis correlate with their own mirror, so the no-structure baseline is below 1 there. This baseline is
the same for every image of a frame type.

Not verified yet: detected landmarks against `.tem` landmarks on the same images (planned: AR1 R0 subset).

## 7. Dead ends and failures

- `as0_lists.py` first run read `fm_graded/graded_log.json` as a mixing level (crash); fixed with a folder filter.
- A43 stored crops: no face found without padding (8 of 8); padded retry added.
- SMDD landmark file in normalised coordinates; first nominal IOD 0.249; fixed (x 256).

## 8. Observations and ideas

- Every AR1 same-person morph (R3) is cross-session; the record's r8 same-person morphs provide same-session
  (colorFERET fa + fb, expression change) and cross-session pairs in the same frame.
- The expanded123 DiffAE blocks contain non-frontal colorFERET captures (rc, qr), useful as a pose stress test.

## 9. Open items and next steps

Finish detection and measurement, write `as0_analyse.py`, compute the registered contrasts, `result.md`, report.

## 10. Handover state (18:25 CET)

| Process | PID | Log | Expected end | If it fails |
|---|---|---|---|---|
| measurement L, Lsoft, R8, S | 2250330 | `/mnt/t7/smad_next/AS0/logs/measure_a.log` | about 19:10 | rerun `as0_measure.py --sets L,Lsoft,R8,S` (finished parts are skipped) |
| chain B | 2272290 | `/mnt/t7/smad_next/AS0/logs/chain_b.log` (+ landmarks_b, iod, measure_b, measure_blank logs) | about 20:10 | rerun `src/AS0/chain_b.sh` (every step resumes from parts) |
| chain A | 2272291 | `/mnt/t7/smad_next/AS0/logs/chain_a.log` (+ landmarks_a.log) | about 20:30 | rerun `src/AS0/chain_a.sh <pid or 0>` |

Compute: CPU only; 0 GPU-hours; 0 USD.

## 11. Reproduce from scratch

```
P=/home/narolski/mambamorph-code/.venv-spark/bin/python; cd /home/narolski/smad-next/src/AS0
$P -I as0_lists.py
OMP_NUM_THREADS=2 nice -n 10 $P -I as0_landmarks.py --threads 2; $P -I as0_landmarks.py --merge
$P -I as0_measure.py --iod
OMP_NUM_THREADS=1 nice -n 10 $P -I as0_measure.py --sets L,Lsoft,R8,S
OMP_NUM_THREADS=1 nice -n 10 $P -I as0_measure.py --sets Fm,G,D,M,Ds,Fe,X
$P -I as0_measure.py --merge; $P -I as0_check.py
OMP_NUM_THREADS=1 nice -n 10 $P -I as0_analyse.py
```

## Log of README updates

- 11 Nov 18:25 CET: first version.
- 11 Nov 18:47 CET: review, amendments A1-A13, chains.
