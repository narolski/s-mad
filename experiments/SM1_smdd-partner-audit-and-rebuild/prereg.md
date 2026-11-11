# SMDD five-partner audit and rebuild of the standard training set (SM1)

Written 11 Nov 2026, 15:50 CET, before any score of this experiment exists and before any score file of any
detector was opened by this owner. Implements ideas `ROUND1_raw.json` data/ideas[1] ("SMDD-T") and
pragmatist/ideas[2] ("SMDD-X"). Already known when this was written: Part 1 counts (below, measured at 15:35, no
score involved) and the SMDD paper's pairing text (checked). SMDD-X is implemented only in part: its history-crossed
arm (e) is skipped (see Data), so only its falsifier text is carried, as non-applicable.

## Known before the run (Part 1, documentation; measured, `p1_structure.json`, `src/SM1/p1_document.py`)

- Training release: 15,000 morphs, 3,853 first contributors (1 to 5 morphs each), **5 second contributors**
  (img054553 3,444; img282038 3,310; img496816 3,260; img337488 2,813; img099545 2,173). All 3,858 contributors are
  files of `os25k_m_t`; none is among the 25,000 genuine renders `os25k_bf_t` (no shared names at all).
- Evaluation release on disk (`SMDD_release_evaluation/m15k_e`, `os25k_bf_e`, `os25k_m_e`): 15,000 morphs, 3,919 first
  contributors, **5 second contributors** (img279570 3,536; img226436 3,331; img141280 3,232; img042475 2,988;
  img005071 1,913), different from the training five. No contributor or genuine name is shared between splits.
- Morph files not 256 x 256: training 733 of 15,000 (4.89%; heights 257 to 264, one 260 x 258); evaluation 417
  (2.78%). All genuine and source renders are 256 x 256.
- Paper (Damer et al., CVPRW 2022, arXiv 2203.06691, HTML version, Section 4; **checked**): "5k of these images are
  chosen randomly as the key morphing images, each is paired with 5 images chosen randomly from the 20k left images
  of the 25k images aimed to create the attacks. This results in 25k morphing pairs." Tool: "OpenCV/dlib morphing
  algorithm ... setting the blending factor to 0.5 and choosing the warping factor randomly from the range
  [0.0,1.0]". After filtering: "the final set of 15k MAs". The release matches "each key has up to 5 partners" but
  the 5 partners are the same 5 renders for every key in each split.

## Hypotheses (plain words)

- H-P (Part 2): released SMDD-trained detectors score a morph higher when its second contributor is one of the five
  training partners than when it is a never-used render (partner memorisation).
- H-R (Part 3): on frozen CLIP features, the SMDD release's pair structure (five partners, disjoint identity pools)
  and its tool change what a head learns; balanced partners and warped halves as genuine images change landmark-cell
  error, the rise under E7, and the flag rate of processed genuine images.

## Data

- Landmarks: genuine renders from `smdd_bona_landmarks_if106.npz` (existing; 3 renders without a face are never
  paired). For `os25k_m_t` no landmark or embedding file exists (checked: every SMDD npz holds the `os25k_bf_t`
  names only), so the existing insightface detector (`FaceAnalysis` buffalo_l, detection + landmark_2d_106, CPU,
  det_size 512, largest face; the `build_arms._if106_one` call) is run on the 3,858 contributors and on 3,000
  seeded non-contributors; buffalo_l ArcFace embeddings in the same pass. Reproduction check: 20 `os25k_bf_t`
  renders through the same pass against the stored if106 points. `.tem` files written from these arrays
  (pixel = normalised x 256), read back with `78_tool_morph.parse_tem`.
- Engine: `scripts/68_hires_morph.morph` as loaded by `scripts/78_tool_morph.py`, unchanged, 256 px in, PNG out
  (`cv2.imwrite`). Wrapper = `src/AF0/af_morph.warped_pair` logic (records the engine's own two float32 warps while it
  runs); halves = `clip(W, 0, 255).astype(uint8)`; asserted on every pair: max |0.5 hA + 0.5 hB − tool output| <= 1.
  Checked on 8 pairs per build that the wrapper's morph is pixel-identical to the unchanged 78 command line.
