# Data build requests (data building, DATA): queue

Owner: data-building owner (DATA). Written 13 Nov 2026 about 19:00-19:03 by the machine clock. **Nothing in this file
is built yet.** Builds start only after the lead's go; items marked "author" also need the author's word. Every
recipe uses only the allowed image operations of OWNER_BRIEF.md (the approved warp script `h1_build.py`, the
unchanged OpenCV and FaceMorpher morphers, constant-colour region blanking, existing E7 outputs, lossless PNG) and the
unchanged aligner (`73_delin_align`, `prep_eval.align`). No resampling, compression or new image code. No closed or
sealed set enters any list. Sources and their status: `DATA_CATALOG.md`.

Products already being built by other owners stay with them (catalogue section 4): GAN morphs of GX1 (AG1 owner),
the border rows of the sealed read (FINAL owner), the second-engine block SbFM (AB1 owner).

Each build will deliver: images under `/mnt/t7/smad_next/DATA/<request>/`, a manifest with one row per image
(source ids, role, engine, sha256), a SHA256SUMS file, the builder in `src/DATA/` with its commit, a catalogue row,
and an 8-image test with the real command line before the full run.

## Status (13 Nov 2026, 19:12 machine clock; lead's go received about 19:04)

- Built: D1a (coverage table), D1d (898 of 900 renders), D2 (941 MEDS pairs, ids on /mnt/t7 only), D5 (balanced
  lists, thin). Records: `README.md` in this folder and `DATA_CATALOG.md` section 3b.
- Held by the lead: D1b until an owner registers a use for it.
- Waiting for the author (the lead is asking): D1c, D3, D4, D6, and a verified copy of the record's 33 GB of frames from
  the home disk. Lead's note on D1c: hull-shaped spliced morphs on the OpenCV path are already allowed; only the
  FaceMorpher splice is new.
- Findings: D1d controls have no matching positive family yet (no FaceMorpher two-person morphs on FFHQ). In AG1,
  MIPGAN-II exists only for FRLL persons; GX1 adds FERET and FRGC. In the sources that already record border and eye
  distance, border-free and high-resolution genuine frames come almost only from MEDS: without MEDS, D5 has 9 images
  per cell over 3 cells.

## Summary

| Request | Purpose | Needs | CPU | GPU |
|---|---|---|---|---|
| D1a paired-control coverage table | which positive families lack same-person, warp-only and one-photo controls | nothing (lists only) | under 0.5 h | 0 |
| D1b CelebA-HQ landmark ladder with paired controls | the ladder's controls on a new training source | lead; author for new generation if the lead judges it so | about 4-8 core-hours (estimate) | 0 |
| D1c paired controls for splices with FaceMorpher | splice family on the second engine | author (splice is not on the allowed list by name) | about 1-2 core-hours | 0 |
| D1d MS1 FFHQ one-photo FaceMorpher renders | one-photo control for FFHQ morphs | lead | under 1 core-hour | 0 |
| D2 MEDS cross-encounter pairs | same-person, different-session genuine hard cases | nothing (lists only) | minutes | 0 |
| D3 look-alike pairs (LA1) | similarity-matched two-person against same-person | author (four open decisions) | see LA1 | 0.5 GPU-h (LA1-0) |
| D4 further landmark engines | engine diversity beyond OpenCV and FaceMorpher | author | per engine 2-4 core-hours | 0 |
| D5 border- and resolution-balanced genuine sets | genuine sets where border and eye distance carry no class | nothing (selection from existing frames) | under 0.5 h | 0 |
| D6 raw-file E7 versions of the FRLL photos (CB1) | separate storage history from the aligner effect | **author** (on his decision list) | - | - |

## D1. Paired controls for every positive family

Rule: for each two-person morph tool(A, B) the same pipeline also gives the same-person morph tool(A, A') (A' = another
photo of A), the warp-only image (A warped to the morph's mean shape, A's texture only) and the one-photo render
tool(A, A) or, for generators, the reconstruction of A alone.

