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
- Added 13 Nov 2026 (lead's instruction after the MS1 post-result review, H-new-5; plan text, not a registration):
  **no fit on a fourth source without a registered own-rule miss guard on an attack pool from an unseen pipeline**
  (details in `prereg_gpu_hypotheses_draft.md`, section "Fourth source").

## 7. Not done / out of scope of part 1

No score, no fit. The comparison (arm "SbM3" against Sb at the same seeds, same GPU type), development marks,
predictions, falsifiers and the pack are part 2, written before any fit and reviewed before any run.

# Part 2: the training comparison (registered at the git commit that adds this part; no fit, no score of any MS1 arm exists at that commit)

Source: `prereg_comparison_draft.md` (cb1cf09) with every fix of the pre-run review
`experiments/reviews/PRERUN_MS1_COMPARISON_20261112.md` (GO WITH FIXES) and the lead's rulings of 12 Nov (relayed after
the review), applied with the reviewer's texts. `date` at writing: see the commit; this part was written from
Thu Nov 12 11:24 PM CET 2026 on.

## 2.0 Lead rulings recorded (under the author's general authorisation of about 22:58, "Execute the necessary commands without waiting for my approval")

- B3 accepted: the Chicago Face Database (CFD) neutral images become a held-out sharp evaluation source (co-primary
  P1-S). CFD will NOT be used for training (lead decision, not the author's specific approval). KDEF neutral-straight
  images are a printed secondary. CelebA-HQ and MUCT are not used for this read.
- M2: a data-volume control arm SbV is added now (five more fits on WCSS).
- The owner may upload and submit on WCSS (no rental): complete workload on the cluster before submission, at most 6
  GPUs at once for MS1, one retry if the scheduler refuses sbatch.

## 2.1 Arms, seeds, platform

- **Sb**: manifest train_Sb (`2cf3fda3…`), FRGC + colorFERET, 8,386 rows.
- **SbM3**: train_SbM3 (`885dff9d…`, 13,414 rows) = train_Sb's rows unchanged (asserted) + 3,263 FFHQ images (part 1).
- **SbV (data-volume control)**: train_SbV (`8920699f52266f9d78bb3b2da30aa28488c4d8e8286404618b198f97535ac820`, 13,414
  rows): train_Sb oversampled within its strata to SbM3's row count (`src/MS1/mkmanifest_vol.py`), no new image.
- Splice share of attack rows (lad_S4 rows / attack rows): Sb 0.1026, SbM3 0.0641, SbV 0.1050 (printed in the result).
- Seeds 403-407 for every arm: 15 fits, ordered seed by seed (Sb, SbM3, SbV), at most 6 at once.
- Unchanged code and flags, different software: `train.py` of the AD4 pack (`cbb2cbd1…`) with the PN1 flags (6,250
  steps, batch 256, LoRA r 2 on q/v, last checkpoint) and `pn1_score.py` (`737d6e35…`), both from the FS1 tree, run
  under WCSS `~/dmenv` (torch 2.11) instead of torch 2.2.1 (Athena container, rented hosts). Driver `src/MS1/run.sh` =
  `src/PN1/run.sh` (`6a23a7a4…`) with these changes only: arm list Sb|SbM3|SbV, results folder `results/MS1`, default
  pack name, and one added line that writes the software versions into each result (`env.txt`).
- Platform: WCSS H100 (lem-gpu-short, `gpu:hopper:1`), one job per fit. GPU name and UUID per fit (`gpu.txt`).
- Fallback rule (M3): "started" means all fifteen tasks are RUNNING or COMPLETED by 13 Nov 2026 12:00 CET. Otherwise the
  A100 fallback runs (SbM3 and SbV seeds 403-405 on one rented A100 PCIe 40 GB, compared with FS1's Sb seeds 403-407
  by the same rules, on the lead's decision), the WCSS array is cancelled, and WCSS fits are never read for MS1. The
  two platforms' fits are never mixed.

## 2.2 Evaluation data (development only)

- In the fit pack (`pn1_eval.csv`): FS1's 19,797 development rows (`f0f29f22…`) + MS1 FFHQ hold-out 1,480 rows (fam
  `ms1ffhq`) + TT1 aligned genuine photos 21,089 (fam `tt1`, cell = TT1 family; TT1 aligned manifest `8b3c6fa9…`).
- Held-out sharp sources, scored after the fits from each kept `last_trainable.pt` with the unchanged PN1 rescorer
  (`src/PN1/rescore.py`, meta.json + last_trainable.pt on the pack's base weights, logit without flip) in ONE separate
  WCSS job, submitted only when its pack is complete and all fit tars exist:
  - **CFD**: every neutral image (`*-N.jpg`) of CFD 3.0.1 (CFD, CFD-INDIA, CFD-MR), one per person, aligned with the
    unchanged `73_delin_align` (`src/MS1/heldout_pool.py cfd`). Pool, sha256 and person count fixed in section 2.9
    before any MS1 score exists. Disclosure: studio capture like FRGC; frames are shrunk about 2.7x (eye distance
    about 330-380 px into 132 px).
  - **KDEF** neutral straight (`??##NES.JPG`, 70 persons x sessions A and B), same aligner; printed only.
  - TT1's border-blanked camera-photo references (R_cam^border) and crop-geometry-matched references, if they exist
    in TT1's registered scoring list at the time this scoring pack is built (`/mnt/t7/smad_next/TT1/border_ref.csv`
    exists, 4,919 rows); printed only.
- Labels: for SbM3, FFHQ is a TRAINED source. ffhqm reads are "trained source (FFHQ), development persons excluded by
  key, file and identity, other alignment pipeline"; MS1 hold-out reads are "trained source (FFHQ), new persons, same
  pipeline". For Sb and SbV, FFHQ is untrained. No sentence calls FFHQ unseen for SbM3. Unseen sources for all arms:
  the seven TT1 families, CFD and KDEF.
- No unseen-source attack read is left in development (the FFHQ morph families are in-source for SbM3).

## 2.3 Thresholds

- Own rule τ_0.5: logit > 0. Decides every primary read.
- τ_cam (printed only): FS1's rule: the larger of the two 5%-false-alarm thresholds of development camera photos
  (development-ladder R0, 100; AF0 validation photos, 126), native only.

## 2.4 Reads, predictions, falsifiers (per network, then across read seeds)

f_k = share of pool k's genuine photos with logit > 0. Primary comparison: SbM3 against Sb. SbV is read against Sb and
against SbM3 with the same statistics, printed only (no claim either way).

**P1-S (co-primary): sharp unseen source, CFD.** Statistic F_S = f_CFD.
**P1-T (co-primary): unseen low-resolution sources with black borders, TT1.** Statistic F_T = unweighted mean of f_k
over the seven TT1 families.
For each co-primary separately:
- Supported if median(F, SbM3) ≤ 0.5 × median(F, Sb) AND the exact one-sided Mann-Whitney test (SbM3 lower, ties
  half) gives p ≤ 0.025 (5 against 5: U ≤ 2 of 25, p = 4/252).
- Falsified if median(F, SbM3) ≥ 0.8 × median(F, Sb) OR p > 0.5.
- Otherwise "inconclusive, no claim".
- Floor: if median(F, Sb) < 0.03, that co-primary is "untestable at the own rule (floor)".
- Power: the test detects only near-complete separation; "inconclusive" is the likely result for effects below about
  1.5 seed-SD.
- Printed: f_k per pool with Clopper-Pearson 95% intervals and a person-cluster bootstrap (2,000 draws,
  `default_rng(20261125)`; TT1 pseudo-identities labelled as such, with TT1's M2 inflation factors applied when TT1's
  registration gives them); F_T without MSU-MFSD (65 images); the number of TT1 families in which SbM3's median f_k is
  below Sb's; P1-T and P2 against TT1's border-blanked references when they exist.

**P2 (secondary): scale-free source offset.** Per unseen pool k (seven TT1 families; CFD printed beside),
AUC_k = AUC(pool k genuine against development camera photos: development-ladder R0 100 + AF0 validation photos 126,
native), pool positive. O = mean over the TT1 families. Supported if median(O, Sb) − median(O, SbM3) ≥ 0.05 AND
Mann-Whitney p ≤ 0.05 (SbM3 lower); falsified if median(O, SbM3) ≥ median(O, Sb); otherwise inconclusive.

**P3 (secondary): same source, new persons.** Own-rule flag share on the 300 MS1 FFHQ hold-out photos (native).
Predicted median over SbM3 seeds ≤ 0.05; falsified for SbM3 if > 0.10. Printed: Sb, SbV; ffhqm HN2 genuine own-rule
flags (2,000); AUC of hold-out u50 against hold-out photos.

**Guards (each on medians across read seeds; Mann-Whitney printed; no claim of improvement).**
- G1 FFHQ landmark_combined AUC (1,000 orig morphs against 2,000 resmatch genuine): median(SbM3) ≥ median(Sb) − 0.03.
  G1 is in-source for SbM3 and biased in its favour. A pass shows no cost on an unseen pipeline. No improvement may be
  claimed.
- G2 development attack detection, FRGC / colorFERET: development-ladder R4 against R2w AUC and AF0 validation u50
  against AF0 validation photos AUC, each median(SbM3) ≥ median(Sb) − 0.02; own-rule miss on development R4 + AF0
  validation u50: median(SbM3) ≤ median(Sb) + 0.05.
- G3 storage at the untrained size (two-sided): standardised median paired shift (112.7 px copy − native) / SD(native
  genuine logits) on development camera photos: |shift(SbM3)| ≤ |shift(Sb)| + 0.10. Printed: MS1 FFHQ hold-out
  (amsl112), the 61.2 px reads, FS1 contrast 2's paired storage share on ffhqm (trained source for SbM3).
- A guard that fails is reported in the P1 sentence ("…, at a cost in …").

**Printed only:** τ_cam flag shares on every unseen pool; training-row minus held-out mean logit per kind; FS1 R1-R6 on
landmark_combined per arm; the smoke gate (2.6).

## 2.5 Seed rules

- A seed is read only if Sb and SbM3 both finished with finite loss and a verified tar (SbV's seeds are read where its
  fit and Sb's exist). A seed with a lost or non-finite arm is dropped and not replaced. A non-finite run is never
  rerun; an infrastructure failure is rerun once, unchanged, on the same partition.
- n read seeds 5 or 4: the tests above (4 against 4: smallest one-sided p 1/70 = 0.014; a co-primary then needs U = 0);
  3 or fewer: "not read (too few seeds)".
- Margins inclusive at full float precision; Mann-Whitney exact by enumeration, ties half. No seed is dropped or chosen
  on any score.
- Deadline: fits finished and fetched by 14 Nov 2026 12:00 CET are read; the held-out scoring job by 14 Nov 18:00 CET.

## 2.6 Smoke gate (printed only, decides nothing)

The WCSS smoke (20 steps, seed 403, arms SbM3, Sb, SbV) prints its first 20 training losses and the hash of its sample
order where train.log shows them; the Sb s403 values are printed beside FS1's Sb s403 `train.log` (rented A100,
torch 2.2.1). The fit array is submitted only after the smoke finished without error.

## 2.7 Outcome sentences (development data; never a benchmark claim)

The effect, if any, belongs to the three-source protocol (photos, morphs, controls, more rows, a smaller splice share).
Nothing is attributed to source diversity alone.

| Outcome | Sentence |
|---|---|
| P1-S supported | "With the three-source protocol, genuine flag rates at the network's own rule fall on a sharp unseen studio source (CFD), n seeds." (+ ", at a cost in <guard>" if a guard fails) |
| P1-T supported | "… fall on seven unseen low-resolution sources with black borders (TT1), n seeds." (same cost rule) |
| P1-S falsified | "The three-source protocol does not make the own-rule threshold transfer to a sharp unseen studio source (CFD)." |
| P1-T falsified | "The three-source protocol does not make the own-rule threshold transfer to unseen low-resolution sources with black borders (TT1)." |
| co-primary untestable (floor), P2 supported | "No own-rule effect measurable on <pool>; scale-free, unseen-source genuine scores move toward the training sources' camera photos." |
| anything else | "inconclusive, no claim" (per co-primary) |
| SbV | printed beside both; if SbV meets a co-primary's support rule against Sb, the sentence adds "the data-volume control shows a similar fall, so the effect is not shown to need the third source". |

Must not claim: anything on benchmarks; "source-invariant"; that FFHQ is unseen for SbM3; a cause (source vs volume vs
border vs splice share); "threshold transfers to unseen sources" in general from TT1 alone.

## 2.8 Disclosures and confounds

- Known before writing: Sb seeds 401/402 own-rule FFHQ genuine flags 5.9 / 7.0% (B 17.8 / 6.4%); FFHQ genuine flagged
  3.5-22.5% at the own rule and 95-98% at τ_cam across PN1 networks. The 0.5 ratio was set knowing these. No TT1, CFD
  or KDEF score of any network exists; the MS1 owner has opened no FS1 fresh-seed tar.
- Data volume: SbM3 13,414 rows against Sb's 8,386 at 6,250 steps (each FRGC / colorFERET row seen 0.63x as often);
  SbV controls the row count, not the content.
- FFHQ content: in-the-wild photos and black frame borders in both classes; FFHQ frames are shrunk into the frame,
  TT1 frames enlarged 1.7-3.5x; the fm61 copies are the only enlarged FFHQ training images. FFHQ adds no splices.
- `exclusion_proof.json` refs_found 3,999 of 4,000: the missing reference is ffhqm genuine key 50727 (no face found by
  prep_eval.kps on its aligned frame); it is excluded from MS1 by key (it is in the FFHQ-Morphs universe).
- Platform: unchanged code and flags, different software (torch 2.11 vs 2.2.1).

## 2.9 Pins

- Pack `/mnt/t7/smad_next/MS1/pn1_pack_ms1.tar` sha256 `c11b16bc7b76236bae80778f9e36cb67bb50de910f73a9dd200a706fc267fe7d` (14,510,059,520 bytes, 51,273 files; adds
  train_SbV.csv to the reviewed pack `dac228f5…`, otherwise the same files; evaluation manifest
  `d1fab6ad4b20f0ec9dd426374ccd56e96368bf7b658b48e3ef31867e1fe470c5`, 42,366 rows).
- `src/MS1/run.sh` `098e94cd2821c415803f1b080b5e655e5c164bed040abffa10afe93bf1f669ed`; `src/MS1/wcss/ms1_fit.sbatch` `5b6dd4e2585493d1dbaa95325cdb84e62ad33446bc9cab9a743d11f83ec41e92` (array 0-14%6, 3 h, 80 GB local);
  `src/MS1/wcss/ms1_smoke.sbatch` `67cbb07ceba11361bf2d9b81f0f476fba369b532a767b0020af31e0a2df7eb7b`; `src/MS1/mkmanifest_vol.py` `11600a8774f5ef198498a5abd64d65035e201268627400de7c735d5d6c11fc8d`; train_SbV.csv `8920699f…`.
- CFD pool (`src/MS1/heldout_pool.py` `c9f8e43952c6e152d0ecea50e601c29da9562cb70d45b691099c6c23d1cdaf6e`): 831 neutral images of 827 persons (CFD 597, CFD-INDIA 146, CFD-MR 88;
  4 persons with two neutral images, both kept), all 831 aligned, 0 failures; `/mnt/t7/smad_next/MS1/cfd/pool.csv`
  sha256 `d6ef6793b588fa981ccb27a575ead4b91ffad0f3fe2b2345973c8ec9866b75a9`; f_CFD counts images.
- KDEF pool: 140 neutral straight images (70 persons x sessions A, B), all aligned; `/mnt/t7/smad_next/MS1/kdef/pool.csv`
  sha256 `e54be768a2b1ab8cb6fc9e9812d6baf1e2009ca06ef35268bbbecd497589d8c3`.
Reader: `src/MS1/ms1_read.py` is extended for P1-S / P1-T / SbV in a later commit, before any tar is fetched; the fetch
is gated on that commit (B2). Kept: every result tar on WCSS PD and a verified copy on `/mnt/t7/smad_next/MS1/results`
before anything is cleaned; trained weights (`last_trainable.pt`) of all fits are kept.

## Deviation MS1-D1 (prepared; `date`: Thu Nov 12 11:54:23 PM CET 2026; registered at the commit that adds it; no fit or score of any MS1 arm exists): rented A100 fallback, in force only if the lead switches

Trigger (lead, 12 Nov, about 23:50): if the WCSS slurm controller does not accept jobs by 13 Nov 2026 01:00 CET, the
lead switches MS1 to rented machines tonight, instead of waiting for the 12:00 rule of part 2 (2.1). The switch is the
lead's decision and is recorded with its `date` in the README when made. Until then part 2 (f748da4) stands unchanged.
- All fifteen fits (Sb, SbM3, SbV at seeds 403-407) run on rented A100 PCIe 40 GB machines of one type (the FS1
  type, A100-PCIE-40GB), three machines; never mixed with WCSS fits. The WCSS array is not submitted, or is cancelled if
  it was submitted; no WCSS MS1 fit is ever read. If the smoke job ran on WCSS, it is printed only.
- Layout, each seed's three arms on one machine: m1 seeds 403 and 406 (6 fits), m2 seeds 404 and 407 (6 fits), m3 seed
  405 (3 fits). (Five fits per machine is impossible with whole seeds; whole seeds are kept because every comparison is
  within seed.) GPU UUID per fit in `gpu.txt`; results printed per machine.
- Software: the FS1 rented setup (image pytorch 2.2.1 / CUDA 12.1, pip pins timm 1.0.27, numpy 1.26.4, pillow 10.2.0,
  as `src/PN1/rented/remote_fs.sh`), so the arms run under FS1's software; versions in each tar (env.txt).
- Held-out step (CFD, KDEF): on each machine, after its fits, every finished fit of that machine is rescored with the
  unchanged `rescore.py` from the held-out pack (`06b64608…`); one tar MS1H_<machine>.tar per machine. (Deviation
  from "one job": each fit is scored on the GPU it was trained on, and no weights move between hosts.) TT1's
  border-blanked references are added only if TT1's scoring list is registered before the machines start; otherwise
  they are scored later on the DGX, labelled "other platform", printed only.
- Reads, rules, predictions, seed rules, deadline: part 2 unchanged; "WCSS" in 2.1 reads "rented A100 PCIe 40 GB".
- Keep rule: weights, logs and scores (fit tars with last_trainable.pt, the held-out tar, every log and rc file) are
  fetched and verified before RELEASE; a second copy of every verified tar in `/home/narolski/ms1_results_copy`;
  RELEASE + FAILED only on a verified partial result whose failures the remote confirms (no tar and non-zero rc); no
  RELEASE when the remote state is unreadable; no pull when /mnt/t7 has under 20 GB free; remote setup requires 50 GB
  free under /workspace.
- Scripts: `src/MS1/rented/drive_ms1.sh` `eb59456334bd623fa909c1963406ae33bd91aadcd1d605ee210eb41618b63ba0`, `src/MS1/rented/remote_ms1.sh` `305b5d5b39f1f991910ea7f77f9e5a05292727887ec19742874a04c03f7fe8b5` (adapted from FS1's
  drive_fs.sh / remote_fs.sh; pins: pack `c11b16bc…`, held-out pack `06b64608…`, run.sh). Test: remote_ms1.sh queue
  run on the DGX with stand-in tasks (two passing, one failing twice: rerun once, rc recorded; held-out step produced
  4 npz for the two passing fits; ALL_DONE written). drive_ms1.sh is syntax-checked only; its pull and RELEASE logic is
  FS1's, not run against a host.
- Cost and time (FS1 measurements on this machine type: 0.468 USD per hour, fit wall 4,026-5,395 s, pack upload
  8.75 GB in 3,122 s): per fit about 1.45 h (larger evaluation list); upload 15.5 GB per machine 1.5 h alone, up to
  about 4.5 h if the three uploads share the DGX uplink. m1 and m2: about 10.5-13.5 h, m3 about 6-9 h. Cost about
  13 USD expected, at most about 17 USD (caps proposed: m1 7, m2 7, m3 4.5 USD). Starting at 01:00, results about
  11:30-14:30 on 13 Nov, within the 14 Nov 12:00 deadline.

## Deviation MS1-D2 (`date`: Fri Nov 13 12:03:29 AM CET 2026; registered at the commit that adds it, before any fit; no fit or score of any MS1 arm exists)

Lead's decision at 00:00 on 13 Nov: WCSS will not start the jobs tonight (priority about 700 against about 10,800 at
the head of 139 waiting jobs); the WCSS smoke job 6308826 was cancelled by the lead; MS1 runs on rented machines under
MS1-D1 (5eadc1b) with these changes:
- GPU model: NVIDIA L40S 48 GB instead of A100 PCIe 40 GB (no single A100 PCIe 40 GB on the market). All fifteen fits
  and the held-out scoring run on that one GPU model; GPU name and UUID in every tar (`gpu.txt`, held-out
  `out/gpu.txt`); never mixed with WCSS or A100 fits. FS1's A100 Sb stays a printed reference only; the smoke
  comparison against FS1's Sb s403 train.log is printed, not a gate. Batch size and every training flag unchanged (48 GB
  holds the 30.8 GB peak). Software pins as MS1-D1 (pytorch 2.2.1 / CUDA 12.1 image, timm 1.0.27, numpy 1.26.4,
  pillow 10.2.0).