- **Part 2 audit set.** Keys: 500 renders from `os25k_m_t` minus the 3,858 contributors (in neither class of the
  training release), first 500 valid faces of a seeded permutation (seed 20261111). Trained partners P1..P5 = the
  five. Unused partners U1..U5 from the remaining valid non-contributors: the look-alike table covers `os25k_bf_t`
  only, so it does not allow rank matching here; instead, in order P1..P5, U_j = the candidate minimising
  |mean cos(keys, c) − mean cos(keys, P_j)| + |sd cos(keys, c) − sd cos(keys, P_j)| (ArcFace), without replacement.
  Images: key x P (2,500), key x U (2,500), P_i x P_j and U_i x U_j (10 + 10, i < j), and the 5 + 5 + 500 renders.
- **Part 3 training arms (equal counts: 25,000 genuine-class + N morphs, N = number of release pairs whose both
  contributors have landmarks, at most 15,000; every arm uses N morphs):**
  (a) release as is (`os25k_bf_t` + `m15k_t`, restricted to the same N pairs as (b));
  (b) the same N release pairs re-made with our engine from `os25k_m_t`;
  (c) balanced partners: N pairs from `os25k_bf_t`, each render a partner at most twice, round-robin over a seeded
  render order taking the best-ranked look-alike (`smdd_bona_lookalikes.npz`) still below its cap;
  (d) as (c), genuine class = 12,500 renders + 12,500 halves (both halves of 6,250 of the (c) pairs), drawn per seed;
  (e) history crossing: **skipped** — the existing shrunk copies (`a47/data47/i3/train/smdd_a47e7`) are stored at
  80 x 80, not the originals' 256 x 256, so the landmark rule given by the lead does not allow them;
  (c′) optional, descriptive: balanced partners drawn at random instead of by look-alike rank (separates balance from
  pair similarity, which (c) changes too).
  Note: (b) → (c) also makes every genuine identity a contributor (shared identity pools) and raises pair similarity.
- **Test frames (existing, unchanged; FRLL persons evaluation only):** `eval.csv` FRLL-Morphs amsl, facemorpher,
  opencv, stylegan, webmorph (orig) against `frll_bona` orig (native) and against `*_resmatch_<family>` (E7); MorDIFF
  and the six DiM cells likewise (DiM descriptive); corrected MAD22 `mad22_canonical_E7_inputs_v3_…/native/<family>`
  against `native/BonaFide` (native) and `e7/<family>` (E7); every row of `/mnt/t7/smad_next/AR1/manifest.csv`
  (R0, R2, R2w, R3, R3m, R4, NC, graded, FRLL bench and bridge); plus halves of the 536 AR1 FRGC/colorFERET (H, B)
  pairs built by the wrapper (checked against AR1's existing OpenCV R4 file within 1 grey level). `eval.csv` MAD22
  rows (old subset) are never used.

## Model and recipe

- Part 2: released detectors through the AR1 scoring path (own MTCNN crop `AR1/crop_rgb.py` in the facenet venv, then
  the `a12_released` adapters as `AR1/score.py --mode rel`; copied into `src/SM1/rel_score.py` with the FE and FS
  weight paths added, sha256 checked against `convert.json`). Primary detectors: MADation ViT-B/16, ViT-L/14, FE
  ViT-B/16, FE ViT-L/14, MixFaceNet-MAD. FS ViT-B/16 and FS ViT-L/14: descriptive, outside the falsifier. Score =
  morph logit, no TTA (`logit_noTTA`). Scorer check: 8 FRLL `eval.csv` frames, whole frame, against the existing
  A12REL `scores_eval.npz` (difference < 1e-3).
- Part 3: frozen OpenAI CLIP ViT-L/14 at 224, the MADation FE release's feature: class token → ln_post → projection
  (768-d) → L2 normalisation, with the FE release's own input convention (whole image, `common.ImageItems` PIL
  bilinear resize to 224, BGR, (x − 0.5) / 0.5). Weights: timm `vit_large_patch14_clip_224.openai` (local cache,
  offline) in the QuickGELU tower `vit_large_patch14_clip_quickgelu_224` that OpenAI CLIP and the FE release use;
  checked equal to the FE ViT-L/14 release tower, and the FE release header applied to these features must reproduce
  its A12REL scores on 8 frames. Head: standardise (training-arm mean/std), Linear(768, 1), class-balanced BCE,
  AdamW lr 1e-3, weight decay 1e-4, batch 256, 20 epochs, last epoch; seeds 401 to 405 (init, shuffle, (d) draw).
  Reference row (not an arm): the FE ViT-L/14 release header on the same features.