### D1a. Coverage table (no images)

- Recipe: read existing manifests only (AR1 `manifest.csv`, AG1 pins, DG1 `validity/*/manifest_full.csv`, SE1,
  PN1 manifests, MS1 `SbM3_files.csv`) and print, per family, engine and person split, the count of two-person
  morphs that have each of the three controls from the same pipeline.
- What is known before counting (from the READMEs):
  - landmark ladder (AR1), OpenCV and FaceMorpher, FRGC / colorFERET: R3, R2w, R2w4 and R2 exist for all 536 hosts
    (R2 equals R0 for OpenCV);
  - MIPGAN-I / II (AG1): R2, R3, R3m, R4 exist; MIPGAN-II only on FRLL persons in AG1 (closed); GX1 adds FERET / FRGC;
  - DiffAE (DG1 set B): REC, SAME, X on the ladder pool;
  - MS1 FFHQ: one photo per person, so no same-person morph and no warp toward a second own photo; R2w4 exists;
  - FaceMorpher splices: none (no splice negatives).
- Sources: manifests only. Expected output: one CSV and a short table. Needs: nothing.

### D1b. CelebA-HQ landmark ladder with its paired controls

- Purpose: the ladder rungs on the approved training source, so a CelebA-HQ morph never arrives without its controls.
- Recipe: the MS1 CelebA-HQ frames already aligned by the unchanged aligner (`smad_next/MS1/celebahq/frames/`, 9,898
  kept images of 3,220 persons; 1,814 persons with two or more images). Per person with two images: R0, R3 = tool(H,
  S), R2w = H warped to mean(H, S), R2w4 = H warped to mean(H, B), R4 = tool(H, B), both unchanged engines (OpenCV
  `78_tool_morph.py`, FaceMorpher `96_facemorpher_tool.py`), PNG. Partner B from the same source and sex, drawn by a
  seeded permutation as in AR1.
- Expected counts: up to 1,814 hosts x 5 rungs x 2 engines, about 18,000 images (fewer after the .tem and eye-distance
  filters). Disk about 10 GB at the AR1 rate.
- Cost: CPU only; time per image not logged in AR1, measured on the 8-image test (estimate 0.5-1.5 s per image per
  core, so about 4-8 core-hours; WCSS `lem-cpu-short` possible).
- Needs: the lead's go. LA1 section 4 calls new morphs with the unchanged engines "an author item"; the author has
  approved CelebA-HQ as a source and the unchanged engines are allowed operations, but whether running them on a new
  source is new generation needing his word is the lead's call. The CelebA-HQ licence check (author, 15 Nov) is open.
  Persons are embedding clusters (no labels): the same-person pair H, S rests on cosine 0.40 grouping.

### D1c. Splice controls with the second engine

- Recipe: FaceMorpher S4 / S3 splices of training hosts with the existing splice code and hull (PN1 / SM1, amendment
  7b), matched negatives as for Sb.
- Counts: 124 training hosts x (S4, S3) = 248, plus matched negatives.
- Needs: **author**: splicing is in use but is not named on the allowed list; the AB1 owner chose "no FaceMorpher
  splices" for SbFM.

### D1d. One-photo FaceMorpher renders on MS1 FFHQ

- Recipe: FaceMorpher tool(H, H) on the 900 MS1 FFHQ frames (OpenCV gives R0 back, so only FaceMorpher).
- Counts: up to 900. Needs: the lead's go.

## D2. NIST MEDS cross-encounter pairs (genuine hard cases)

- Purpose: two genuine photos of one person from different sessions, as hard genuine cases and as the reference
  range for same-person similarity.
- Recipe: from `smad_next/TT1/meds/meds_manifest.csv` (aligned frames already exist; no image operation): every pair
  of aligned images of one person from different encounters, with glintr100 cosine if the existing TT1-M embeddings
  hold it (otherwise listed without), eye distance, border fraction.