- Leases (lease folders `/mnt/t7/smad_next/vast/<name>`): ms1m1 seeds 403+406 (cap 8 USD, 13 h; GPU-771bd979…),
  ms1m2 seeds 404+407 (cap 10 USD, 13 h; GPU-214a6ac4…), ms1m3 seed 405 (cap 6 USD, 9 h; GPU-b1d985cf…).
- Held-out step now includes TT1's registered references (TT1-S at 01557ce; list `tt1_score.csv` `c0055b51…` pinned
  at ccd6319): R_cam (417, ids prefixed `rcam_`), R_cam_border (7 x 417), R_cam_geo224 and R_cam_geo112 (417 each),
  R_ffhq_border (2,000), fam `tt1ref`, as part 2 (2.2) allows. Held-out pack rebuilt:
  `/mnt/t7/smad_next/MS1/ms1_heldout_pack.tar` `396a7ebeacf1f4b31077e04e0588e0ff84b9287457b8980ea95c9c91fee693a7`
  (7,141 rows: CFD 831, KDEF 140, tt1ref 6,170; manifest `e77fa2e4…`; builder `11daa10b48609d0cbcc4b302367e1458192f7af10782f40ba64671390588ef06`); the CFD and KDEF rows are
  unchanged. Printed against them (no new decision rule): own-rule flags of R_cam_border(k) beside f_k, and
  AUC(TT1 family k against R_cam_border(k)) beside P2's AUC_k.