## Readings

- Part 2, per detector: paired gap = mean over keys of [mean logit of its 5 key x P morphs − mean logit of its 5
  key x U morphs], 95% percentile interval from 10,000 bootstrap draws over keys (seed 20261111); AUC key x P vs
  key x U with the same key bootstrap; per-partner gaps (P_j vs U_j); descriptive two-way (keys x partners)
  bootstrap; logits of the 5 P and 5 U renders as percentiles of the 500 key renders; P x P vs U x U means.
  Keys whose MTCNN crop fails on any of their 10 morphs are dropped (count printed).
- Part 3, per arm and seed: EER per cell, native and E7; rise = EER(E7) − EER(native); means over the 7 landmark
  cells (FRLL amsl, facemorpher, opencv, webmorph; MAD22 FaceMorpher, OpenCV, Webmorph), the 7 FRLL diffusion cells
  (MorDIFF + 6 DiM) and the GAN cells; flag rate of the AR1 FRGC/colorFERET halves and warp-only images (R2w, both
  tools) and of R3m at the head's EER threshold on AR1 FRGC/colorFERET OpenCV R0 vs R4 (primary) and on FRLL OpenCV
  native (secondary); within-person neutral-above-smiling AUC on FRLL genuine frames (primary) and corrected MAD22
  native BonaFide; AR1 AUCs R2w vs R4, R0 vs R4, R3 vs R4. Summary per arm = mean of the 5 seeds' metrics (no score
  fusion), 95% interval from the two-way pigeonhole person bootstrap (`a41_read` Draw, B = 2,000, the same draws for
  all arms and seeds); arm differences paired on the same draws. Every seed printed in CSV.

## Falsifiers (fixed before the run)

- **Part 2 (lead, fixed):** no partner memorisation if the paired gap interval includes 0 for every detector. A
  detector shows memorisation if its interval lies above 0; an interval below 0 is reported as a reversed
  partner effect.
- **SMDD-T (data, ideas[1], verbatim):** "Partner claim dropped if balanced partners vs our tool on release pairs
  differ by less than 1 EER point on the mean of the 7 landmark cells (FRLL 4, corrected MAD22 3) with an interval
  including 0, and the releases' seen-partner vs unseen-partner gap has an interval including 0. Halves arm fails if
  its landmark-cell mean EER is more than 5 points worse than the balanced arm, or if the flag rate on FRGC/colorFERET
  halves at the EER threshold is not at least halved." Applied as: balanced = (c), our tool on release pairs = (b),
  halves arm = (d) vs (c); EER on native cells (E7 printed beside); halves = the AR1 FRGC/colorFERET halves, threshold
  = the primary one above; "releases' gap" = the Part 2 primary detectors.
- **SMDD-X (pragmatist, ideas[2], verbatim):** "SMDD-X ViT-B/16 at the last checkpoint still rises more than 4 points
  under E7 on the diffusion cells (reference +11.39 [8.00, 14.78] from 8 existing networks); or its FRLL
  FaceMorpher/OpenCV E7 error is more than 3 points worse than those 8 networks (3.6/5.8)." Not applicable here: it
  concerns LoRA ViT-B/16 fits of the history-crossed set, which needs arm (e) (skipped) and fits not run in SM1. The
  frozen-head analogues (diffusion-cell E7 rise; FRLL FaceMorpher/OpenCV E7 EER) are printed as descriptive context.