- Counts (computed 13 Nov from the manifest, counts only): 865 aligned images of 400 persons; 157 persons with two or
  more encounters hold 560 images and **941 cross-encounter image pairs**.
- Terms: ids only, kept on the machines; no image, file name or identifier in the repository or any figure. The list
  lives under `/mnt/t7/smad_next/DATA/D2/`; the repository gets counts only.
- Needs: nothing for the list. Building morphs of MEDS persons would be new generation on a restricted source: author.

## D3. Look-alike pairs (LA1 plan)

Not acted on. Decisions open in `experiments/LA1_look-alike-pair-search/plan.md`:
1. Permission to obtain the CelebA-HQ-to-CelebA index mapping and the attribute file (CelebAMask-HQ release); the
   CelebA labels are on disk (`data-celeb-aligned/split.csv`), the HQ link is not. Without the mapping the CelebA-HQ
   search is not run.
2. Embedding-only exclusion against FRLL / FEI / MAD22 references, or acceptance that this overlap is unchecked.
3. Whether CASIA overlap matters for a measurement-only search (the 0.40 guard removes look-alikes by construction).
4. Whether to request a twins set (none on disk).
5. Later: generation of morphs for any matched arm (author item).
- The first registrable step, LA1-0 (labelled tail calibration on 128 px CelebA, about 0.5 GPU-hour), needs the
  lead's go, the author's (the instruction named WCSS) and its own pre-run check.

## D4. Further landmark engines

| Engine | Code on disk | Issue | Needs |
|---|---|---|---|
| MediaPipe-478 Delaunay + Poisson (`h1_build.py`, approved warp script) | yes | it is the engine of the closed H1 benchmark; training on it makes H1 a seen engine | author |
| WebMorph (`baselines/webmorph`, PHP + `72_align_morph.R`) | yes, run status not verified | MAD22 and FRLL-Morphs have a WebMorph family; training on it makes those cells seen; the record trained on WebMorph morphs | author |
| dlib-68 landmarks with the OpenCV morpher (`baselines/dlib68`; the record's `cv68_*`) | yes | a landmark-detector variant of an existing engine, not a new blend | author (counts as a new engine variant?) |
| AMSL | outputs only (`baselines/amsl_out`) | no code | not possible |

Recipe for any approved engine: the AR1 rungs (R0, R2w, R3, R4, R2w4) on the training hosts (124-156) and on the
development hosts, unchanged code, PNG, plus the coverage of D1a. Cost about 2-4 core-hours per engine (estimate).

## D5. Border- and resolution-balanced genuine sets

- Purpose: genuine sets in which the aligner's border and the source eye distance are spread like the attack side,
  so neither can carry the class.
- Recipe: selection only from existing aligned frames and their manifests: TT1 `aligned_manifest.csv` (border_frac,
  ied_src, enlarge), MEDS `meds_manifest.csv` (same columns), MS1 FFHQ / CelebA-HQ logs, AR1 / AF0 photos. Strata by
  border fraction (none / any) and eye-distance bins matched to the attack families' distributions on development
  data; seeded draws within strata. No image is changed (blanking a border in would be a new use of constant-colour
  blanking: author).
- Counts: to be printed by stratum before any use; TT1 alone holds 25,241 aligned frames.
- Needs: nothing for the selection lists. Using them in a registered arm needs that owner's registration.

## D6. Raw-file E7 versions of the FRLL photos (request from CB1, relayed by the dispatcher for the lead, 13 Nov)

- Purpose (CB1): separate pure storage history from the aligner effect for the released detectors (example in
  `experiments/CB1_competitor-baselines-corrected-mad22/result.md`: MADation ViT-B/16 AMSL EER 3.91 on raw genuine
  photos against 24.42 on aligned-frame E7, `cb1_released_rs1_bpcer.csv` lines 2 and 4).
- Recipe: not drafted (needs storage code applied to raw FRLL files; FRLL is a closed benchmark).
- Status: **needs the author's word**; on his decision list. No build.