- Scripts: drive_ms1.sh `60c2ca71a76f7493ebe3dac1fea64ca6c965958d9ce905d977dbb6271dd09d3b` (held-out pin updated), remote_ms1.sh `5484c6e117cb1c7d09a202da446f7bdca5305acc1b430cf936bcbc290e438403` (held-out families cfd, kdef, tt1ref).
- Everything else of part 2 and MS1-D1 unchanged.

- MS1-D2 note (`date`: Fri Nov 13 12:33:45 AM CET 2026; no fit had started on ms1m1): lease ms1m1 (GPU-771bd979…) was released by the lead before
  any fit because its upload stalled; queue m1 (seeds 403+406) runs on the replacement ms1m1b (L40S 48 GB,
  GPU-c1ff3444-2b67-80c8-b31d-2c9ad1528acc, cap 10 USD, 13 h). Same GPU model; nothing else changes.

# Part 3: zero-GPU reads after the part-2 read (registered at the git commit that adds this part; `date` at writing: Fri Nov 13 10:06:18 AM CET 2026; no part-3 statistic exists on real scores)

Source: post-result review `experiments/reviews/REVIEW_MS1_20261113.md` (F8; hypotheses H-new-4 and item 3) and the
lead's instruction (13 Nov, about 10:10): produce the missing registered printed items; register and run the two
zero-GPU hypotheses; one results-reviewer pass. Disclosure: written after the part-2 read and the review; the review
recomputed some quantities already (CFD flags by group and sex for Sb; no correlation with the norming variables and
no train-minus-held-out gap was computed by anyone). Data: the existing MS1 result tars and held-out npz (sha256 in
`rented_kept/`), the MS1 evaluation manifest (d1fab6ad…), the CFD pool (d6ef6793…), the CFD 3.0.1 norming workbook
(main set, U.S. norming), the pinned cues file `/mnt/t7/smad_next/PN1/cues/a14_lcomb.npz`. Reader
`src/MS1/ms1_part3.py` sha256 `9986a87045c6635425d85dddf4e9ff80cd59e0478ab8b5f644691fdc4c7daf44` (tested on mock scores only: `ms1_part3_mock.json`), run once with thread caps.