## Guards

Wrapper equality on every pair and against the 78 command line; landmark reproduction; feature-path and scorer
reproduction checks; keys and unused partners outside both training classes (asserted); FRLL, FRGC and FERET persons
never in training; no image operation other than the unchanged engine, PNG writes, the existing MTCNN crop path and
the existing loader resize.

## Stop rule and budget

DGX only; at most 6 CPU processes at nice 10; GPU checked with `nvidia-smi`, under 12 GB. About 1.5 GPU-hours.
Order: smoke pass (50 keys = 500 audit pairs; arms at 500 morphs + 834 genuine, seed 401) written to `result.md`
first, then full scale.

## Command (tested on 8 images)

`src/SM1/{p1_document,landmarks,pairs,build,rel_score,feats,heads,read_p2,read_p3}.py`, each run first with
`--limit 8`; exact command lines in `result.md`.

## Pre-run review

11 Nov 2026, about 16:00 CET, `experiment-reviewer`: **GO WITH FIXES** (1 blocker, 4 majors, minors). Every fix
below is registered here at 16:10 CET, before the smoke pass and before any score of this experiment exists.

## Amendment A1 (registered before any score; from the pre-run review)

1. **Part 2, partner-level test (blocker).** The lead's falsifier stays as written. A detector is said to "show
   partner memorisation" only if (i) its key-bootstrap paired-gap interval lies above 0 **and** (ii) the partner-level
   placebo test passes: on the first 100 keys, each key is also morphed with 20 placebo partners (random valid
   non-contributor renders, not keys, not U; seeded); per partner, mean logit over the 100 keys; one-sided exact
   permutation p of "the 5 trained partners rank above the 25 unused partners (5 matched + 20 placebo)" (Mann-Whitney
   U, all C(30,5) assignments) < 0.05. Printed beside it: the exact sign-flip p over the 5 matched pairs (minimum 1/32)
   and a two-way (keys x partners) bootstrap. Supporting difference-in-differences: the 5,000 key x P / key x U
   images (plus placebo) are also scored by every Part 3 head on whole-image features; gap(arm) for arms (a), (b) (saw
   the five partners) and (b′), (c), (c′), (d) (never saw any of the 30); DiD = gap(a or b) − gap(c′), paired key
   bootstrap. Arm (b) serves as the positive control for test power; the FE ViT-L/14 release header on the same
   whole-image features is printed beside.
2. **SMDD-T partner condition (major).** "The releases' seen-partner vs unseen-partner gap has an interval including
   0" is applied as: no primary detector shows partner memorisation under item 1. The strict reading (every primary
   detector's key-bootstrap interval includes 0) is printed beside. A reversed gap (interval below 0) is not
   memorisation. The 1-point, 5-point and halving rules use the 5-seed mean point estimate; intervals printed beside.
3. **Arm isolation (major).** (c′) is mandatory. New arm (b′): the release's N first-contributor slots kept, each
   second contributor (one of the five) replaced by a random unused `os25k_m_t` render (not a key, U or placebo), each
   replacement used at most twice; this needs landmarks for about 6,000 more non-contributor renders (same insightface
   pass). Steps then read: (a)→(b) tool; (b)→(b′) partner balance only; (b′)→(c′) source pool and shared identity
   pools; (c′)→(c) pair similarity (look-alike vs random); (c)→(d) halves. Pool-cue check: 5-fold head (same recipe,
   seed 401) on 5,000 `os25k_bf_t` vs 5,000 `os25k_m_t` non-contributor renders, out-of-fold AUC.
4. **Responsiveness gate (major).** Per detector, AUC of all audit morphs (key x P and key x U) against the 500 key
   renders; below 0.70 the detector's Part 2 reading is "descriptive" (the audit morphs are not read as morphs).
