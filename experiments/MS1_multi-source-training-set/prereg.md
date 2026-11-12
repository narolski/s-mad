# Multi-source training set for threshold transfer (MS1): build plan

Part 1 of the registration: the training set (what is built, from which persons, by which unchanged code). Part 2,
the training comparison, is a separate section added later, before any fit, and goes through an independent pre-run
review before anything runs.

## 0. Approvals and rulings (machine-clock times from `date`)

- Author, 12 Nov about 22:55 CET, his words: "3. Please do build it ASAP." in answer to "Multi-source training set:
  build aligned photos, morphs and controls from FFHQ and Multi-PIE". Rental budget for the day: 50 USD. Recorded by
  the owner at `date`: Thu Nov 12 11:01:39 PM CET 2026.
- Author, about 22:58 (relayed by the lead): "Execute the necessary commands without waiting for my approval" (within
  the budget and every standing rule).
- Multi-PIE as held is unusable (owner's finding, lead agreed): `multipie.zip` holds only pre-cut 128 x 128 face crops
  (129,480 in `Multi_Pie/HR_128` and 129,480 nearest-neighbour copies of 4x-shrunk crops in `LR_4x_Nearest`); session
  01 only, recordings 01 (neutral) and 02 (smile), 13 cameras, 20 illuminations, 249 subjects; `probe/` holds 2 of
  the same crops. The unchanged aligner (`73_delin_align`) found eyes about 39 px apart (2 of 3 test crops detected),
  so every frame would be enlarged about 3.4x into the 512 frame (eyes 132 px apart): native resolution below the
  61 px shrink floor the author has not approved and below the 60 px floor of the protected genuine pools.
- FLUXSynID was proposed as a replacement. Author, about 23:05 (relayed): "Do not use FluxSynID. Instead, propose
  datasets to obtain." FLUXSynID is not used; nothing was aligned or built from it (the owner had listed the zip and
  opened one identity's 4 images in the scratchpad to measure them; those copies are deleted). The zip is untouched.
- Lead decision (about 23:05): build and register the three-source arm (FRGC, colorFERET, FFHQ) now; write builders and
  the balancing rule so that one or two further real photo sources can be added later without redoing FFHQ.

## 1. Hypothesis (plain words)

The PN1 networks (CLIP ViT-B/16 + LoRA, MADation recipe, Sb manifest) rank morphs above genuine photos, but their
decision threshold does not carry over to genuine photos of an unseen source: FRGC / colorFERET photos sit on the
floor of a bounded score range, other sources sit higher. If genuine photos AND morphs AND matched controls of a third
capture source are in training, "genuine = FRGC / colorFERET photo" stops being a usable rule, and genuine flag rates
at the network's own rule fall on sources never trained on. Every added source contributes its own morphs and
controls, never only genuine photos; otherwise "source X = genuine" becomes the new shortcut.

## 2. The existing set this extends (train_Sb, sha256 `2cf3fda3…`, 8,386 balanced rows, 5,535 unique images)

Unique images per kind (label 0 = negative, 1 = attack); FRGC / colorFERET:

| kind | what | FRGC | colorFERET |
|---|---|---|---|
| af0_photo (0) | aligned camera photo | 50 | 468 |
| af0_photo61 (0) | stored-small copy, 61.2 px between the eyes | 25 | 229 |
| af0_zero (0) | warp-only image toward the two-person mean shape | 400 | 330 |
| af0_half (0) | both warped halves of every u50 pair | 800 | 656 |
| af0_half61 (0) | stored-small copy of one half per pair | 200 | 163 |
| af0_u50 (1) | two-person OpenCV-style morph, 0.5 | 400 | 328 |
| af0_u5061 (1) | stored-small copy of the morph | 200 | 166 |
| lad_R0 (0) | ladder host photo | 130 | 26 |
| lad_R2w (0) | warp-only toward the host's same-person mean shape | 130 | 26 |
| lad_half (0) | the two warped halves of R4 | 204 | 44 |
| lad_R4 (1) | two-person morph with the look-alike partner | 102 | 22 |
| lad_S4 (1) | spliced morph: R2w4 with R4 pixels inside the R4 hull | 102 | 22 |
| lad_S0 (0) | matched negative: R2w4 with R2w pixels inside the R4 hull | 130 | 26 |
| lad_S3 (0) | matched negative: R2w with same-person-morph pixels inside the R4 hull | 130 | 26 |
| total | | 3,003 | 2,532 |

## 3. The new source: FFHQ

### 3.1 Exclusion of every development image (by file identity and by identity)

FFHQ is also the development comparison set (`/mnt/t7/smad_heldout/ffhq_morphs`, manifests/ffhqm.csv). Excluded from
every MS1 training or MS1 hold-out image, before any alignment:
- by key: every key in FFHQ-Morphs `pairs.csv` (5,000 pairs, 10,000 contributors) and `bonafide_only.csv` (10,000),
  i.e. the whole FFHQ-Morphs universe (20,000 keys, a superset of the 2,000 ffhqm genuine persons and the 2,000
  contributors of its 1,000 sampled pairs); plus every key named in `ffhqm_meta.csv` and `protocol/*.txt` (checked to
  be inside the 20,000);
- by file content: sha256 of every MS1 raw FFHQ file against the sha256 of the raw files of all 20,000 excluded keys
  (exact duplicates under another key would be caught);
- by identity (FFHQ has no identity labels; one image is treated as one person): glintr100 cosine (the registered
  route `src/AR1/fr.py`, imported unchanged) between every MS1 candidate and (a) the 2,000 ffhqm genuine frames, (b) the
  2,000 raw contributor images of ffhqm's 1,000 sampled pairs, (c) every earlier kept MS1 candidate. A candidate with
  cosine ≥ 0.40 to any of them is dropped (a likely second photo of the same person). The other 8,000 FFHQ-Morphs
  contributors are excluded by key and file only (they are not in any development read). Stated limitation: duplicates
  below 0.40 cannot be excluded.
- Proof written to `experiments/MS1_multi-source-training-set/exclusion_proof.json` (counts of overlaps by key, by
  sha256 and by identity: all must be 0 for kept images; the largest cosine kept is printed).

### 3.2 Persons

Candidates: the 50,000 FFHQ keys outside the exclusion set, in the order `random.Random(20261112).shuffle(sorted keys)`.
Processed in that order through the unchanged aligner (`scripts/73_delin_align.align`, insightface detection + 106
landmarks, its own frontal filter, 2-point eye similarity into the 512 frame; the call of `src/AR1/frll_prep.py`) and
the identity rule above, until 900 persons are kept. Kept persons are dealt in kept order: the first 450 = AF0-style
training persons, next 150 = ladder training hosts, last 300 = MS1 development hold-out persons. Every attempted key,
its outcome (no face, frontal filter, duplicate) and every kept frame's sha256 are listed.

### 3.3 Image kinds per FFHQ person (all OpenCV-style engine; FaceMorpher never in training)

AF0-style part (450 persons; the rules of `src/AF0/pairs.py` with FFHQ as the only database and one photo per person):
- af0_photo: the aligned frame (450).
- af0_zero, af0_u50: per field 400 pairs; hosts cycle through the shuffled persons, partner = a random other person of
  the same part (rng `random.Random(20261111 + 401 + 1000)`, AF0's loop and draw order); each pair has its own field
  seed. zero = the engine's warped host (W_A), u50 = the unchanged engine at 0.5 (`src/AF0/af_morph.py` `_job`,
  imported unchanged; written to MS1 paths).
- af0_half: both warped halves of every u50 pair (np.clip(W, 0, 255).astype(uint8) of the engine's own warped images,
  the one line of `src/AF0/ghost.py`) = 800.
- stored-small copies: AF0's softened training list rule (`lists_extra.py soft_src`: photos, u50 morphs and one half
  per u50 pair, A for even pair index, B for odd), strengths alternating amsl112 / fm61 by row as AF0's
  `soften.py build --alternate`; only the fm61 copies enter training (as in train_Sb). Built through `soften.e7_branch`
  (prep_eval's registered shrink-and-enlarge branch, imported unchanged, pin `374408ab…`). Expected: photo61 225,
  u5061 200, half61 200. The amsl112 rows are not built for training persons.
Ladder part (150 hosts; the rules of `src/AR1/pool.py`): partner B by a Hungarian assignment without fixed points that
maximises glintr100 cos(H_p, H_q) (AR1 uses cos(H_p, S_q); FFHQ has no second photo, so S := H).
- lad_R0: the frame (150); lad_R4: `78_tool_morph.py` opencv on (H_p, H_B(p)), unchanged script (150); lad_half: the
  two warped halves of each R4 pair (300); R2w4 (warp-only toward the R4 mean shape, `variants.warp_cv`, unchanged) is
  built for the record but is not a training kind (as in train_Sb).

FFHQ cannot supply (one photo per person): lad_R2w (needs the same-person mean shape), R3 and therefore lad_S3, lad_S0
(needs R2w) and, by design, lad_S4: S4 without its matched S0 / S3 negatives would recreate inside FFHQ exactly the
"splice positives without matched negatives" condition that the Sp ablation tests, i.e. "seam = morph". So FFHQ
contributes no spliced images; its warp-only negatives are af0_zero (two-person geometry) only. A mirror-based S0
(R2wm inside R2w4) was considered and rejected: it is a kind train_Sb does not contain. Consequence, stated: spliced
images remain FRGC / colorFERET only; the per-source kind mix differs (FFHQ: no splice kinds).

Expected FFHQ training images: 450 + 225 + 400 + 400 + 800 + 200 + 200 + 150 + 150 + 300 = 3,275 unique
(FRGC 3,003, colorFERET 2,532). Counts bind only as targets; shortfalls are reported, not filled from another source.

### 3.4 MS1 FFHQ development hold-out (person-disjoint from every MS1 training person and from ffhqm)

300 persons, same pipeline: photo (300), stored copies at fm61 and amsl112 for every photo (amsl112 is a size never
trained), u50 morphs of 150 pairs within the hold-out (hosts = the first 150 hold-out persons, partners drawn by the AF0
rule inside the hold-out), the u50 morphs' fm61 and amsl112 copies, 150 zero images (placement only). This is the
"same source, new people" pool; ffhqm (the HN2 persons and landmark_combined) is the "same source, other pipeline"
pool.

## 4. Gates (as the existing ladder used)

- Alignment success share (printed per source; no threshold forces a rerun).
- Pixel checks on 8 pairs: af_morph u50 equals the unchanged engine `hm.morph` bit for bit; zero equals clip(W_A);
  78_tool_morph R4 of the same pair equals u50 (same engine) or the difference is printed.
- Path equivalence: the MS1 wrappers re-run on 4 existing AF0 FRGC rows (u50, zero, one half, one fm61 copy) must
  reproduce the existing files pixel for pixel; if not, the build stops.
- Stored copies: aligned flag and native eye distance from e7_branch printed; rows whose re-alignment fails are dropped
  and counted.
- Identity: R4 partner cosines printed (median); exclusion proof all zero.
- Every produced image has its sha256 in `MS1/lists/*.csv`; the builder scripts' sha256 and those of every imported
  unchanged file (`73_delin_align.py`, `78_tool_morph.py`, `68_hires_morph.py`, `af_morph.py`, `soften.py`,
  `prep_eval.py`, `variants.py`, `fr.py`) are recorded in `build_log.json`.

## 5. Balancing rule (amendment 4, extended)

Class balance inside each stratum database x storage history by seeded repetition of the smaller class
(`src/PN1/mkmanifests.py` `balanced`, imported unchanged). The four strata of train_Sb keep their original seeds
(20261111 + their index in Sb's sorted strata: feret|native 0, feret|s61 1, frgc|native 2, frgc|s61 3), so the
FRGC / colorFERET rows of the multi-source manifest equal train_Sb's rows (checked as a multiset). Each new stratum j
(sorted, e.g. ffhq|native, ffhq|s61) uses 20261111 + 100 + j. No balancing across databases: each source enters with
its natural unique count (FFHQ about 3,275 against 3,003 and 2,532), stated. A stratum with one class only stops the
build. New sources later: same rule, new strata appended with the next indices; existing rows unchanged.

## 6. Requirements for a further source (for the author's dataset choice)

A source is usable if it provides:
- native inter-eye distance ≥ 132 px in the raw photo (the frame's own eye distance, so the frame is never an
  enlargement; ≥ 112.7 px at the least, so that the untrained 112.7 px stored copy is a true shrink); never below
  61.2 px;
- frontal, neutral, unoccluded photos that pass the unchanged aligner's frontal filter (nose within 0.16 of the eye
  distance of the eye midpoint, eyes level within 0.12);
- identity labels with at least two photos per person, preferably from different sessions (needed for R2w, R3, S0, S3
  and so for the matched negatives of the spliced morphs);
- a licence that allows research use and publication of results (and of pair lists);
- no overlap with any benchmark set (FRLL, MAD22, MorDIFF, DiM, H1 / CASIA-WebFace, FEI, sealed sets) or with
  ffhqm.
Persons needed: about 900 (600 training, 300 hold-out), of which at least 150 training persons with two photos;
minimum workable 400 (300 training incl. 100 with two photos, 100 hold-out).

## 7. Not done / out of scope of part 1

No score, no fit. The comparison (arm "SbM3" against Sb at the same seeds, same GPU type), development marks,
predictions, falsifiers and the pack are part 2, written before any fit and reviewed before any run.