## 3.1 Printed items (no decision)

(a) Training-row minus held-out mean logit per kind and network (PN1 amendment 4 item 3 form): training rows from each
fit's `scores_train.npz` (unique rows of its own manifest), held-out rows of the same kind from the evaluation
manifest (FRGC / colorFERET: AF0 validation photos, their 61.2 px copies, zero, halves, u50; development-ladder R0,
R2w, R4; development splice S0, S3, S4; FFHQ kinds of SbM3: the MS1 hold-out photo, fm61 photo, zero, u50, fm61 u50).
(b) FS1 R1-R6 per arm (Sb, SbM3, SbV) and seed on FFHQ landmark_combined, `src/PN1/fs_read.rreads` unchanged.
(c) The smoke gate: not producible (the WCSS smoke job was cancelled by the lead on 13 Nov 00:00 before it ran; the
rented runs had no separate smoke).

## 3.2 H-mem (memorisation or dilution; zero GPU)

Statement: SbM3 sees each FRGC / colorFERET image 0.63x as often as Sb, so it memorises them less. Gap per kind =
mean(train) − mean(held-out) for attack kinds and mean(held-out) − mean(train) for negative kinds (positive = training
rows scored more confidently than held-out rows of the same kind). M = mean gap over the 11 FRGC / colorFERET kinds
listed in 3.1 (a). **Supported** if M(SbM3) < M(Sb) on ≥ 4 of 5 seeds; **falsified** if M(SbM3) ≥ M(Sb) on ≥ 4 of 5
seeds; otherwise "inconclusive". Printed: SbV, every kind's gap. Reading if supported: consistent with dilution; it
cannot separate dilution from diversity (that needs the step-matched arm, H-new-2, GPU).