5. **Halves flag rates (major).** Primary stays. Printed beside: flag rate at the fixed threshold that flags 5% of
   AR1 FRGC/colorFERET R0 photos; AUC halves vs R0; FaceMorpher R2w (cross-tool). EER threshold = the score t at
   which |FPR − FNR| is smallest over the observed scores, flag = score >= t (no interpolation). The halving rule is
   "uninformative" if arm (c)'s flag rate is below 5%.
6. **Partner matching (minor).** Matching cost = sum of standardised absolute differences (pool SD) of mean cos to
   keys, SD of cos to keys, inter-ocular distance (106-point eye centres) and a yaw proxy (nose-tip x offset from the
   eye midpoint / IOD). Per partner: IOD, yaw proxy, MTCNN box size printed.
7. **Seed spread (minor).** Descriptive training-pair bootstrap: per arm 5 extra heads (seeds 401 to 405) on training
   sets resampled with replacement (genuine by render, morphs by pair); spread printed.
8. **Arm (a) size cue (minor).** Sensitivity row (a256): arm (a) restricted to its 256 x 256 morph files.
9. **Scorer path (minor).** `rel_score.py` differs from `AR1/score.py` only in the weight table and in dropping the
   feature hook (diff printed); AR1's `score.py` is run unchanged (into SM1's folder) on 8 SM1 crops and must match
   `rel_score.py` within 1e-5.
10. **Operations (minor).** `.tem` files only under `/mnt/t7/smad_next/SM1/tem` (lists name them explicitly).
    Stages run one after another (never Pool + DataLoader at once). Landmark reproduction tolerance 0.05 px. In (c)
    and (c′) no unordered pair repeats; a render whose 32 look-alikes are all at cap is skipped (it stays genuine-only).
    Descriptive row (d+): 25,000 renders + 12,500 halves (unequal count). Smoke-pass numbers are written as the lead
    asked; the design above does not change after them (bug fixes only, logged). If the run stops partway, falsifiers
    are evaluated only on complete arms (5 seeds) and missing pieces are listed.

## Amendment A2 (16:15 CET, before any score; throughput)

The DGX CPU is oversubscribed (load average 70 to 140 on 20 cores; my nice-10 workers get 10 to 15% of a core each),
so the insightface pass runs at about 1 image per CPU-second. The "extra" landmark stage (6,000 renders) is dropped.
Arm (b′) instead draws its replacement partners from the valid non-contributor pool renders that are not keys, U or
placebo (about 2,475 renders), each used at most 7 times (ceil(N / pool size)); still about 500 times fewer uses
per partner than the release's five (2,173 to 3,444). Everything else in A1.3 is unchanged.

## Amendment A3 (16:45 CET, lead's message after vetting round 2, `ideas/CONSOLIDATED_v2.md` sections 1 and 4; registered before any score of the tests below exists)

Framing corrections: disjoint identity pools of the two classes are SMDD's documented design ("will not go into a
morphing process"), not a finding. The finding is five partner images in total per split, where the paper's sentence
reads naturally as five per key image: "the release differs from the natural reading of the paper", never "a bug".
SMDD-trained detectors reach 0.42 to 2.51% EER on the evaluation split, whose five partners differ, so partner
memorisation is not expected to be a main explanation; the tests decide. Terms: the rebuilt and audit morphs are
for internal use only (T7 and the WCSS project space, never public); the licence text is quoted in `result.md`.

New tests, no new image, run first (released detectors through the Part 2 scoring path: own MTCNN crop, `rel_score.py`,
no-TTA logit; primary five detectors; FS variants descriptive if time allows):
- **T-A, training split against evaluation split.** Score all 15,000 training morphs (`m15k_t`), all 15,000 evaluation
  morphs (`m15k_e`), and 5,000 seeded genuine renders of each split (`os25k_bf_t`, `os25k_bf_e`). Threshold t = EER
  threshold on the training split (its 5,000 genuine vs its 15,000 morphs, rule of A1.5). Miss rate at t per second
  contributor (5 training partners; 5 evaluation partners) and pooled per split; difference = pooled evaluation miss
  rate − pooled training miss rate, interval from 2,000 bootstrap draws over first contributors within each split.
  Reading (lead): a difference within 1 point means partner memorisation is not needed. Caveat fixed now: the
  training morphs are the detectors' own training images, so a larger difference may come from memorising images,
  not partners. Printed beside: evaluation-split EER and the false-alarm rate on evaluation genuine renders at t.
