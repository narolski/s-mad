# Look-alike pair search (LA1): plan

Status: plan and draft registration only. Nothing is built, embedded or searched yet. Author's instruction, 13 Nov 2026
(relayed by the lead at 18:30): "Yes, plan the look alike pairs search on WCSS". Nothing of LA1 enters the frozen method
(Sb, seeds 403-407, frozen by the author's ruling at 18:28). Development and training data only.

## Goal

Find cross-person photo pairs whose glintr100 face-recognition similarity overlaps the same-person range of the ladder
pools: cos_HS 5-95% 0.77-0.93; colorFERET reaches 0.69. With such pairs, a later arm can match two-person and
same-person splices on similarity (blend-difference attribution, BD1: within same-person splices Sb's flags follow
low similarity, partial ρ −0.15 to −0.26 on development hosts). Pools already grouped at cosine 0.40 (the MS1
CelebA-HQ persons, the FFHQ pool) cannot contain such pairs by construction. Identity labels are therefore what make
the search possible: they tell a look-alike from an undetected same-person pair.

## 1. Sources

| Source | On disk | Persons / images | Resolution | Labels | Licence / terms | Use |
|---|---|---|---|---|---|---|
| **CelebA-HQ** (`Datasety/downloads/CelebA-HQ/CelebA-HQ-1024.zip`, HF mirror) | images yes; **identity labels no** | 30,000 images; about 6,200 CelebA identities (official mapping); 22,806 already aligned by the unchanged aligner with glintr100 embeddings in `MS1/celebahq/emb_*.npz` | 1024 px | **needs** CelebA `identity_CelebA.txt` + the CelebA-HQ-to-CelebA index mapping (CelebAMask-HQ release); not on disk (the `CelebAMask-HQ` folder is empty) | CelebA: non-commercial research, no redistribution; the mirror's apache-2.0 tag is not the original licence (author to check, as already noted) | **best source** |
| FRGC-2.0 full (`Datasety/FRGC-2.0`) | yes | 568 subjects, 39,328 stills | high | yes | FRGC licence (in use) | val10 subjects are sealed (VAL-X); every other FRGC subject is already a training subject. Usable only within PN1 training persons, about 427 already in the ladder pool |
| colorFERET (`Datasety/colorferet`) | yes | about 994 subjects, about 11,000 images | 512 × 768 | yes | NIST licence (in use) | same restriction (val split sealed; training persons only) |
| MUCT (`Datasety/downloads/MUCT`) | yes (tarballs) | 276 subjects, 3,755 images, 5 cameras | 480 × 640 | yes | research; no reproduction in public documents except consenting subjects | small new labelled source |
| NIST SD32 MEDS I-II | yes | 380 + 518 subjects (417 with ≥ 2 images), 2,018 JPEG, frontal and profile mixed | mugshot | yes (+ sex, race, pose metadata) | NIST terms: research only, no further distribution, **no image in any figure, repository or artifact**, NIST acknowledged | small new labelled source, pair lists only |
| FFHQ-1024 | yes | 70,000 images | 1024 px | **none** | CC BY-NC-SA | not usable (no labels) |
| Multi-PIE | yes (zip) | 128 px crops only | 128 px | yes | — | unusable (MS1) |
| FLUXSynID | yes | 14,889 synthetic identities | 1024 px | yes | — | **ruled out by the author** (12 Nov) |
| CFD, KDEF | yes | 597 / 70 persons | high | yes | — | **evaluation sources of MS1** (CFD co-primary read): excluded |
| Twins or sibling sets (ND-TWINS, etc.) | **no** | — | — | — | licence on request | not available; an author item if wanted |

**Closed and excluded** (never opened for LA1, no row in any list): CASIA-WebFace (H1 source), FRLL and everything
built on it (FRLL-Morphs, MorDIFF, DiM, MAD22 genuine photos), FEI, MAD22, SMDD (training only), FFHQ-Morphs
(development comparison set), the sealed sets (VAL-X / val10 persons, FST, A12SP).

**Overlap checks** (embeddings only; no closed image is opened):
- Reuse the MS1 guard. Every candidate image is compared, by glintr100 cosine at ≥ 0.40, against the existing
  reference embeddings `MS1/celebahq/ref_{casia,ffhq,frgcferet,tt1,cfd,kdef}.npz`. Overlapping identities are dropped
  (MS1 dropped 2,444 CelebA-HQ persons this way).
- Persons in the PN1 test and development ladder hosts and in the sealed FRGC / colorFERET val10 split are excluded
  through the PN1 split files (never valx.csv).
- **FRLL, FEI and MAD22 references:** an embedding-only exclusion against `AR1/frll_src_emb.npz` and an FEI / MAD22
  reference would close the gap. These are closed-set files, so their use (for exclusion only) needs the lead's and
  the author's explicit OK. Without it, the overlap is stated as unchecked: celebrities against volunteers, unlikely
  but not shown.

## 2. The search (WCSS)

- **Embeddings.** Use the same route as every ladder number: `src/AR1/fr.py` (prep_eval.kps, insightface norm_crop,
  glintr100.onnx through `a2f_common.embed_crops('glint')`).
  - CelebA-HQ: the 22,806 embeddings already exist, so this needs 0 GPU.
  - MUCT and MEDS: about 5,800 images.
  - FRGC / colorFERET training persons: about 40,000 images, needed only if those persons are wanted beyond the ladder
    pool.
- **Environment.** `~/dmenv` (torch 2.11, cu128) is frozen and nothing is installed into it. The embedding job builds
  `python -m venv --system-site-packages $TMPDIR/la1env` and installs, with `pip install --no-index --find-links`,
  wheels shipped in the job's pack: onnx, onnx2torch, onnxruntime, insightface and opencv-python-headless, at the
  versions recorded on the DGX. A smoke test on 8 images checks embeddings against the DGX values (cosine ≥ 0.999 per
  image). The GB10 and H100 differ, so the gate is on embeddings, not on logits.
  - Fallback with no GPU at all: onnxruntime-CPU on `lem-cpu-short`, about 1-2 CPU-hours for 6,000 images.
- **All-pairs search.** Cross-identity cosine for every image pair across identities, blocked by database and in GPU
  or CPU matrix blocks.
  - CelebA-HQ: 22,806² / 2 ≈ 2.6 × 10⁸ dot products, minutes on one CPU. MUCT + MEDS: trivial. No nearest-neighbour
    index is needed at this size.
  - For each identity pair, keep the best image pair and the count of image pairs above 0.6.
- **GPU-hours.** 0 for CelebA-HQ (embeddings exist; the search runs on the DGX CPU or `lem-cpu-short`). About 0.2
  H100-hours, or 2 CPU-hours, for MUCT + MEDS embeddings. About 1 H100-hour if all FRGC / colorFERET training images
  are added.
- **Job layout.** One tar in and one tar out. All IO in `$TMPDIR`, `--extra=FORCE_RM_TMPDIR`. Submission goes through
  the dispatcher's queue (`/mnt/t7/smad_next/dispatch/submit_queue/wcss_la1_<name>.cmd`), behind the method-relevant
  jobs. No placeholder jobs.
- **Outputs (no images).** `pairs.csv`: id_a, id_b, identity_a, identity_b, source, cosine, cosine under a second FR
  model, yaw and pitch estimates (from the 106-point landmarks of the aligner), inter-eye distance, sex (CelebA
  attribute / MEDS metadata), aligner outcome for both images, and the label-noise flags (section 5). A summary table
  of counts by cosine band. MEDS rows carry ids only.

## 3. Expected yield (stated uncertainly)

Calibration in hand (glintr100):
- **Our ladder pools.** FRGC 427 persons, 181,902 cross-person image pairs: 4 above 0.4 and 2 above 0.6
  (max 0.686). colorFERET 11,772 pairs: 0 above 0.4. The tail rate is therefore about 1 × 10⁻⁵ per image pair above
  0.6, and the two FRGC pairs may be label errors or relatives.
- **Labelled CelebA** (MS1 calibration, 2,000 images): impostor 99.9th percentile 0.236, false-match rate at 0.40 of
  1.45 × 10⁻⁵. Above 0.6 it is not measured (no event in about 10⁶ pairs).

| Source | cross-identity image pairs | ≥ 0.6 | ≥ 0.7 | ≥ 0.77 |
|---|---|---|---|---|
| CelebA-HQ (22,806 aligned, about 6,200 ids) | ≈ 2.6 × 10⁸ | 0 to about 2,600 (upper bound at 10⁻⁵, which would be mostly label noise); realistic tens to a few hundred identity pairs | few to tens | **0 to a few** (relatives, twins or label errors) |
| MUCT + MEDS (about 5,800 images, about 700 ids) | ≈ 1.7 × 10⁷ | 0 to about 170; realistic 0-10 | 0-2 | ≈ 0 |
| FRGC / colorFERET training persons | ≈ 3 × 10⁸ (FRGC 39k images) | as the ladder rate: tens, mostly multi-image duplicates of the same pair of persons | few | ≈ 0 |

- **Uncertainty.** The impostor tail of glintr100 above 0.6 is not measured on any labelled set we hold; the numbers
  span two orders of magnitude.
- **Most likely outcome.** The same-person range (≥ 0.77) is reached only by relatives or label noise. A realistic
  overlap band is **0.60-0.77**: high look-alikes against the least similar same-person pairs (colorFERET same-person
  pairs reach 0.69; BD1's least-similar quintile is ≤ 0.834).
- **Quality filters and expected loss:**
  - frontal filter of the unchanged aligner: CelebA-HQ 76% pass (22,806 of 30,000), so about 58% of image pairs
    survive;
  - inter-eye distance ≥ the ladder minimum;
  - both photos aligned with a .tem written;
  - the same sex;
  - no pair whose either image failed detection.

  Expect about 50% of candidate pairs to be lost overall. A pose difference cap (|Δyaw| ≤ 15°) removes a further
  10-20%.

## 4. What a later matched arm would need (author item)

- **Images.**
  - Two-person morphs and splices of the look-alike pairs, built with the unchanged engines (OpenCV-style R4, warp R2w4,
    splice S4 with the amendment-7b hull).
  - Same-person counterparts (R3, R2w, S3) from identities with two usable photos, matched to the look-alikes on
    similarity, blend energy D and colour shift D_dc (BD1 measures).
  - This is new image generation with the unchanged engines, so it is an **author item**, as is the CelebA-HQ licence
    check.
- **Go / no-go on the pair count.**
  - **Go** if, after the filters and the label-noise control, ≥ 100 identity pairs at cosine ≥ 0.60 exist, each with
    a same-person counterpart within ±0.03 cosine. That is the scale of Sb's 124 unique training S4 hosts.
  - **No-go** if < 30.
  - Between 30 and 100: an evaluation-only contrast (no training arm), read on the existing networks.
- Nothing enters the frozen method. Any arm is an ablation labelled post-freeze.

## 5. Label-noise control (automatic; no manual check)

A cross-identity pair (a, b) with high cosine is kept as a look-alike only if all of the following hold:
1. **Identity coherence.** Both identities have ≥ 2 usable images, and their own within-identity cosines are
   consistent (median ≥ 0.6). This removes identities whose label is itself mixed.
2. **Cross-pair consistency.** The median cosine over all image pairs between a and b is below the 10th percentile
   of a's and of b's within-identity cosines. A mislabelled same person usually shows high cross similarity for
   all its image pairs. A look-alike shows a high maximum but a lower median.
3. **Near-duplicate check.** Perceptual-hash distance between the two images exceeds a threshold fixed on known
   duplicates. This removes the same photo filed under two identities.
4. **Second model.** glintr100 and the WebFace42M ArcFace model (`a2f_common` 'a2f') both put the pair below each
   identity's within-identity 10th percentile. This guards against one model's error.
5. **Attributes.** Recorded sex agrees (look-alikes are kept only with the same sex). A pair with conflicting
   metadata (MEDS race or sex) is flagged and printed, not used.

The rule cannot exclude true relatives (twins, siblings), who are by definition two persons. They are kept and
flagged. Their share is printed.

## What is needed from the author

1. **CelebA identity labels.** Permission to download `identity_CelebA.txt` and the CelebA-HQ-to-CelebA mapping
   (CelebAMask-HQ), and the licence check of the HF CelebA-HQ mirror (already open).
2. An OK for embedding-only exclusion against FRLL / FEI / MAD22 references, or acceptance that this overlap is
   unchecked.
3. A decision whether to request a twins set (not on disk).
4. Later, the generation of morphs for any matched arm.

## Revision after the pre-run check (`experiments/reviews/PRERUN_LA1_PLAN_20261113.md`, GO WITH FIXES as a plan)

These corrections take precedence over the sections above where they differ.

1. **CelebA labels are on disk; the HQ link is not.** `/mnt/t7/Datasety/datasets_processed/data-celeb-aligned/split.csv`
   holds 202,084 rows (image_id, person_id, split) over 10,177 identities. MS1 already used it for calibration. Those
   images are 128 × 128 JPEG, not 178 × 218 as the MS1 README says. Missing are only the CelebA-HQ-to-CelebA index
   mapping and `CelebAMask-HQ-attribute-anno.txt` (sex), both from the CelebAMask-HQ release. The mapping is never
   rebuilt by embedding matching, which would be circular exactly in the tail being searched. If the mapping cannot
   be obtained, the CelebA-HQ search is not run.
2. **The MS1 overlap guard would remove look-alikes on purpose.** At 0.40 over 31,715 CASIA crops, chance alone flags
   about 37% of images (the TT1 references add about 15%). The flagged images are those similar to many faces, the
   look-alike population itself. With MS1's 9,898 kept images there are only about 4.9 × 10⁷ pairs.
   - Author or lead decision: does CASIA overlap matter for a measurement-only search?
   - If it does, a per-identity rule with a calibrated threshold applies: per-image false-hit rate ≤ 1e-3 over the
     whole reference set, or ≥ 2 of 3 crops of one CASIA identity at ≥ 0.40. Yields are printed with and without the
     guard.
   - The CASIA references were built by MS1 for exclusion with the lead's approval. FRLL / FEI / MAD22 references need
     the same explicit OK.
3. **Label-noise control replaced** (the old rules missed single wrong images and had no defined target):
   - (a) **Image-level test first.** Drop image a_i if its median cosine to its own identity is lower than to any
     other identity, or below a fixed percentile of the genuine distribution.
   - (b) **For a candidate pair (a_i, b_j),** require that a_i is closer to its own identity than to b, and b_j closer
     to its own than to a.
   - (c) The second model (WebFace42M ArcFace) applies the same tests on the same images.
   - (d) **Same-photo duplicates:** glintr100 cosine ≥ 0.97 together with landmark agreement. No perceptual hash,
     because it would need a downscale.
   - All thresholds are fixed on labelled CelebA (128 px), not on the target set. Recall is checked automatically by
     relabelling known same-person images (noise injection).
   - Relatives cannot be detected, since CelebA identities carry no names. Their share is not measured, and this is
     stated.
4. **Sources and route.**
   - **MUCT is dropped.** Its inter-eye distance is 87-93 px, below the 112.7 px filter, and only camera a (751
     images) is frontal. It is reported as descriptive only.
   - **Alignment step added.** The unchanged `73_delin_align` runs on MEDS (and any new source) before embedding,
     because the `.tem` and frontal filters need it.
   - **The GPU route is hard-wired.** `a2f_common` forces `TorchSession(..., "cuda")`, so an onnxruntime-CPU fallback
     would need a code change. `ar1_common` and `a2f_common` also pin local paths.
   - **Recommendation to the author:** run the about 2,000 MEDS images and the second-model embeddings on the DGX
     (minutes); the CPU all-pairs search needs no WCSS. If WCSS is kept, the job pack maps these paths, and the smoke
     test compares 8 images against DGX references.
   - CPU tasks are staged under `staging/LA1/cpu/` for the lead. Queue files are named `wcss_<owner>_<name>.cmd`.
   - The WebFace42M embeddings do not exist yet for CelebA-HQ, so rule (c) is not 0 GPU (about 0.1 GPU-hour).
5. **Go rule.**
   - Count a **disjoint matching**: each identity used once.
   - Same-person counterparts are matched without replacement **from the same source** (CelebA-HQ against
     CelebA-HQ), on cosine ±0.03, pose and inter-eye distance. Matching across sources would leave the source as a
     shortcut; CelebA-HQ is super-resolved texture.
   - **Go:** ≥ 100 disjoint pairs. **No-go:** < 50 (with 30 pairs the AUC 95% interval is about ±0.15). Between the
     two: evaluation-only.
   - The go threshold is near or above the median expectation. Published glintr100-class models reach a false-match
     rate of 1e-6 at about 0.4, so true impostors at ≥ 0.6 should be far rarer than 1e-5.
   - The MS1 CelebA calibration used about 2 × 10⁶ impostor pairs.
6. **Same-person reference range.** It is the S3 hosts' cos_HS 5-95% (0.77-0.93). BD1 prereg's "0.70-0.94" is
   corrected in BD1 amendment 3.
7. **Exclusions.** FRGC / colorFERET training persons would need about 40,000 new embeddings. The 427 ladder persons
   are PN1 hosts and are excluded from LA1. LA1 adds:
   - a person list with a role column and a set-difference assertion against the val10 rule
     (`prep_train.is_val`);
   - a written guarantee that the CelebA-HQ identities LA1 uses stay disjoint from any MS1 held-out set.
8. **Definitions.**
   - yaw and pitch: from the 106-point .tem by the existing `ar1_common` pose helper, or not reported if none exists;
   - sex: from the CelebAMask-HQ attribute file;
   - same-photo threshold: cosine 0.97.

### First step that could be registered now (on disk only): LA1-0, a labelled tail calibration

- **What:** run glintr100 and the WebFace42M ArcFace on about 20,000 images of `data-celeb-aligned` (128 px CelebA,
  labelled; not a closed set), about 2 × 10⁸ impostor pairs.
- **Measures:** the impostor tail at ≥ 0.6 / 0.7 / 0.77, which turns the two-orders-of-magnitude yield guess into a
  number. It also tunes and freezes the label-noise rules with the injection test.
- **Cost:** about 0.5 GPU-hour or less on the DGX, or WCSS once the route above exists.
- **Not registered here:** it needs the lead's go (and the author's, since the instruction named WCSS) and its own
  pre-run check.

Note on times (13 Nov, 18:48 by the machine clock): the freeze ruling was at about 18:27 by the machine clock (the
lead's relay said 18:28). The lead's relay of the LA1 instruction was stamped "18:30" from memory; LA1's first commit is
7121c76 at 18:36:59. Times are taken from `date` and git only (NOTEBOOK, "CORRECTION OF TIMES").

Ownership (13 Nov 18:58 machine clock, lead via the dispatcher): DATA builds the look-alike pair set (search, manifests, checksums, catalogue entry) following this plan. The PR1 owner keeps the hypothesis, the registration and any read that uses the pairs. Nothing is built until the author answers the open decisions (mapping and attribute files, where it runs, the CASIA overlap guard, a twins set).