## 3.3 H-new-4 (appearance cue on smooth faces; zero GPU)

Statement: Sb's CFD false flags follow perceived femininity (blending smooths skin), which FFHQ genuine photos
counter-train. Within each CFD race group (A, B, L, W; the 597 main-set models with U.S. norming), Spearman ρ of the
network's CFD logit with the "Feminine" norming mean, per seed; group ρ = median over the 5 seeds. **Supported** if
ρ(Sb) > 0.2 in ≥ 3 of 4 groups AND |ρ(SbM3)| < 0.1 in ≥ 3 of 4 groups; **falsified** if ρ(Sb) < 0.1 in ≥ 3 of 4 groups;
otherwise "inconclusive". Printed: Masculine, Attractive, Babyfaced, AgeRated, LuminanceMedian; own-rule flag rates by
group and self-reported gender (mean over seeds). Associational only; never a causal or demographic-bias claim
beyond these development images.

## Part 3b: printed-only amendment (registered at the git commit that adds it; `date` at writing: Fri Nov 13 10:14:01 AM CET 2026; not yet computed)

Lead's decision after the part-3 review (`experiments/reviews/REVIEW_MS1_PART3_20261113.md`): register before computing,
printed only (no decision rule), one reviewer pass. Disclosure: the reviewer already computed these quantities post hoc
(rank AUC Sb 0.541-0.557 vs SbM3 0.514-0.535; within-sex ρ(Feminine) women Sb 0.248, SbM3 0.007); this amendment
reproduces them with registered code. Reader `src/MS1/ms1_part3b.py` sha256 `e93bd4523d0a8113375d1f590fb21ea54129b3760a5a7bd250fb2048bebf4eb4` (mock-tested only), run once with
thread caps.
- (a) Rank-AUC memorisation per kind and network: P[training row scored more confidently than a held-out row of the
  same kind] (ties half), same rows and held-out pools as part 3; A = mean over the 11 FRGC / colorFERET kinds; printed:
  per kind, A per network, seeds with A(SbM3) < A(Sb) and A(SbV) < A(Sb).