- **T-B, partner ranking.** Score 5,000 seeded non-contributor source renders of each split (`os25k_m_t`, `os25k_m_e`)
  plus the 5 + 5 partner renders. Per detector: percentile of each training partner among the training-split renders
  (higher logit = more attack-like), count in the top 10% (chance of 5 of 5 = 1e-5; binomial p printed); control =
  the 5 evaluation partners among the evaluation-split renders.
- **T-C, file names.** Every file of `m15k_t`, `m15k_e`, `os25k_bf_t`, `os25k_bf_e` against the release's `train.csv` /
  `evaluation.csv` (listed, present, label consistent with folder); every morph name parsed (done in Part 1).
Paired audit addition: a third partner set KE = each key x each of the 5 evaluation-split partners (renders from
`os25k_m_e`, landmarks by the same insightface pass), for a bridge to the original tool: per evaluation partner, mean
logit of our-engine KE morphs beside the mean logit of the original-tool evaluation morphs with that partner (T-A).
Readings of A1.1 unchanged (KE is not part of the placebo set).
**Partner-count dose curve (frozen CLIP ViT-L/14, Part 3 recipe, seeds 401 to 405):** the release's N first-contributor
slots (the keys of arm b) with K different second contributors, K = 5 (arm b: the five), 50, 500, and all ~2,475
available pool renders (arm b′); K = 50 and 500 drawn seeded from the same replacement pool, each used N / K times.
K = 5,000 needs about 2,600 more landmarked renders (dropped in A2); built only if they become available. Read:
5-seed mean native EER on the 7 landmark cells; flag rates of AR1 halves and R2w at the primary and the R0-5%
thresholds. "Flat" (the property is a curiosity for this recipe) = every K within 1 EER point of K = 5 with an
interval including 0, and every flag rate within 5 points of K = 5.
**Rebuild acceptance (Laplacian variance):** per arm, variance of `cv2.Laplacian` (grey, 64-bit float) at the stored
256 px, 2,000 seeded morphs against 2,000 seeded images of the same arm's genuine class; AUC with lower variance =
morph. Also morph against its own two halves (arms c, d). The release arm (a) is expected at >= 0.99. A rebuilt arm
is **accepted** only at AUC <= 0.65; otherwise every reading of that arm is labelled "still separable by sharpness"
and is descriptive, and falsifier readings that involve it are printed but marked not decisive. (Making it pass would
need sharpness-matched negatives, which needs the author's yes for the shrink-and-enlarge path or a blur.) Every
rebuilt file is checked to be 256 x 256.
**Expression:** the existing cue-check expression probe (`src/C_cue_checks`, lower-face thumbnail classifier, as is)
on 5,000 seeded genuine renders and 5,000 seeded release morphs of the training split: smile rate per class.
*Note added 16:55, before running:* the probe reads a fixed pixel box `[300:432, 150:366]` of the eye-aligned 512
frame; SMDD files are 256-px FFHQ-aligned renders, so it cannot run as is without the aligner (a resampling step not
on my allowed list). Substitute, geometry only: logistic probe (standardised, C = 0.1) on the 20 mouth points
(106-point indices 52 to 71) expressed relative to the eye midpoint and divided by the inter-ocular distance,
trained on the AR1 FRLL frames' existing `.tem` files (102 neutral `_03` vs 102 smiling `_08`, 5-fold by person
accuracy printed); applied to the stored if106 points of all genuine renders and, for morphs, to the mean of the two
contributors' points (the engine's own morph geometry; SMDD's tool used a random warp factor, so this is approximate
for release files). Smile rate = share with probability > 0.5, per class.

## Amendment A4 (17:05 CET, lead's message: author approvals; before any score)

- Terms: the author accepts SMDD's condition (derived morphs published and shared with the SMDD authors at release
  time). The exact sentence stays quoted in `result.md`.
