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

## Amendment A8 (18:18 CET, throughput; before any T-A / T-B score was read or written)

The shared GB10 GPU runs at 96% utilisation from other jobs; the first group of three small releases scored 1,600
of the 50,010 T-A / T-B images in 285 s (loader workers idle, so GPU-bound), which puts the full set at several
hours per ViT-L/14 release. The DGX pass therefore scores a seeded stratified subsample (`flists/tab_sub.csv`,
seed 20261111 + 40): per split 500 morphs per partner (2,500), 1,000 genuine renders, 400 non-contributor source
renders, and all 5 partner renders (7,810 images); primary five releases first, the two FS variants after. The
readings of A3 are unchanged (rank percentiles among 400 renders per split). The full 50,010-image set stays in
`flists/tab.csv` for a GPU machine if one becomes available (released-detector scoring may run there, A7).

## Amendment A9 (18:50 CET, lead's instruction; before any score of these networks exists)

**Full fits on Athena with the unchanged MADation ViT-L/14 recipe of the record's retrains** (the M3L row as run by
the morph-free networks experiment AD4: `train.py --arch a12_clip_vitl14_madation --regime d0 --split train90
--lofo none --lr 3.33e-06 --res 224 --recipe=v1 --label-smoothing=0 --drop-path=0 --sampler=prior --final=last
--steps=6250 --ft=lora --lora-targets=qv --lora-r=2 --lora-alpha=4 --lora-rs --lora-dropout=0.4
--lora-train-norms=0 --opt=adamw --wd=0.05 --head-lr=3.33e-05 --bs=32 --accum=8 --aug=flip --sched=const
--clip-grad=5 --pos-weight=1`), last checkpoint, seeds 401 to 405, for arms (a) release as is, (c) balanced
partners, (d) balanced partners plus warped halves, (e) history crossing: 20 networks, the arm compositions of
`compose.py` (identical lists to the frozen heads), every row `source = smdd` so regime d0 keeps them. Scored with
AD4's scorer (`ad4_score.py`, the score.py core, no TTA key) on AD4's evaluation manifest (FRLL-Morphs, MorDIFF, DiM,
corrected MAD22, native and E7) and on the AR1 ladder images (snapshot of `AR1/manifest.csv`, sha256 9c69d44f…) plus
the AR1 FRGC/colorFERET halves. Readings and falsifier mapping as for the frozen heads (Part 3, A1, A3), computed by
`read_p3.py` on these networks' scores; reported as a separate block "LoRA fits". Budget: at most 150 A100-hours;
smoke first (8 images, a few steps). If a fit fails it is rerun once with the same seed; a second failure is
reported, never replaced by another seed.

## Amendment A10 (19:25 CET, author's decision of 19:13 via the lead; before arm (f) is built and before any score)

- **Arm (f)** = arm (e) plus JPEG copies made by the existing registered `prep_eval.degrade` (imported, never copied
  or edited; sha256 374408ab…), operations `jpeg90` and `jpeg70` only (`jpeg50` is held out as a test condition;
  `blur1`, `resample50`, `chip` are not used on training images). Assignment fixed per image, independent of the head
  seed: a seeded third of every image that can enter arm (e) (renders, their shrunk copies, halves, their shrunk
  copies, (c) morphs, their shrunk copies; seed 20261111 + 50, by id) gets a JPEG copy, half of those at quality 90 and
  half at 70; the copy is the decoded JPEG stored as lossless PNG (as the evaluation files are). Composition per seed:
  arm (e)'s composition with every assigned image replaced by its JPEG copy, so about one third of each class is a
  JPEG copy (same share in both classes); equal counts kept. Built on the DGX (the platform of the existing
  evaluation files); first verified by reproducing one existing `jpeg70` evaluation file byte for byte with
  `prep_eval`'s own `degrade` + `align` (verification only; the aligner is never used on training images).
  Five LoRA fits of arm (f), seeds 401 to 405, same recipe and settings as A9; frozen-feature heads of (f) as for
  the other arms; Laplacian acceptance as for (e).
- **New reads for all arms** (frozen heads and LoRA fits): flag rate of the FRLL genuine photos under `jpeg70` and
  `jpeg50` (existing evaluation files `eval/frllm/frll_bona/*_{jpeg70,jpeg50}.png`, 204 each; `jpeg90` printed too)
  at (i) the network's own rule (logit ≥ 0, i.e. probability ≥ 0.5) and (ii) the development threshold = the score
  flagging 5% of untouched development photos (AR1 FRGC/colorFERET R0, as A1.5), each with the miss rate at the same
  threshold on the FRLL-Morphs families (per family and pooled over the 4 landmark families). Person-bootstrap
  intervals; every seed printed. Running LoRA tasks score the JPEG frames only if the frames reach Athena before
  they start; otherwise a scoring-only job re-scores the saved trainable parameters (no retraining).