- (b) Within-sex reads on CFD (597 main-set models): Spearman ρ(CFD logit, Feminine) within each self-reported sex,
  pooled over race groups and per race group × sex, per seed, median over seeds; own-rule flag rates and counts by race
  group × sex per seed.
- Adopted for any later arm (lead, 13 Nov): the memorisation statistic is the rank AUC of (a), not the mean-logit gap.
- CelebA-HQ / fourth-source plan (written here and in `prereg_gpu_hypotheses_draft.md`): beside the own-rule miss guard
  on an attack pool from an unseen pipeline, two printed guards: sex-stratified CFD own-rule flags and within-sex
  ρ(CFD logit, Feminine), per arm. Warning recorded (reviewer): CelebA-HQ images are super-resolved and often heavily
  made up, so this source may teach "smooth means genuine" and raise misses on smooth morphs.

- Part 3b note (13 Nov, after its review REVIEW_MS1_PART3B_20261113.md; the registered text above is unchanged): the
  rank-AUC memorisation statistic for later arms is printed with the per-kind table, the count of kinds below 0.5 and
  per-seed paired differences against the reference arm on identical row sets, kinds and weights fixed at
  registration. For the CelebA-HQ printed guards: per-seed ρ paired against the Sb reference with flag counts beside it,
  signed ρ (does the feminine-means-attack link return?); the unseen-pipeline miss guard printed stratified by parent sex
  (a smoothness / make-up proxy if available); CFD stays printed-only (not a selection set).

# Part 4: dilution against diversity (G2) and splice share (G3) on WCSS H100 (registered at the git commit that adds this part; `date` at writing: Fri Nov 13 02:30:37 PM CET 2026; no part-4 fit, smoke or score exists)

Not registered until copied into `prereg.md` at a commit before the smoke and before any part-4 fit. Lead's
instruction, 13 Nov 14:10: the two drafted training experiments go to WCSS, all fits and all scoring of each on the
H100 in the fit job, with their own comparators there; the own-rule miss guard on the unseen-pipeline attack pool and
the printed within-sex guards in the registration; a pre-run check; one smoke through the real path; then the
submission files to the dispatcher queue. Source texts: `prereg_gpu_hypotheses_draft.md` G2 and G3; reviews
REVIEW_MS1_20261113.md (H-new-2, H-new-3), REVIEW_MS1_PART3_20261113.md, REVIEW_MS1_PART3B_20261113.md.

## 4.1 Arms, fits, platform

- Arms (all new fits, one platform; none of the L40S fits is used): **Sb** (train_Sb, 6,250 steps), **Sb63** (train_Sb
  at 3,938 = 0.63 × 6,250 steps, the per-image exposure of FRGC / colorFERET rows in SbM3), **SbM3** (train_SbM3, 6,250),
  **SbM3S** (train_SbM3S, 6,250: SbM3 with 97 of its 124 spliced-morph rows entered twice before the per-stratum
  balance, so the splice share of attack rows is 0.1026 = Sb's; `src/MS1/mkmanifest_s4.py`, manifest
  `eaefef80c3a2d2167bbcd65e9da9815347af4c42f7803576736bb2c89ec731e5`, 13,414 rows).
