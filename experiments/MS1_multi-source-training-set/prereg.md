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