## Amendment A11 (20:05 CET, lead's message after the protocol-network pre-run review F4 / improvement 7; before any of these networks exists)

- **ViT-B/16 LoRA fits** with the record's MADation ViT-B/16 recipe (AD4's M3 command: `--arch a12_clip_vitb16_madation
  --bs=256`, every other flag as A9), last checkpoint, seeds 401 and 402, on `-A plgmultivision-gpu-a100`, for arms
  (a) release, (c) balanced partners, (d) balanced partners with halves as genuine, (e) history-crossed, (f)
  JPEG-crossed: 10 fits (the lead's list named "the rebuilt arm with halves (c)"; both c and d are run so either reading
  is covered; about 9 A100-hours). Same compositions, scorers and manifests as A9 / A10.
- **Additional read for every network (ViT-L/14 and ViT-B/16 fits, frozen heads):** flag rate of each
  history-matched genuine pool (the E7 copies of every FRLL-Morphs, MorDIFF, DiM and corrected-MAD22 cell) at (i) the
  network's own 0.5 rule and (ii) a development threshold set on camera photos only (the score flagging 5% of the
  AR1 FRGC/colorFERET R0 photos), each with the miss rate of that cell's morphs at the same threshold.
- **Validity condition fixed now:** the storage-history comparison counts only if arm (a) shows the failure, i.e. more
  than 10% of some history-matched genuine pool flagged at one of the two thresholds, for that recipe; otherwise the
  storage half of the question is reported as "failure not reproduced for this recipe".
- **Storage strata (checked before any fit):** arms a to d, K = 50, K = 500 hold 256-px files only (arm a also the 733
  release files 257 to 264 px tall); arm e holds 256 px and the 80-px a47-style copies; arm f holds 256 px, 256 px +
  JPEG, 80 px, 80 px + JPEG. Morph share per stratum (seed 401): e 0.371 / 0.371; f 0.367 / 0.379 / 0.370 / 0.372
  (overall 0.371), so class balance holds inside each storage stratum and no seeded repetition is needed.

## Amendment A12, post hoc addendum (11 Nov 21:10 CET; after the independent review `experiments/reviews/REVIEW_SM1_20261111.md`; registered before each item is run; the registered rows and verdicts above stay unchanged)

Everything here is **post hoc** (designed after Part 2 and the frozen Part 3 were read) unless an item says it is
scored for the first time; every Part 3 number carries "our frames, first-test data, arms fixed in advance".

Tonight, zero GPU:
1. **Evaluation-partner reference (review F1).** For every score set of Part 2 (releases on crops; releases on whole
   files; every frozen head, all 5 seeds; the FE header): gap(trained − KE) and gap(KE − matched unused U), both as
   the mean over keys of the per-key difference of means over the 5 partners, 10,000 key-bootstrap draws (seed
   20261111); own-rule miss rate (logit < 0) by partner kind (KP, KE, KU, KX, PP, UU); head-arm DiD of gap(trained −
   KE) between arms trained with and without the five. Reported size of the trace = trained − KE. Trained − U stays
   the registered row; it is biased because U was matched only on cosine to keys, IOD and yaw, and U scores about 1
   logit below other untrained partners on heads that saw none of them.
2. **Sharpness inside storage strata (F2).** Arms d, e, f (seed-401 compositions; 2,000 + 2,000 images): Laplacian-
   variance AUC inside each storage stratum (256 px; 80 px; 256 px + JPEG; 80 px + JPEG), at stored size and at the
   loader's 224 px; and a two-variable rule: 5-fold out-of-fold AUC of a logistic regression on (stratum indicators,
   log variance at 224 px). The pooled 0.72 is never cited as a reduction.