- G2 uses Sb, Sb63, SbM3; G3 uses Sb, SbM3, SbM3S. Sb and SbM3 are shared: **20 fits** (4 arms × seeds 403-407), not 30.
- Platform: WCSS H100 (lem-gpu-short, `gpu:hopper:1`), `~/dmenv` (torch 2.11.0+cu128, timm 1.0.30; supports sm_90;
  printed by the smoke with `torch.cuda.get_arch_list()`), one job per fit (array 0-19%6), seed by seed. Training and
  scoring commands unchanged (train.py of the AD4 pack, PN1 flags; pn1_score.py with TF32 on) except `--steps` for Sb63.
  Every score of part 4 is made in its fit job on the H100 (evaluation manifest includes CFD and KDEF); nothing is
  compared with L40S or A100 scores.
- Driver `src/MS1/run_p4.sh` (`db75e5b6b6184a1cb3bd8990b8449d5115c364a8a66a769e4634a48f3a09a9b1`) = `src/MS1/run.sh` with: arm list Sb|SbM3|Sb63|SbM3S (Sb63 →
  train_Sb.csv, default steps 3,938), default pack `pn1_pack_ms2.tar`, results folder `results/MS1P4`, and a line writing the training-manifest sha256
  into the result (`manifest.txt`). DGX smoke of run_p4.sh (Sb63, 20 steps, 64 rows) passed; the reader's configuration
  check parsed its tar.
- Pack `/mnt/t7/smad_next/MS1/pn1_pack_ms2.tar` sha256 `79c2a7b883e8e8adb5860c9b84746ea26754e89159d49702e8b23ec4ad254f81`
  (14,871,592,960 bytes, 52,245 files; `build_pack_ms2.py` `c50f85f1…`): the part-2 pack plus train_SbM3S.csv and the
  CFD (831) and KDEF (140) frames; evaluation manifest `f7a5c98c7b2ccdd968108131c248f4a0e77d3c050f001e0ce0eaaacdeb3ac396`
  (43,337 rows).
- Smoke `src/MS1/wcss/ms1p4_smoke.sbatch` (`2ccc82180d8d85cc658355f9b90f19ddbee2c8ead27db1d34985a2377dcb1a2d`): 20 steps, 64 scoring rows, arms Sb63 and SbM3S, seed 403,
  through run_p4.sh; the fit array `src/MS1/wcss/ms1p4_fit.sbatch` (`e0b19fccaa00fea87287b37675bec220c9fc8f553de65dddc0a48e387a06c44f`) is queued only after the smoke log
  shows MS1P4_SMOKE_DONE.
- Reader `src/MS1/ms1_read_p4.py` (`d5b7985a33e7869d31da42c95b789bec5dbca50ba28bb6278b352e51be7ec091`; tested on mock scores only), run once.

## 4.2 G2: dilution against diversity

Statement: SbM3's CFD gain (part 2, P1-S) comes from seeing each FRGC / colorFERET image 0.63 times as often, not from
the third source. Statistic: CFD own-rule genuine flag rate (831 images), per network.
- Positive control (the P1-S effect must replicate on the H100): median(SbM3) ≤ 0.5 × median(Sb) AND exact one-sided
  Mann-Whitney p ≤ 0.025 (SbM3 lower); otherwise G2 is "uninformative (positive control not met)". Floor: median(Sb) <
  0.02 → "untestable (floor)".
- **Supported** if median(Sb63) ≤ 0.5 × median(Sb) AND p ≤ 0.025 (Sb63 lower). **Falsified** if median(Sb63) ≥ 0.8 ×
  median(Sb) OR p > 0.5. Otherwise "inconclusive, no claim". Ties half; margins inclusive. A floor hit on the control
  reads "untestable (floor)".
- What each outcome can show (pre-run check F3): Sb63 is the first 3,938 steps of Sb's same-seed run (constant LR, last
  checkpoint), so it changes per-image exposure AND total optimisation length, and the CFD flag is the own rule
  (logit > 0), whose calibration also changes with steps. "Supported" means "stopping Sb at matched per-image exposure
  reproduces at least half of SbM3's CFD gain without a third source"; it does not separate per-image exposure from
  total optimisation length. "Falsified" means "matched exposure by truncation does not reproduce it". (3,938 steps is
  0.8% above the exact 0.625 exposure of 3,908.)
- Printed: the fraction explained (Sb − Sb63) / (Sb − SbM3) of median CFD flags; per-seed paired Sb63 − Sb (same seed
  and data order); a scale-free CFD read (AUC of CFD against the development AF0 camera photos, and CFD mean logit
  minus the camera-photo mean); the training-row margin per arm (median logit of negative and attack training rows);
  rank-AUC memorisation (part 3b rules: per-kind table, count of kinds below 0.5, per-seed paired differences against
  Sb); TT1 F, MS1 FFHQ hold-out flags, KDEF flags.

## 4.3 G3: splice share

Statement: the S4 cost of SbM3 (development S4 against S0/S3 AUC 0.891 → 0.881, part-2 review F5) comes from the smaller
splice share. Statistic: AUC of development S4 (100) against development S0 + S3 (200), per network.
- Control: AUC(SbM3) < AUC(Sb) on at least n−1 of n read seeds (n = 5) or n of n (n = 4), AND Δ = median AUC(Sb) −
  median AUC(SbM3) ≥ 0.006; otherwise "uninformative (cost not replicated)".