- **Arm (e), history crossing, now run in full.** Shrink step = the existing registered call, unchanged:
  `a47_data.py` (sha256 fcd48e1a…) `_one`, i.e. `cv2.imread(IMREAD_COLOR)` → `prep_eval.degrade(img, "R",
  scale=0.3125)` (prep_eval.py sha256 374408ab…, imported unchanged: `cv2.INTER_AREA` 256 → 80 px) → lossless PNG
  (`cv2.imencode`, read back and compared). Run on the DGX only (same OpenCV as the stored copies). Verified first on 8
  genuine renders against the stored copies in `a47/data47/i3/train/smdd_a47e7/os25k_bf_t` (bytes equal required); the
  stored copies are then reused for the genuine renders, and the call is applied to the (c) morphs and their halves.
  Composition per seed (equal counts): genuine class 25,000 = 6,250 renders + 6,250 shrunk renders + 6,250 halves +
  6,250 shrunk halves (disjoint items, seeded draw); morph class N = N/2 (c) morphs + N/2 shrunk copies of the other
  (c) morphs. The loader upsamples an 80-px file to 224 as it does every input. No other resampling code.
- Laplacian-variance acceptance (A3) on every arm including (e): computed at the stored size (256 px; arms a to d)
  and at the loader's 224-px input (all arms; the acceptance number for (e), whose files have two stored sizes).

## Amendment A5 (17:10 CET, bug fix before any score)

The first smoke build stopped on a pair whose render has landmark points outside the 256-px frame: the unchanged
engine raises a cv2.error there (empty crop in `warpAffine`), and the unchanged `78_tool_morph.py` command line skips
such a pair (`fail += 1`). Fixed: (1) `build.py` now records an engine failure as `tool_failed` and writes nothing,
as 78 does; (2) a render is admissible for pairing only if all 106 points lie inside [0, 255] in x and y (367 of the
24,997 genuine renders are excluded; the same rule applies to `os25k_m_t` renders, so N counts release pairs whose
two contributors are both admissible). Excluded renders stay in the genuine class. Lists, smoke subsets and the WCSS
packs are rebuilt with this rule; the 705 files of the aborted smoke build are deleted (made by this experiment).

## Amendment A6 (17:25 CET, throughput; before any score)

My nice-10 processes get about 9% of a core each (measured: 210 CPU-s in 40 min), so an MTCNN crop pass over the
50,010 T-A / T-B images would take about 3 hours. T-A and T-B are therefore scored on whole files: the existing A39
release path (SMDD's own 256-px files, resized to 224 by the loader, then each release's adapter; no crop), all seven
releases in one pass (`rel_multi.py`, each image decoded once, no TTA). Both T-A and T-B compare images of the same
kind under one path (training vs evaluation split; partner render vs other renders), so the framing difference from
the releases' training crops is common to both sides. The Part 2 paired audit keeps the registered crop path as
primary and is also scored on whole files (secondary, the bridge to T-A / T-B).

## Amendment A7 (17:58 CET, lead's decision; before any score of the rebuilt-arm heads)

**Platform rule.** All features that enter one comparison come from one platform. Every feature set used to train
or evaluate the rebuilt-arm heads (training images of all arms; the evaluation, ladder and audit images those heads
are judged on) is extracted on one x86 CUDA machine (Athena or a rented GPU, the lead decides), with the AD4
environment (torch 2.2.1 cu121, timm 1.0.27, pillow 10.2.0, numpy 1.26.4), from a self-contained pack. Features
of the same images made on the DGX (the 14,120 FRLL evaluation frames already extracted) serve only as an equivalence
check on a few hundred images: maximum absolute feature difference, and the AUC difference of one head scored on
both. The released-detector tests (Part 2, T-A, T-B) score released networks and stay on the DGX.

Questions passed to the lead (not acted on): is a half (A's texture on the A–B mean shape) a genuine image under
ruling 1; may the 256-px landmarks be scaled to the 80-px `a47` copies (would enable arm e)?

## Result

`result.md`.