3. **Fixed-threshold paired table (F5)** from the existing head scores, every arm, 5 seeds: at the camera-photo
   threshold (5% of AR1 FRGC/colorFERET R0) and at each head's own rule (logit ≥ 0): flag rates of AR1 halves, R2w
   (both tools), each history-matched pool, untouched FRLL photos, JPEG 90 / 70 / 50, the JPEG increments (JPEG q
   minus untouched, paired on the same 204 photos), and the miss rates at the same threshold (FRLL landmark-4
   pooled; each history-matched cell's morphs; AR1 OpenCV R4). Person-bootstrap intervals of the 5-seed mean.
4. **Rewrite of `result.md`** with the review's section 3 wording; withdrawn statements marked WITHDRAWN with reasons.
   **Class balance of arm f inside storage strata** printed for all five seeds.

12 Nov, CPU (post hoc):
5. **Heads with the release recipe (H-new-4).** The FZ1 recipe (Linear(768, 2) on normalised features, BCE on
   one-hot targets, AdamW lr 1e-2, wd 0.05, the release's warm-up + cosine-restart scheduler per epoch, 40 epochs,
   batch 256, drop_last, clip 5) on the existing arm features, seeds 401 to 405. The release recipe also flips
   images (p 0.5, cached flipped features); flipped features of our arms do not exist, so the refit is **without
   flip** (deviation stated); flipped features would be a short Athena job if wanted. Prediction (review): arm (a)
   diffusion rise ≤ +5 and the a → e reduction < 3 points; falsified if the rise stays ≥ +8.
6. **Border-matched re-read of the Part 3 steps (H-new-3)** with EV1's per-frame border fractions: steps b → b′,
   b′ → c′, c′ → c, c → d, d → e recomputed within border strata (matched pairs where no border-free stratum exists).
   Prediction: b → b′ shrinks by more than half; falsified if it stays within 1 point.
7. **Partner-level variance of SMDD evaluation-split error (H-new-6)** from the T-A scores: EER per evaluation
   partner (its 500 morphs against the 1,000 genuine renders) per release, and a two-way (first contributor x
   partner) bootstrap interval of the pooled EER against the one-way interval. Prediction: per-partner spread > 5
   points and two-way interval ≥ 3x one-way; falsified if spread < 2 points.
8. **File names against image content (F11)**: 100 seeded morphs per split; buffalo_l ArcFace cosine of the morph to
   its named second contributor against the other four partners of the split, and to its named first contributor
   against 20 random renders; share of morphs whose named partner is the most similar of the five.
9. **Logit against sharpness (H-new-2)**: per arm and class of training images (2,000 each, seed 401 heads),
   Spearman correlation of the head logit with the log Laplacian variance at 224 px; prediction: more negative from
   b → K = 50 → b′; falsified if |Δρ| < 0.05 from b to b′.

GPU and build work (each scored for the first time after this registration; Athena `-A plgmultivision-gpu-a100
--exclude=t0010`):
10. **Audit set scored by every LoRA fit (H-new-5)**: a scoring-only job per finished fit rebuilds the network from
    `meta.json` + `last_trainable.pt` (frozen weights from the AD4 pack), scores the 10,055 audit images (whole
    image, the fits' own loader), and the reader of item 1 is applied. Prediction: LoRA arm (a) gives trained − KE
    ≥ 1 logit and the DiD against LoRA arm (c) has an interval above 0; falsified if the interval includes 0 for
    ViT-L/14.
11. **Frozen arm with five random pool partners (H-new-1)**: the N release first-contributor slots, second
    contributors = 5 seeded random valid pool renders that are not audit renders (each used about N / 5 times),
    built with the unchanged engine (leaseB while it exists, else the DGX within the cap), features on Athena, heads
    as Part 3 (5 seeds). Prediction: landmark-7 native EER ≥ 6.5%; falsified if ≤ 5.5%.
12. **ViT-B/16 LoRA fits of arms b and b′**, seeds 401 and 402 (A11 recipe and reads).
13. **History copies at a size not used in training**: the existing 61.2- and 112.7-px copies of the protocol-network
    experiment (`/mnt/t7/smad_next/AF0/img/`) scored by the arm (e) and (f) frozen heads (features on Athena) and,
    if cheap, by their LoRA fits: flag rate at both thresholds against the 80-px copies of the same photos.

A12 implementation notes (11 Nov 21:15, before any score of items 5 to 13):
- Item 10: `sm1_lora_audit.py` + `athena_lora_audit.sbatch` (one scoring-only job over the finished fits, FITS list);
  the network = `common.build_run_model(meta)` + `ad4eval/last_trainable.pt` of the fit's result tar; a fit is
  scored only if 256 rows of its own AD4 evaluation scores are reproduced within 2e-3. Logit = log(p / (1 − p)) of
  the no-TTA score (as `lora_read.py`); the reader of item 1 is applied per fit family (ViT-L/14, ViT-B/16).
- Item 11: the list `armd5.csv` (`pairs_d5.py`: the dose construction of `pairs.py` with K = 5, seed SEED + 35; the
  pool reconstruction must reproduce `armd50.csv` and `armd500.csv` exactly); built on leaseB as an overlay task on
  pack b (same engine and `build.py` files, sha256 checked; 8-pair DGX reference check); features on Athena; heads
  and reads as Part 3 (arm name d5; steps b → d5 and d5 → K = 50 added).
- Item 12: `athena_lora_b2.sbatch` (ARMS b, bp; RECIPE m3; MANIFESTS `sm1lora_manifests_b`); `lora_run.sh` gains
  only the manifest-tar variable (default unchanged) and the armsb image set for b and b′.
- Item 9 uses a 500-draw image bootstrap per class (stated in the script).

## Amendment A13: ViT-B/16 fits on one rented A100 (lead, 11 Nov about 22:10; registered before any fit result)

Athena cannot start the queue tonight (12 of 48 nodes work); the author approved rented machines within tonight's
budget. **All ViT-B/16 LoRA fits of this experiment come from one machine type**: a rented A100 40 GB running the
Docker image `pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime` with the packages pinned as
`src/athena/containers/smad_torch221_cu121_v1.def` (`src/SM1/rented/`, RUNBOOK.md). The ViT-L/14 fits stay on Athena.
- Fits: arms a, c, e, f at seeds 401 and 402 first, then the partner-only arms b and b′ at seeds 401 and 402 (12
  fits; arm d is not in this set). Recipe, compositions, command lines and reads as A11 (`lora_run.sh` RECIPE m3,
  unchanged), with the data read from the once-unpacked packs (same pinned tars as Athena) instead of a per-job RAM
  disk; each fit also scores the audit set (A12 item 10).
- Smoke: 200 steps on arm a seed 401; the Athena ViT-B/16 jobs (3545957 array, 3546034 array) are cancelled only
  after it passes. A failed fit is rerun once unchanged.
- Results: one tar + sha256 per fit, verified, in `/mnt/t7/smad_next/SM1/results_rented/`.
- Note (12 Nov 02:50, before any registered ViT-B/16 reading): the rented machine is an NVIDIA RTX 6000 Ada
  Generation (48 GB), not an A100 (`/mnt/t7/smad_next/vast/sm1b/driver.log`; 1.41 steps/s). The rule stands with
  that machine type: all ViT-B/16 fits of this experiment come from this one RTX 6000 Ada machine.
- Reading (lead, 12 Nov): the first registered ViT-B/16 reading is made when the eighth fit (arms a, c, e, f x seeds
  401, 402) is back; earlier single-seed rows are descriptive and labelled incomplete.

## Amendment A14: rank read of the LoRA audit (12 Nov, registered before any score of Athena job 3547052 is opened)

After the ViT-B/16 review (`experiments/reviews/REVIEW_SM1_VITB_20261112.md`, F6): the LoRA heads are Linear(·, 1) on
normalised features with ‖w‖ about 3.8, so logits are bounded near ±3.8 and trained-partner morphs sit at the ceiling;
the registered H-new-5 threshold (trained − KE ≥ 1 logit, item 10) cannot be reached on such a head. H-new-5 stays as
registered and is reported; the decision read for the ViT-L/14 audit (job 3547052, fits SM1L_a_s401 and s402) is:
- **H-new-D**: within-key AUC of the 5 trained-partner morphs over the 5 KE morphs of the same key (500 keys; AUC per
  key over the 25 pairs, ties one half, averaged over keys; pooled over the 2 seeds by averaging the per-key AUC), 10,000
  key-bootstrap draws (seed 20261111). Prediction: trained − KE < 0.2 logit but AUC ≥ 0.70. Falsified if AUC ≤ 0.60.
  Reported beside it: trained − KE (item 1 reader) and the same AUC for the ViT-B/16 fits (already read by the reviewer).

## Amendment A15 (registered 12 Nov after the pre-run check and the lead's approval; no score exists at registration)

Development data only; no benchmark cell is scored. Saved ViT-B/16 fits SM1B_{a,e,f}_s{401,402} (rebuilt from their
result tars, reproduction check on 256 stored rows) scored on the rented machine sm1b after its last registered fit
(`src/SM1/rented/remote_dev.sh`, `drive_v2.sh dev`; manifest `/mnt/t7/smad_next/SM1/dev_a14/sm1_dev_eval.csv`, 4,152
rows; 3,080 new files, 0.55 GB, sha256 per file):
- development diffusion ladder (DG1 add-on, 536 FRGC / colorFERET hosts): X20 (two-person diffusion mix, morph class),
  REC20 (one-person diffusion reconstruction: a genuine image with the generator's history), SAME20;
- AR1 camera photos R0 and OpenCV morphs R4 of the same 536 hosts (unsoftened, already on the machine);
- AF0 softened copies (112.7 / 61.2 px): R0 of 200 hosts, R4 of 536 hosts.
Readings (logit of the no-TTA score; AR1 person bootstrap, B = 10,000, the same draws for every fit; 2-seed means):
- **H-new-A** (MorDIFF detection is mostly the storage cue): AUC(X20 > AR1 R0) "native" and AUC(X20 > REC20)
  "history-matched". Prediction: e's history-matched AUC ≤ 0.65 and a's AUC drops by ≥ 0.15 from native to history-
  matched. Falsified if e's history-matched AUC ≥ 0.80.
- **H-new-E** (e penalises camera detail): per host, logit(softened R0) − logit(R0), mean over hosts, per strength.
  Prediction: < 0 for e and > 0 for a. Falsified if e's increment ≥ 0.
- Descriptive, scale-free (H-new-B AUC part): paired AUC of a photo against its softened copy (R0 vs R0 soft) for e and
  f; prediction difference < 0.05; falsified if ≥ 0.10 with an interval excluding 0.
Cost: about 0.3 GPU-h on the RTX 6000 Ada (6 networks x 4,152 images x 2 passes, plus 256 check rows each).
Deviation (12 Nov 16:00, dated after the run): A15 ran on lease `sm1dev`, another rented RTX 6000 Ada (sm1b was
destroyed at 15:31:55 before A15 produced a score); same pinned packs, same scorer (sha256 925f372d…), reproduction
check max diff 0.0 on 6 of 6 fits.
Pre-run check (experiment-reviewer, 12 Nov): GO WITH FIXES; fixes applied before any score:
- The reproduction check no longer touches a benchmark row: it rescores the first 256 stored rows of the fit's
  `ar1eval/scores_eval.npz` (all AR1 FRGC/colorFERET R0 camera photos; same scorer, same TTA and resolution) against
  `sm1_ar1_eval.csv`; no benchmark folder or manifest is linked into the dev work folder.
- The machine is not released before the dev step: `drive_v2.sh dev` writes DEV_PLANNED and holds RELEASE until 6 of
  6 dev tars are verified; the remote script is detached; a missing fit tar is logged and skipped.
- Bootstrap unit: the host (536 FRGC / colorFERET hosts; X20 keyed by host, partners re-enter as hosts), B = 10,000,
  seed 20261111. The 200 softened R0 hosts are AF0's `ar1soft_src.csv` (the lead's list). SAME20 is descriptive only.
- H-new-A: native contrast (X20 vs AR1 R0) mixes diffusion history with crop, resolution and file format; the
  history-matched contrast (X20 vs REC20) decides. Zone 0.65 < AUC(e) < 0.80 = undecided.
- H-new-E: floor check on the stored ar1eval scores of the 200 hosts (zero GPU, done before registration): share of R0
  within 0.2 logit of the lower bound −‖w‖ + b: a 0.69 / 0.73, e 0.00 / 0.00, f 0.00 / 0.00. So a's "> 0" part is
  favoured mechanically and is descriptive; the decision is on e only: supported if e's mean increment < 0 with the
  host-bootstrap interval below 0 at both strengths; falsified if e's increment ≥ 0 with the interval above 0 at both;
  otherwise undecided.
- H-new-B AUC part: difference e − f of the paired AUC (photo against its softened copy), both strengths reported.

## Amendment A17: H-n3, stratified identity contrast on the A15 scores (12 Nov, zero GPU; registered before computing)

After the review `experiments/reviews/REVIEW_SM1_12FITS_A15_20261112.md`. Scores: the existing A15 tars (fits a, e, f x
seeds 401, 402; logit of the no-TTA score). Contrast: X20 (two-person mix) over SAME20 (one-person mix), the 536 hosts.
Strata, each pooled over X20 and SAME20: (i) quintiles of the face-box Laplacian variance (`lapvar_box`,
`/mnt/t7/smad_next/FZ2/read_addon_items.csv`); (ii) quintiles of θ, the angle between the two inverted noise maps
(`theta_xT` of DG1's `gen_rows.csv`, joined on list / pool / file). Stratified AUC = AUC within each stratum, averaged
with weights n_X x n_SAME of the stratum. Host bootstrap B = 10,000, seed 20261111 (the A15 draws); 2-seed means.
- **H-n3a**: Laplacian-stratified AUC a − e within ±0.03 (point); falsified if |a − e| > 0.03 with the interval
  excluding 0.
- **H-n3b**: θ-stratified AUC ≤ 0.58 for every arm (point); falsified if any arm > 0.58 with the interval above 0.58.
Unstratified X20-over-SAME20 AUC reported beside them.

## Amendment A16: H-n1, latent-mix path (registered 12 Nov about 23:00 after the author's approval; development data only; no score exists at registration)

Saved ViT-B/16 fits SM1B_{a,e,f}_s{401,402} (rebuilt from their tars; reproduction check on 256 stored AR1 camera-photo
rows) scored on existing DG1 add-on rungs of the 536 FRGC / colorFERET hosts: FRESH1_20, NOISES20, NOISEX20, SEMS20,
SEMX20, MIR20 and REC20 again (3,752 images, 0.24 GB; manifest `/mnt/t7/smad_next/SM1/dev_a16/sm1_dev16_eval.csv`,
per-file sha256 `dev16_files.sha256`). No benchmark cell. About 0.2 GPU-h (RTX 6000 Ada). Host bootstrap B = 10,000
(seed 20261111), 2-seed means, logit of the no-TTA score.
- **H-n1** (arm a's mix signal comes from decoding a latent that is not the photo's own). Prediction: a separates
  FRESH1_20 and NOISES20 from REC20 at AUC ≥ 0.70, while NOISEX20 over NOISES20 and SEMX20 over SEMS20 stay ≤ 0.60;
  e about 0.5 throughout. Falsified if FRESH1_20 and NOISES20 over REC20 are ≤ 0.55 and SEMX20 over SEMS20 ≥ 0.70
  (then a reads semantic mixing). Otherwise undecided. MIR20 over REC20 descriptive.
- Platform (12 Nov 23:10, before any A16 score): WCSS H100 (lem-gpu-short), Python `~/dmenv` (torch 2.11.0+cu128,
  timm 1.0.30, numpy 2.5.2, pillow 12.3.0), not the rented RTX 6000 Ada / torch 2.2.1 of the fits. Platform equivalence
  = each fit's rebuilt network reproduces its 256 stored AR1 camera-photo rows within max |score diff| ≤ 2e-3 (the
  scorer's tolerance); if any fit fails, that fit is not scored, the job is stopped for review and the lead rents an RTX
  6000 Ada instead. Only FRGC / colorFERET AR1 frames, the DG1 rungs and the code / weights are staged (no benchmark
  frame). Script `src/SM1/wcss/wcss_a16.sbatch`.
- Packs: the local copies were deleted in the author-approved disk clean-up; ad4_pack, sm1gpu_img_test and
  sm1lora_manifests_v2 are fetched back from Athena (packs/AD4, packs/SM1) and checked against the recorded sha256
  before upload.
- Command (fresh lease; the lead starts it): `nohup setsid bash /home/narolski/smad-next/src/SM1/rented/drive_v2.sh
  HOST PORT LEASE dev16fresh > LEASE/sm1_dev16.log 2>&1 &` (uploads ad4_pack, test images, manifests v2 (about 22 GB),
  the 6 fit tars and the 0.24 GB of rungs; RELEASE only after 6 of 6 SM1E tars and the machine logs are back).

## Amendment A18: H-n2, does the standard recipe add X-vs-SAME information beyond the measured traces? (registered 12 Nov ~23:45, after the pre-run review `experiments/reviews/PRERUN_SM1_A18_20261112.md`, GO WITH FIXES, all applied; no score exists)

Author's go (12 Nov about 22:55): SAME20 may be labelled genuine for this development experiment, and DG1 shards may
be used for training. Lead's decision: θ is allowed as a floor covariate; the image-statistics-only floor is printed
too. Development data only: no benchmark row anywhere (the fit script links no benchmark folder or manifest; the scorer
runs only on the test shards and the training rows). Claim limited to FRGC test hosts on a single render platform.
- Data (`src/SM1/hn2_lists.py` → `/mnt/t7/smad_next/SM1/hn2/`; existing DG1 add-on images, no new image): 536 FRGC /
  colorFERET hosts, 8 shards of 67. Train = shards 0–5, test = shards 6–7 (all test hosts FRGC, rented-GPU renders):
  disjoint hosts; X20 rows with host and partner on different sides are dropped (2), so the 55 test partner cycles are
  unseen. Arm RS: attack X20 (401), genuine REC20 + SAME20 (804); the only difference between X20 and SAME20 is the
  second person. Arm R is dropped (descriptive only, and already shown by A15 / PN1); a third RS seed replaces it.
  Test: 133 X20, 134 SAME20, 134 REC20. Manifests sha256: train_hn2RS 9f4b056c…, sm1_hn2_test e0b7c840…; 1,606 image
  files with per-file sha256. `flagged` in `read_addon_items.csv` = DG1's input checks (FZ2 `fz2_read.py:124`): a
  wedge or greyscale input, a probable twin pair, or a shared capture date (test: 10 X20, 3 SAME20 flagged).
- Recipe: A11 m3 (CLIP ViT-B/16 + LoRA, `lora_run.sh` command line unchanged: 6,250 steps, batch 256, lr 3.33e-6, LoRA
  r 2 on q, v), seeds 401, 402, 403 (`rented/fit_hn2.sh`, `rented/remote_hn2.sh`; WCSS variant `wcss/wcss_hn2.sbatch`;
  a 200-step smoke fit first). Disclosure (review M1): with 1,205 training rows this is about 1,330 epochs (the SMDD
  fits: about 40); memorisation is possible, so the training-row AUC is reported per fit; the step count is not changed.
  A failed fit is rerun once; a fit with a non-finite loss or scores is never rerun and is reported. Platform: rented
  RTX 6000 Ada (Docker pins as A13) or WCSS H100 (`~/dmenv`, torch 2.11) — the one used is recorded; all A18 fits on
  one platform. Keep rule: one result tar per fit (test and training-row scores, `last_trainable.pt`, `meta.json`,
  train log) back with sha256, and the machine / job logs, before any clean-up.
- **Primary read (registered, review B1 text; cross-fit variant):** Floor F = logistic regression of X20 vs SAME20 on
  (θ, face-box Laplacian, PNG bytes, asymmetry, d). ΔAUC = AUC of a logistic model on (F inputs + network logit) over F
  alone, both cross-fit on test-shard folds (the 55 test partner cycles in 5 folds, seeded; fit on 4, predict the 5th;
  not on the memorised training rows); 2-seed mean (401, 402); bootstrap over partner cycles (B = 10,000, seed
  20261111; `src/SM1/hn2_incr.py`, `src/SM1/hn2_read.py`). **Falsified (signal beyond measured traces) if ΔAUC ≥ 0.05
  with lower bound > 0; supported if the upper bound < 0.03; otherwise undecided.** The decision needs both RS seeds 401
  and 402 finite; with fewer, the verdict is "undecided (incomplete)" (asserted in the reader). Reported with and
  without flagged rows; ΔAUC over the image-statistics floor F_img (F without θ) printed beside it; seed 403 and the
  3-seed mean as a stability check. Secondary: raw, Laplacian- and θ-stratified X20 over SAME20; X20 / SAME20 over
  REC20.
- **Outcome sentences (review B2):** supported → "With this generator and this recipe (6,250 steps on 1,205 images,
  about 1,330 epochs, 2 seeds; FRGC, single render platform), the network adds no X-vs-SAME information beyond simple
  statistics and the noise-angle θ. This does not show that no second-identity signal exists in diffusion morphs."
  Falsified → "With this generator and this recipe (…), the network adds X-vs-SAME information beyond the measured
  traces (θ, sharpness, size, asymmetry); unmeasured render traces are not excluded." Undecided → no claim.
- **Parallel arm, zero GPU (review improvement 1):** linear probe (logistic regression on standardised features) on
  the existing frozen CLIP (clip_mad) and DINOv2 features of the DG1 shards (`/mnt/t7/smad_next/FZ2/results/dgx/out/`),
  trained on X20 vs SAME20 of shards 0–5, scored on shards 6–7, read with the same incremental-over-floor test and
  thresholds (per feature set; `src/SM1/a18_probe.py`), run on the DGX CPU right after this registration.
- Cost: 3 fits x about 78 min (RTX 6000 Ada) or less on H100, + smoke and scoring; about 4 h; upload ad4_pack 11.2 GB
  + 0.6 GB of images.

## Deviation D1 for A16 and A18 (13 Nov ~00:05, before any A16 score or A18 fit)

The WCSS jobs 6308741 (A16) and 6308742 (A18) are queued with a forecast start of 15 Nov 01:00. Platform for both:
one rented RTX 6000 Ada (lease `sm1dg`, 89.221.67.144:16307; Docker `pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime` +
the `smad_torch221_cu121_v1.def` pins), the platform the ViT-B/16 fits were trained and scored on. A16: the
reproduction check tolerance stays max |score diff| ≤ 2e-3 on 256 stored AR1 camera-photo rows per fit (exact
agreement, 0.0, is expected, as on sm1dev). A18: three RS fits, recipe, lists, decision rule and reader unchanged; all
A18 fits on this one platform. Order on the lease: A16 (`drive_v2.sh dev16fresh`), then the A18 smoke and the three
fits (`hn2fresh`). Keep rule: scores, weights and logs fetched and verified before RELEASE; RELEASE plus FAILED on a
verified partial result. The rented copies are the registered ones; the WCSS jobs stay queued until those are
verified, are then cancelled, and any WCSS output is never read.

## Amendment A19: follow-ups of the A16 / A18 review (13 Nov ~08:00; registered before computing; development data only)

After `experiments/reviews/REVIEW_SM1_A16_A18_20261113.md`. CPU only on the DGX (OMP 2, nice 10; its GPU is used by
another owner until 14 Nov morning).
- **H-N1 (noise path; the key one).** The three saved A18 fits (HN2_RS_s401/402/403; rebuilt from `meta.json` +
  `hn2test/last_trainable.pt`) score the existing DG1 rungs NOISEX20, NOISES20, SEMX20, SEMS20, FRESH1_20 and REC20 of
  the test shards 6–7 (134 hosts; `src/SM1/a19_rungs.py`). Reproduction check first: the 401 stored test scores of
  each fit (`hn2test/scores_eval.npz`) must be reproduced within max |score diff| ≤ 2e-3. On the DGX CPU stack (torch
  2.12) this check is expected to FAIL (the stack changes ViT logits by up to 0.09). If it fails, the run is reported
  as "platform not equivalent, ranks only": Spearman rank agreement with the stored rows and the rung AUCs as
  descriptive numbers, no registered verdict; the registered reading then waits for a rented RTX 6000 Ada (the A18
  platform) with the same script. The check is not relaxed. Prediction (2-seed mean 401, 402; host bootstrap):
  NOISEX20 over NOISES20 ≥ 0.90 and SEMX20 over SEMS20 ≤ 0.70 (supported: noise path); falsified (semantic or identity
  path) if SEMX20 over SEMS20 ≥ 0.85 and above NOISEX20 over NOISES20; otherwise undecided. FRESH1_20 over REC20
  descriptive.
- **H-N2 (identity in the output).** glintr100 (AR1 `fr.py` route: prep_eval.kps → norm_crop → a2f glint) cosine of
  each test X20 render to its partner's source photo (AR1 pool `H` of the partner pid) and to the host's photo. Within
  X20 on shard 6 (the shard with saved noise maps; 66 rows), partial Spearman ρ of the A18 network logit (2-seed mean)
  with the render-to-partner cosine, given the extended floor (F + band cosines c0–c3 + 8x8 low-pass cosine + semantic-
  code cosine; ranks residualised by least squares), partner-cycle bootstrap B = 10,000. Falsified if ρ ≤ 0.10 with
  the upper bound < 0.25; supported if ρ ≥ 0.25 with the lower bound > 0.10; otherwise undecided. Also on all 133 X20
  rows given F (descriptive).
- **H-N4 (A16 smoothness).** From the A16 scores: FRESH1_20 over REC20 for arm e, stratified by face-box Laplacian
  quintiles (pooled over FRESH1_20 + REC20, weights n x n), 2-seed mean, host bootstrap. Supported if ≥ 0.45;
  falsified if ≤ 0.40; otherwise undecided.
- Post hoc addendum (not registered, labelled so): the reviewer's extended-floor read of A18, recomputed on shard 6
  (cross-fit on shard-6 partner cycles), and a variant whose extended floor is fit on the training shards 0–5 (codes
  of shards 0–1 fetched from Athena) and combined with the network logit cross-fit on shard 6.

## DRAFT A20 (for the author's decision, not registered): protocol arm with render-matched diffusion controls

Add DG1 shards 0–5 to the protocol training set (PN1's protocol recipe): X20 as attack, REC20 and SAME20 as genuine;
2 arms (protocol with and without the DG1 controls) x 2 seeds, about 6–8 GPU-h (Athena packs exist; or rented). Read
on shards 6–7 (REC20 flag rate at the camera threshold, X20 detection) and on the FFHQ development families. Could
claim: fewer false alarms on diffusion-processed genuine photos, development data, this generator. Could not claim:
second-identity detection, other generators, any benchmark. MorDIFF is built on the same diffusion autoencoder, so a
later benchmark gain would be partly same-family; any frozen benchmark read must state this. Needs: the author's go,
a pre-run review, a registration.

Questions passed to the lead (not acted on): is a half (A's texture on the A–B mean shape) a genuine image under
ruling 1; may the 256-px landmarks be scaled to the 80-px `a47` copies (would enable arm e)?

## Result

`result.md`.