- **Supported** if median AUC(SbM3S) − median AUC(SbM3) ≥ 0.5 Δ AND median AUC(SbM3S) ≥ median AUC(Sb) − 0.005.
  **Falsified** if median AUC(SbM3S) − median AUC(SbM3) ≤ 0.25 Δ. Supported is checked first; otherwise "inconclusive,
  no claim". Printed beside the verdict, not part of it: median CFD own-rule flags of SbM3S (≤ 0.01 or not), and the
  FFHQ landmark_combined miss of SbM3S against SbM3. (From the L40S SDs: P(falsified | no recovery) ≈ 0.8,
  P(falsified | full recovery) ≈ 0.04, P(supported | full recovery) ≈ 0.85; on the L40S the control held: AUC .891 vs
  .881, SbM3 lower on 5 of 5.)
- Disclosed side change of SbM3S: inside FRGC / colorFERET native strata the attack rows that make room for the doubled
  S4 rows are u50 (2,711 → 2,502 rows) and R4 (435 → 386); per-image S4 exposure 661 (Sb 662, SbM3 413).

## 4.4 Guards (each new arm Sb63, SbM3, SbM3S against Sb, same seeds)

- **Own-rule miss guard, attack pool from an unseen pipeline** (FFHQ landmark_combined orig, 1,000; no arm trained on
  its morph pipeline): holds if median miss(arm) ≤ median miss(Sb) + 0.05 AND the per-seed excess is > 0.10 on at most
  1 seed. A failing guard is printed with the arm's verdict ("at a cost in unseen-pipeline misses"); it does not change
  G2 or G3, which are mechanism tests. Parent-sex strata: not available (FFHQ parents carry no sex labels). Known in
  advance: on the L40S SbM3 failed this guard (miss median 0.585 against Sb 0.271); SbM3S is also printed against SbM3
  (its comparator for source familiarity).
- **Printed within-sex guards (part 3b note):** per seed, signed ρ(CFD logit, Feminine) within women and within men, paired
  against Sb, with the flagged counts beside it; sex-stratified CFD own-rule flags.

## 4.5 Seed rules, deadline, cost

- A seed is read for G2 (G3) only if all its arms finished with finite logits, a verified tar and a passing
  configuration check (per tar: steps 3,938 for Sb63 and 6,250 otherwise and limit 0 in task_info.txt; the training
  manifest sha256 in manifest.txt equal to the registered one; gpu.txt naming an H100; env.txt identical across tars);
  a failed check is "config mismatch", treated as an infrastructure failure. A timeout or NODE_FAIL is an
  infrastructure failure. 4 or 5 read seeds → the rules above (5 against 5: "supported" needs U ≥ 23 of 25; 4 against 4:
  U = 16 of 16); 3 or fewer → "not read". A non-finite run is never rerun; an infrastructure failure once, unchanged,
  same partition. No seed chosen on a score. If dilution explains only about half the gain, the likely G2 result is
  "inconclusive".
- Deadline: fits finished and fetched by 14 Nov 2026 15:00 CET are read; fewer than 4 read seeds then is reported as
  "not read (deadline)", with no extension without an amendment.
- The fit array fails fast unless `~/dmenv` is torch 2.11.0+cu128 / timm 1.0.30 with sm_90 (shared environment); the
  smoke asserts the same. The dispatcher places the array behind the method-critical arrays.
- Cost: about 1.1 H100-h per fit (6,250 steps) and about 0.75 for Sb63: about 21 H100-h, free (WCSS); jobs sort behind
  the method-relevant ones (dispatcher queue).
- Disclosure: written after the part-2 read, its review and part 3 (H-mem supported by mean logit and rank AUC; it
  does not separate dilution from regularisation). The L40S values of Sb and SbM3 are known; the H100 fits are new. The
  G2 floor (0.02, against P1-S's 0.03) was set after seeing Sb's L40S CFD median 0.035 and seed 407 at 0.018.
- Pre-run check: experiment-reviewer (opus), GO WITH FIXES (F1-F8), all applied (G3 rule, per-tar configuration check,
  G2 interpretation and prints, floor label, paired prints, guard notes, power and deadline text, environment asserts);
  the reader was mock-tested on every G3 branch (uninformative, inconclusive, falsified, supported) and G2.

- Part 4 operational note (`date`: Fri Nov 13 02:34:13 PM CET 2026; before any part-4 job was submitted): lead's instruction: the array throttle in
  `src/MS1/wcss/ms1p4_fit.sbatch` is raised from 6 to 20 (account cap 32 GPUs; free GPUs this evening); nothing else
  changes. New sha256 `0e084217d5919b246fb4880d2101d49b30a5e014828a6594caf10247461f9c32` (was e0b19fcc…). The array file is queued beside the smoke and is valid only if the smoke
  passes (the dispatcher cancels it otherwise). The lead's answers: the G2 wording "truncation reproduces it" is
  acceptable; `~/dmenv` is frozen for today's batches; the dispatcher orders the queue (no --nice needed).

## Part 4 amendment A1: fetch deadline (`date`: Fri Nov 13 03:45:30 PM CET 2026; registered at the commit that adds it)

Lead's instruction: WCSS is saturated and the part-4 jobs (smoke 6312973, array 6312974) have no start forecast. The
part-4 read deadline in 4.5 moves from "fits finished and fetched by 14 Nov 2026 15:00 CET" to **14 Nov 2026 18:00 CET**
(end of the experiment stage); fewer than 4 read seeds at 18:00 is reported as "not read (deadline)". Nothing else
changes. At this commit no part-4 tar, smoke result or score exists.
